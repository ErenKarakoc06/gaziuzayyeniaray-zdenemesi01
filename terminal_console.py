        param set <name> <value> : Parametre değerini ayarla
        mode <flight_mode> : Uçuş modunu değiştir
        arm              : Motorları arm et
        disarm          : Motorları disarm et
        takeoff <alt>   : Belirtilen yüksekliğe kalk
        land            : İniş yap
        rtl             : Return to Launch
        wp list         : Waypoint'leri listele
        wp clear        : Tüm waypoint'leri temizle
        calibrate       : Kalibrasyon menüsü
        logs           : Log dosyalarını göster
        """
        self.write_terminal(help_text, "info")

    def handle_set_command(self, params):
        try:
            param_name, value = params.split()
            self.write_terminal(f"Parametre ayarlanıyor: {param_name} = {value}\n", "system")
            # TODO: MAVLink parameter_set mesajı gönder
        except ValueError:
            self.write_terminal("Hata: Geçersiz set komutu formatı. Örnek: set PARAM_NAME VALUE\n", "error")

    def apply_filter(self):
        filter_text = self.log_filter.text().lower()
        log_level = self.log_level.currentText()
        
        # Mevcut içeriği geçici olarak sakla
        current_text = self.terminal_output.toPlainText()
        self.terminal_output.clear()
        
        # Filtreleme uygula
        for line in current_text.split('\n'):
            if filter_text in line.lower():
                if log_level == "ALL" or f"[{log_level}]" in line:
                    self.terminal_output.appendPlainText(line)

    def handle_command(self, command):
        """MAVLink komutlarını işle ve yanıtları göster"""
        parts = command.lower().split()
        if not parts:
            return

        cmd = parts[0]
        if cmd == "mode":
            if len(parts) > 1:
                self.change_flight_mode(parts[1])
            else:
                self.write_terminal("Hata: Uçuş modu belirtilmedi\n", "error")
        
        elif cmd == "arm":
            self.arm_vehicle()
        
        elif cmd == "disarm":
            self.disarm_vehicle()
        
        elif cmd == "takeoff":
            if len(parts) > 1:
                try:
                    altitude = float(parts[1])
                    self.takeoff_vehicle(altitude)
                except ValueError:
                    self.write_terminal("Hata: Geçersiz yükseklik değeri\n", "error")
            else:
                self.write_terminal("Hata: Yükseklik belirtilmedi\n", "error")
        
        elif cmd == "land":
            self.land_vehicle()
        
        elif cmd == "rtl":
            self.rtl_vehicle()
        
        elif cmd == "wp":
            if len(parts) > 1:
                if parts[1] == "list":
                    self.list_waypoints()
                elif parts[1] == "clear":
                    self.clear_waypoints()
                else:
                    self.write_terminal("Hata: Geçersiz waypoint komutu\n", "error")
            else:
                self.write_terminal("Hata: Waypoint alt komutu belirtilmedi\n", "error")
        
        elif cmd == "calibrate":
            self.show_calibration_menu()
        
        elif cmd == "logs":
            self.show_logs()

    def change_flight_mode(self, mode):
        valid_modes = ["stabilize", "altitude", "position", "auto", "guided", "loiter", "rtl", "land"]
        if mode.lower() in valid_modes:
            self.write_terminal(f"Uçuş modu değiştiriliyor: {mode.upper()}\n", "system")
            # TODO: MAVLink set_mode mesajı gönder
        else:
            self.write_terminal(f"Hata: Geçersiz uçuş modu. Geçerli modlar: {', '.join(valid_modes)}\n", "error")

    def arm_vehicle(self):
        self.write_terminal("Araç arm ediliyor...\n", "system")
        # TODO: MAVLink arm komutu gönder

    def disarm_vehicle(self):
        self.write_terminal("Araç disarm ediliyor...\n", "system")
        # TODO: MAVLink disarm komutu gönder

    def takeoff_vehicle(self, altitude):
        self.write_terminal(f"Kalkış yapılıyor... Hedef yükseklik: {altitude}m\n", "system")
        # TODO: MAVLink takeoff komutu gönder

    def land_vehicle(self):
        self.write_terminal("İniş yapılıyor...\n", "system")
        # TODO: MAVLink land komutu gönder

    def rtl_vehicle(self):
        self.write_terminal("RTL (Return to Launch) başlatılıyor...\n", "system")
        # TODO: MAVLink RTL komutu gönder

    def list_waypoints(self):
        self.write_terminal("Waypoint'ler getiriliyor...\n", "system")
        # TODO: MAVLink mission_request_list mesajı gönder

    def clear_waypoints(self):
        self.write_terminal("Waypoint'ler temizleniyor...\n", "system")
        # TODO: MAVLink mission_clear_all mesajı gönder

    def show_calibration_menu(self):
        calibration_text = """
Kalibrasyon Seçenekleri:
1. İvmeölçer Kalibrasyonu
2. Pusula Kalibrasyonu
3. Jiroskop Kalibrasyonu
4. Seviye Kalibrasyonu
5. ESC Kalibrasyonu
6. Radyo Kalibrasyonu

Kalibrasyon başlatmak için: calibrate <numara>
"""
        self.write_terminal(calibration_text, "info")

    def show_logs(self):
        self.write_terminal("Log dosyaları getiriliyor...\n", "system")
        # TODO: MAVLink log_request_list mesajı gönder

    def handle_mavlink_message(self, message):
        """MAVLink mesajlarını işle ve terminalde göster"""
        msg_type = message.get_type()
        
        if msg_type == "STATUSTEXT":
            severity = message.severity
            text = message.text
            
            if severity <= 3:  # ERROR
                level = "error"
            elif severity <= 4:  # WARNING
                level = "warning"
            elif severity <= 6:  # INFO
                level = "info"
            else:  # DEBUG
                level = "debug"
            
            self.write_terminal(f"{text}\n", level)
        
        elif msg_type == "COMMAND_ACK":
            result = message.result
            if result == 0:  # MAV_RESULT_ACCEPTED
                self.write_terminal("Komut başarıyla kabul edildi\n", "info")
            else:
                self.write_terminal(f"Komut hatası: {result}\n", "error")