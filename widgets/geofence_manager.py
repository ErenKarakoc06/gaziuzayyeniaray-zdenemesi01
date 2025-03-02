from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QSpinBox, QDoubleSpinBox, QGroupBox, 
                            QTableWidget, QTableWidgetItem, QMessageBox)
from PyQt6.QtCore import pyqtSignal

class GeofenceManager(QWidget):
    fence_updated = pyqtSignal(dict)  # Geofence ayarları
    
    def __init__(self):
        super().__init__()
        self.fence_points = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Geofence parametreleri
        param_group = QGroupBox("Geofence Parametreleri")
        param_layout = QVBoxLayout()

        # Yükseklik sınırları
        height_layout = QHBoxLayout()
        height_layout.addWidget(QLabel("Minimum Yükseklik (m):"))
        self.min_height = QSpinBox()
        self.min_height.setRange(0, 500)
        height_layout.addWidget(self.min_height)

        height_layout.addWidget(QLabel("Maksimum Yükseklik (m):"))
        self.max_height = QSpinBox()
        self.max_height.setRange(0, 500)
        self.max_height.setValue(120)
        height_layout.addWidget(self.max_height)
        param_layout.addLayout(height_layout)

        # Maksimum yarıçap
        radius_layout = QHBoxLayout()
        radius_layout.addWidget(QLabel("Maksimum Yarıçap (m):"))
        self.max_radius = QSpinBox()
        self.max_radius.setRange(0, 5000)
        self.max_radius.setValue(500)
        radius_layout.addWidget(self.max_radius)
        param_layout.addLayout(radius_layout)

        param_group.setLayout(param_layout)
        layout.addWidget(param_group)

        # Geofence noktaları tablosu
        points_group = QGroupBox("Geofence Noktaları")
        points_layout = QVBoxLayout()

        self.points_table = QTableWidget()
        self.points_table.setColumnCount(2)
        self.points_table.setHorizontalHeaderLabels(['Enlem', 'Boylam'])
        points_layout.addWidget(self.points_table)

        # Nokta kontrol butonları
        button_layout = QHBoxLayout()
        
        add_point_btn = QPushButton("Nokta Ekle")
        add_point_btn.clicked.connect(self.add_fence_point)
        button_layout.addWidget(add_point_btn)

        remove_point_btn = QPushButton("Nokta Sil")
        remove_point_btn.clicked.connect(self.remove_fence_point)
        button_layout.addWidget(remove_point_btn)

        clear_points_btn = QPushButton("Tümünü Temizle")
        clear_points_btn.clicked.connect(self.clear_fence_points)
        button_layout.addWidget(clear_points_btn)

        points_layout.addLayout(button_layout)
        points_group.setLayout(points_layout)
        layout.addWidget(points_group)

        # Geofence kontrolleri
        control_layout = QHBoxLayout()
        
        self.activate_btn = QPushButton("Geofence Aktifleştir")
        self.activate_btn.clicked.connect(self.activate_geofence)
        control_layout.addWidget(self.activate_btn)

        self.deactivate_btn = QPushButton("Geofence Deaktifleştir")
        self.deactivate_btn.clicked.connect(self.deactivate_geofence)
        self.deactivate_btn.setEnabled(False)
        control_layout.addWidget(self.deactivate_btn)

        layout.addLayout(control_layout)
        self.setLayout(layout)

    def add_fence_point(self):
        row = self.points_table.rowCount()
        self.points_table.insertRow(row)
        self.points_table.setItem(row, 0, QTableWidgetItem("0.0"))
        self.points_table.setItem(row, 1, QTableWidgetItem("0.0"))

    def remove_fence_point(self):
        current_row = self.points_table.currentRow()
        if current_row >= 0:
            self.points_table.removeRow(current_row)

    def clear_fence_points(self):
        self.points_table.setRowCount(0)

    def activate_geofence(self):
        if self.points_table.rowCount() < 3:
            QMessageBox.warning(self, "Uyarı", 
                              "Geofence için en az 3 nokta gerekli!")
            return

        # Geofence verilerini topla
        fence_data = {
            'min_height': self.min_height.value(),
            'max_height': self.max_height.value(),
            'max_radius': self.max_radius.value(),
            'points': []
        }

        for row in range(self.points_table.rowCount()):
            lat = float(self.points_table.item(row, 0).text())
            lon = float(self.points_table.item(row, 1).text())
            fence_data['points'].append({'lat': lat, 'lon': lon})

        self.fence_updated.emit(fence_data)
        self.activate_btn.setEnabled(False)
        self.deactivate_btn.setEnabled(True)

    def deactivate_geofence(self):
        self.fence_updated.emit({})  # Boş geofence
        self.activate_btn.setEnabled(True)
        self.deactivate_btn.setEnabled(False)