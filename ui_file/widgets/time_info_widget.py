from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import QTimer, Qt, QDateTime
from datetime import datetime
import pytz

class TimeInfoWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.start_timer()

    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 0, 5, 0)  # Kenar boşluklarını azalt

        # UTC Zaman etiketi
        self.utc_label = QLabel()
        self.utc_label.setStyleSheet("""
            QLabel {
                color: #E0E0E0;
                font-family: 'Consolas', 'Courier New';
                font-size: 12px;
                padding: 2px 5px;
                background-color: #2D2D2D;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.utc_label)

        # Boşluk ekle
        layout.addSpacing(10)

        # Kullanıcı bilgisi etiketi
        self.user_label = QLabel(f"User: {self.get_current_user()}")
        self.user_label.setStyleSheet("""
            QLabel {
                color: #E0E0E0;
                font-family: 'Consolas', 'Courier New';
                font-size: 12px;
                padding: 2px 5px;
                background-color: #2D2D2D;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.user_label)

        # Sağa hizalama için esnek boşluk
        layout.addStretch()

        self.setLayout(layout)
        self.update_time()

    def start_timer(self):
        # Her saniye güncelle
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # 1000ms = 1 saniye

    def update_time(self):
        # UTC zamanı al ve formatla
        utc_now = datetime.now(pytz.UTC)
        formatted_time = utc_now.strftime("%Y-%m-%d %H:%M:%S UTC")
        self.utc_label.setText(formatted_time)

    def get_current_user(self):
        return "ErenKarakoc06"  # Kullanıcı adını döndür

    def stop_timer(self):
        if hasattr(self, 'timer'):
            self.timer.stop()