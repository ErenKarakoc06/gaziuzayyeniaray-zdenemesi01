from PyQt6.QtWidgets import QOpenGLWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtCore import Qt, QRectF
import math

class AdvancedHUD(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 300)
        self.data = {
            'pitch': 0,
            'roll': 0,
            'heading': 0,
            'altitude': 0,
            'airspeed': 0,
            'groundspeed': 0,
            'vertical_speed': 0,
            'gps_status': 0,
            'battery_voltage': 0,
            'battery_percent': 0,
            'mode': 'UNKNOWN'
        }
        self.font = QFont('Monospace', 10)

    def update_data(self, new_data: dict):
        self.data.update(new_data)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Arka plan
        painter.fillRect(self.rect(), QColor(0, 0, 0))
        
        # HUD çizimi
        self.draw_attitude_indicator(painter)
        self.draw_heading_indicator(painter)
        self.draw_altitude_speed_bars(painter)
        self.draw_status_info(painter)

    def draw_attitude_indicator(self, painter):
        center_x = self.width() / 2
        center_y = self.height() / 2
        
        # Yapay ufuk için transformasyon
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(-self.data['roll'])
        
        # Ufuk çizgisi
        sky_color = QColor(0, 128, 255)
        ground_color = QColor(139, 69, 19)
        
        pitch_pixel_ratio = 2  # Derece başına piksel
        pitch_offset = self.data['pitch'] * pitch_pixel_ratio
        
        # Gökyüzü
        painter.fillRect(QRectF(-200, -1000, 400, 1000 + pitch_offset), sky_color)
        # Yeryüzü
        painter.fillRect(QRectF(-200, pitch_offset, 400, 1000), ground_color)
        
        # Pitch çizgileri
        painter.setPen(QPen(Qt.GlobalColor.white, 2))
        for pitch in range(-90, 91, 10):
            y = -pitch * pitch_pixel_ratio + pitch_offset
            if abs(pitch) % 30 == 0:
                width = 100
            else:
                width = 50
            
            if pitch != 0:  # 0 derecede çizgi çizme
                painter.drawLine(-width/2, y, width/2, y)
                # Derece göstergesi
                if abs(pitch) % 30 == 0:
                    painter.drawText(-width/2 - 30, y + 5, f"{abs(pitch)}")
                    painter.drawText(width/2 + 10, y + 5, f"{abs(pitch)}")
        
        painter.restore()

    def draw_heading_indicator(self, painter):
        compass_y = self.height() - 50
        compass_width = self.width() - 100
        
        painter.setPen(QPen(Qt.GlobalColor.white, 2))
        
        # Pusula arkplanı
        painter.fillRect(50, compass_y - 20, compass_width, 40, QColor(0, 0, 0, 150))
        
        # Pusula çizgileri ve sayıları
        heading = self.data['heading']
        for i in range(-30, 31, 5):
            x = self.width()/2 + (i * 10) - (heading % 10) * 10
            if x >= 50 and x <= self.width() - 50:
                if i % 10 == 0:
                    # Ana yönler
                    heading_mark = (heading - i + 360) % 360
                    if heading_mark == 0:
                        text = "N"
                    elif heading_mark == 90:
                        text = "E"
                    elif heading_mark == 180:
                        text = "S"
                    elif heading_mark == 270:
                        text = "W"
                    else:
                        text = str(heading_mark)
                    painter.drawText(x - 10, compass_y - 25, text)
                    painter.drawLine(x, compass_y - 15, x, compass_y + 15)
                else:
                    painter.drawLine(x, compass_y - 10, x, compass_y + 10)

    def draw_altitude_speed_bars(self, painter):
        # Yükseklik çubuğu
        alt_x = self.width() - 60
        self.draw_vertical_scale(painter, 
                               alt_x, 
                               self.data['altitude'], 
                               "ALT", 
                               "m",
                               step=10)
        
        # Hız çubuğu
        speed_x = 60
        self.draw_vertical_scale(painter, 
                               speed_x, 
                               self.data['groundspeed'], 
                               "GND", 
                               "m/s",
                               step=5)

    def draw_vertical_scale(self, painter, x, value, label, unit, step=5):
        height = self.height() - 100
        y = 50
        width = 40
        
        # Arka plan
        painter.fillRect(x - width/2, y, width, height, QColor(0, 0, 0, 150))
        
        # Değer çizgileri
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        
        # Orta değer
        mid_value = round(value / step) * step
        
        for i in range(-5, 6):
            current_value = mid_value + (i * step)
            if current_value >= 0:
                y_pos = self.height()/2 - (i * 20)
                painter.drawLine(x - width/2, y_pos, x - width/4, y_pos)
                painter.drawText(x - width/2, y_pos + 5, str(current_value))
        
        # Ana değer göstergesi
        painter.setPen(QPen(Qt.GlobalColor.yellow, 2))
        y_value = self.height()/2
        painter.drawText(x - width/2, y_value - 15, f"{label}")
        painter.drawText(x - width/2, y_value + 25, f"{value:.1f}{unit}")

    def draw_status_info(self, painter):
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        painter.setFont(self.font)
        
        # Sol üst köşe bilgileri
        text_y = 20
        painter.drawText(10, text_y, f"Mode: {self.data['mode']}")
        text_y += 20
        painter.drawText(10, text_y, 
                        f"Battery: {self.data['battery_voltage']:.1f}V ({self.data['battery_percent']}%)")
        text_y += 20
        painter.drawText(10, text_y, f"GPS: {self.data['gps_status']}")