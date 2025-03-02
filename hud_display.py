from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
import math

class HUDDisplay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        self.telemetry_data = {
            'roll': 0,
            'pitch': 0,
            'yaw': 0,
            'altitude': 0,
            'airspeed': 0,
            'groundspeed': 0,
            'heading': 0,
            'battery_voltage': 0,
            'battery_current': 0,
            'battery_remaining': 0,
            'gps_fix': 0,
            'gps_satellites': 0,
            'mode': 'STABILIZE'
        }
        
        # Görsel özelleştirmeler
        self.colors = {
            'background': QColor(0, 0, 0, 200),
            'horizon': QColor(0, 255, 0),
            'text': QColor(0, 255, 0),
            'warning': QColor(255, 165, 0),
            'critical': QColor(255, 0, 0)
        }
        
        self.fonts = {
            'small': QFont('Monospace', 8),
            'normal': QFont('Monospace', 10),
            'large': QFont('Monospace', 12)
        }
        
        # Güncelleme zamanlayıcısı
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_hud)
        self.update_timer.start(50)  # 20 Hz

    def update_telemetry(self, data):
        self.telemetry_data.update(data)
        self.update()

    def update_hud(self):
        # Telemetri verilerini güncelle (MAVLink'ten)
        pass

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Arka plan
        painter.fillRect(self.rect(), self.colors['background'])
        
        # Ana HUD elemanları
        self.draw_attitude_indicator(painter)
        self.draw_altitude_tape(painter)
        self.draw_speed_tape(painter)
        self.draw_heading_tape(painter)
        self.draw_status_info(painter)

    def draw_attitude_indicator(self, painter):
        center_x = self.width() / 2
        center_y = self.height() / 2
        width = self.width() * 0.8
        height = self.height() * 0.6
        
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(-self.telemetry_data['roll'])
        
        # Yapay ufuk çizgisi
        painter.setPen(QPen(self.colors['horizon'], 2))
        pitch_offset = self.telemetry_data['pitch'] * height / 60.0
        painter.drawLine(-width/2, pitch_offset, width/2, pitch_offset)
        
        # Pitch çizgileri
        for pitch in range(-60, 61, 10):
            y = -pitch * height / 60.0 + pitch_offset
            if abs(pitch) == 0:
                line_width = width * 0.5
            else:
                line_width = width * 0.2
            
            if -height/2 <= y <= height/2:
                painter.drawLine(-line_width/2, y, line_width/2, y)
                
                if pitch != 0:
                    painter.drawText(-line_width/2 - 20, y + 5, f"{abs(pitch)}")
        
        painter.restore()

    def draw_altitude_tape(self, painter):
        x = self.width() - 60
        height = self.height() * 0.8
        
        painter.setPen(self.colors['text'])
        
        # Altimetre arka planı
        painter.fillRect(x, (self.height() - height)/2, 50, height, 
                        QColor(0, 0, 0, 150))
        
        # Yükseklik değerleri
        alt = self.telemetry_data['altitude']
        for i in range(-5, 6):
            y = self.height()/2 + i * height/10
            display_alt = int(alt - i * 10)
            painter.drawText(x + 5, y + 5, f"{display_alt:3d}m")
        
        # Mevcut yükseklik işaretçisi
        painter.setPen(QPen(self.colors['horizon'], 2))
        painter.drawRect(x - 5, self.height()/2 - 10, 60, 20)
        painter.drawText(x + 5, self.height()/2 + 5, f"{int(alt):3d}m")

    def draw_speed_tape(self, painter):
        x = 10
        height = self.height() * 0.8
        
        painter.setPen(self.colors['text'])
        
        # Hız göstergesi arka planı
        painter.fillRect(x, (self.height() - height)/2, 50, height,
                        QColor(0, 0, 0, 150))
        
        # Hız değerleri
        speed = self.telemetry_data['groundspeed']
        for i in range(-5, 6):
            y = self.height()/2 + i * height/10
            display_speed = int(speed - i * 5)
            if display_speed >= 0:
                painter.drawText(x + 5, y + 5, f"{display_speed:3d}")
        
        # Mevcut hız işaretçisi
        painter.setPen(QPen(self.colors['horizon'], 2))
        painter.drawRect(x - 5, self.height()/2 - 10, 60, 20)
        painter.drawText(x + 5, self.height()/2 + 5, f"{int(speed):3d}")

    def draw_heading_tape(self, painter):
        y = 20
        width = self.width() * 0.8
        
        painter.setPen(self.colors['text'])
        
        # Pusula arka planı
        painter.fillRect((self.width() - width)/2, y, width, 30,
                        QColor(0, 0, 0, 150))
        
        # Yön değerleri
        heading = self.telemetry_data['heading']
        center_x = self.width() / 2
        for i in range(-5, 6):
            x = center_x + i * width/10
            display_heading = (int(heading) + i * 30) % 360
            painter.drawText(x - 10, y + 20, f"{display_heading:03d}")
        
        # Mevcut yön işaretçisi
        painter.setPen(QPen(self.colors['horizon'], 2))
        painter.drawRect(center_x - 15, y - 5, 30, 40)
        painter.drawText(center_x - 10, y + 20, f"{int(heading):03d}")

    def draw_status_info(self, painter):
        painter.setPen(self.colors['text'])
        painter.setFont(self.fonts['normal'])
        
        # Sol alt bilgiler
        y = self.height() - 60
        painter.drawText(10, y, f"BAT: {self.telemetry_data['battery_voltage']:.1f}V")
        painter.drawText(10, y + 20, f"CUR: {self.telemetry_data['battery_current']:.1f}A")
        painter.drawText(10, y + 40, f"REM: {self.telemetry_data['battery_remaining']}%")
        
        # Sağ alt bilgiler
        x = self.width() - 100
        painter.drawText(x, y, f"GPS: {self.telemetry_data['gps_fix']}")
        painter.drawText(x, y + 20, f"SAT: {self.telemetry_data['gps_satellites']}")
        
        # Üst bilgiler
        painter.setFont(self.fonts['large'])
        mode_text = self.telemetry_data['mode']
        mode_width = painter.fontMetrics().horizontalAdvance(mode_text)
        painter.drawText(self.width()/2 - mode_width/2, 15, mode_text)
