from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel
from PyQt6.QtCore import QTimer

class TelemetryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QGridLayout()
        
        # Telemetri etiketleri
        self.labels = {
            'latitude': QLabel('Enlem: N/A'),
            'longitude': QLabel('Boylam: N/A'),
            'altitude': QLabel('Yükseklik: N/A'),
            'speed': QLabel('Hız: N/A'),
            'heading': QLabel('Yön: N/A'),
        }
        
        # Etiketleri layout'a ekle
        row = 0
        for label in self.labels.values():
            layout.addWidget(label, row, 0)
            row += 1
        
        self.setLayout(layout)