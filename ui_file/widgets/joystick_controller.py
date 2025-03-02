from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox
from PyQt6.QtCore import QTimer, pyqtSignal
import pygame

class JoystickController(QWidget):
    # Joystick sinyalleri
    throttle_changed = pyqtSignal(float)  # -1 to 1
    roll_changed = pyqtSignal(float)      # -1 to 1
    pitch_changed = pyqtSignal(float)     # -1 to 1
    yaw_changed = pyqtSignal(float)       # -1 to 1
    button_pressed = pyqtSignal(int)      # Button number

    def __init__(self):
        super().__init__()
        self.init_joystick()
        self.init_ui()
        
        # Joystick güncelleme zamanlayıcısı
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_joystick)
        self.update_timer.start(20)  # 50Hz güncelleme

    def init_joystick(self):
        pygame.init()
        pygame.joystick.init()
        self.joystick = None
        self.available_joysticks = []
        self.update_available_joysticks()

    def init_ui(self):
        layout = QVBoxLayout()

        # Joystick seçimi
        select_layout = QHBoxLayout()
        self.joystick_combo = QComboBox()
        self.update_joystick_list()
        select_layout.addWidget(QLabel("Joystick:"))
        select_layout.addWidget(self.joystick_combo)
        
        # Yenile butonu
        refresh_btn = QPushButton("Yenile")
        refresh_btn.clicked.connect(self.refresh_joysticks)
        select_layout.addWidget(refresh_btn)
        
        layout.addLayout(select_layout)

        # Joystick değerleri
        self.values_layout = QVBoxLayout()
        self.axis_labels = {
            'Throttle': QLabel('Throttle: 0.0'),
            'Roll': QLabel('Roll: 0.0'),
            'Pitch': QLabel('Pitch: 0.0'),
            'Yaw': QLabel('Yaw: 0.0')
        }
        
        for label in self.axis_labels.values():
            self.values_layout.addWidget(label)
        
        layout.addLayout(self.values_layout)
        self.setLayout(layout)

    def update_available_joysticks(self):
        self.available_joysticks = [
            pygame.joystick.Joystick(x).get_name()
            for x in range(pygame.joystick.get_count())
        ]

    def update_joystick_list(self):
        self.joystick_combo.clear()
        self.joystick_combo.addItems(self.available_joysticks)
        self.joystick_combo.currentIndexChanged.connect(self.select_joystick)

    def refresh_joysticks(self):
        pygame.joystick.quit()
        pygame.joystick.init()
        self.update_available_joysticks()
        self.update_joystick_list()

    def select_joystick(self, index):
        if 0 <= index < len(self.available_joysticks):
            if self.joystick:
                self.joystick.quit()
            self.joystick = pygame.joystick.Joystick(index)
            self.joystick.init()

    def update_joystick(self):
        if not self.joystick:
            return

        pygame.event.pump()
        
        # Eksenleri oku
        try:
            throttle = -self.joystick.get_axis(1)  # Y ekseni
            roll = self.joystick.get_axis(0)       # X ekseni
            pitch = self.joystick.get_axis(3)      # Sağ analog Y
            yaw = self.joystick.get_axis(2)        # Sağ analog X

            # Değerleri güncelle ve sinyalleri gönder
            self.axis_labels['Throttle'].setText(f'Throttle: {throttle:.2f}')
            self.axis_labels['Roll'].setText(f'Roll: {roll:.2f}')
            self.axis_labels['Pitch'].setText(f'Pitch: {pitch:.2f}')
            self.axis_labels['Yaw'].setText(f'Yaw: {yaw:.2f}')

            self.throttle_changed.emit(throttle)
            self.roll_changed.emit(roll)
            self.pitch_changed.emit(pitch)
            self.yaw_changed.emit(yaw)

            # Butonları kontrol et
            for i in range(self.joystick.get_numbuttons()):
                if self.joystick.get_button(i):
                    self.button_pressed.emit(i)

        except pygame.error:
            pass

    def closeEvent(self, event):
        if self.joystick:
            self.joystick.quit()
        pygame.quit()
        super().closeEvent(event)