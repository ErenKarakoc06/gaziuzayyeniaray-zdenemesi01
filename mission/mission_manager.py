from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                            QTableWidgetItem, QPushButton, QComboBox, QLabel,
                            QSpinBox, QDoubleSpinBox, QGroupBox, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
import numpy as np
from datetime import datetime

class MissionManager(QWidget):
    mission_updated = pyqtSignal(list)  # Görev noktaları
    mission_started = pyqtSignal()
    mission_completed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.mission_points = []
        self.current_mission = None
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()

        # Görev Planlama
        planning_group = QGroupBox("Görev Planlama")
        planning_layout = QVBoxLayout()

        # Görev tipi seçimi 
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Görev Tipi:"))
        self.mission_type = QComboBox()
        self.mission_type.addItems([
            "Waypoint Navigation",
            "Grid Survey",
            "Perimeter Scan",
            "Point of Interest",
            "Search Pattern",
            "Custom Mission"
        ])
        type_layout.addWidget(self.mission_type)
        planning_layout.addLayout(type_layout)

        # Görev parametreleri
        param_layout = QHBoxLayout()
        
        param_layout.addWidget(QLabel("Yükseklik (m):"))
        self.altitude = QSpinBox()
        self.altitude.setRange(0, 500)
        self.altitude.setValue(50)
        param_layout.addWidget(self.altitude)

        param_layout.addWidget(QLabel("Hız (m/s):"))
        self.speed = QDoubleSpinBox()
        self.speed.setRange(0, 20)
        self.speed.setValue(5)
        param_layout.addWidget(self.speed)

        planning_layout.addLayout(param_layout)

        # Görev noktaları tablosu
        self.mission_table = QTableWidget()
        self.mission_table.setColumnCount(6)
        self.mission_table.setHorizontalHeaderLabels([
            'Sıra', 'Enlem', 'Boylam', 'Yükseklik', 'Komut', 'Parametre'
        ])
        planning_layout.addWidget(self.mission_table)

        # Tablo kontrolleri
        table_controls = QHBoxLayout()
        
        add_point_btn = QPushButton("Nokta Ekle")
        add_point_btn.clicked.connect(self.add_mission_point)
        table_controls.addWidget(add_point_btn)

        remove_point_btn = QPushButton("Noktayı Sil")
        remove_point_btn.clicked.connect(self.remove_mission_point)
        table_controls.addWidget(remove_point_btn)

        clear_points_btn = QPushButton("Tümünü Temizle")
        clear_points_btn.clicked.connect(self.clear_mission_points)
        table_controls.addWidget(clear_points_btn)

        planning_layout.addLayout(table_controls)
        planning_group.setLayout(planning_layout)
        layout.addWidget(planning_group)

        # Görev Optimizasyonu
        optimization_group = QGroupBox("Görev Optimizasyonu")
        optimization_layout = QVBoxLayout()

        # Optimizasyon parametreleri
        opt_params = QHBoxLayout()
        
        opt_params.addWidget(QLabel("Optimizasyon Kriteri:"))
        self.opt_criteria = QComboBox()
        self.opt_criteria.addItems([
            "Minimum Mesafe",
            "Minimum Süre",
            "Minimum Enerji",
            "Maksimum Kapsama"
        ])
        opt_params.addWidget(self.opt_criteria)

        optimization_layout.addLayout(opt_params)

        # Optimizasyon kontrolleri
        opt_controls = QHBoxLayout()
        
        optimize_btn = QPushButton("Görevi Optimize Et")
        optimize_btn.clicked.connect(self.optimize_mission)
        opt_controls.addWidget(optimize_btn)

        simulation_btn = QPushButton("Simülasyon")
        simulation_btn.clicked.connect(self.simulate_mission)
        opt_controls.addWidget(simulation_btn)

        optimization_layout.addLayout(opt_controls)
        optimization_group.setLayout(optimization_layout)
        layout.addWidget(optimization_group)

        # Görev Kontrolü
        control_group = QGroupBox("Görev Kontrolü")
        control_layout = QHBoxLayout()

        upload_btn = QPushButton("Görevi Yükle")
        upload_btn.clicked.connect(self.upload_mission)
        control_layout.addWidget(upload_btn)

        start_btn = QPushButton("Görevi Başlat")
        start_btn.clicked.connect(self.start_mission)
        control_layout.addWidget(start_btn)

        pause_btn = QPushButton("Görevi Duraklat")
        pause_btn.clicked.connect(self.pause_mission)
        control_layout.addWidget(pause_btn)

        abort_btn = QPushButton("Görevi İptal Et")
        abort_btn.clicked.connect(self.abort_mission)
        control_layout.addWidget(abort_btn)

        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        self.setLayout(layout)

    def add_mission_point(self):
        row = self.mission_table.rowCount()
        self.mission_table.insertRow(row)
        
        # Varsayılan değerler
        self.mission_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
        self.mission_table.setItem(row, 1, QTableWidgetItem("0.0"))
        self.mission_table.setItem(row, 2, QTableWidgetItem("0.0"))
        self.mission_table.setItem(row, 3, QTableWidgetItem(str(self.altitude.value())))
        
        # Komut seçici
        command_selector = QComboBox()
        command_selector.addItems([
            "WAYPOINT",
            "LOITER",
            "RTL",
            "LAND",
            "TAKEOFF"
        ])
        self.mission_table.setCellWidget(row, 4, command_selector)
        
        self.mission_table.setItem(row, 5, QTableWidgetItem("0"))

    def remove_mission_point(self):
        current_row = self.mission_table.currentRow()
        if current_row >= 0:
            self.mission_table.removeRow(current_row)
            self.update_sequence_numbers()

    def clear_mission_points(self):
        self.mission_table.setRowCount(0)
        self.mission_points = []
        self.mission_updated.emit([])

    def update_sequence_numbers(self):
        for row in range(self.mission_table.rowCount()):
            self.mission_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))

    def optimize_mission(self):
        if self.mission_table.rowCount() < 2:
            QMessageBox.warning(self, "Uyarı", "En az 2 nokta gerekli!")
            return

        optimization_type = self.opt_criteria.currentText()
        
        # Noktaları topla
        points = []
        for row in range(self.mission_table.rowCount()):
            try:
                point = {
                    'lat': float(self.mission_table.item(row, 1).text()),
                    'lon': float(self.mission_table.item(row, 2).text()),
                    'alt': float(self.mission_table.item(row, 3).text()),
                    'command': self.mission_table.cellWidget(row, 4).currentText(),
                    'param': float(self.mission_table.item(row, 5).text())
                }
                points.append(point)
            except ValueError:
                QMessageBox.warning(self, "Hata", f"Geçersiz değer - Satır {row + 1}")
                return

        # Optimizasyon algoritması
        if optimization_type == "Minimum Mesafe":
            optimized = self.optimize_distance(points)
        elif optimization_type == "Minimum Süre":
            optimized = self.optimize_time(points)
        elif optimization_type == "Minimum Enerji":
            optimized = self.optimize_energy(points)
        else:  # Maksimum Kapsama
            optimized = self.optimize_coverage(points)

        # Optimize edilmiş rotayı göster
        self.update_mission_table(optimized)
        self.mission_updated.emit(optimized)

    def optimize_distance(self, points):
        # TSP benzeri optimizasyon
        coords = np.array([[p['lat'], p['lon']] for p in points])
        n_points = len(coords)
        
        def calculate_total_distance(order):
            ordered = coords[order]
            return np.sum(np.sqrt(np.sum(np.diff(ordered, axis=0)**2, axis=1)))

        # Başlangıç sıralaması
        current_order = np.arange(n_points)
        best_distance = calculate_total_distance(current_order)
        best_order = current_order.copy()

        # 2-opt algoritması
        improved = True
        while improved:
            improved = False
            for i in range(1, n_points-2):
                for j in range(i+1, n_points):
                    new_order = current_order.copy()
                    new_order[i:j] = new_order[i:j][::-1]
                    new_distance = calculate_total_distance(new_order)
                    
                    if new_distance < best_distance:
                        best_distance = new_distance
                        best_order = new_order.copy()
                        improved = True
            current_order = best_order.copy()

        return [points[i] for i in best_order]

    def simulate_mission(self):
        if not self.mission_points:
            QMessageBox.warning(self, "Uyarı", "Simülasyon için görev noktaları gerekli!")
            return

        # Simülasyon parametreleri
        sim_speed = 10  # 10x hız
        update_rate = 100  # ms

        # Simülasyon durumu
        self.sim_current_point = 0
        self.sim_position = {
            'lat': self.mission_points[0]['lat'],
            'lon': self.mission_points[0]['lon'],
            'alt': 0
        }

        def update_simulation():
            if self.sim_current_point >= len(self.mission_points):
                self.sim_timer.stop()
                QMessageBox.information(self, "Simülasyon", "Simülasyon tamamlandı!")
                return

            target = self.mission_points[self.sim_current_point]
            
            # Pozisyonu güncelle
            dx = (target['lat'] - self.sim_position['lat']) * sim_speed * update_rate / 1000
            dy = (target['lon'] - self.sim_position['lon']) * sim_speed * update_rate / 1000
            dz = (target['alt'] - self.sim_position['alt']) * sim_speed * update_rate / 1000

            self.sim_position['lat'] += dx
            self.sim_position['lon'] += dy
            self.sim_position['alt'] += dz

            # Hedefe varış kontrolü
            dist = np.sqrt((target['lat'] - self.sim_position['lat'])**2 +
                         (target['lon'] - self.sim_position['lon'])**2 +
                         (target['alt'] - self.sim_position['alt'])**2)

            if dist < 0.0001:  # Yaklaşık 10m
                self.sim_current_point += 1

            # GUI güncelleme sinyali gönder
            # TODO: Harita ve telemetri güncellemesi

        self.sim_timer = QTimer()
        self.sim_timer.timeout.connect(update_simulation)
        self.sim_timer.start(update_rate)

    def upload_mission(self):
        try:
            # Görev noktalarını topla
            mission = []
            for row in range(self.mission_table.rowCount()):
                point = {
                    'seq': int(self.mission_table.item(row, 0).text()),
                    'lat': float(self.mission_table.item(row, 1).text()),
                    'lon': float(self.mission_table.item(row, 2).text()),
                    'alt': float(self.mission_table.item(row, 3).text()),
                    'command': self.mission_table.cellWidget(row, 4).currentText(),
                    'param': float(self.mission_table.item(row, 5).text())
                }
                mission.append(point)

            # MAVLink üzerinden gönder
            self.upload_mission_to_vehicle(mission)
            QMessageBox.information(self, "Başarılı", "Görev araca yüklendi!")

        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Görev yükleme hatası: {str(e)}")

    def upload_mission_to_vehicle(self, mission):
        # TODO: MAVLink mission upload implementasyonu
        pass

    def start_mission(self):
        if not self.current_mission:
            QMessageBox.warning(self, "Uyarı", "Başlatılacak görev yok!")
            return

        # TODO: MAVLink mission start komutu
        self.mission_started.emit()

    def pause_mission(self):
        # TODO: MAVLink mission pause komutu
        pass

    def abort_mission(self):
        result = QMessageBox.question(
            self, "Görevi İptal Et",
            "Görevi iptal etmek istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            # TODO: MAVLink mission abort komutu
            self.current_mission = None
