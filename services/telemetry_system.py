from services.mavlink_handler import MAVLinkHandler
from datetime import datetime
import json
import os

class TelemetrySystem:
    def __init__(self):
        self.mavlink = MAVLinkHandler()
        self.logging_enabled = False
        self.log_file = None
        
    def start_logging(self):
        if not self.logging_enabled:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            self.log_file = open(f'logs/telemetry_{timestamp}.json', 'w')
            self.logging_enabled = True
            
    def stop_logging(self):
        if self.logging_enabled and self.log_file:
            self.log_file.close()
            self.logging_enabled = False
            
    def log_data(self, data):
        if self.logging_enabled and self.log_file:
            timestamp = datetime.utcnow().isoformat()
            log_entry = {
                'timestamp': timestamp,
                'data': data
            }
            self.log_file.write(json.dumps(log_entry) + '\n')