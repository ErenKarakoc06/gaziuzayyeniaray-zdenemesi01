from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QComboBox, QProgressBar, QLabel, QFileDialog,
                            QMessageBox)
from PyQt6.QtCore import pyqtSignal, QThread
import serial.tools.list_ports
import os

class FirmwareLoader(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Port seçimi
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Port:"))
        self.port_combo = QComboBox()
        self.refresh_ports()
        port_layout.addWidget(self.port_combo)
        
        refresh_button = QPushButton("Yenile")
        refresh_button.clicked.connect(self.refresh_ports)
        port_layout.addWidget(refresh_button)
        layout.addLayout(port_layout)

        # Firmware seçimi
        firmware_layout = QHBoxLayout()
        self.firmware_path = QLabel("Firmware seçilmedi")
        firmware_layout.addWidget(self.firmware_path)
        
        select_button = QPushButton("Firmware Seç")
        select_button.clicked.connect(self.select_firmware)
        firmware_layout.addWidget(select_button)
        layout.addLayout(firmware_layout)

        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        layout.addWidget(self.progress_bar)

        # Durum etiketi
        self.status_label = QLabel("Hazır")
        layout.addWidget(self.status_label)

        # Yükleme butonu
        self.upload_button = QPushButton("Firmware Yükle")
        self.upload_button.clicked.connect(self.upload_firmware)
        self.upload_button.setEnabled(False)
        layout.addWidget(self.upload_button)

        self.setLayout(layout)

    def refresh_ports(self):
        self.port_combo.clear()
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo.addItems(ports)

    def select_firmware(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Firmware Dosyası Seç",
            "",
            "Firmware Files (*.px4 *.apj *.bin);;All Files (*.*)"
        )
        if file_name:
            self.firmware_path.setText(file_name)
            self.upload_button.setEnabled(True)

    def upload_firmware(self):
        if not self.port_combo.currentText():
            QMessageBox.warning(self, "Hata", "Lütfen bir port seçin!")
            return

        if not os.path.exists(self.firmware_path.text()):
            QMessageBox.warning(self, "Hata", "Firmware dosyası bulunamadı!")
            return

        # Yükleme işlemini başlat
        self.upload_button.setEnabled(False)
        self.status_label.setText("Firmware yükleniyor...")
        self.progress_bar.setValue(0)

        # Yükleme işlemi için worker thread başlat
        self.upload_thread = FirmwareUploadThread(
            self.port_combo.currentText(),
            self.firmware_path.text()
        )
        self.upload_thread.progress_updated.connect(self.update_progress)
        self.upload_thread.status_updated.connect(self.update_status)
        self.upload_thread.finished.connect(self.upload_completed)
        self.upload_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_status(self, status):
        self.status_label.setText(status)

    def upload_completed(self, success):
        self.upload_button.setEnabled(True)
        if success:
            QMessageBox.information(self, "Başarılı", "Firmware yükleme tamamlandı!")
        else:
            QMessageBox.critical(self, "Hata", "Firmware yükleme başarısız!")