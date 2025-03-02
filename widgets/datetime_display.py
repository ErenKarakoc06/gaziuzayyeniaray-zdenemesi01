from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import QTimer, Qt
from datetime import datetime
import pytz

class DateTimeDisplay(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.start_timer()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Ana frame
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        frame.setStyleSheet("""
            QFrame {
                background-color: #2D2D2D;
                border: 1px solid #3D3D3D;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        
        frame_layout = QVBoxLayout()

        # UTC zaman gösterimi
        self.time_label = QLabel()
        self.time_label.setStyleSheet("""
            QLabel {
                color: #E0E0E0;
                font-family: 'Consolas', 'Courier New';
                font-size: 12px;
                font-weight: bold;
            }
        """)
        frame_layout.addWidget(self.time_label)

        # Kullanıcı bilgisi
        self.user_label = QLabel()
        self.user_label.setStyleSheet("""
            QLabel {
                color: #E0E0E0;
                font-family: 'Consolas', 'Courier New';
                font-size: 12px;
                font-weight: bold;
            }
        """)
        frame_layout.addWidget(self.user_label)

        frame.setLayout(frame_layout)
        layout.addWidget(frame)
        self.setLayout(layout)
        
        self.update_display()

    def update_display(self):
        # UTC zamanı formatla
        utc_now = datetime.now(pytz.UTC)
        time_str = utc_now.strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.setText(f"Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): {time_str}")
        
        # Kullanıcı bilgisini güncelle
        self.user_label.setText(f"Current User's Login: ErenKarakoc06")

    def start_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(1000)  # Her saniye güncelle

    def stop_timer(self):
        if hasattr(self, 'timer'):
            self.timer.stop()