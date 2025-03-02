from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QSpinBox, QProgressBar, QGroupBox, 
                            QMessageBox, QTabWidget, QSlider)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
import time

class HardwareTestModule(QWidget):
    test_completed = pyqtSignal(str, bool)  # test_type, success

    def __init__(self):
        super().__init__()
        self.current_user = "ErenKarakoc06"
        self.current_time_utc = "2025-03-02 18:23:42"
        self.test_results = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Üst bilgi paneli
        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel(f"Kullanıcı: {self.current_user}"))
        info_layout.addWidget(QLabel(f"UTC: {self.current_time_utc}"))
        layout.addLayout(info_layout)

        # Test sekmeleri
        tabs = QTabWidget()
        tabs.addTab(self.create_esc_tab(), "ESC Kalibrasyon")
        tabs.addTab(self.create_motor_tab(), "Motor Test")
        tabs.addTab(self.create_servo_tab(), "Servo Test")
        tabs.addTab(self.create_sensor_tab(), "Sensör Test")
        layout.addWidget(tabs)

        # Durum ve ilerleyiş
        self.status_label = QLabel("Hazır")
        layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def create_esc_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # ESC Kalibrasyon Grubu
        calib_group = QGroupBox("ESC Kalibrasyon")
        calib_layout = QVBoxLayout()

        # Adım 1: Batarya Kontrolü
        step1_layout = QHBoxLayout()
        step1_layout.addWidget(QLabel("1. Bataryayı Çıkarın"))
        self.battery_check = QPushButton("Kontrol Et")
        self.battery_check.clicked.connect(self.check_battery)
        step1_layout.addWidget(self.battery_check)
        calib_layout.addLayout(step1_layout)

        # Adım 2: ESC Sinyal Ayarı
        step2_layout = QHBoxLayout()
        step2_layout.addWidget(QLabel("2. Maksimum Sinyal:"))
        self.max_signal = QSpinBox()
        self.max_signal.setRange(1000, 2000)
        self.max_signal.setValue(2000)
        step2_layout.addWidget(self.max_signal)
        calib_layout.addLayout(step2_layout)

        # Adım 3: Kalibrasyon
        self.start_calib_btn = QPushButton("Kalibrasyonu Başlat")
        self.start_calib_btn.clicked.connect(self.start_esc_calibration)
        calib_layout.addWidget(self.start_calib_btn)

        calib_group.setLayout(calib_layout)
        layout.addWidget(calib_group)

        # Sonuçlar
        results_group = QGroupBox("Kalibrasyon Sonuçları")
        results_layout = QVBoxLayout()
        self.esc_results = QLabel("Henüz kalibrasyon yapılmadı")
        results_layout.addWidget(self.esc_results)
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        widget.setLayout(layout)
        return widget

    def create_motor_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Motor Test Grubu
        test_group = QGroupBox("Motor Test")
        test_layout = QVBoxLayout()

        # Motor seçimi
        motor_layout = QHBoxLayout()
        motor_layout.addWidget(QLabel("Motor Seçimi:"))
        self.motor_select = QSpinBox()
        self.motor_select.setRange(1, 8)
        motor_layout.addWidget(self.motor_select)
        test_layout.addLayout(motor_layout)

        # Throttle kontrolü
        throttle_layout = QHBoxLayout()
        throttle_layout.addWidget(QLabel("Throttle:"))
        self.throttle_slider = QSlider(Qt.Orientation.Horizontal)
        self.throttle_slider.setRange(0, 100)
        self.throttle_slider.valueChanged.connect(self.update_throttle)
        throttle_layout.addWidget(self.throttle_slider)
        self.throttle_value = QLabel("0%")
        throttle_layout.addWidget(self.throttle_value)
        test_layout.addLayout(throttle_layout)

        # Test kontrolleri
        control_layout = QHBoxLayout()
        
        self.start_motor_btn = QPushButton("Başlat")
        self.start_motor_btn.clicked.connect(self.start_motor_test)
        control_layout.addWidget(self.start_motor_btn)
        
        self.stop_motor_btn = QPushButton("Durdur")
        self.stop_motor_btn.clicked.connect(self.stop_motor_test)
        self.stop_motor_btn.setEnabled(False)
        control_layout.addWidget(self.stop_motor_btn)
        
        test_layout.addLayout(control_layout)
        test_group.setLayout(test_layout)
        layout.addWidget(test_group)

        # Motor durumu
        status_group = QGroupBox("Motor Durumu")
        status_layout = QVBoxLayout()
        self.motor_status = QLabel("Hazır")
        status_layout.addWidget(self.motor_status)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        widget.setLayout(layout)
        return widget

    def create_servo_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Servo Test Grubu
        test_group = QGroupBox("Servo Test")
        test_layout = QVBoxLayout()

        # Servo seçimi
        servo_layout = QHBoxLayout()
        servo_layout.addWidget(QLabel("Servo Seçimi:"))
        self.servo_select = QSpinBox()
        self.servo_select.setRange(1, 16)
        servo_layout.addWidget(self.servo_select)
        test_layout.addLayout(servo_layout)

        # Pozisyon kontrolü
        pos_layout = QHBoxLayout()
        pos_layout.addWidget(QLabel("Pozisyon:"))
        self.servo_slider = QSlider(Qt.Orientation.Horizontal)
        self.servo_slider.setRange(-100, 100)
        self.servo_slider.valueChanged.connect(self.update_servo_position)
        pos_layout.addWidget(self.servo_slider)
        self.position_value = QLabel("0°")
        pos_layout.addWidget(self.position_value)
        test_layout.addLayout(pos_layout)

        # Test sekansı
        sequence_layout = QHBoxLayout()
        self.sequence_btn = QPushButton("Test Sekansı Başlat")
        self.sequence_btn.clicked.connect(self.start_servo_sequence)
        sequence_layout.addWidget(self.sequence_btn)
        test_layout.addLayout(sequence_layout)

        test_group.setLayout(test_layout)
        layout.addWidget(test_group)

        # Servo durumu
        status_group = QGroupBox("Servo Durumu")
        status_layout = QVBoxLayout()
        self.servo_status = QLabel("Hazır")
        status_layout.addWidget(self.servo_status)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        widget.setLayout(layout)
        return widget

    def create_sensor_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Sensör Test Grubu
        test_group = QGroupBox("Sensör Test")
        test_layout = QVBoxLayout()

        # Sensör seçimi
        sensor_layout = QHBoxLayout()
        sensor_layout.addWidget(QLabel("Sensör:"))
        self.sensor_select = QComboBox()
        self.sensor_select.addItems([
            "IMU",
            "Barometre",
            "GPS",
            "Compass",
            "Akım Sensörü",
            "Voltaj Sensörü"
        ])
        sensor_layout.addWidget(self.sensor_select)
        test_layout.addLayout(sensor_layout)

        # Test başlat
        self.start_sensor_btn = QPushButton("Sensör Testi Başlat")
        self.start_sensor_btn.clicked.connect(self.start_sensor_test)
        test_layout.addWidget(self.start_sensor_btn)

        test_group.setLayout(test_layout)
        layout.addWidget(test_group)

        # Sensör verileri
        data_group = QGroupBox("Sensör Verileri")
        data_layout = QVBoxLayout()
        self.sensor_data = QLabel("Test başlatılmadı")
        data_layout.addWidget(self.sensor_data)
        data_group.setLayout(data_layout)
        layout.addWidget(data_group)

        widget.setLayout(layout)
        return widget

    def check_battery(self):
        # TODO: MAVLink ile batarya durumu kontrolü
        battery_removed = True  # Simüle edilmiş kontrol
        
        if battery_removed:
            self.battery_check.setStyleSheet("background-color: green")
            self.battery_check.setText("Batarya Çıkarıldı ✓")
            self.start_calib_btn.setEnabled(True)
        else:
            self.battery_check.setStyleSheet("background-color: red")
            self.battery_check.setText("Bataryayı Çıkarın!")
            self.start_calib_btn.setEnabled(False)

    def start_esc_calibration(self):
        msg = "ESC kalibrasyonu başlatılacak. Devam etmek istiyor musunuz?"
        reply = QMessageBox.question(self, 'ESC Kalibrasyon', msg,
                                   QMessageBox.StandardButton.Yes | 
                                   QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.progress_bar.show()
            self.progress_bar.setValue(0)
            self.status_label.setText("Kalibrasyon başlatılıyor...")
            
            # Kalibrasyon adımları
            self.calibration_step = 0
            self.calibration_timer = QTimer()
            self.calibration_timer.timeout.connect(self.execute_calibration_step)
            self.calibration_timer.start(1000)

    def execute_calibration_step(self):
        steps = [
            "ESC'lere maksimum sinyal gönderiliyor...",
            "Batarya bağlantısı bekleniyor...",
            "Minimum sinyal gönderiliyor...",
            "Kalibrasyon tamamlanıyor..."
        ]
        
        if self.calibration_step < len(steps):
            self.status_label.setText(steps[self.calibration_step])
            self.progress_bar.setValue((self.calibration_step + 1) * 25)
            self.calibration_step += 1
        else:
            self.calibration_timer.stop()
            self.progress_bar.hide()
            self.status_label.setText("Kalibrasyon tamamlandı")
            self.esc_results.setText("Kalibrasyon başarıyla tamamlandı\nTüm ESC'ler senkronize edildi")
            self.test_completed.emit("esc_calibration", True)

    def update_throttle(self, value):
        self.throttle_value.setText(f"{value}%")
        if hasattr(self, 'current_motor'):
            # TODO: MAVLink ile motor throttle değerini güncelle
            pass

    def start_motor_test(self):
        motor = self.motor_select.value()
        msg = f"Motor {motor} test edilecek. Devam etmek istiyor musunuz?"
        reply = QMessageBox.question(self, 'Motor Test', msg,
                                   QMessageBox.StandardButton.Yes | 
                                   QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.current_motor = motor
            self.start_motor_btn.setEnabled(False)
            self.stop_motor_btn.setEnabled(True)
            self.motor_status.setText(f"Motor {motor} test ediliyor...")
            
            # TODO: MAVLink ile motor testi başlat
            self.update_throttle(self.throttle_slider.value())

    def stop_motor_test(self):
        if hasattr(self, 'current_motor'):
            # TODO: MAVLink ile motoru durdur
            self.motor_status.setText("Test durduruldu")
            self.start_motor_btn.setEnabled(True)
            self.stop_motor_btn.setEnabled(False)
            self.throttle_slider.setValue(0)
            delattr(self, 'current_motor')

    def update_servo_position(self, value):
        self.position_value.setText(f"{value}°")
        # TODO: MAVLink ile servo pozisyonunu güncelle

    def start_servo_sequence(self):
        servo = self.servo_select.value()
        self.sequence_btn.setEnabled(False)
        self.servo_status.setText(f"Servo {servo} test sekansı çalışıyor...")
        
        # Test sekansı
        self.sequence_step = 0
        self.sequence_timer = QTimer()
        self.sequence_timer.timeout.connect(self.execute_servo_sequence)
        self.sequence_timer.start(1000)

    def execute_servo_sequence(self):
        positions = [-100, 0, 100, 0]  # Test pozisyonları
        
        if self.sequence_step < len(positions):
            position = positions[self.sequence_step]
            self.servo_slider.setValue(position)
            self.sequence_step += 1
        else:
            self.sequence_timer.stop()
            self.sequence_btn.setEnabled(True)
            self.servo_status.setText("Test sekansı tamamlandı")
            self.test_completed.emit("servo_test", True)

    def start_sensor_test(self):
        sensor = self.sensor_select.currentText()
        self.start_sensor_btn.setEnabled(False)
        self.sensor_data.setText(f"{sensor} testi başlatılıyor...")
        
        # Sensör testi
        self.sensor_timer = QTimer()
        self.sensor_timer.timeout.connect(lambda: