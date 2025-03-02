from PyQt6.QtWidgets import (QWidget, QGridLayout, QLabel, 
                            QProgressBar, QFrame)
from PyQt6.QtCore import Qt

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QGridLayout()

        # Göstergeler için stil
        style = """
            QFrame {
                background-color: #2D2D2D;
                border: 1px solid #3D3D3D;
                border-radius: 5px;
                padding: 5px;
            }
            QLabel {
                color: #E0E0E0;
                font-family: 'Segoe UI';
                font-size: 12px;
            }
            QProgressBar {
                background-color: #1D1D1D;
                border: 1px solid #3D3D3D;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """

        # Göstergeler
        indicators = [
            ("Batarya", "battery_frame", 0, 100, "%"),
            ("Sinyal Gücü", "signal_frame", 0, 100, "%"),
            ("GPS HDOP", "gps_frame", 0, 10, ""),
            ("Motor Gücü", "motor_frame", 0, 100, "%")
        ]

        for i, (name, frame_name, min_val, max_val, unit) in enumerate(indicators):
            frame = QFrame()
            frame.setStyleSheet(style)
            frame_layout = QGridLayout()

            # Başlık
            title = QLabel(name)
            frame_layout.addWidget(title, 0, 0, 1, 2)

            # Değer
            value_label = QLabel("0" + unit)
            value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            frame_layout.addWidget(value_label, 0, 1)

            # Progress bar
            progress = QProgressBar()
            progress.setMinimum(min_val)
            progress.setMaximum(max_val)
            progress.setValue(0)
            frame_layout.addWidget(progress, 1, 0, 1, 2)

            frame.setLayout(frame_layout)
            setattr(self, frame_name, frame)
            setattr(self, f"{frame_name}_value", value_label)
            setattr(self, f"{frame_name}_progress", progress)

            # Grid'e yerleştir
            layout.addWidget(frame, i // 2, i % 2)

        self.setLayout(layout)

    def update_battery(self, value):
        self.battery_frame_value.setText(f"{value}%")
        self.battery_frame_progress.setValue(value)
        if value < 20:
            self.battery_frame_progress.setStyleSheet("QProgressBar::chunk { background-color: #F44336; }")
        elif value < 50:
            self.battery_frame_progress.setStyleSheet("QProgressBar::chunk { background-color: #FFC107; }")
        else:
            self.battery_frame_progress.setStyleSheet("QProgressBar::chunk { background-color: #4CAF50; }")

    def update_signal(self, value):
        self.signal_frame_value.setText(f"{value}%")
        self.signal_frame_progress.setValue(value)

    def update_gps(self, hdop):
        self.gps_frame_value.setText(f"{hdop:.1f}")
        # HDOP değerini 0-100 aralığına dönüştür
        normalized = max(0, min(100, (10 - hdop) * 10))
        self.gps_frame_progress.setValue(normalized)

    def update_motor(self, value):
        self.motor_frame_value.setText(f"{value}%")
        self.motor_frame_progress.setValue(value)