        geotag_group.setLayout(geotag_layout)
        layout.addWidget(geotag_group)

        self.setLayout(layout)

    def load_log_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Log Dosyası Seç",
            "",
            "Log Dosyaları (*.bin *.log);;Tüm Dosyalar (*.*)"
        )
        
        if file_path:
            try:
                # Log dosyasını oku
                self.log_data = self.parse_log_file(file_path)
                self.file_label.setText(f"Dosya: {os.path.basename(file_path)}")
                QMessageBox.information(self, "Başarılı", "Log dosyası yüklendi!")
            except Exception as e:
                QMessageBox.warning(self, "Hata", f"Log dosyası yüklenemedi: {str(e)}")

    def parse_log_file(self, file_path):
        # Log formatını kontrol et
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.bin':
            return self.parse_binary_log(file_path)
        elif ext == '.log':
            return self.parse_text_log(file_path)
        else:
            raise ValueError("Desteklenmeyen log formatı")

    def parse_binary_log(self, file_path):
        # Binary log parser
        data = {}
        try:
            with open(file_path, 'rb') as f:
                # TODO: Binary log format parsing
                # ArduPilot binary log format implementasyonu
                pass
            return data
        except Exception as e:
            raise Exception(f"Binary log parse hatası: {str(e)}")

    def parse_text_log(self, file_path):
        # Text log parser
        data = {
            'ATTITUDE': [],
            'GPS': [],
            'CURRENT': [],
            'BATTERY': [],
            'RCIN': [],
            'SERVO_OUTPUT': [],
            'IMU': []
        }
        
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    if line.startswith('ATTITUDE'):
                        # Örnek: ATTITUDE,timestamp,roll,pitch,yaw
                        parts = line.strip().split(',')
                        data['ATTITUDE'].append({
                            'timestamp': float(parts[1]),
                            'roll': float(parts[2]),
                            'pitch': float(parts[3]),
                            'yaw': float(parts[4])
                        })
                    elif line.startswith('GPS'):
                        # GPS verilerini parse et
                        parts = line.strip().split(',')
                        data['GPS'].append({
                            'timestamp': float(parts[1]),
                            'lat': float(parts[2]),
                            'lon': float(parts[3]),
                            'alt': float(parts[4]),
                            'hdop': float(parts[5])
                        })
                    # Diğer veri tipleri için benzer parsing
            return data
        except Exception as e:
            raise Exception(f"Text log parse hatası: {str(e)}")

    def analyze_log(self):
        if not self.log_data:
            QMessageBox.warning(self, "Uyarı", "Önce log dosyası yükleyin!")
            return

        analysis_type = self.analysis_type.currentText()
        
        try:
            if analysis_type == "Uçuş Performansı":
                results = self.analyze_flight_performance()
            elif analysis_type == "Batarya Analizi":
                results = self.analyze_battery()
            elif analysis_type == "Motor Performansı":
                results = self.analyze_motor_performance()
            elif analysis_type == "Sensör Sağlığı":
                results = self.analyze_sensor_health()
            elif analysis_type == "GeoTag Analizi":
                results = self.analyze_geotag()
            
            self.display_results(results)
            self.analysis_completed.emit(results)

        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Analiz hatası: {str(e)}")

    def analyze_flight_performance(self):
        results = {}
        
        # Uçuş süresi
        if 'GPS' in self.log_data and self.log_data['GPS']:
            start_time = self.log_data['GPS'][0]['timestamp']
            end_time = self.log_data['GPS'][-1]['timestamp']
            flight_time = end_time - start_time
            results['flight_time'] = flight_time
        
        # Maksimum yükseklik
        if 'GPS' in self.log_data:
            max_alt = max(point['alt'] for point in self.log_data['GPS'])
            results['max_altitude'] = max_alt
        
        # Ortalama hız
        # TODO: Hız hesaplaması
        
        # Stabilite analizi
        if 'ATTITUDE' in self.log_data:
            roll_std = np.std([point['roll'] for point in self.log_data['ATTITUDE']])
            pitch_std = np.std([point['pitch'] for point in self.log_data['ATTITUDE']])
            results['stability'] = {
                'roll_deviation': roll_std,
                'pitch_deviation': pitch_std
            }
        
        return results

    def analyze_battery(self):
        results = {}
        
        if 'BATTERY' in self.log_data:
            voltages = [point.get('voltage', 0) for point in self.log_data['BATTERY']]
            currents = [point.get('current', 0) for point in self.log_data['BATTERY']]
            
            results['min_voltage'] = min(voltages)
            results['max_current'] = max(currents)
            results['avg_power'] = np.mean(np.array(voltages) * np.array(currents))
            
            # Voltage sag analizi
            voltage_sag = max(voltages) - min(voltages)
            results['voltage_sag'] = voltage_sag
            
            # Batarya sağlığı değerlendirmesi
            health_score = self.evaluate_battery_health(voltages, currents)
            results['health_score'] = health_score
        
        return results

    def evaluate_battery_health(self, voltages, currents):
        # Batarya sağlığı skorlama algoritması
        # 0-100 arası bir skor döndürür
        try:
            voltage_stability = 100 - (np.std(voltages) * 10)
            current_efficiency = 100 - (np.mean(currents) / max(currents) * 100)
            
            health_score = (voltage_stability + current_efficiency) / 2
            return max(0, min(100, health_score))
        except:
            return 0

    def display_results(self, results):
        self.results_table.setRowCount(0)
        
        for key, value in results.items():
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            
            # Parametre adı
            self.results_table.setItem(row, 0, QTableWidgetItem(key))
            
            # Değer
            if isinstance(value, dict):
                value_str = json.dumps(value, indent=2)
            else:
                value_str = str(value)
            self.results_table.setItem(row, 1, QTableWidgetItem(value_str))
            
            # Durum değerlendirmesi
            status = self.evaluate_parameter_status(key, value)
            status_item = QTableWidgetItem(status)
            if status == "İyi":
                status_item.setBackground(Qt.GlobalColor.green)
            elif status == "Orta":
                status_item.setBackground(Qt.GlobalColor.yellow)
            else:
                status_item.setBackground(Qt.GlobalColor.red)
            self.results_table.setItem(row, 2, status_item)

    def evaluate_parameter_status(self, parameter, value):
        # Parametre değerlerini değerlendir
        if parameter == 'flight_time':
            if value > 600:  # 10 dakikadan uzun uçuş
                return "İyi"
            elif value > 300:  # 5 dakikadan uzun uçuş
                return "Orta"
            else:
                return "Kötü"
        elif parameter == 'max_altitude':
            if value < 400:
                return "İyi"
            elif value < 500:
                return "Orta"
            else:
                return "Kötü"
        elif parameter == 'health_score':
            if value > 80:
                return "İyi"
            elif value > 60:
                return "Orta"
            else:
                return "Kötü"
        return "Değerlendirilmedi"

    def export_report(self):
        if not self.log_data:
            QMessageBox.warning(self, "Uyarı", "Önce analiz yapın!")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Raporu Kaydet",
            f"flight_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            "HTML Dosyaları (*.html)"
        )
        
        if file_path:
            try:
                self.generate_html_report(file_path)
                QMessageBox.information(self, "Başarılı", "Rapor kaydedildi!")
            except Exception as e:
                QMessageBox.warning(self, "Hata", f"Rapor oluşturma hatası: {str(e)}")

    def generate_html_report(self, file_path):
        # HTML rapor şablonu
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Uçuş Analiz Raporu</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background-color: #f0f0f0; padding: 10px; }
                .section { margin: 20px 0; }
                .good { color: green; }
                .medium { color: orange; }
                .bad { color: red; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f0f0f0; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Uçuş Analiz Raporu</h1>
                <p>Oluşturulma Tarihi: {date}</p>
            </div>
            {content}
        </body>
        </html>
        """

        # Rapor içeriğini oluştur
        content = "<div class='section'><h2>Analiz Sonuçları</h2><table>"
        content += "<tr><th>Parametre</th><th>Değer</th><th>Durum</th></tr>"
        
        for row in range(self.results_table.rowCount()):
            param = self.results_table.item(row, 0).text()
            value = self.results_table.item(row, 1).text()
            status = self.results_table.item(row, 2).text()
            
            status_class = ""
            if status == "İyi":
                status_class = "good"
            elif status == "Orta":
                status_class = "medium"
            else:
                status_class = "bad"
            
            content += f"<tr><td>{param}</td><td>{value}</td><td class='{status_class}'>{status}</td></tr>"
        
        content += "</table></div>"

        # Grafikleri ekle
        if hasattr(self, 'plot_data'):
            content += "<div class='section'><h2>Grafikler</h2>"
            for plot_name, plot_path in self.plot_data.items():
                content += f"<img src='{plot_path}' alt='{plot_name}' style='max-width: 100%;'><br>"
            content += "</div>"

        # HTML dosyasını oluştur
        html_content = html_template.format(
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            content=content
        )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)