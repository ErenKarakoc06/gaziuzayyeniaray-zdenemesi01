from pymavlink import mavutil
import threading
import time

class MAVLinkHandler:
    def __init__(self):
        self.connection = None
        self.is_connected = False
        self.vehicle_data = {
            'altitude': 0,
            'groundspeed': 0,
            'mode': 'UNKNOWN',
            'gps_fix': 0,
            'pitch': 0,
            'roll': 0,
            'heading': 0
        }
        self.listeners = []

    def connect(self, connection_string):
        try:
            self.connection = mavutil.mavlink_connection(connection_string)
            self.is_connected = True
            # Mesaj dinleme thread'ini başlat
            self.read_thread = threading.Thread(target=self._read_messages)
            self.read_thread.daemon = True
            self.read_thread.start()
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def disconnect(self):
        if self.connection:
            self.is_connected = False
            self.connection.close()

    def _read_messages(self):
        while self.is_connected:
            try:
                msg = self.connection.recv_match(blocking=True, timeout=1.0)
                if msg:
                    self._handle_message(msg)
            except Exception as e:
                print(f"Error reading message: {e}")
                time.sleep(0.1)

    def _handle_message(self, msg):
        msg_type = msg.get_type()
        
        if msg_type == "GLOBAL_POSITION_INT":
            self.vehicle_data['altitude'] = msg.relative_alt / 1000.0
        elif msg_type == "VFR_HUD":
            self.vehicle_data['groundspeed'] = msg.groundspeed
            self.vehicle_data['heading'] = msg.heading
        elif msg_type == "ATTITUDE":
            self.vehicle_data['pitch'] = msg.pitch
            self.vehicle_data['roll'] = msg.roll
        elif msg_type == "HEARTBEAT":
            self.vehicle_data['mode'] = mavutil.mode_string_v10(msg)
        elif msg_type == "GPS_RAW_INT":
            self.vehicle_data['gps_fix'] = msg.fix_type

        # Dinleyicileri bilgilendir
        for listener in self.listeners:
            listener(self.vehicle_data)

    def add_listener(self, listener):
        self.listeners.append(listener)

    def remove_listener(self, listener):
        if listener in self.listeners:
            self.listeners.remove(listener)