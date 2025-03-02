from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QPushButton, QComboBox, QSpinBox, 
                            QDoubleSpinBox, QGroupBox, QLabel)
from PyQt6.QtCore import Qt

class MissionPlannerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.waypoints = []

    def init_ui(self):
        layout = QVBoxLayout()

        # Görev tablosu
        self.mission_table = QTableWidget()
        self.mission_table.setColumnCount(8)
        self.mission_table.setHorizontalHeaderLabels([
            'Sıra', 'Komut', 'Param1', 'Param2', 'Param3', 'Param4', 
            'Enlem', 'Boylam'
        ])
        layout.addWidget(self.mission_table)

        # Kontrol butonları
        button_layout = QHBoxLayout()
        
        self.add_wp_btn = QPushButton("Waypoint Ekle")
        self.add_wp_btn.clicked.connect(self.add_waypoint)
        
        self.remove_wp_btn = QPushButton("Waypoint Sil")
        self.remove_wp_btn.clicked.connect(self.remove_waypoint)
        
        self.clear_btn = QPushButton("Tümünü Temizle")
        self.clear_btn.clicked.connect(self.clear_mission)
        
        self.upload_btn = QPushButton("Görevi Yükle")
        self.upload_btn.clicked.connect(self.upload_mission)
        
        self.download_btn = QPushButton("Görevi İndir")
        self.download_btn.clicked.connect(self.download_mission)
        
        button_layout.addWidget(self.add_wp_btn)
        button_layout.addWidget(self.remove_wp_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.upload_btn)
        button_layout.addWidget(self.download_btn)
        
        layout.addLayout(button_layout)

        # Waypoint ayarları
        wp_settings = QGroupBox("Waypoint Ayarları")
        wp_layout = QGridLayout()
        
        # Komut seçici
        self.cmd_combo = QComboBox()
        self.cmd_combo.addItems([
            "WAYPOINT",
            "TAKEOFF",
            "LAND",
            "RTL",
            "LOITER",
            "ROI"
        ])
        wp_layout.addWidget(QLabel("Komut:"), 0, 0)
        wp_layout.addWidget(self.cmd_combo, 0, 1)
        
        # Yükseklik
        self.altitude_spin = QSpinBox()
        self.altitude_spin.setRange(0, 1000)
        self.altitude_spin.setSuffix("m")
        wp_layout.addWidget(QLabel("Yükseklik:"), 1, 0)
        wp_layout.addWidget(self.altitude_spin, 1, 1)
        
        # Bekleme süresi
        self.delay_spin = QDoubleSpinBox()
        self.delay_spin.setRange(0, 600)
        self.delay_spin.setSuffix("s")
        wp_layout.addWidget(QLabel("Bekleme:"), 2, 0)
        wp_layout.addWidget(self.delay_spin, 2, 1)
        
        wp_settings.setLayout(wp_layout)
        layout.addWidget(wp_settings)

        self.setLayout(layout)

    def add_waypoint(self):
        row = self.mission_table.rowCount()
        self.mission_table.insertRow(row)
        
        # Sıra numarası
        self.mission_table.setItem(row, 0, QTableWidgetItem(str(row)))
        
        # Komut
        self.mission_table.setItem(row, 1, QTableWidgetItem(self.cmd_combo.currentText()))
        
        # Parametreler
        for i in range(2, 8):
            self.mission_table.setItem(row, i, QTableWidgetItem("0"))

    def remove_waypoint(self):
        current_row = self.mission_table.currentRow()
        if current_row >= 0:
            self.mission_table.removeRow(current_row)
            self.reorder_waypoints()

    def clear_mission(self):
        self.mission_table.setRowCount(0)

    def reorder_waypoints(self):
        for row in range(self.mission_table.rowCount()):
            self.mission_table.item(row, 0).setText(str(row))

    def upload_mission(self):
        # Görevi araca yükle
        mission_items = []
        for row in range(self.mission_table.rowCount()):
            item = {
                'seq': int(self.mission_table.item(row, 0).text()),
                'command': self.mission_table.item(row, 1).text(),
                'param1': float(self.mission_table.item(row, 2).text()),
                'param2': float(self.mission_table.item(row, 3).text()),
                'param3': float(self.mission_table.item(row, 4).text()),
                'param4': float(self.mission_table.item(row, 5).text()),
                'lat': float(self.mission_table.item(row, 6).text()),
                'lon': float(self.mission_table.item(row, 7).text())
            }
            mission_items.append(item)
        
        # TODO: MAVLink üzerinden görevi gönder

    def download_mission(self):
        # Araçtan görevi al
        # TODO: MAVLink üzerinden görevi al
        pass