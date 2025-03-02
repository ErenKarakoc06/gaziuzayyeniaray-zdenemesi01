from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QSpinBox, QComboBox, QGroupBox, QCheckBox)
from PyQt6.QtCore import pyqtSignal

class FailsafeSettings(QWidget):
    settings_updated = pyqtSignal(dict)  # Failsafe ayarları

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Batarya Failsafe
        battery_group = QGroupBox("Batarya Failsafe")
        battery_layout = QVBoxLayout()

        # Düşük batarya seviyesi
        low_batt_layout = QHBoxLayout()
        low_batt_layout.addWidget(QLabel("Düşük Batarya Seviyesi (%):"))
        self.low_battery = QSpinBox()
        self.low_battery.setRange(0, 100)
        self.low_battery.setValue(20)
        low_batt_layout.addWidget(self.low_battery)

        # Kritik batarya seviyesi
        critical_batt_layout = QHBoxLayout()
        critical_batt_layout.addWidget(QLabel("Kritik Batarya Seviyesi (%):"))
        self.critical_battery = QSpinBox()
        self.critical_battery.setRange(0, 100)
        self.critical_battery.setValue(10)
        critical_batt_layout.addWidget(self.critical_battery)

        battery_layout.addLayout(low_batt_layout)
        battery_layout.addLayout(critical_batt_layout)
        battery_group.setLayout(battery_layout)
        layout.addWidget(battery_group)

        # RC Failsafe
        rc_group = QGroupBox("RC Failsafe")
        rc_layout = QVBoxLayout()

        # RC kaybı süresi
        rc_timeout_layout = QHBoxLayout()
        rc_timeout_layout.addWidget(QLabel("RC Timeout (sn):"))
        self.rc_timeout = QSpinBox()
        self.rc_timeout.setRange(1, 60)
        self.rc_timeout.setValue(3)
        rc_timeout_layout.addWidget(self.rc_timeout)
        rc_layout.addLayout(rc_timeout_layout)

        rc_group.setLayout(rc_layout)
        layout.addWidget(rc_group)

        # GPS Failsafe
        gps_group = QGroupBox("GPS Failsafe")
        gps_layout = QVBoxLayout()

        # Minimum uydu sayısı
        min_sat_layout = QHBoxLayout()
        min_sat_layout.addWidget(QLabel("Minimum Uydu Sayısı:"))
        self.min_satellites = QSpinBox()
        self.min_satellites.setRange(0, 20)
        self.min_satellites.setValue(6)
        min_sat_layout.addWidget(self.min_satellites)
        gps_layout.addLayout(min_sat_layout)

        # Maksimum HDOP
        max_hdop_layout = QHBoxLayout()
        max_hdop_layout.addWidget(QLabel("Maksimum HDOP:"))
        self.max_hdop = QDoubleSpinBox()
        self.max_hdop.setRange(0, 10)
        self.max_hdop.setValue(2.0)
        max_hdop_layout.addWidget(self.max_hdop)
        gps_layout.addLayout(max_hdop_layout)

        gps_group.setLayout(gps_layout)
        layout.addWidget(gps_group)

        # Failsafe Aksiyonları
        action_group = QGroupBox("Failsafe Aksiyonları")
        action_layout = QVBoxLayout()

        # Düşük batarya aksiyonu
        self.low_battery_action = QComboBox()
        self.low_battery_action.addItems([
            "Uyarı Ver",
            "RTL'e Geç",
            "Land'a Geç"
        ])
        action_layout.addWidget(QLabel("Düşük Batarya Aksiyonu:"))
        action_layout.addWidget(self.low_battery_action)

        # Kritik batarya aksiyonu
        self.critical_battery_action = QComboBox()
        self.critical_battery_action.addItems([
            "RTL'e Geç",
            "Land'a Geç",
            "Acil İniş"
        ])
        action_layout.addWidget(QLabel("Kritik Batarya Aksiyonu:"))
        action_layout.addWidget(self.critical_battery_action)

        # RC kaybı aksiyonu
        self.rc_loss_action = QComboBox()
        self.rc_loss_action.addItems([
            "Hover",
            "RTL'e Geç",
            "Land'a Geç"
        ])
        action_layout.addWidget(QLabel("RC Kaybı Aksiyonu:"))
        action_layout.addWidget(self.rc_loss_action)

        # GPS kaybı aksiyonu
        self.gps_loss_action = QComboBox()
        self.gps_loss_action.addItems([
            "Hover",
            "Land'a Geç",
            "Acil İniş"
        ])
        action_layout.addWidget(QLabel("GPS Kaybı Aksiyonu:"))
        action_layout.addWidget(self.gps_loss_action)

        action_group.setLayout(action_layout)
        layout.addWidget(action_group)

        # Kontrol butonları
        control_layout = QHBoxLayout()
        
        save_btn = QPushButton("Ayarları Kaydet")
        save_btn.clicked.connect(self.save_settings)
        control_layout.addWidget(save_btn)

        apply_btn = QPushButton("Ayarları Uygula")
        apply_btn.clicked.connect(self.apply_settings)
        control_layout.addWidget(apply_btn)

        layout.addLayout(control_layout)
        self.setLayout(layout)

    def save_settings(self):
        settings = self.get_current_settings()
        # TODO: Ayarları dosyaya kaydet

    def apply_settings(self):
        settings = self.get_current_settings()
        self.settings_updated.emit(settings)

    def get_current_settings(self):
        return {
            'battery': {
                'low_level': self.low_battery.value(),
                'critical_level': self.critical_battery.value(),
                'low_action': self.low_battery_action.currentText(),
                'critical_action': self.critical_battery_action.currentText()
            },
            'rc': {
                'timeout': self.rc_timeout.value(),
                'loss_action': self.rc_loss_action.currentText()
            },
            'gps': {
                'min_satellites': self.min_satellites.value(),
                'max_hdop': self.max_hdop.value(),
                'loss_action': self.gps_loss_action.currentText()
            }
        }