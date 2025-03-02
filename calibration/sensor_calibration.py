from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QProgressBar, QStackedWidget, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

class SensorCalibration(QWidget):
    calibration_started = pyqtSignal(str)  # sensor type
    calibration_completed = pyqtSignal(str, bool)  # sensor type, success

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.current_calibration = None
        self.calibration_steps = []
        self.current_step = 0

    def init_ui(self):
        layout = QVBoxLayout()

        # Kalibrasyon seçimi
        self.calib_buttons = QHBoxLayout()
        
        sensors = [
            ("Pusula", "compass"),
            ("İvmeölçer", "accel"),
            ("Jiroskop", "gyro"),
            ("Seviye", "level")
        ]

        for name, sensor_type in sensors:
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, s=sensor_type: self.start_calibration(s))
            self.calib_buttons.addWidget(btn)
        
        layout.addLayout(self.calib_buttons)

        # Kalibrasyon talimatları
        self.instruction_widget = QStackedWidget()
        
        # Pusula kalibrasyonu
        self.compass_widget = self.create_compass_widget()
        self.instruction_widget.addWidget(self.compass_widget)
        
        # İvmeölçer kalibrasyonu
        self.accel_widget = self.create_accel_widget()
        self.instruction_widget.addWidget(self.accel_widget)
        
        layout.addWidget(self.instruction_widget)

        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Durum etiketi
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def create_compass_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        instructions = [
            "1. Aracı yatay düzlemde döndürün",
            "2. Aracı burnunuz aşağı bakacak şekilde döndürün",
            "3. Aracı sağ tarafı aşağı bakacak şekilde döndürün"
        ]
        
        for instruction in instructions:
            label = QLabel(instruction)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
        
        widget.setLayout(layout)
        return widget

    def create_accel_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        instructions = [
            "1. Aracı düz bir yüzeye yerleştirin",
            "2. Aracı burnunuz yukarı bakacak şekilde yerleştirin",
            "3. Aracı sağ tarafı yukarı bakacak şekilde yerleştirin",
            "4. Aracı ters çevirin"
        ]
        
        for instruction in instructions:
            label = QLabel(instruction)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
        
        widget.setLayout(layout)
        return widget

    def start_calibration(self, sensor_type):
        self.current_calibration = sensor_type
        self.calibration_started.emit(sensor_type)
        
        if sensor_type == "compass":
            self.instruction_widget.setCurrentWidget(self.compass_widget)
            self.calibration_steps = [
                "Yatay düzlemde döndürme",
                "Dikey düzlemde döndürme",
                "Yan düzlemde döndürme"
            ]
        elif sensor_type == "accel":
            self.instruction_widget.setCurrentWidget(self.accel_widget)
            self.calibration_steps = [
                "Düz pozisyon",
                "Burun yukarıda",
                "Sağ taraf yukarıda",
                "Ters pozisyon"
            ]
        
        self.current_step = 0
        self.progress_bar.setValue(0)
        self.update_status()
        
        # Simüle edilmiş kalibrasyon ilerlemesi
        self.calibration_timer = QTimer()
        self.calibration_timer.timeout.connect(self.simulate_calibration_progress)
        self.calibration_timer.start(1000)  # Her saniye güncelle

    def simulate_calibration_progress(self):
        if self.current_step >= len(self.calibration_steps):
            self.calibration_timer.stop()
            self.calibration_completed.emit(self.current_calibration, True)
            QMessageBox.information(self, "Kalibrasyon Tamamlandı", 
                                  f"{self.current_calibration} kalibrasyonu başarıyla tamamlandı!")
            return

        progress = (self.current_step * 100) // len(self.calibration_steps)
        self.progress_bar.setValue(progress)
        self.update_status()
        self.current_step += 1

    def update_status(self):
        if self.current_step < len(self.calibration_steps):
            self.status_label.setText(
                f"Adım {self.current_step + 1}/{len(self.calibration_steps)}: "
                f"{self.calibration_steps[self.current_step]}"
            )
        else:
            self.status_label.setText("Kalibrasyon tamamlandı!")