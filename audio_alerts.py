from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QCheckBox
from PyQt6.QtCore import Qt, pyqtSignal, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
import os
import json

class AudioAlerts(QWidget):
    alert_triggered = pyqtSignal(str)  # alert_type

    def __init__(self):
        super().__init__()
        self.alerts = {
            'battery_low': {
                'file': 'sounds/battery_low.wav',
                'enabled': True,
                'threshold': 20
            },
            'altitude_warning': {
                'file': 'sounds/altitude_warning.wav',
                'enabled': True,
                'threshold': 100
            },
            'gps_lost': {
                'file': 'sounds/gps_lost.wav',
                'enabled': True
            },
            'mode_change': {
                'file': 'sounds/mode_change.wav',
                'enabled': True
            },
            'mission_complete': {
                'file': 'sounds/mission_complete.wav',
                'enabled': True
            },
            'failsafe': {
                'file': 'sounds/failsafe.wav',
                'enabled': True
            }
        }
        
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout()

        # Ses uyarıları listesi
        self.alert_list = QListWidget()
        for alert_type, alert_data in self.alerts.items():
            item = QListWidget.Item()
            item_widget = self.create_alert_item_widget(alert_type, alert_data)
            self.alert_list.addItem(item)
            self.alert_list.setItemWidget(item, item_widget)
        
        layout.addWidget(self.alert_list)

        # Test kontrolleri
        test_layout = QHBoxLayout()
        
        test_btn = QPushButton("Seçili Uyarıyı Test Et")
        test_btn.clicked.connect(self.test_selected_alert)
        test_layout.addWidget(test_btn)

        test_all_btn = QPushButton("Tüm Uyarıları Test Et")
        test_all_btn.clicked.connect(self.test_all_alerts)
        test_layout.addWidget(test_all_btn)

        layout.addLayout(test_layout)

        self.setLayout(layout)

    def create_alert_item_widget(self, alert_type, alert_data):
        widget = QWidget()
        layout = QHBoxLayout()
        
        # Uyarı adı
        name_label = QLabel(alert_type.replace('_', ' ').title())
        layout.addWidget(name_label)
        
        # Etkinleştirme checkbox'ı
        enable_cb = QCheckBox("Etkin")
        enable_cb.setChecked(alert_data['enabled'])
        enable_cb.stateChanged.connect(
            lambda state, t=alert_type: self.toggle_alert(t, state)
        )
        layout.addWidget(enable_cb)
        
        # Ses düzeyi kontrolü
        volume_label = QLabel("Ses:")
        layout.addWidget(volume_label)
        
        volume_slider = QSlider(Qt.Orientation.Horizontal)
        volume_slider.setRange(0, 100)
        volume_slider.setValue(100)
        volume_slider.valueChanged.connect(
            lambda value, t=alert_type: self.set_alert_volume(t, value)
        )
        layout.addWidget(volume_slider)
        
        widget.setLayout(layout)
        return widget

    def toggle_alert(self, alert_type, enabled):
        self.alerts[alert_type]['enabled'] = bool(enabled)
        self.save_settings()

    def set_alert_volume(self, alert_type, volume):
        if hasattr(self.alerts[alert_type], 'volume'):
            self.alerts[alert_type]['volume'] = volume / 100.0
            self.save_settings()

    def play_alert(self, alert_type):
        if not self.alerts[alert_type]['enabled']:
            return

        sound_file = self.alerts[alert_type]['file']
        if os.path.exists(sound_file):
            self.media_player.setSource(QUrl.fromLocalFile(sound_file))
            self.media_player.play()
            self.alert_triggered.emit(alert_type)

    def test_selected_alert(self):
        current_item = self.alert_list.currentItem()
        if current_item:
            alert_type = list(self.alerts.keys())[self.alert_list.row(current_item)]
            self.play_alert(alert_type)

    def test_all_alerts(self):
        for alert_type in self.alerts:
            self.play_alert(alert_type)

    def load_settings(self):
        try:
            with open('config/audio_alerts.json', 'r') as f:
                settings = json.load(f)
                for alert_type, alert_data in settings.items():
                    if alert_type in self.alerts:
                        self.alerts[alert_type].update(alert_data)
        except FileNotFoundError:
            pass

    def save_settings(self):
        os.makedirs('config', exist_ok=True)
        with open('config/audio_alerts.json', 'w') as f:
            json.dump(self.alerts, f, indent=4)

    def handle_telemetry(self, data):
        """Telemetri verilerine göre uyarıları tetikle"""
        
        # Batarya seviyesi kontrolü
        if 'battery' in data:
            battery_level = data['battery'].get('level', 100)
            if battery_level <= self.alerts['battery_low']['threshold']:
                self.play_alert('battery_low')

        # İrtifa kontrolü
        if 'altitude' in data:
            altitude = data['altitude']
            if altitude >= self.alerts['altitude_warning']['threshold']:
                self.play_alert('altitude_warning')

        # GPS durumu kontrolü
        if 'gps' in data:
            if data['gps'].get('fix', 0) == 0:
                self.play_alert('gps_lost')

        # Failsafe kontrolü
        if 'status' in data and data['status'].get('failsafe', False):
            self.play_alert('failsafe')