from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QComboBox, QSlider, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView
import folium
import numpy as np
import json
import os

class Map3DView(QWidget):
    location_selected = pyqtSignal(float, float, float)  # lat, lon, alt
    
    def __init__(self):
        super().__init__()
        self.map_view = None
        self.current_position = None
        self.waypoints = []
        self.flight_path = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Harita kontrolleri
        controls_layout = QHBoxLayout()
        
        # Harita tipi seçimi
        controls_layout.addWidget(QLabel("Harita Tipi:"))
        self.map_type = QComboBox()
        self.map_type.addItems([
            "Terrain",
            "Satellite",
            "Hybrid",
            "OpenStreetMap"
        ])
        self.map_type.currentTextChanged.connect(self.change_map_type)
        controls_layout.addWidget(self.map_type)

        # 3D görünüm kontrolü
        self.view_3d = QCheckBox("3D Görünüm")
        self.view_3d.stateChanged.connect(self.toggle_3d_view)
        controls_layout.addWidget(self.view_3d)

        # Yükseklik abartma kontrolü
        controls_layout.addWidget(QLabel("Yükseklik Abartma:"))
        self.elevation_scale = QSlider(Qt.Orientation.Horizontal)
        self.elevation_scale.setRange(1, 5)
        self.elevation_scale.setValue(1)
        self.elevation_scale.valueChanged.connect(self.update_elevation_scale)
        controls_layout.addWidget(self.elevation_scale)

        # Görünürlük kontrolleri
        self.show_waypoints = QCheckBox("Waypoints")
        self.show_waypoints.setChecked(True)
        self.show_waypoints.stateChanged.connect(self.update_map)
        controls_layout.addWidget(self.show_waypoints)

        self.show_flight_path = QCheckBox("Uçuş Yolu")
        self.show_flight_path.setChecked(True)
        self.show_flight_path.stateChanged.connect(self.update_map)
        controls_layout.addWidget(self.show_flight_path)

        layout.addLayout(controls_layout)

        # Harita görünümü
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)

        self.setLayout(layout)
        self.init_map()

    def init_map(self):
        # Başlangıç konumu (Ankara)
        center = [39.9334, 32.8597]
        
        # Folium haritası oluştur
        self.map_view = folium.Map(
            location=center,
            zoom_start=13,
            tiles='Stamen Terrain'
        )
        
        # 3D terrain layer ekle
        self.add_terrain_layer()
        
        # Haritayı göster
        self.save_and_display_map()

    def add_terrain_layer(self):
        # Mapbox terrain layer
        terrain = folium.TileLayer(
            tiles='https://api.mapbox.com/v4/mapbox.terrain-rgb/{z}/{x}/{y}.pngraw?access_token=YOUR_MAPBOX_TOKEN',
            attr='Mapbox',
            name='Terrain'
        )
        terrain.add_to(self.map_view)

    def change_map_type(self, map_type):
        if map_type == "Terrain":
            self.map_view.tiles = 'Stamen Terrain'
        elif map_type == "Satellite":
            self.map_view.tiles = 'Stamen Satellite'
        elif map_type == "Hybrid":
            self.map_view.tiles = 'Stamen Hybrid'
        else:
            self.map_view.tiles = 'OpenStreetMap'
        
        self.save_and_display_map()

    def toggle_3d_view(self, state):
        if state:
            # 3D görünümü etkinleştir
            self.elevation_scale.setEnabled(True)
            self.update_elevation_scale(self.elevation_scale.value())
        else:
            # 2D görünüme dön
            self.elevation_scale.setEnabled(False)
            self.update_map()

    def update_elevation_scale(self, value):
        if self.view_3d.isChecked():
            # 3D görünümü güncelle
            self.map_view.options['terrain_exaggeration'] = value
            self.save_and_display_map()

    def add_waypoint(self, lat, lon, alt):
        waypoint = {
            'lat': lat,
            'lon': lon,
            'alt': alt
        }
        self.waypoints.append(waypoint)
        self.update_map()

    def add_flight_path_point(self, lat, lon, alt):
        point = {
            'lat': lat,
            'lon': lon,
            'alt': alt
        }
        self.flight_path.append(point)
        self.update_map()

    def update_map(self):
        if not self.map_view:
            return

        # Haritayı temizle
        self.map_view.erase()

        # Waypoint'leri göster
        if self.show_waypoints.isChecked():
            for i, wp in enumerate(self.waypoints):
                folium.Marker(
                    [wp['lat'], wp['lon']],
                    popup=f'WP{i+1}: Alt={wp["alt"]}m',
                    icon=folium.Icon(color='red', icon='info-sign')
                ).add_to(self.map_view)

        # Uçuş yolunu göster
        if self.show_flight_path.isChecked() and len(self.flight_path) > 1:
            points = [[p['lat'], p['lon']] for p in self.flight_path]
            folium.PolyLine(
                points,
                weight=2,
                color='blue',
                opacity=0.8
            ).add_to(self.map_view)

        # Mevcut konumu göster
        if self.current_position:
            folium.Marker(
                [self.current_position['lat'], self.current_position['lon']],
                popup=f'Current Alt={self.current_position["alt"]}m',
                icon=folium.Icon(color='green', icon='plane')
            ).add_to(self.map_view)

        self.save_and_display_map()

    def save_and_display_map(self):
        # Haritayı geçici dosyaya kaydet
        temp_file = "temp_map.html"
        self.map_view.save(temp_file)
        
        # Web görünümünde göster
        self.web_view.setUrl(QUrl.fromLocalFile(os.path.abspath(temp_file)))

    def update_current_position(self, lat, lon, alt):
        self.current_position = {
            'lat': lat,
            'lon': lon,
            'alt': alt
        }
        self.update_map()

    def clear_waypoints(self):
        self.waypoints = []
        self.update_map()

    def clear_flight_path(self):
        self.flight_path = []
        self.update_map()