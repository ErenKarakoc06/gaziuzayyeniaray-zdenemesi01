from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                            QLabel, QPushButton, QComboBox, QProgressBar)
from PyQt6.QtCore import QTimer, pyqtSignal, Qt
import requests
import json
from datetime import datetime, timedelta
import numpy as np

class WeatherStation(QWidget):
    weather_updated = pyqtSignal(dict)
    weather_alert = pyqtSignal(str)
    flight_status_changed = pyqtSignal(bool, str)  # uygunluk durumu, mesaj

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.weather_data = {}
        self.weather_thresholds = {
            'wind_speed': 10.0,  # m/s
            'visibility': 5000,  # metre
            'rain_rate': 0.5,    # mm/saat
            'temperature': {
                'min': -10,      # Celsius
                'max': 40        # Celsius
            },
            'pressure_change': 5  # hPa/saat
        }
        
        # Otomatik güncelleme
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_weather)
        self.update_timer.start(300000)  # 5 dakikada bir güncelle

    def init_ui(self):
        layout = QVBoxLayout()

        # Hava Durumu Bilgileri
        weather_group = QGroupBox("Anlık Hava Durumu")
        weather_layout = QVBoxLayout()

        # Temel parametreler
        self.labels = {
            'temperature': QLabel("Sıcaklık: -- °C"),
            'humidity': QLabel("Nem: -- %"),
            'pressure': QLabel("Basınç: -- hPa"),
            'wind_speed': QLabel("Rüzgar Hızı: -- m/s"),
            'wind_direction': QLabel("Rüzgar Yönü: -- °"),
            'visibility': QLabel("Görüş: -- km"),
            'clouds': QLabel("Bulut Oranı: -- %"),
            'precipitation': QLabel("Yağış: -- mm/h")
        }

        for label in self.labels.values():
            weather_layout.addWidget(label)

        weather_group.setLayout(weather_layout)
        layout.addWidget(weather_group)

        # Tahmin Bilgileri
        forecast_group = QGroupBox("Hava Tahmini")
        forecast_layout = QVBoxLayout()

        # Tahmin süresi seçimi
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Tahmin Süresi:"))
        self.forecast_duration = QComboBox()
        self.forecast_duration.addItems(["3 Saat", "6 Saat", "12 Saat", "24 Saat"])
        time_layout.addWidget(self.forecast_duration)
        forecast_layout.addLayout(time_layout)

        # Tahmin bilgileri
        self.forecast_labels = [QLabel() for _ in range(4)]
        for label in self.forecast_labels:
            forecast_layout.addWidget(label)

        forecast_group.setLayout(forecast_layout)
        layout.addWidget(forecast_group)

        # Uçuş Uygunluğu
        flight_group = QGroupBox("Uçuş Uygunluğu Analizi")
        flight_layout = QVBoxLayout()

        # Parametrelerin durumu
        self.parameter_status = {
            'wind': QProgressBar(),
            'visibility': QProgressBar(),
            'precipitation': QProgressBar(),
            'temperature': QProgressBar()
        }

        for param, bar in self.parameter_status.items():
            bar.setRange(0, 100)
            bar.setTextVisible(True)
            label = QLabel(param.capitalize())
            flight_layout.addWidget(label)
            flight_layout.addWidget(bar)

        # Genel durum
        self.flight_status = QLabel("Uçuş Durumu: Değerlendiriliyor...")
        self.flight_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        flight_layout.addWidget(self.flight_status)

        flight_group.setLayout(flight_layout)
        layout.addWidget(flight_group)

        # Kontroller
        controls_layout = QHBoxLayout()
        
        update_btn = QPushButton("Güncelle")
        update_btn.clicked.connect(self.update_weather)
        controls_layout.addWidget(update_btn)

        settings_btn = QPushButton("Ayarlar")
        settings_btn.clicked.connect(self.show_settings)
        controls_layout.addWidget(settings_btn)

        layout.addLayout(controls_layout)
        self.setLayout(layout)

    def update_weather(self):
        try:
            # OpenWeatherMap API'den veri al
            api_key = "YOUR_API_KEY"
            lat, lon = 40.0, 32.0  # Varsayılan konum
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
            
            response = requests.get(url)
            data = response.json()

            # Verileri işle
            self.weather_data = {
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'wind_speed': data['wind']['speed'],
                'wind_direction': data['wind']['deg'],
                'visibility': data.get('visibility', 10000),
                'clouds': data['clouds']['all'],
                'precipitation': data.get('rain', {}).get('1h', 0)
            }

            # Label'ları güncelle
            self.update_labels()

            # Uçuş uygunluğunu değerlendir
            self.evaluate_flight_conditions()

            # Tahmin verilerini güncelle
            self.update_forecast()

            # Sinyal gönder
            self.weather_updated.emit(self.weather_data)

        except Exception as e:
            print(f"Hava durumu güncelleme hatası: {str(e)}")

    def update_labels(self):
        self.labels['temperature'].setText(f"Sıcaklık: {self.weather_data['temperature']:.1f} °C")
        self.labels['humidity'].setText(f"Nem: {self.weather_data['humidity']}%")
        self.labels['pressure'].setText(f"Basınç: {self.weather_data['pressure']} hPa")
        self.labels['wind_speed'].setText(f"Rüzgar Hızı: {self.weather_data['wind_speed']} m/s")
        self.labels['wind_direction'].setText(f"Rüzgar Yönü: {self.weather_data['wind_direction']}°")
        self.labels['visibility'].setText(f"Görüş: {self.weather_data['visibility']/1000:.1f} km")
        self.labels['clouds'].setText(f"Bulut Oranı: {self.weather_data['clouds']}%")
        self.labels['precipitation'].setText(f"Yağış: {self.weather_data['precipitation']} mm/h")

    def evaluate_flight_conditions(self):
        conditions = {}
        warnings = []

        # Rüzgar değerlendirmesi
        wind_score = max(0, 100 - (self.weather_data['wind_speed'] / self.weather_thresholds['wind_speed'] * 100))
        self.parameter_status['wind'].setValue(int(wind_score))
        if wind_score < 50:
            warnings.append("Yüksek rüzgar hızı")

        # Görüş değerlendirmesi
        visibility_score = min(100, self.weather_data['visibility'] / self.weather_thresholds['visibility'] * 100)
        self.parameter_status['visibility'].setValue(int(visibility_score))
        if visibility_score < 50:
            warnings.append("Düşük görüş mesafesi")

        # Yağış değerlendirmesi
        precip_score = max(0, 100 - (self.weather_data['precipitation'] / self.weather_thresholds['rain_rate'] * 100))
        self.parameter_status['precipitation'].setValue(int(precip_score))
        if precip_score < 50:
            warnings.append("Yağış var")

        # Sıcaklık değerlendirmesi
        temp = self.weather_data['temperature']
        temp_range = self.weather_thresholds['temperature']['max'] - self.weather_thresholds['temperature']['min']
        temp_score = max(0, 100 - (abs(temp - (self.weather_thresholds['temperature']['max'] + self.weather_thresholds['temperature']['min'])/2) / (temp_range/2) * 100))
        self.parameter_status['temperature'].setValue(int(temp_score))
        if temp_score < 50:
            warnings.append("Uygun olmayan sıcaklık")

        # Genel değerlendirme
        overall_score = np.mean([wind_score, visibility_score, precip_score, temp_score])
        flight_suitable = overall_score >= 70

        # Durumu güncelle
        status_text = "UYGUN" if flight_suitable else "UYGUN DEĞİL"
        self.flight_status.setText(f"Uçuş Durumu: {status_text}")
        if warnings:
            self.weather_alert.emit("\n".join(warnings))

        self.flight_status_changed.emit(flight_suitable, "\n".join(warnings) if warnings else "Uçuşa uygun koşullar")

    def update_forecast(self):
        try:
            hours = int(self.forecast_duration.currentText().split()[0])
            api_key = "YOUR_API_KEY"
            lat, lon = 40.0, 32.0
            url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
            
            response = requests.get(url)
            data = response.json()

            for i, forecast in enumerate(data['list'][:4]):
                time = datetime.fromtimestamp(forecast['dt'])
                temp = forecast['main']['temp']
                wind = forecast['wind']['speed']
                desc = forecast['weather'][0]['description']
                
                self.forecast_labels[i].setText(
                    f"{time.strftime('%H:%M')}: {temp:.1f}°C, {wind}m/s, {desc}"
                )

        except Exception as e:
            print(f"Tahmin güncelleme hatası: {str(e)}")

    def show_settings(self):
        # TODO: Hava durumu ayarları dialog'unu göster
        pass

    def closeEvent(self, event):
        self.update_timer.stop()
        super().closeEvent(event)