from PyQt6.QtWidgets import QStatusBar, QLabel
from PyQt6.QtCore import QTimer
from datetime import datetime
import pytz

class CustomStatusBar(QStatusBar):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.start_timer()

    def init_ui(self):
        # UTC Zaman
        self.time_label = QLabel()
        self.time_label.setStyleSheet("""
            QLabel {
                color: #E0E0E0;
                font-family: 'Consolas', 'Courier New';
                font-size: 12px;
                padding: 2px 5px;
            }
        """)
        self.addPermanentWidget(self.time_label)

        # Kullanıcı bilgisi
        self.user_label = QLabel(f"User: ErenKarakoc06")
        self.user_label.setStyleSheet("""
            QLabel {
                color: #E0E0E0;
                font-family: 'Consolas', 'Courier New';
                font-size: 12px;
                padding: 2px 5px;
            }
        """)
        self.addPermanentWidget(self.user_label)

        self.update_time()

    def start_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

    def update_time(self):
        utc_now = datetime.now(pytz.UTC)
        formatted_time = utc_now.strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.setText(f"UTC: {formatted_time}")

    def stop_timer(self):
        if hasattr(self, 'timer'):
            self.timer.stop()