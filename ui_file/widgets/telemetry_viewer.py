from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel
from PyQt6.QtCore import Qt

class TelemetryViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QGridLayout()

        # Telemetri etiketleri
        self.labels = {
            'armed': QLabel('Arm Durumu: Disarmed'),
            'mode': QLabel('Mod: ---'),
            'altitude': QLabel('Yükseklik: 0.0 m'),
            'relative_alt': QLabel('Bağıl Yükseklik: 0.0 m'),
            'groundspeed': QLabel('Yer Hızı: 0.0 m/s'),
            'airspeed': QLabel('Hava Hızı: 0.0 m/s'),
            'heading': QLabel('Yön: 0°'),
            'gps_fix': QLabel('GPS Fix: 0'),
            'gps_satellites': QLabel('GPS Uydu: 0'),
            'battery': QLabel('Batarya: 0.0V (0%)'),
            'current': QLabel('Akım: 0.0A'),
            'consumed': QLabel('Tüketilen: 0 mAh')
        }

        # Etiketleri grid'e yerleştir
        row = 0
        col = 0
        for label in self.labels.values():
            layout.addWidget(label, row, col)
            row += 1
            if row > 5:  # 6 satırdan sonra yeni sütuna geç
                row = 0
                col += 1

        self.setLayout(layout)

    def update_telemetry(self, data):
        if 'armed' in data:
            self.labels['armed'].setText(f"Arm Durumu: {'Armed' if data['armed'] else 'Disarmed'}")
        if 'mode' in data:
            self.labels['mode'].setText(f"Mod: {data['mode']}")
        if 'altitude' in data:
            self.labels['altitude'].setText(f"Yükseklik: {data['altitude']:.1f} m")
        if 'relative_alt' in data:
            self.labels['relative_alt'].setText(f"Bağıl Yükseklik: {data['relative_alt']:.1f} m")
        if 'groundspeed' in data:
            self.labels['groundspeed'].setText(f"Yer Hızı: {data['groundspeed']:.1f} m/s")
        if 'airspeed' in data:
            self.labels['airspeed'].setText(f"Hava Hızı: {data['airspeed']:.1f} m/s")
        if 'heading' in data:
            self.labels['heading'].setText(f"Yön: {data['heading']}°")
        if 'gps_fix' in data:
            self.labels['gps_fix'].setText(f"GPS Fix: {data['gps_fix']}")
        if 'gps_satellites' in data:
            self.labels['gps_satellites'].setText(f"GPS Uydu: {data['gps_satellites']}")
        if 'battery' in data:
            self.labels['battery'].setText(f"Batarya: {data['voltage']:.1f}V ({data['battery_remaining']}%)")
        if 'current' in data:
            self.labels['current'].setText(f"Akım: {data['current']:.1f}A")
        if 'battery_consumed' in data:
            self.labels['consumed'].setText(f"Tüketilen: {data['battery_consumed']} mAh")