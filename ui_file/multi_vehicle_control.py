from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
                            QPushButton, QLabel, QComboBox, QSpinBox, 
                            QDoubleSpinBox, QGroupBox, QTableWidget, 
                            QTableWidgetItem, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from .widgets.vehicle_status import VehicleStatusWidget
from simulation.ardupilot_sitl import ArdupilotSITL

class MultiVehicleControl(QWidget):
    def __init__(self):
        super().__init__()
        self.sitl = ArdupilotSITL()
        self.vehicles = {}
        self.init_ui()
        
        # SITL sinyallerini bağla
        self.sitl.state_updated.connect(self.update_vehicle_state)
        self.sitl.connection_status.connect(self.handle_connection_status)
        self.sitl.log_message.connect(self.handle_log_message)

    def init_ui(self):
        layout = QVBoxLayout()

        # Araç Kontrolü
        control_group = QGroupBox("Araç Kontrolü")
        control_layout = QVBoxLayout()

        # Yeni araç ekleme
        add_layout = QHBoxLayout()
        
        self.vehicle_type = QComboBox()
        self.vehicle_type.addItems(['quad', 'hexa', 'octa', 'plane', 'rover'])
        add_layout.addWidget(QLabel("Araç Tipi:"))
        add_layout.addWidget(self.vehicle_type)

        self.vehicle_id = QSpinBox()
        self.vehicle_id.setRange(1, 255)
        add_layout.addWidget(QLabel("Araç ID:"))
        add_layout.addWidget(self.vehicle_id)

        add_btn = QPushButton("Araç Ekle")
        add_btn.clicked.connect(self.add_vehicle)
        add_layout.addWidget(add_btn)

        control_layout.addLayout(add_layout)

        # Araç listesi ve durumları
        self.vehicle_tabs = QTabWidget()
        control_layout.addWidget(self.vehicle_tabs)

        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        # Toplu Kontroller
        batch_group = QGroupBox("Toplu Kontroller")
        batch_layout = QHBoxLayout()

        arm_all_btn = QPushButton("Tümünü Arm Et")
        arm_all_btn.clicked.connect(self.arm_all_vehicles)
        batch_layout.addWidget(arm_all_btn)

        disarm_all_btn = QPushButton("Tümünü Disarm Et")
        disarm_all_btn.clicked.connect(self.disarm_all_vehicles)
        batch_layout.addWidget(disarm_all_btn)

        takeoff_all_btn = QPushButton("Toplu Kalkış")
        takeoff_all_btn.clicked.connect(self.takeoff_all_vehicles)
        batch_layout.addWidget(takeoff_all_btn)

        rtl_all_btn = QPushButton("Tümünü RTL'e Al")
        rtl_all_btn.clicked.connect(self.rtl_all_vehicles)
        batch_layout.addWidget(rtl_all_btn)

        batch_group.setLayout(batch_layout)
        layout.addWidget(batch_group)

        self.setLayout(layout)

    def add_vehicle(self):
        vehicle_id = self.vehicle_id.value()
        if vehicle_id in self.vehicles:
            QMessageBox.warning(self, "Hata", f"Vehicle {vehicle_id} zaten mevcut!")
            return

        # Yeni araç sekmesi oluştur
        vehicle_widget = VehicleStatusWidget(vehicle_id)
        self.vehicle_tabs.addTab(vehicle_widget, f"Vehicle {vehicle_id}")
        
        # SITL instance başlat
        location = {
            'lat': 40.0 + (vehicle_id * 0.001),  # Her araç için farklı konum
            'lon': 32.0,
            'alt': 0,
            'heading': 0
        }
        
        if self.sitl.start_instance(vehicle_id, self.vehicle_type.currentText(), location):
            self.vehicles[vehicle_id] = vehicle_widget
            vehicle_widget.command_requested.connect(
                lambda cmd, params: self.handle_vehicle_command(vehicle_id, cmd, params)
            )

    def update_vehicle_state(self, data):
        vehicle_id = data['vehicle_id']
        if vehicle_id in self.vehicles:
            self.vehicles[vehicle_id].update_state(data['state'])

    def handle_connection_status(self, connected, message):
        if connected:
            QMessageBox.information(self, "Bağlantı", message)
        else:
            QMessageBox.warning(self, "Bağlantı Kesildi", message)

    def handle_log_message(self, message):
        print(f"SITL Log: {message}")  # Veya log paneline ekle

    def handle_vehicle_command(self, vehicle_id, command, params=None):
        self.sitl.send_command(vehicle_id, command, params)

    def arm_all_vehicles(self):
        for vehicle_id in self.vehicles:
            self.sitl.send_command(vehicle_id, 'COMPONENT_ARM_DISARM', {'arm': 1})

    def disarm_all_vehicles(self):
        for vehicle_id in self.vehicles:
            self.sitl.send_command(vehicle_id, 'COMPONENT_ARM_DISARM', {'arm': 0})

    def takeoff_all_vehicles(self):
        for vehicle_id in self.vehicles:
            self.sitl.send_command(vehicle_id, 'NAV_TAKEOFF', {'altitude': 10})

    def rtl_all_vehicles(self):
        for vehicle_id in self.vehicles:
            self.sitl.send_command(vehicle_id, 'NAV_RETURN_TO_LAUNCH')

    def closeEvent(self, event):
        self.sitl.stop_all()
        super().closeEvent(event)