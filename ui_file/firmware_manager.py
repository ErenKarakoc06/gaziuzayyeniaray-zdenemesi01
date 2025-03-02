from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QProgressBar, QComboBox, QGroupBox,
                            QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
import requests
import json
import os

class FirmwareManager(QWidget):
    update_started = pyqtSignal(str)  # Firmware versiyonu
    update_progress = pyqtSignal(int)  # İlerleme yüzdesi
    update_completed = pyqtSignal(bool, str)  # Başarı durumu, mesaj

    def __init__(self):
        super().__init__()
        self.firmware_list = {}
        self.current_version = None
        self.init_ui()
        self.load_firmware_list()

    def init_ui(self):
        layout = QVBoxLayout()

        # Mevcut Firmware Bilgisi
        current_group = QGroupBox("Mevcut Firmware")
        current_layout = QVBoxLayout()
        
        self.current_version_label = QLabel("Yüklü Versiyon: Kontrol ediliyor...")
        current_layout.addWidget(self.current_version_label)
        
        self.vehicle_type_label = QLabel("Araç Tipi: --")
        current_layout.addWidget(self.vehicle_type_label)
        
        current_group.setLayout(current_layout)
        layout.addWidget(current_group)

        # Firmware Güncelleme
        update_group = QGroupBox("Firmware Güncelleme")
        update_layout = QVBoxLayout()

        # Firmware seçimi
        select_layout = QHBoxLayout()
        select_layout.addWidget(QLabel("Firmware Versiyonu:"))
        self.firmware_selector = QComboBox()
        self.firmware_selector.currentTextChanged.connect(self.on_firmware_selected)
        select_layout.addWidget(self.firmware_selector)
        update_layout.addLayout(select_layout)

        # Firmware detayları
        self.firmware_details = QLabel()
        update_layout.addWidget(self.firmware_details)

        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        update_layout.addWidget(self.progress_bar)

        # Kontrol butonları
        button_layout = QHBoxLayout()
        
        self.check_updates_btn = QPushButton("Güncellemeleri Kontrol Et")
        self.check_updates_btn.clicked.connect(self.check_updates)
        button_layout.addWidget(self.check_updates_btn)

        self.download_btn = QPushButton("İndir")
        self.download_btn.clicked.connect(self.download_firmware)
        self.download_btn.setEnabled(False)
        button_layout.addWidget(self.download_btn)

        self.flash_btn = QPushButton("Yükle")
        self.flash_btn.clicked.connect(self.flash_firmware)
        self.flash_btn.setEnabled(False)
        button_layout.addWidget(self.flash_btn)

        update_layout.addLayout(button_layout)
        update_group.setLayout(update_layout)
        layout.addWidget(update_group)

        # Gelişmiş Seçenekler
        advanced_group = QGroupBox("Gelişmiş Seçenekler")
        advanced_layout = QHBoxLayout()

        custom_file_btn = QPushButton("Özel Firmware Dosyası")
        custom_file_btn.clicked.connect(self.select_custom_firmware)
        advanced_layout.addWidget(custom_file_btn)

        backup_btn = QPushButton("Mevcut Firmware Yedekle")
        backup_btn.clicked.connect(self.backup_current_firmware)
        advanced_layout.addWidget(backup_btn)

        advanced_group.setLayout(advanced_layout)
        layout.addWidget(advanced_group)

        self.setLayout(layout)

    def load_firmware_list(self):
        try:
            # ArduPilot firmware API'sinden verileri çek
            url = "https://firmware.ardupilot.org/manifest.json"
            response = requests.get(url)
            self.firmware_list = response.json()
            
            # Firmware seçeneklerini güncelle
            self.firmware_selector.clear()
            for version in self.firmware_list['versions']:
                self.firmware_selector.addItem(f"ArduCopter {version['version']}")

        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Firmware listesi yüklenemedi: {str(e)}")

    def check_updates(self):
        try:
            # Mevcut versiyonu kontrol et
            # TODO: MAVLink üzerinden versiyon bilgisi al
            self.current_version = "4.3.0"  # Örnek versiyon
            self.current_version_label.setText(f"Yüklü Versiyon: {self.current_version}")
            
            # Güncellemeleri kontrol et
            latest_version = self.firmware_list['versions'][0]['version']
            if latest_version > self.current_version:
                msg = f"Yeni versiyon mevcut: {latest_version}"
                self.download_btn.setEnabled(True)
            else:
                msg = "Firmware güncel"
                self.download_btn.setEnabled(False)
            
            QMessageBox.information(self, "Güncelleme Kontrolü", msg)

        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Güncelleme kontrolü başarısız: {str(e)}")

    def on_firmware_selected(self, version):
        try:
            # Seçilen firmware detaylarını göster
            version_info = next(
                (v for v in self.firmware_list['versions'] if v['version'] in version),
                None
            )
            
            if version_info:
                details = (
                    f"Versiyon: {version_info['version']}\n"
                    f"Yayın Tarihi: {version_info.get('release_date', 'N/A')}\n"
                    f"Boyut: {version_info.get('size', 'N/A')} bytes\n"
                    f"SHA256: {version_info.get('sha256', 'N/A')[:8]}..."
                )
                self.firmware_details.setText(details)
                self.download_btn.setEnabled(True)
            else:
                self.firmware_details.setText("Versiyon bilgisi bulunamadı")
                self.download_btn.setEnabled(False)

        except Exception as e:
            self.firmware_details.setText(f"Hata: {str(e)}")
            self.download_btn.setEnabled(False)

    def download_firmware(self):
        try:
            version = self.firmware_selector.currentText()
            version_info = next(
                (v for v in self.firmware_list['versions'] if v['version'] in version),
                None
            )
            
            if not version_info:
                raise ValueError("Firmware bilgisi bulunamadı")

            # İndirme işlemi
            url = version_info['url']
            self.progress_bar.setValue(0)
            
            def download_progress(count, block_size, total_size):
                progress = int(count * block_size * 100 / total_size)
                self.progress_bar.setValue(progress)
                self.update_progress.emit(progress)

            filename = f"ardupilot_{version_info['version']}.apj"
            filepath = os.path.join(os.path.expanduser("~"), "Downloads", filename)
            
            # Dosyayı indir
            urllib.request.urlretrieve(url, filepath, download_progress)
            
            self.flash_btn.setEnabled(True)
            QMessageBox.information(self, "Başarılı", "Firmware indirildi!")

        except Exception as e:
            QMessageBox.warning(self, "Hata", f"İndirme başarısız: {str(e)}")

    def flash_firmware(self):
        result = QMessageBox.question(
            self,
            "Firmware Yükleme",
            "Firmware yüklemesi başlatılacak. Devam etmek istiyor musunuz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            try:
                # TODO: MAVLink üzerinden firmware yükleme
                self.update_started.emit(self.firmware_selector.currentText())
                # Simüle edilmiş yükleme işlemi
                for i in range(101):
                    self.progress_bar.setValue(i)
                    self.update_progress.emit(i)
                    QApplication.processEvents()
                    time.sleep(0.1)
                
                self.update_completed.emit(True, "Firmware başarıyla yüklendi")
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
            self.firmware_selector.setCurrentText(file_path)
            self.download_btn.setEnabled(False)
            self.flash_btn.setEnabled(True)

    def backup_current_firmware(self):
        try:
            # TODO: MAVLink üzerinden mevcut firmware'i yedekle
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Firmware Yedeğini Kaydet",
                f"ardupilot_backup_{self.current_version}.apj",
                "Firmware Dosyaları (*.apj)"
            )
            
            if save_path:
                # Simüle edilmiş yedekleme işlemi
                with open(save_path, 'wb') as f:
                    f.write(b'Simulated firmware backup')
                QMessageBox.information(self, "Başarılı", "Firmware yedeği alındı!")

        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Yedekleme başarısız: {str(e)}")