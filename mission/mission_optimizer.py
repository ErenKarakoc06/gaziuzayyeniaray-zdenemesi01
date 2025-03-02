from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QSpinBox, QDoubleSpinBox, QComboBox, 
                            QProgressBar, QGroupBox)
from PyQt6.QtCore import pyqtSignal
import numpy as np
from scipy.optimize import minimize

class MissionOptimizer(QWidget):
    optimization_completed = pyqtSignal(list)  # optimize edilmiş waypoint'ler

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.waypoints = []

    def init_ui(self):
        layout = QVBoxLayout()

        # Optimizasyon parametreleri
        param_group = QGroupBox("Optimizasyon Parametreleri")
        param_layout = QVBoxLayout()

        # Optimizasyon kriteri
        criteria_layout = QHBoxLayout()
        criteria_layout.addWidget(QLabel("Optimizasyon Kriteri:"))
        self.opt_criteria = QComboBox()
        self.opt_criteria.addItems([
            "Minimum Mesafe",
            "Minimum Süre",
            "Minimum Enerji",
            "Maksimum Kapsama"
        ])
        criteria_layout.addWidget(self.opt_criteria)
        param_layout.addLayout(criteria_layout)

        # Kısıtlamalar
        constraints_layout = QHBoxLayout()
        
        # Maksimum yükseklik
        constraints_layout.addWidget(QLabel("Maks. Yükseklik (m):"))
        self.max_altitude = QSpinBox()
        self.max_altitude.setRange(0, 500)
        self.max_altitude.setValue(120)
        constraints_layout.addWidget(self.max_altitude)
        
        # Minimum mesafe
        constraints_layout.addWidget(QLabel("Min. Waypoint Mesafesi (m):"))
        self.min_distance = QSpinBox()
        self.min_distance.setRange(1, 100)
        self.min_distance.setValue(5)
        constraints_layout.addWidget(self.min_distance)
        
        param_layout.addLayout(constraints_layout)

        # Araç parametreleri
        vehicle_layout = QHBoxLayout()
        
        # Hız
        vehicle_layout.addWidget(QLabel("Hedef Hız (m/s):"))
        self.target_speed = QDoubleSpinBox()
        self.target_speed.setRange(0, 20)
        self.target_speed.setValue(5)
        vehicle_layout.addWidget(self.target_speed)
        
        # Dönüş yarıçapı
        vehicle_layout.addWidget(QLabel("Min. Dönüş Yarıçapı (m):"))
        self.turn_radius = QDoubleSpinBox()
        self.turn_radius.setRange(0, 50)
        self.turn_radius.setValue(5)
        vehicle_layout.addWidget(self.turn_radius)
        
        param_layout.addLayout(vehicle_layout)
        
        param_group.setLayout(param_layout)
        layout.addWidget(param_group)

        # Optimizasyon kontrolleri
        control_layout = QHBoxLayout()
        
        self.optimize_btn = QPushButton("Görevi Optimize Et")
        self.optimize_btn.clicked.connect(self.optimize_mission)
        control_layout.addWidget(self.optimize_btn)
        
        self.reset_btn = QPushButton("Sıfırla")
        self.reset_btn.clicked.connect(self.reset_optimization)
        control_layout.addWidget(self.reset_btn)
        
        layout.addLayout(control_layout)

        # İlerleme çubuğu
        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        self.setLayout(layout)

    def set_waypoints(self, waypoints):
        self.waypoints = waypoints
        self.optimize_btn.setEnabled(len(waypoints) > 1)

    def optimize_mission(self):
        if len(self.waypoints) < 2:
            return

        self.progress.setValue(0)
        criterion = self.opt_criteria.currentText()

        # Optimizasyon parametreleri
        params = {
            'max_altitude': self.max_altitude.value(),
            'min_distance': self.min_distance.value(),
            'target_speed': self.target_speed.value(),
            'turn_radius': self.turn_radius.value()
        }

        # Başlangıç noktaları
        x0 = np.array([wp['lat'] for wp in self.waypoints] + 
                     [wp['lon'] for wp in self.waypoints] +
                     [wp['alt'] for wp in self.waypoints])

        # Kısıtlamalar
        constraints = self.create_constraints(params)

        # Optimizasyon
        if criterion == "Minimum Mesafe":
            result = self.optimize_distance(x0, constraints)
        elif criterion == "Minimum Süre":
            result = self.optimize_time(x0, constraints, params)
        elif criterion == "Minimum Enerji":
            result = self.optimize_energy(x0, constraints, params)
        else:  # Maksimum Kapsama
            result = self.optimize_coverage(x0, constraints)

        # Sonuçları işle
        if result.success:
            self.process_optimization_result(result.x)
            self.progress.setValue(100)
        else:
            self.progress.setValue(0)

    def create_constraints(self, params):
        def altitude_constraint(x):
            n = len(x) // 3
            return params['max_altitude'] - x[2*n:]  # alt değerleri

        def distance_constraint(x):
            n = len(x) // 3
            lats = x[:n]
            lons = x[n:2*n]
            distances = []
            for i in range(n-1):
                d = self.haversine_distance(lats[i], lons[i], lats[i+1], lons[i+1])
                distances.append(d - params['min_distance'])
            return np.array(distances)

        return [
            {'type': 'ineq', 'fun': altitude_constraint},
            {'type': 'ineq', 'fun': distance_constraint}
        ]

    def haversine_distance(self, lat1, lon1, lat2, lon2):
        R = 6371000  # Dünya yarıçapı (metre)
        phi1 = np.radians(lat1)
        phi2 = np.radians(lat2)
        delta_phi = np.radians(lat2 - lat1)
        delta_lambda = np.radians(lon2 - lon1)

        a = (np.sin(delta_phi/2) * np.sin(delta_phi/2) +
             np.cos(phi1) * np.cos(phi2) *
             np.sin(delta_lambda/2) * np.sin(delta_lambda/2))
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        return R * c

    def optimize_distance(self, x0, constraints):
        def objective(x):
            n = len(x) // 3
            total_distance = 0
            for i in range(n-1):
                total_distance += self.haversine_distance(
                    x[i], x[n+i], x[i+1], x[n+i+1]
                )
            return total_distance

        return minimize(objective, x0, constraints=constraints)

    def optimize_time(self, x0, constraints, params):
        def objective(x):
            n = len(x) // 3
            total_time = 0
            for i in range(n-1):
                distance = self.haversine_distance(
                    x[i], x[n+i], x[i+1], x[n+i+1]
                )
                # Basit zaman hesabı (dönüşleri hesaba katarak)
                time = distance / params['target_speed']
                