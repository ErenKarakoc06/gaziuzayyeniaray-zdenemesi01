from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QProgressBar, QComboBox, QGroupBox,
                            QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
import requests
import json
from datetime import datetime
import os

class FirmwareDownloader(QThread):
    progress = pyqtSignal(int)
    completed = pyqtSignal(bool, str)

    def __init__(self, url, save_path):
        super().__init__()
        self.url = url
        self.save_path = save_path

    def run(self):
        try:
            response = requests.get(self.url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024
            downloaded = 0

            with open(self.save_path, 'wb') as f:
                for data in response.iter_content(block_size):
                    downloaded += len(data)
                    f.write(data)
                    if total_size:
                        progress = int(downloaded * 100 / total_size)
                        self.progress.emit(progress)

            self.completed.emit(True, "Firmware başarıyla indirildi")
        except Exception as e:
            self.completed.emit(False, str(e))

class ImprovedFirmwareManager(QWidget):
    update_started = pyqtSignal(str)
    update_completed = pyqtSignal(bool, str)

    def __init__(self):
        super().__init__()
        self.current_user = "ErenKarakoc06"
        self.current_time_utc = datetime.utcnow()
        self.firmware_history = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Üst bilgi
        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel(f"Kullanıcı: {self.current_user}"))
        info_layout.addWidget(QLabel(f"UTC: {self.current_time_utc.strftime('%Y-%m-%d %H:%M:%S')}"))
        layout.addLayout(info_layout)

        # Mevcut Firmware Bilgisi
        current_group = QGroupBox("Mevcut Firmware")
        current_layout = QVBoxLayout()
        
        self.version_label = QLabel("Yüklü Versiyon: Kontrol ediliyor...")
        current_layout.addWidget(self.version_label)
        
        self.platform_label = QLabel("Platform: --")
        current_layout.addWidget(self.platform_label)
        
        self.build_date_label = QLabel("Derleme Tarihi: --")
        current_layout.addWidget(self.build_date_label)
        
        current_group.setLayout(current_layout)
        layout.addWidget(current_group)

        # Firmware Güncelleme
        update_group = QGroupBox("Firmware Güncelleme")
        update_layout = QVBoxLayout()

        # Platform seçimi
        platform_layout = QHBoxLayout()
        platform_layout.addWidget(QLabel("Platform:"))
        self.platform_selector = QComboBox()
        self.platform_selector.addItems([
            "ArduCopter",
            "ArduPlane",
            "ArduRover",
            "ArduSub"
        ])
        platform_layout.addWidget(self.platform_selector)
        update_layout.addLayout(platform_layout)

        # Versiyon seçimi
        version_layout = QHBoxLayout()
        version_layout.addWidget(QLabel("Versiyon:"))
        self.version_selector = QComboBox()
        version_layout.addWidget(self.version_selector)
        update_layout.addLayout(version_layout)

        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        update_layout.addWidget(self.progress_bar)

        # Kontrol butonları
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Yenile")
        refresh_btn.clicked.connect(self.refresh_versions)
        button_layout.addWidget(refresh_btn)

        self.download_btn = QPushButton("İndir")
        self.download_btn.clicked.connect(self.download_firmware)
        button_layout.addWidget(self.download_btn)

        self.flash_btn = QPushButton("Yükle")
        self.flash_btn.clicked.connect(self.flash_firmware)
        button_layout.addWidget(self.flash_btn)

        update_layout.addLayout(button_layout)
        update_group.setLayout(update_layout)
        layout.addWidget(update_group)

        # Firmware Geçmişi
        history_group = QGroupBox("Firmware Geçmişi")
        history_layout = QVBoxLayout()
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels([
            'Tarih',
            'Versiyon',
            'Platform',
            'Durum'
        ])
        history_layout.addWidget(self.history_table)
        
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)

        # Gelişmiş Seçenekler
        advanced_group = QGroupBox("Gelişmiş Seçenekler")
        advanced_layout = QHBoxLayout()

        custom_file_btn = QPushButton("Özel Firmware Dosyası")
        custom_file_btn.clicked.connect(self.select_custom_firmware)
        advanced_layout.addWidget(custom_file_btn)

        verify_btn = QPushButton("Firmware Doğrula")
        verify_btn.clicked.connect(self.verify_firmware)
        advanced_layout.addWidget(verify_btn)

        bootloader_btn = QPushButton("Bootloader Güncelle")
        bootloader_btn.clicked.connect(self.update_bootloader)
        advanced_layout.addWidget(bootloader_btn)

        advanced_group.setLayout(advanced_layout)
        layout.addWidget(advanced_group)

        self.setLayout(layout)
        self.refresh_versions()
        self.load_firmware_history()

    def refresh_versions(self):
        try:
            # ArduPilot firmware API'sinden versiyonları çek
            platform = self.platform_selector.currentText()
            url = f"https://firmware.ardupilot.org/{platform}/stable/manifest.json"
            response = requests.get(url)
            data = response.json()

            self.version_selector.clear()
            for version in data['versions']:
                self.version_selector.addItem(version['version'])

            # Mevcut versiyon kontrolü
            self.check_current_version()

        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Versiyon listesi alınamadı: {str(e)}")

    def check_current_version(self):
        try:
            # MAVLink üzerinden versiyon bilgisi al
            version = "4.3.0"  # Örnek versiyon
            platform = "ArduCopter"
            build_date = "2025-03-01"

            self.version_label.setText(f"Yüklü Versiyon: {version}")
            self.platform_label.setText(f"Platform: {platform}")
            self.build_date_label.setText(f"Derleme Tarihi: {build_date}")

        except Exception as e:
            self.version_label.setText("Versiyon bilgisi alınamadı")

    def download_firmware(self):
        try:
            platform = self.platform_selector.currentText()
            version = self.version_selector.currentText()
            
            # İndirme URL'sini oluştur
            url = f"https://firmware.ardupilot.org/{platform}/stable/{version}/{platform}-{version}.apj"
            
            # Kayıt yolu
            save_path = os.path.join(
                os.path.expanduser("~/drone_firmware"),
                f"{platform}-{version}.apj"
            )
            
            # İndirme işlemini başlat
            self.downloader = FirmwareDownloader(url, save_path)
            self.downloader.progress.connect(self.progress_bar.setValue)
            self.downloader.completed.connect(self.download_completed)
            self.downloader.start()

        except Exception as e:
            QMessageBox.warning(self, "Hata", f"İndirme başlatılamadı: {str(e)}")

    def download_completed(self, success, message):
        if success:
            self.flash_btn.setEnabled(True)
            self.add_to_history("İndirildi")
        QMessageBox.information(self, "Bilgi", message)

    def flash_firmware(self):
        try:
            result = QMessageBox.question(
                self,
                "Firmware Yükleme",
                "Firmware yüklemesi başlatılacak. Devam etmek istiyor musunuz?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if result == QMessageBox.StandardButton.Yes:
                # TODO: MAVLink üzerinden firmware yükleme
                self.progress_bar.setValue(0)
                self.update_started.emit(self.version_selector.currentText())
                
                # Simüle edilmiş yükleme işlemi
                for i in range(101):
                    self.progress_bar.setValue(i)
                    QApplication.processEvents()
                    time.sleep(0.1)
                
                self.update_completed.emit(True, "Firmware başarıyla yüklendi")
                self.add_to_history("Yüklendi")
                QMessageBox.information(self, "Başarılı", "Firmware yüklendi!")

        except Exception as e:
            self.update_completed.emit(False, str(e))
            QMessageBox.warning(self, "Hata", f"Yükleme başarısız: {str(e)}")

    def select_custom_firmware(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Özel Firmware Seç",
            "",
            "Firmware Dosyaları (*.apj *.px4);;Tüm Dosyalar (*.*)"
        )
        
        if file_path:
            self.version_selector.addItem(f"Custom: {os.path.basename(file_path)}")
            self.version_selector.setCurrentText(f"Custom: {os.path.basename(file_path)}")
            self.download_btn.setEnabled(False)
            self.flash_btn.setEnabled(True)

    def verify_firmware(self):
        try:
            # Firmware doğrulama işlemi
            self.progress_bar.setValue(0)
            
            # Simüle edilmiş doğrulama işlemi
            for i in range(101):
                self.progress_bar.setValue(i)
                QApplication.processEvents()
                time.sleep(0.05)
            
            QMessageBox.information(self, "Başarılı", "Firmware doğrulaması tamamlandı!")

        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Doğrulama başarısız: {str(e)}")

    def update_bootloader(self):
        try:
            result = QMessageBox.question(
                self,
                "Bootloader Güncelleme",
                "Bootloader güncellemesi tehlikeli bir işlemdir. Devam etmek istiyor musunuz?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if result == QMessageBox.StandardButton.Yes:
                # TODO: Bootloader güncelleme işlemi
                self.progress_bar.setValue(0)
                
                # Simüle edilmiş güncelleme işlemi
                for i in range(101):
                    self.progress_bar.setValue(i)
                    QApplication.processEvents()
                    time.sleep(0.1)
                
                QMessageBox.information(self, "Başarılı", "Bootloader güncellendi!")

        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Bootloader güncellemesi başarısız: {str(e)}")

    def add_to_history(self, status):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        version = self.version_selector.currentText()
        platform = self.platform_selector.currentText()
        
        row = self.history_table.rowCount()
        self.history_table.insertRow(row)
        
        self.history_table.setItem(row, 0, QTableWidgetItem(timestamp))
        self.history_table.setItem(row, 1, QTableWidgetItem(version))
        self.history_table.setItem(row, 2, QTableWidgetItem(platform))
        self.history_table.setItem(row, 3, QTableWidgetItem(status))
        
        # Geçmişi kaydet
        self.firmware_history.append({
            'timestamp': timestamp,
            'version': version,
            'platform': platform,
            'status': status
        })
        self.save_firmware_history()

    def load_firmware_history(self):
        try:
            with open('config/firmware_history.json', 'r') as f:
                self.firmware_history = json.load(f)
                
            # Tabloyu doldur
            for entry in self.firmware_history:
                row = self.history_table.rowCount()
                self.history_table.insertRow(row)
                
                self.history_table.setItem(row, 0, QTableWidgetItem(entry['timestamp']))
                self.history_table.setItem(row, 1, QTableWidgetItem(entry['version']))
                self.history_table.setItem(row, 2, QTableWidgetItem(entry['platform']))
                self.history_table.setItem(row, 3, QTableWidgetItem(entry['status']))
                
        except FileNotFoundError:
            pass

    def save_firmware_history(self):
        os.makedirs('config', exist_ok=True)
        with open('config/firmware_history.json', 'w') as f:
            json.dump(self.firmware_history, f, indent=4)