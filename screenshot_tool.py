from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QScreen, QGuiApplication
import os
from datetime import datetime

class ScreenshotTool(QWidget):
    screenshot_taken = pyqtSignal(str)  # screenshot_path
    
    def __init__(self):
        super().__init__()
        self.screenshot_dir = os.path.expanduser("~/drone_screenshots")
        self.ensure_screenshot_directory()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Kontroller
        controls_layout = QHBoxLayout()
        
        full_screen_btn = QPushButton("Tam Ekran")
        full_screen_btn.clicked.connect(self.take_full_screenshot)
        controls_layout.addWidget(full_screen_btn)

        window_btn = QPushButton("Aktif Pencere")
        window_btn.clicked.connect(self.take_window_screenshot)
        controls_layout.addWidget(window_btn)

        region_btn = QPushButton("Bölge Seç")
        region_btn.clicked.connect(self.take_region_screenshot)
        controls_layout.addWidget(region_btn)

        layout.addLayout(controls_layout)

        # Önizleme
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(320, 240)
        layout.addWidget(self.preview_label)

        # Son görüntü bilgisi
        self.info_label = QLabel("Hazır")
        layout.addWidget(self.info_label)

        self.setLayout(layout)

    def ensure_screenshot_directory(self):
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)

    def take_full_screenshot(self):
        try:
            screen = QGuiApplication.primaryScreen()
            if screen:
                screenshot = screen.grabWindow(0)
                self.save_screenshot(screenshot)
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Ekran görüntüsü alınamadı: {str(e)}")

    def take_window_screenshot(self):
        try:
            window = QGuiApplication.activeWindow()
            if window:
                screen = QGuiApplication.primaryScreen()
                screenshot = screen.grabWindow(window.winId())
                self.save_screenshot(screenshot)
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Pencere görüntüsü alınamadı: {str(e)}")

    def take_region_screenshot(self):
        # Region selector widget'ı göster
        self.region_selector = RegionSelector(self)
        self.region_selector.region_selected.connect(self.capture_region)
        self.region_selector.showFullScreen()

    def capture_region(self, rect):
        try:
            screen = QGuiApplication.primaryScreen()
            if screen:
                screenshot = screen.grabWindow(0, rect.x(), rect.y(), 
                                            rect.width(), rect.height())
                self.save_screenshot(screenshot)
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Bölge görüntüsü alınamadı: {str(e)}")

    def save_screenshot(self, pixmap):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(self.screenshot_dir, filename)
        
        if pixmap.save(filepath):
            self.update_preview(pixmap)
            self.info_label.setText(f"Kaydedildi: {filepath}")
            self.screenshot_taken.emit(filepath)
        else:
            QMessageBox.warning(self, "Hata", "Görüntü kaydedilemedi")

    def update_preview(self, pixmap):
        scaled_pixmap = pixmap.scaled(
            self.preview_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.preview_label.setPixmap(scaled_pixmap)

class RegionSelector(QWidget):
    region_selected = pyqtSignal(object)  # QRect
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.start_pos = None
        self.current_pos = None
        self.is_selecting = False

    def paintEvent(self, event):
        if self.start_pos and self.current_pos:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.GlobalColor.red, 2))
            
            # Seçim alanını göster
            rect = self.get_selection_rect()
            painter.drawRect(rect)
            
            # Yarı saydam overlay
            overlay = QColor(0, 0, 0, 100)
            painter.fillRect(self.rect(), overlay)
            painter.eraseRect(rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.pos()
            self.current_pos = self.start_pos
            self.is_selecting = True

    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.current_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_selecting:
            self.is_selecting = False
            self.current_pos = event.pos()
            self.region_selected.emit(self.get_selection_rect())
            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()

    def get_selection_rect(self):
        if not self.start_pos or not self.current_pos:
            return QRect()
            
        return QRect(
            min(self.start_pos.x(), self.current_pos.x()),
            min(self.start_pos.y(), self.current_pos.y()),
            abs(self.current_pos.x() - self.start_pos.x()),
            abs(self.current_pos.y() - self.start_pos.y())
        )