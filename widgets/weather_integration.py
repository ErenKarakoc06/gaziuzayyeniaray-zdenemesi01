from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                            QLabel, QPushButton, QComboBox)
from PyQt6.QtCore import QTimer, pyqtSignal
import requests
import json
from datetime import datetime, timedelta

class WeatherWidget(QWidget):
    weather_updated = pyqtSignal(dict)  # Hava durumu verileri
    weather_alert = pyqtSignal(str)     # Hava durumu uyarıları

    def __init__(self):
        super().__init__()
        self.api_key = "YOUR_WEATHER_API_KEY"  # OpenWeatherMap API anahtarı
        self.current_location = None
        self.init_ui()
        
        # Otomatik güncelleme zamanlayıcısı
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_weather)
        self.update_timer.start(300000)  # Her 5 dakikada bir güncelle

    def init_ui(self):
        layout = QVBoxLayout()

        # Mevcut hava durumu
        current_group = QGroupBox("Mevcut Hava Durumu")
        current_layout = QVBoxLayout()

        # Temel bilgiler
        self.temperature_label = QLabel("Sıcaklık: -- °C")
        self.humidity_label = QLabel("Nem: -- %")
        self.pressure_label = QLabel("Basınç: -- hPa")
        self.wind_label = QLabel("Rüzgar: -- m/s, -- °")
        self.visibility_label = QLabel("Görüş: -- km")
        self.clouds_label = QLabel("Bulut: -- %")
        self.rain_label = QLabel("Yağış: -- mm")

        current_layout.addWidget(self.temperature_label)
        current_layout.addWidget(self.humidity_label)
        current_layout.addWidget(self.pressure_label)
        current_layout.addWidget(self.wind_label)
        current_layout.addWidget(self.visibility_label)
        current_layout.addWidget(self.clouds_label)
        current_layout.addWidget(self.rain_label)

        current_group.setLayout(current_layout)
        layout.addWidget(current_group)

        # Tahmin
        forecast_group = QGroupBox("Hava Tahmini")
        forecast_layout = QVBoxLayout()

        # Tahmin süresi seçimi
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Tahmin Süresi:"))
        self.forecast_duration = QComboBox()
        self.forecast_duration.addItems(["3 Saat", "6 Saat", "12 Saat", "24 Saat"])
        self.forecast_duration.currentTextChanged.connect(self.update_weather)
        duration_layout.addWidget(self.forecast_duration)
        forecast_layout.addLayout(duration_layout)

        # Tahmin etiketleri
        self.forecast_labels = []
        for _ in range(4):  # 4 zaman dilimi için tahmin
            label = QLabel()
            self.forecast_labels.append(label)
            forecast_layout.addWidget(label)

        forecast_group.setLayout(forecast_layout)
        layout.addWidget(forecast_group)

        # Uçuş uygunluğu
        flight_group = QGroupBox("Uçuş Uygunluğu")
        flight_layout = QVBoxLayout()

        self.flight_status = QLabel("Uçuş Durumu: Değerlendiriliyor...")
        self.flight_warnings = QLabel("Uyarılar: --")
        flight_layout.addWidget(self.flight_status)
        flight_layout.addWidget(self.flight_warnings)

        flight_group.setLayout(flight_layout)
        layout.addWidget(flight_group)

        # Kontroller
        controls_layout = QHBoxLayout()
        
        update_btn = QPushButton("Güncelle")
        update_btn.clicked.connect(self.update_weather)
        controls_layout.addWidget(update_btn)

        layout.addLayout(controls_layout)
        self.setLayout(layout)

    def set_location(self, lat, lon):
        self.current_location = (lat, lon)
        self.update_weather()

    def update_weather(self):
        if not self.current_location:
            return

        try:
            # Mevcut hava durumu
            current_url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'lat': self.current_location[0],
                'lon': self.current_location[1],
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(current_url, params=params)
            current_data = response.json()

            # Temel bilgileri güncelle
            self.temperature_label.setText(f"Sıcaklık: {current_data['main']['temp']:.1f} °C")
            self.humidity_label.setText(f"Nem: {current_data['main']['humidity']}%")
            self.pressure_label.setText(f"Basınç: {current_data['main']['pressure']} hPa")
            self.wind_label.setText(
                f"Rüzgar: {current_data['wind']['speed']} m/s, {current_data['wind'].get('deg', 0)}°"
            )
            self.visibility_label.setText(f"Görüş: {current_data.get('visibility', 0)/1000:.1f} km")
            self.clouds_label.setText(f"Bulut: {current_data['clouds']['all']}%")
            
            if 'rain' in current_data:
                self.rain_label.setText(f"Yağış: {current_data['rain'].get('1h', 0)} mm")
            else:
                self.rain_label.setText("Yağış: 0 mm")

            # Tahmin verilerini al
            forecast_url = f"http://api.openweathermap.org/data/2.5/forecast"
            response = requests.get(forecast_url, params=params)
            forecast_data = response.json()

            # Tahminleri güncelle
            hours = int(self.forecast_duration.currentText().split()[0])
            steps = min(4, hours // 3)
            
            for i in range(steps):
                forecast = forecast_data['list'][i]
                time = datetime.fromtimestamp(forecast['dt'])
                self.forecast_labels[i].setText(
                    f"{time.strftime('%H:%M')}: "
                    f"{forecast['main']['temp']:.1f}°C, "
                    f"{forecast['wind']['speed']} m/s, "
                    f"{forecast['weather'][0]['description']}"
                )

            # Uçuş uygunluğunu değerlendir
            self.evaluate_flight_conditions(current_data, forecast_data)

            # Sinyal gönder
            self.weather_updated.emit({
                'current': current_data,
                'forecast': forecast_data
            })

        except Exception as e:
            print(f"Hava durumu güncellenirken hata: {e}")

    def evaluate_flight_conditions(self, current, forecast):
        warnings = []
        is_safe = True

        # Rüzgar kontrolü
        if current['wind']['speed'] > 10:
            warnings.append("Yüksek rüzgar hızı")
            is_safe = False

        # Görüş kontrolü
        if current.get('visibility', 0) < 5000:
            warnings.append("Düşük görüş mesafesi")
            is_safe = False

        # Yağış kontrolü
        if 'rain' in current:
            warnings.append("Yağış var")
            is_safe = False

        # Sıcaklık kontrolü
        if current['main']['temp'] < 0 or current['main']['temp'] > 40:
            warnings.append("Uygun olmayan sıcaklık")
            is_safe = False

        # Durum güncelleme
        status = "UYGUN" if is_safe else "UYGUN DEĞİL"
        self.flight_status.setText(f"Uçuş Durumu: {status}")
        self.flight_warnings.setText(f"Uyarılar: {', '.join(warnings) if warnings else 'Yok'}")

        # Tehlikeli durum varsa uyarı sinyali gönder
        if warnings:
            self.weather_alert.emit(", ".join(warnings))