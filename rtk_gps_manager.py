                self.position_table.setItem(2, 1, QTableWidgetItem(f"{alt:.2f}m"))
                
                # RTK kalite durumunu güncelle
                status_text = {
                    0: "Geçersiz",
                    1: "Standalone",
                    2: "DGPS",
                    4: "RTK Fix",
                    5: "RTK Float"
                }.get(quality, "Bilinmiyor")
                
                self.status_label.setText(f"Durum: {status_text} ({satellites} uydu, HDOP: {hdop:.1f})")
                self.rtk_status_changed.emit(status_text)
                
                # Pozisyon sinyali gönder
                self.position_updated.emit(lat, lon, alt)
                
            except ValueError as e:
                print(f"GGA parse hatası: {str(e)}")

    def _parse_rmc(self, line):
        parts = line.split(',')
        if len(parts) >= 12:
            try:
                # RMC mesajını parse et
                status = parts[2]
                speed = float(parts[7]) * 1.852  # knots to km/h
                course = float(parts[8])
                date = parts[9]
                
                # Ek bilgileri güncelle
                if hasattr(self, 'speed_label'):
                    self.speed_label.setText(f"Hız: {speed:.1f} km/h")
                if hasattr(self, 'course_label'):
                    self.course_label.setText(f"Yön: {course:.1f}°")
                
            except ValueError as e:
                print(f"RMC parse hatası: {str(e)}")

    def closeEvent(self, event):
        self.disconnect_rtk()
        event.accept()