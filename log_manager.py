from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QProgressBar, QTableWidget, QTableWidgetItem,
                            QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
import os
import datetime
import json

class LogManager(QWidget):
    log_downloaded = pyqtSignal(str)  # log dosya yolu
    log_uploaded = pyqtSignal(str)    # log dosya yolu
    
    def __init__(self):
        super().__init__()
        self.log_directory = os.path.expanduser("~/drone_logs")
        self.ensure_log_directory()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Log listesi
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(5)
        self.log_table.setHorizontalHeaderLabels([
            'Tarih',
            'Boyut',
            'Süre',
            'Durum',
            'İşlemler'
        ])
        layout.addWidget(self.log_table)

        # Kontroller
        controls_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Yenile")
        refresh_btn.clicked.connect(self.refresh_logs)
        controls_layout.addWidget(refresh_btn)

        download_btn = QPushButton("Seçili Logları İndir")
        download_btn.clicked.connect(self.download_selected_logs)
        controls_layout.addWidget(download_btn)

        upload_btn = QPushButton("Log Yükle")
        upload_btn.clicked.connect(self.upload_log)
        controls_layout.addWidget(upload_btn)

        delete_btn = QPushButton("Seçili Logları Sil")
        delete_btn.clicked.connect(self.delete_selected_logs)
        controls_layout.addWidget(delete_btn)

        layout.addLayout(controls_layout)

        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)
        self.refresh_logs()

    def ensure_log_directory(self):
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)

    def refresh_logs(self):
        try:
            # MAVLink üzerinden log listesini al
            self.request_log_list()
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Log listesi alınamadı: {str(e)}")

    def request_log_list(self):
        # TODO: MAVLink log_request_list mesajı gönder
        # Şimdilik örnek veriler
        logs = [
            {
                'id': 1,
                'date': datetime.datetime.now() - datetime.timedelta(days=1),
                'size': 1024 * 1024,
                'duration': 3600,
                'status': 'Completed'
            },
            {
                'id': 2,
                'date': datetime.datetime.now(),
                'size': 512 * 1024,
                'duration': 1800,
                'status': 'In Progress'
            }
        ]
        self.update_log_table(logs)

    def update_log_table(self, logs):
        self.log_table.setRowCount(0)
        
        for log in logs:
            row = self.log_table.rowCount()
            self.log_table.insertRow(row)
            
            # Tarih
            date_item = QTableWidgetItem(
                log['date'].strftime('%Y-%m-%d %H:%M:%S')
            )
            self.log_table.setItem(row, 0, date_item)
            
            # Boyut
            size_item = QTableWidgetItem(
                self.format_size(log['size'])
            )
            self.log_table.setItem(row, 1, size_item)
            
            # Süre
            duration_item = QTableWidgetItem(
                self.format_duration(log['duration'])
            )
            self.log_table.setItem(row, 2, duration_item)
            
            # Durum
            status_item = QTableWidgetItem(log['status'])
            self.log_table.setItem(row, 3, status_item)
            
            # İşlem butonları
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            download_btn = QPushButton("İndir")
            download_btn.clicked.connect(
                lambda checked, log_id=log['id']: self.download_log(log_id)
            )
            actions_layout.addWidget(download_btn)
            
            delete_btn = QPushButton("Sil")
            delete_btn.clicked.connect(
                lambda checked, log_id=log['id']: self.delete_log(log_id)
            )
            actions_layout.addWidget(delete_btn)
            
            actions_widget.setLayout(actions_layout)
            self.log_table.setCellWidget(row, 4, actions_widget)

    def format_size(self, size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    def format_duration(self, seconds):
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def download_selected_logs(self):
        selected_rows = self.log_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Uyarı", "Lütfen indirilecek logları seçin")
            return
        
        # İndirme klasörünü seç
        download_dir = QFileDialog.getExistingDirectory(
            self,
            "İndirme Klasörü Seç",
            self.log_directory
        )
        
        if download_dir:
            self.progress_bar.setRange(0, len(selected_rows))
            self.progress_bar.setValue(0)
            self.progress_bar.show()
            
            for row in range(self.log_table.rowCount()):
                if self.log_table.item(row, 0).isSelected():
                    log_id = row + 1  # Örnek log ID
                    self.download_log(log_id, download_dir)
                    self.progress_bar.setValue(self.progress_bar.value() + 1)
            
            self.progress_bar.hide()
            QMessageBox.information(self, "Başarılı", "Seçili loglar indirildi")

    def download_log(self, log_id, download_dir=None):
        if not download_dir:
            download_dir = self.log_directory
        
        try:
            # TODO: MAVLink log_request_data mesajı gönder
            # Şimdilik örnek