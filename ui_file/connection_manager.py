from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QComboBox, QLabel, QLineEdit, QMessageBox)
from PyQt6.QtCore import pyqtSignal
import serial.tools.list_ports

class ConnectionManager(QWidget):
    connection_requested = pyqtSignal(str, int)
    disconnection_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Bağlantı ayarları
        connection_layout = QHBoxLayout()

        # Port seçimi
        self.port_combo = QComboBox()
        self.refresh_ports()
        connection_layout.addWidget(QLabel("Port:"))
        connection_layout.addWidget(self.port_combo)

        # Baud rate seçimi
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(['57600', '115200', '921600'])
        self.baud_combo.setCurrentText('57600')
        connection_layout.addWidget(QLabel("Baud:"))
        connection_layout.addWidget(self.baud_combo)

        # Bağlantı butonları
        self.connect_btn = QPushButton("Bağlan")
        self.connect_btn.clicked.connect(self.connect)
        self.disconnect_btn = QPushButton("Bağlantıyı Kes")
        self.disconnect_btn.clicked.connect(self.disconnect)
        self.disconnect_btn.setEnabled(False)
        
        connection_layout.addWidget(self.connect_btn)
        connection_layout.addWidget(self.disconnect_btn)

        # Yenile butonu
        self.refresh_btn = QPushButton("Portları Yenile")
        self.refresh_btn.clicked.connect(self.refresh_ports)
        connection_layout.addWidget(self.refresh_btn)

        layout.addLayout(connection_layout)
        self.setLayout(layout)

    def refresh_ports(self):
        self.port_combo.clear()
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo.addItems(ports)

    def connect(self):
        port = self.port_combo.currentText()
        baud = int(self.baud_combo.currentText())
        
        if port:
            self.connection_requested.emit(port, baud)
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
        else:
            QMessageBox.warning(self, "Bağlantı Hatası", 
                              "Lütfen bir port seçin!")

    def disconnect(self):
        self.disconnection_requested.emit()
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)