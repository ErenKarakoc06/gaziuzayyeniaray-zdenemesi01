from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QComboBox, QSpinBox, QColorDialog, 
                            QCheckBox, QGroupBox, QTabWidget, QSlider)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont

class HUDCustomization(QWidget):
    settings_changed = pyqtSignal(dict)  # HUD ayarları

    def __init__(self):
        super().__init__()
        self.hud_settings = {
            'elements': {
                'artificial_horizon': {
                    'enabled': True,
                    'position': {'x': 0.5, 'y': 0.5},
                    'size': 1.0,
                    'color': QColor(0, 255, 0),
                    'opacity': 0.8
                },
                'altitude_tape': {
                    'enabled': True,
                    'position': {'x': 0.9, 'y': 0.5},
                    'size': 1.0,
                    'color': QColor(0, 255, 0),
                    'show_units': True
                },
                'speed_tape': {
                    'enabled': True,
                    'position': {'x': 0.1, 'y': 0.5},
                    'size': 1.0,
                    'color': QColor(0, 255, 0),
                    'show_units': True
                },
                'compass': {
                    'enabled': True,
                    'position': {'x': 0.5, 'y': 0.1},
                    'size': 1.0,
                    'color': QColor(0, 255, 0),
                    'show_cardinal': True
                },
                'battery_indicator': {
                    'enabled': True,
                    'position': {'x': 0.1, 'y': 0.9},
                    'size': 1.0,
                    'warning_level': 20,
                    'critical_level': 10
                },
                'flight_mode': {
                    'enabled': True,
                    'position': {'x': 0.5, 'y': 0.05},
                    'font_size': 14,
                    'color': QColor(0, 255, 0)
                }
            },
            'general': {
                'background_opacity': 0.3,
                'font_family': 'Arial',
                'units': 'metric'
            }
        }
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Ana ayarlar sekmesi
        tabs = QTabWidget()
        tabs.addTab(self.create_elements_tab(), "HUD Elemanları")
        tabs.addTab(self.create_general_tab(), "Genel Ayarlar")
        tabs.addTab(self.create_layout_tab(), "Yerleşim")
        layout.addWidget(tabs)

        # Önizleme ve kontroller
        preview_group = QGroupBox("Önizleme")
        preview_layout = QVBoxLayout()
        
        self.preview_widget = HUDPreview(self.hud_settings)
        preview_layout.addWidget(self.preview_widget)
        
        control_layout = QHBoxLayout()
        
        apply_btn = QPushButton("Uygula")
        apply_btn.clicked.connect(self.apply_settings)
        control_layout.addWidget(apply_btn)
        
        reset_btn = QPushButton("Varsayılana Dön")
        reset_btn.clicked.connect(self.reset_settings)
        control_layout.addWidget(reset_btn)
        
        preview_layout.addLayout(control_layout)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        self.setLayout(layout)

    def create_elements_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        for element_name, settings in self.hud_settings['elements'].items():
            group = QGroupBox(element_name.replace('_', ' ').title())
            element_layout = QVBoxLayout()
            
            # Etkinleştirme
            enable_cb = QCheckBox("Etkin")
            enable_cb.setChecked(settings['enabled'])
            enable_cb.stateChanged.connect(
                lambda state, e=element_name: self.toggle_element(e, state)
            )
            element_layout.addWidget(enable_cb)
            
            # Boyut kontrolü
            if 'size' in settings:
                size_layout = QHBoxLayout()
                size_layout.addWidget(QLabel("Boyut:"))
                size_slider = QSlider(Qt.Orientation.Horizontal)
                size_slider.setRange(50, 150)
                size_slider.setValue(int(settings['size'] * 100))
                size_slider.valueChanged.connect(
                    lambda value, e=element_name: self.set_element_size(e, value/100)
                )
                size_layout.addWidget(size_slider)
                element_layout.addLayout(size_layout)
            
            # Renk seçici
            if 'color' in settings:
                color_layout = QHBoxLayout()
                color_layout.addWidget(QLabel("Renk:"))
                color_btn = QPushButton()
                color_btn.setStyleSheet(
                    f"background-color: {settings['color'].name()};"
                )
                color_btn.clicked.connect(
                    lambda checked, e=element_name: self.choose_color(e)
                )
                color_layout.addWidget(color_btn)
                element_layout.addLayout(color_layout)
            
            # Özel ayarlar
            if element_name == 'battery_indicator':
                warn_layout = QHBoxLayout()
                warn_layout.addWidget(QLabel("Uyarı Seviyesi (%):"))
                warn_spin = QSpinBox()
                warn_spin.setRange(0, 100)
                warn_spin.setValue(settings['warning_level'])
                warn_spin.valueChanged.connect(
                    lambda value: self.set_battery_warning(value)
                )
                warn_layout.addWidget(warn_spin)
                element_layout.addLayout(warn_layout)
            
            elif element_name == 'flight_mode':
                font_layout = QHBoxLayout()
                font_layout.addWidget(QLabel("Yazı Boyutu:"))
                font_spin = QSpinBox()
                font_spin.setRange(8, 24)
                font_spin.setValue(settings['font_size'])
                font_spin.valueChanged.connect(
                    lambda value: self.set_font_size('flight_mode', value)
                )
                font_layout.addWidget(font_spin)
                element_layout.addLayout(font_layout)
            
            group.setLayout(element_layout)
            layout.addWidget(group)

        widget.setLayout(layout)
        return widget

    def create_general_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Arka plan opaklığı
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Arka Plan Opaklığı:"))
        opacity_slider = QSlider(Qt.Orientation.Horizontal)
        opacity_slider.setRange(0, 100)
        opacity_slider.setValue(int(self.hud_settings['general']['background_opacity'] * 100))
        opacity_slider.valueChanged.connect(self.set_background_opacity)
        opacity_layout.addWidget(opacity_slider)
        layout.addLayout(opacity_layout)

        # Yazı tipi
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("Yazı Tipi:"))
        font_combo = QComboBox()
        font_combo.addItems(['Arial', 'Helvetica', 'Courier', 'Times New Roman'])
        font_combo.setCurrentText(self.hud_settings['general']['font_family'])
        font_combo.currentTextChanged.connect(self.set_font_family)
        font_layout.addWidget(font_combo)
        layout.addLayout(font_layout)

        # Birim sistemi
        units_layout = QHBoxLayout()
        units_layout.addWidget(QLabel("Birim Sistemi:"))
        units_combo = QComboBox()
        units_combo.addItems(['metric', 'imperial'])
        units_combo.setCurrentText(self.hud_settings['general']['units'])
        units_combo.currentTextChanged.connect(self.set_units)
        units_layout.addWidget(units_combo)
        layout.addLayout(units_layout)

        widget.setLayout(layout)
        return widget

    def create_layout_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Sürükle-bırak düzenleyici
        self.layout_editor = HUDLayoutEditor(self.hud_settings)
        layout.addWidget(self.layout_editor)

        widget.setLayout(layout)
        return widget

    def toggle_element(self, element_name, state):
        self.hud_settings['elements'][element_name]['enabled'] = bool(state)
        self.preview_widget.update_settings(self.hud_settings)

    def set_element_size(self, element_name, size):
        self.hud_settings['elements'][element_name]['size'] = size
        self.preview_widget.update_settings(self.hud_settings)

    def choose_color(self, element_name):
        current_color = self.hud_settings['elements'][element_name]['color']
        color = QColorDialog.getColor(current_color, self)
        if color.isValid():
            self.hud_settings['elements'][element_name]['color'] = color
            self.preview_widget.update_settings(self.hud_settings)
            # Renk butonunu güncelle
            self.sender().setStyleSheet(f"background-color: {color.name()};")

    def set_battery_warning(self, value):
        self.hud_settings['elements']['battery_indicator']['warning_level'] = value
        self.preview_widget.update_settings(self.hud_settings)

    def set_font_size(self, element_name, size):
        self.hud_settings['elements'][element_name]['font_size'] = size
        self.preview_widget.update_settings(self.hud_settings)

    def set_background_opacity(self, value):
        self.hud_settings['general']['background_opacity'] = value / 100
        self.preview_widget.update_settings(self.hud_settings)

    def set_font_family(self, font_family):
        self.hud_settings['general']['font_family'] = font_family
        self.preview_widget.update_settings(self.hud_settings)

    def set_units(self, units):
        self.hud_settings['general']['units'] = units
        self.preview_widget.update_settings(self.hud_settings)

    def apply_settings(self):
        self.settings_changed.emit(self.hud_settings)

    def reset_settings(self):
        # Varsayılan ayarları yükle
        self.__init__()
        self.preview_widget.update_settings(self.hud_settings)