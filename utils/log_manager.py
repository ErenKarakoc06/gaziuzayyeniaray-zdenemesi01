import os
from datetime import datetime
import json
import csv

class LogManager:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        self.current_log_file = None
        self.current_csv_file = None
        self.csv_writer = None
        self.ensure_log_directory()

    def ensure_log_directory(self):
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def start_logging(self):
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        
        # JSON log dosyası
        json_filename = os.path.join(self.log_dir, f'telemetry_{timestamp}.json')
        self.current_log_file = open(json_filename, 'w')

        # CSV log dosyası
        csv_filename = os.path.join(self.log_dir, f'telemetry_{timestamp}.csv')
        self.current_csv_file = open(csv_filename, 'w', newline='')
        self.csv_writer = None  # İlk veri geldiğinde başlıklar oluşturulacak

    def log_data(self, data: dict):
        # JSON formatında kaydet
        timestamp = datetime.utcnow().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'data': data
        }
        self.current_log_file.write(json.dumps(log_entry) + '\n')

        # CSV formatında kaydet
        if self.csv_writer is None:
            # CSV başlıklarını oluştur
            headers = ['timestamp'] + list(data.keys())
            self.csv_writer = csv.DictWriter(self.current_csv_file, fieldnames=headers)
            self.csv_writer.writeheader()

        # CSV satırını yaz
        row_data = {'timestamp': timestamp}
        row_data.update(data)
        self.csv_writer.writerow(row_data)

    def stop_logging(self):
        if self.current_log_file:
            self.current_log_file.close()
            self.current_log_file = None

        if self.current_csv_file:
            self.current_csv_file.close()
            self.current_csv_file = None
            self.csv_writer = None