from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QComboBox, QLabel, QSpinBox, QGroupBox)
from PyQt6.QtCore import QProcess, pyqtSignal, Qt
import os
import json

class SITLManager(QWidget):
    simulation_started = pyqtSignal(dict)  # Simülasyon parametreleri
    simulation_stopped = pyqtSignal()
    vehicle_state_updated = pyqtSignal(dict)  # Araç durumu

    def __init__(self):
        super().__init__()
        self.processes = {}  # Simülasyon süreçleri
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Simülasyon Kontrolleri
        control_group = QGroupBox("Simülasyon Kontrolleri")
        control_layout = QVBoxLayout()

        # Araç tipi seçimi
        vehicle_layout = QHBoxLayout()
        vehicle_layout.addWidget(QLabel("Araç Tipi:"))
        self.vehicle_type = QComboBox()
        self.vehicle_type.addItems(["Quadcopter", "Hexacopter", "Plane", "Rover"])
        vehicle_layout.addWidget(self.vehicle_type)
        control_layout.addLayout(vehicle_layout)

        # Başlangıç konumu
        position_layout = QHBoxLayout()
        position_layout.addWidget(QLabel("Başlangıç Konumu:"))
        self.latitude = QSpinBox()
        self.latitude.setRange(-90, 90)
        self.longitude = QSpinBox()
        self.longitude.setRange(-180, 180)
        position_layout.addWidget(self.latitude)
        position_layout.addWidget(self.longitude)
        control_layout.addLayout(position_layout)

        # İnstans sayısı (çoklu araç için)
        instance_layout = QHBoxLayout()
        instance_layout.addWidget(QLabel("Araç Sayısı:"))
        self.instance_count = QSpinBox()
        self.instance_count.setRange(1, 10)
        instance_layout.addWidget(self.instance_count)
        control_layout.addLayout(instance_layout)

        # Kontrol butonları
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Simülasyonu Başlat")
        self.start_button.clicked.connect(self.start_simulation)
        self.stop_button = QPushButton("Simülasyonu Durdur")
        self.stop_button.clicked.connect(self.stop_simulation)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        control_layout.addLayout(button_layout)

        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        # Simülasyon Durumu
        status_group = QGroupBox("Simülasyon Durumu")
        status_layout = QVBoxLayout()
        self.status_label = QLabel("Hazır")
        status_layout.addWidget(self.status_label)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        self.setLayout(layout)

    def start_simulation(self):
        num_instances = self.instance_count.value()
        vehicle_type = self.vehicle_type.currentText().lower()
        
        for i in range(num_instances):
            # Her araç için benzersiz port ve ID oluştur
            sysid = 1 + i
            mavlink_port = 14550 + i
            simulator_port = 5760 + i
            
            # Simülasyon parametreleri
            params = {
                "vehicle_type": vehicle_type,
                "sysid": sysid,
                "mavlink_port": mavlink_port,
                "simulator_port": simulator_port,
                "latitude": self.latitude.value(),
                "longitude": self.longitude.value()
            }
            
            # SITL sürecini başlat
            process = QProcess()
            cmd = self.build_sitl_command(params)
            process.start(cmd)
            
            self.processes[sysid] = {
                "process": process,
                "params": params
            }
            
            # Süreci izle
            process.readyReadStandardOutput.connect(
                lambda p=process: self.handle_output(p)
            )
            process.readyReadStandardError.connect(
                lambda p=process: self.handle_error(p)
            )

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText(f"Çalışıyor ({num_instances} araç)")
        self.simulation_started.emit({"num_instances": num_instances})

    def stop_simulation(self):
        for sysid, data in self.processes.items():
            process = data["process"]
            if process.state() == QProcess.ProcessState.Running:
                process.terminate()
                process.waitForFinished(1000)
                if process.state() == QProcess.ProcessState.Running:
                    process.kill()

        self.processes.clear()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Durduruldu")
        self.simulation_stopped.emit()

    def build_sitl_command(self, params):
        # ArduPilot SITL komutunu oluştur
        cmd = f"sim_vehicle.py -v {params['vehicle_type']}"
        cmd += f" --sysid {params['sysid']}"
        cmd += f" --mavproxy-args=\"--master tcp:127.0.0.1:{params['simulator_port']}"
        cmd += f" --out 127.0.0.1:{params['mavlink_port']}\""
        cmd += f" --location {params['latitude']},{params['longitude']},0,0"
        return cmd

    def handle_output(self, process):
        data = process.readAllStandardOutput().data().decode()
        # Simülasyon çıktısını işle ve durumu güncelle
        self.parse_simulation_output(data)

    def handle_error(self, process):
        data = process.readAllStandardError().data().decode()
        # Hata mesajlarını işle
        self.status_label.setText(f"Hata: {data}")

    def parse_simulation_output(self, output):
        # Simülasyon çıktısını parse et ve araç durumunu güncelle
        try:
            # Örnek çıktı formatı: {"lat": 47.123, "lon": 8.456, "alt": 100}
            state = json.loads(output)
            self.vehicle_state_updated.emit(state)
        except:
            pass

    def closeEvent(self, event):
        self.stop_simulation()
        super().closeEvent(event)