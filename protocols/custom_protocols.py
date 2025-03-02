from PyQt6.QtCore import QObject, pyqtSignal
import serial
import struct
import time
import threading

class ProtocolManager(QObject):
    data_received = pyqtSignal(str, dict)  # protocol_type, data
    error_occurred = pyqtSignal(str)  # error_message
    
    def __init__(self):
        super().__init__()
        self.protocols = {
            'LTM': LTMProtocol(),
            'FrSky': FrSkyProtocol(),
            'CustomSensor': CustomSensorProtocol()
        }
        self.active_protocols = []
        self.running = False
        self.thread = None

    def start_protocol(self, protocol_type, port, baudrate=115200):
        if protocol_type not in self.protocols:
            self.error_occurred.emit(f"Desteklenmeyen protokol: {protocol_type}")
            return False
            
        try:
            protocol = self.protocols[protocol_type]
            protocol.connect(port, baudrate)
            self.active_protocols.append(protocol_type)
            
            if not self.running:
                self.running = True
                self.thread = threading.Thread(target=self._read_loop)
                self.thread.daemon = True
                self.thread.start()
            
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"Protokol başlatılamadı: {str(e)}")
            return False

    def stop_protocol(self, protocol_type):
        if protocol_type in self.active_protocols:
            self.protocols[protocol_type].disconnect()
            self.active_protocols.remove(protocol_type)
            
        if not self.active_protocols:
            self.running = False
            if self.thread:
                self.thread.join()
                self.thread = None

    def _read_loop(self):
        while self.running:
            for protocol_type in self.active_protocols:
                try:
                    data = self.protocols[protocol_type].read_data()
                    if data:
                        self.data_received.emit(protocol_type, data)
                except Exception as e:
                    self.error_occurred.emit(f"Veri okuma hatası ({protocol_type}): {str(e)}")
            time.sleep(0.01)

class LTMProtocol:
    def __init__(self):
        self.serial = None
        self.frame_types = {
            'G': self._parse_gps_frame,
            'A': self._parse_attitude_frame,
            'S': self._parse_status_frame
        }

    def connect(self, port, baudrate):
        self.serial = serial.Serial(port, baudrate, timeout=1)

    def disconnect(self):
        if self.serial:
            self.serial.close()
            self.serial = None

    def read_data(self):
        if not self.serial:
            return None
            
        # LTM frame başlangıcını ara
        if self.serial.read() != b'$' or self.serial.read() != b'T':
            return None
            
        frame_type = self.serial.read().decode()
        if frame_type not in self.frame_types:
            return None
            
        return self.frame_types[frame_type]()

    def _parse_gps_frame(self):
        data = self.serial.read(14)
        lat, lon, speed, alt, sats = struct.unpack('<iiHHB', data)
        return {
            'latitude': lat / 10000000,
            'longitude': lon / 10000000,
            'speed': speed,
            'altitude': alt,
            'satellites': sats
        }

    def _parse_attitude_frame(self):
        data = self.serial.read(6)
        pitch, roll, heading = struct.unpack('<hhH', data)
        return {
            'pitch': pitch / 10,
            'roll': roll / 10,
            'heading': heading
        }

    def _parse_status_frame(self):
        data = self.serial.read(7)
        voltage, current, rssi, airspeed, flags = struct.unpack('<HHBBB', data)
        return {
            'voltage': voltage / 100,
            'current': current / 100,
            'rssi': rssi,
            'airspeed': airspeed,
            'armed': bool(flags & 1),
            'failsafe': bool(flags & 2)
        }

class FrSkyProtocol:
    def __init__(self):
        self.serial = None
        self.buffer = bytearray()

    def connect(self, port, baudrate):
        self.serial = serial.Serial(port, baudrate, timeout=1)

    def disconnect(self):
        if self.serial:
            self.serial.close()
            self.serial = None

    def read_data(self):
        if not self.serial:
            return None
            
        # FrSky frame başlangıcını ara
        while True:
            if len(self.buffer) < 3:
                self.buffer.extend(self.serial.read(1))
                continue
                
            if self.buffer[0] == 0x7E and self.buffer[1] == 0x7E:
                frame_type = self.buffer[2]
                frame_length = self._get_frame_length(frame_type)
                
                if len(self.buffer) >= frame_length:
                    frame = self.buffer[:frame_length]
                    self.buffer = self.buffer[frame_length:]
                    return self._parse_frame(frame_type, frame[3:-1])
                    
            self.buffer.pop(0)

    def _get_frame_length(self, frame_type):
        # Frame tiplerine göre uzunlukları belirle
        lengths = {
            0x10: 8,   # GPS Data
            0x11: 6,   # Attitude
            0x12: 7    # Status
        }
        return lengths.get(frame_type, 0)

    def _parse_frame(self, frame_type, data):
        if frame_type == 0x10:  # GPS
            lat, lon = struct.unpack('<ii', data[:8])
            return {
                'type': 'gps',
                'latitude': lat / 10000000,
                'longitude': lon / 10000000
            }
        elif frame_type == 0x11:  # Attitude
            pitch, roll = struct.unpack('<hh', data[:4])
            return {
                'type': 'attitude',
                'pitch': pitch / 10,
                'roll': roll / 10
            }
        elif frame_type == 0x12:  # Status
            voltage, current = struct.unpack('<HH', data[:4])
            return {
                'type': 'status',
                'voltage': voltage / 100,
                'current': current / 100
            }
        return None

class CustomSensorProtocol:
    def __init__(self):
        self.serial = None
        self.sensors = {}

    def connect(self, port, baudrate):
        self.serial = serial.Serial(port, baudrate, timeout=1)

    def disconnect(self):
        if self.serial:
            self.serial.close()
            self.serial = None

    def add_sensor(self, sensor_id, name, data_format):
        self.sensors[sensor_id] = {
            'name': name,
            'format': data_format
        }

    def read_data(self):
        if not self.serial:
            return None
            
        # Özel sensör protokolü başlangıcını ara
        if self.serial.read() != b'#':
            return None
            
        sensor_id = ord(self.serial.read())
        if sensor_id not in self.sensors:
            return None
            
        sensor = self.sensors[sensor_id]
        data_length = struct.calcsize(sensor['format'])
        data = self.serial.read(data_length)
        
        if len(data) != data_length:
            return None
            
        values = struct.unpack(sensor['format'], data)
        return {
            'sensor': sensor['name'],
            'values': values
        }