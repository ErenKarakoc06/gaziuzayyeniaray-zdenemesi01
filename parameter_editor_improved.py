from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QPushButton, QLineEdit, QLabel,
                            QComboBox, QMessageBox, QMenu, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal
from datetime import datetime
import json
import csv

class ImprovedParameterEditor(QWidget):
    parameter_changed = pyqtSignal(str, float)  # param_name, new_value
    
    def __init__(self, current_user="ErenKarakoc06", current_time_utc="2025-03-02 18:20:49"):
        super().__init__()
        self.current_user = current_user
        self.current_time_utc = datetime.strptime(current_time_utc, "%Y-%m-%d %H:%M:%S")
        self.parameters = {}
        self.parameter_history = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Üst bilgi paneli
        info_panel = QHBoxLayout()
        info_panel.addWidget(QLabel(f"Kullanıcı: {self.current_user}"))
        info_panel.addWidget(QLabel(f"UTC: {self.current_time_utc.strftime('%Y-%m-%d %H:%M:%S')}"))
        layout.addLayout(info_panel)

        # Arama ve filtreleme
        search_group = QGroupBox("Arama ve Filtreleme")
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Parametre ara...")
        self.search_input.textChanged.connect(self.filter_parameters)
        search_layout.addWidget(self.search_input)
        
        self.category_filter = QComboBox()
        self.category_filter.addItems([
            "Tümü",
            "Temel Ayarlar",
            "Uçuş Kontrolü",
            "Failsafe",
            "Telemetri",
            "EKF",
            "Motor",
            "RC",
            "Sensörler"
        ])
        self.category_filter.currentTextChanged.connect(self.filter_parameters)
        search_layout.addWidget(self.category_filter)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)

        # Parametre tablosu
        self.param_table = QTableWidget()
        self.param_table.setColumnCount(6)
        self.param_table.setHorizontalHeaderLabels([
            'Parametre',
            'Değer',
            'Birim',
            'Açıklama',
            'Min-Max',
            'Varsayılan'
        ])
        self.param_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.param_table.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.param_table)

        # Kontrol butonları
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Yenile")
        refresh_btn.clicked.connect(self.refresh_parameters)
        button_layout.addWidget(refresh_btn)

        save_btn = QPushButton("Değişiklikleri Kaydet")
        save_btn.clicked.connect(self.save_changes)
        button_layout.addWidget(save_btn)

        load_btn = QPushButton("Parametre Dosyası Yükle")
        load_btn.clicked.connect(self.load_parameters)
        button_layout.addWidget(load_btn)

        export_btn = QPushButton("Dışa Aktar")
        export_btn.clicked.connect(self.export_parameters)
        button_layout.addWidget(export_btn)

        layout.addLayout(button_layout)

        # Değişiklik geçmişi
        history_group = QGroupBox("Parametre Değişiklik Geçmişi")
        history_layout = QVBoxLayout()
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels([
            'Tarih',
            'Kullanıcı',
            'Parametre',
            'Eski Değer',
            'Yeni Değer'
        ])
        history_layout.addWidget(self.history_table)
        
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)

        self.setLayout(layout)
        self.load_parameter_history()
        self.refresh_parameters()

    def refresh_parameters(self):
        # Örnek parametre verileri
        self.parameters = {
            'PILOT_THR_FILT': {
                'value': 2.0,
                'unit': 'Hz',
                'description': 'Throttle input filter',
                'min': 0,
                'max': 10,
                'default': 2.0,
                'category': 'RC'
            },
            'ATC_ACCEL_P_MAX': {
                'value': 110000.0,
                'unit': 'cm/s/s',
                'description': 'Pitch acceleration limit',
                'min': 0,
                'max': 180000,
                'default': 110000.0,
                'category': 'Uçuş Kontrolü'
            },
            'BATT_CAPACITY': {
                'value': 3300,
                'unit': 'mAh',
                'description': 'Battery capacity',
                'min': 0,
                'max': 50000,
                'default': 3300,
                'category': 'Temel Ayarlar'
            }
        }
        self.update_parameter_table()

    def update_parameter_table(self):
        self.param_table.setRowCount(0)
        
        for param_name, param_data in self.parameters.items():
            if self.should_show_parameter(param_name, param_data):
                row = self.param_table.rowCount()
                self.param_table.insertRow(row)
                
                # Parametre adı
                self.param_table.setItem(row, 0, QTableWidgetItem(param_name))
                
                # Değer (düzenlenebilir)
                value_item = QTableWidgetItem(str(param_data['value']))
                value_item.setFlags(value_item.flags() | Qt.ItemFlag.ItemIsEditable)
                self.param_table.setItem(row, 1, value_item)
                
                # Birim
                self.param_table.setItem(row, 2, QTableWidgetItem(param_data.get('unit', '')))
                
                # Açıklama
                self.param_table.setItem(row, 3, QTableWidgetItem(param_data.get('description', '')))
                
                # Min-Max
                min_max = f"{param_data.get('min', '-')} - {param_data.get('max', '-')}"
                self.param_table.setItem(row, 4, QTableWidgetItem(min_max))
                
                # Varsayılan değer
                self.param_table.setItem(row, 5, QTableWidgetItem(str(param_data.get('default', ''))))

    def should_show_parameter(self, param_name, param_data):
        # Arama filtresini kontrol et
        search_text = self.search_input.text().lower()
        if search_text and not (search_text in param_name.lower() or 
                              search_text in param_data.get('description', '').lower()):
            return False

        # Kategori filtresini kontrol et
        category = self.category_filter.currentText()
        if category != "Tümü" and param_data.get('category') != category:
            return False

        return True

    def filter_parameters(self):
        self.update_parameter_table()

    def show_context_menu(self, position):
        menu = QMenu()
        
        reset_action = menu.addAction("Varsayılana Sıfırla")
        copy_action = menu.addAction("Değeri Kopyala")
        history_action = menu.addAction("Değişiklik Geçmişi")
        
        action = menu.exec(self.param_table.viewport().mapToGlobal(position))
        
        if action == reset_action:
            self.reset_parameter_to_default()
        elif action == copy_action:
            self.copy_parameter_value()
        elif action == history_action:
            self.show_parameter_history()

    def reset_parameter_to_default(self):
        current_row = self.param_table.currentRow()
        if current_row >= 0:
            param_name = self.param_table.item(current_row, 0).text()
            if param_name in self.parameters:
                old_value = self.parameters[param_name]['value']
                new_value = self.parameters[param_name]['default']
                
                self.parameters[param_name]['value'] = new_value
                self.param_table.item(current_row, 1).setText(str(new_value))
                
                self.add_to_history(param_name, old_value, new_value)
                self.parameter_changed.emit(param_name, new_value)

    def copy_parameter_value(self):
        current_row = self.param_table.currentRow()
        if current_row >= 0:
            value = self.param_table.item(current_row, 1).text()
            QApplication.clipboard().setText(value)

    def show_parameter_history(self):
        current_row = self.param_table.currentRow()
        if current_row >= 0:
            param_name = self.param_table.item(current_row, 0).text()
            
            # Parametre geçmişini filtrele
            param_history = [
                entry for entry in self.parameter_history 
                if entry['parameter'] == param_name
            ]
            
            if param_history:
                history_text = "\n".join([
                    f"{entry['date']} - {entry['old_value']} -> {entry['new_value']}"
                    for entry in param_history
                ])
                QMessageBox.information(self, f"{param_name} Geçmişi", history_text)
            else:
                QMessageBox.information(
                    self, 
                    "Geçmiş", 
                    "Bu parametre için değişiklik geçmişi bulunamadı."
                )

    def save_changes(self):
        try:
            # TODO: Parametreleri MAVLink üzerinden gönder
            QMessageBox.information(self, "Başarılı", "Değişiklikler kaydedildi!")
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Değişiklikler kaydedilemedi: {str(e)}")

    def load_parameters(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Parametre Dosyası Seç",
            "",
            "Parametre Dosyaları (*.param);;Tüm Dosyalar (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    new_params = json.load(f)
                
                # Parametreleri güncelle
                for param_name, param_data in new_params.items():
                    if param_name in self.parameters:
                        old_value = self.parameters[param_name]['value']
                        new_value = param_data['value']
                        
                        self.parameters[param_name]['value'] = new_value
                        self.add_to_history(param_name, old_value, new_value)
                
                self.update_parameter_table()
                QMessageBox.information(self, "Başarılı", "Parametreler yüklendi!")
                
            except Exception as e:
                QMessageBox.warning(self, "Hata", f"Dosya yüklenemedi: {str(e)}")

    def export_parameters(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Parametreleri Kaydet",
            f"parameters_{self.current_time_utc.strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Dosyası (*.csv);;Parametre Dosyası (*.param)"
        )
        
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.export_to_csv(file_path)
                else:
                    self.export_to_param(file_path)
                    
                QMessageBox.information(self, "Başarılı", "Parametreler dışa aktarıldı!")
                
            except Exception as e:
                QMessageBox.warning(self, "Hata", f"Dışa aktarma başarısız: {str(e)}")

    def export_to_csv(self, file_path):
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Parametre', 'Değer', 'Birim', 'Açıklama', 'Min', 'Max', 'Varsayılan'])
            
            for param_name, param_data in self.parameters.items():
                writer.writerow([
                    param_name,
                    param_data['value'],
                    param_data.get('unit', ''),
                    param_data.get('description', ''),
                    param_data.get('min', ''),
                    param_data.get('max', ''),
                    param_data.get('default', '')
                ])

    def export_to_param(self, file_path):
        with open(file_path, 'w') as f:
            json.dump(self.parameters, f, indent=4)

    def add_to_history(self, param_name, old_value, new_value):
        entry = {
            'date': self.current_time_utc.strftime("%Y-%m-%d %H:%M:%S"),
            'user': self.current_user,
            'parameter': param_name,
            'old_value': old_value,
            'new_value': new_value
        }
        self.parameter_history.append(entry)
        
        # Geçmiş tablosunu güncelle
        row = self.history_table.rowCount()
        self.history_table.insertRow(row)
        
        self.history_table.setItem(row, 0, QTableWidgetItem(entry['date']))
        self.history_table.setItem(row, 1, QTableWidgetItem(entry['user']))
        self.history_table.setItem(row, 2, QTableWidgetItem(entry['parameter']))
        self.history_table.setItem(row, 3, QTableWidgetItem(str(entry['old_value'])))
        self.history_table.setItem(row, 4, QTableWidgetItem(str(entry['new_value'])))
        
        self.save_parameter_history()

    def load_parameter_history(self):
        try:
            with open('config/parameter_history.json', 'r') as f:
                self.parameter_history = json.load(