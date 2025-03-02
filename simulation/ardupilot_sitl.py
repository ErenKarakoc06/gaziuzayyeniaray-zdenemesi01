from PyQt6.QtCore import QProcess, QTimer, pyqtSignal, QObject
import os
import json
import time
import math

class ArdupilotSITL(QObject):
    state_updated = pyqtSignal(dict)
    connection_status = pyqtSignal(bool, str)
    log_message = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.processes = {}
        self.vehicle_states = {}
        self.frame_types = {
            'quad': 'copter',
            'hexa': 'copter',
            'octa': 'copter',
            'plane': 'plane',
            'rover': 'rover'
        }
        self.init_params = {
            'copter': {
                'SYSID_THISMAV': 1,
                'FRAME_CLASS': 1,  # Quad
                'FS_THR_ENABLE': 1,  # Failsafe aktif
                'BATT_MONITOR': 4,  # Batarya izleme aktif
            },
            'plane': {
                'SYSID_THISMAV': 1,
                'STALL_PREVENTION': 1,
                'TKOFF_ROTATE_SPD': 15,
            },
            'rover': {
                'SYSID_THISMAV': 1,
                'WP_RADIUS': 2,
                'TURN_RADIUS': 2,
            }
        }

    def start_instance(self, vehicle_id, frame_type, location, params=None):
        """SITL instance başlat"""
        if vehicle_id in self.processes:
            self.log_message.emit(f"Vehicle {vehicle_id} zaten çalışıyor")
            return False

        vehicle_type = self.frame_types.get(frame_type, 'copter')
        base_port = 5760 + (vehicle_id * 10)

        # SITL parametrelerini oluştur
        sitl_params = [
            '--model', frame_type,
            '--home', f"{location['lat']},{location['lon']},{location['alt']},{location['heading']}",
            '--base-port', str(base_port),
            '--instance', str(vehicle_id)
        ]

        # ArduPilot SITL sürecini başlat
        process = QProcess()
        process.setProgram('sim_vehicle.py')
        process.setArguments(['-v', vehicle_type] + sitl_params)
        
        # Çıktıları izle
        process.readyReadStandardOutput.connect(
            lambda: self.handle_output(vehicle_id, process.readAllStandardOutput())
        )
        process.readyReadStandardError.connect(
            lambda: self.handle_error(vehicle_id, process.readAllStandardError())
        )

        try:
            process.start()
            self.processes[vehicle_id] = {
                'process': process,
                'type': vehicle_type,
                'ports': {
                    'sitl': base_port,
                    'mavlink': base_port + 1,
                    'debug': base_port + 2
                }
            }
            
            # Başlangıç parametrelerini ayarla
            self.configure_vehicle(vehicle_id, params)
            
            self.connection_status.emit(True, f"Vehicle {vehicle_id} başlatıldı")
            return True

        except Exception as e:
            self.log_message.emit(f"SITL başlatma hatası: {str(e)}")
            return False

    def configure_vehicle(self, vehicle_id, custom_params=None):
        """Araç parametrelerini ayarla"""
        if vehicle_id not in self.processes:
            return

        vehicle_type = self.processes[vehicle_id]['type']
        params = self.init_params.get(vehicle_type, {}).copy()
        
        # Özel parametreleri ekle
        if custom_params:
            params.update(custom_params)

        # MAVLink üzerinden parametreleri gönder
        for param_id, value in params.items():
            self.send_parameter(vehicle_id, param_id, value)

    def send_parameter(self, vehicle_id, param_id, value):
        """MAVLink üzerinden parametre gönder"""
        port = self.processes[vehicle_id]['ports']['mavlink']
        # TODO: MAVLink parameter_set mesajı gönder

    def stop_instance(self, vehicle_id):
        """SITL instance durdur"""
        if vehicle_id in self.processes:
            process = self.processes[vehicle_id]['process']
            process.terminate()
            process.waitForFinished(5000)
            if process.state() == QProcess.ProcessState.Running:
                process.kill()
            del self.processes[vehicle_id]
            self.connection_status.emit(False, f"Vehicle {vehicle_id} durduruldu")

    def stop_all(self):
        """Tüm SITL instance'ları durdur"""
        for vehicle_id in list(self.processes.keys()):
            self.stop_instance(vehicle_id)

    def handle_output(self, vehicle_id, output):
        """SITL çıktılarını işle"""
        try:
            data = output.data().decode().strip()
            if data:
                # Telemetri verilerini parse et
                if 'FLT:' in data:
                    self.parse_telemetry(vehicle_id, data)
                self.log_message.emit(f"Vehicle {vehicle_id}: {data}")
        except Exception as e:
            self.log_message.emit(f"Çıktı işleme hatası: {str(e)}")

    def handle_error(self, vehicle_id, error):
        """SITL hata mesajlarını işle"""
        try:
            data = error.data().decode().strip()
            if data:
                self.log_message.emit(f"Vehicle {vehicle_id} ERROR: {data}")
        except Exception as e:
            self.log_message.emit(f"Hata işleme hatası: {str(e)}")

    def parse_telemetry(self, vehicle_id, data):
        """Telemetri verilerini parse et"""
        try:
            # FLT: GPS lat, lon, alt, roll, pitch, yaw, velocity
            parts = data.split(':')[1].strip().split(',')
            state = {
                'lat': float(parts[0]),
                'lon': float(parts[1]),
                'alt': float(parts[2]),
                'roll': float(parts[3]),
                'pitch': float(parts[4]),
                'yaw': float(parts[5]),
                'velocity': float(parts[6])
            }
            self.vehicle_states[vehicle_id] = state
            self.state_updated.emit({
                'vehicle_id': vehicle_id,
                'state': state
            })
        except Exception as e:
            self.log_message.emit(f"Telemetri parse hatası: {str(e)}")

    def get_vehicle_state(self, vehicle_id):
        """Araç durumunu döndür"""
        return self.vehicle_states.get(vehicle_id, None)

    def send_command(self, vehicle_id, command, params=None):
        """Araca komut gönder"""
        if vehicle_id not in self.processes:
            return False

        try:
            # MAVLink komutu oluştur ve gönder
            port = self.processes[vehicle_id]['ports']['mavlink']
            # TODO: MAVLink command_long mesajı gönder
            return True
        except Exception as e:
            self.log_message.emit(f"Komut gönderme hatası: {str(e)}")
            return False