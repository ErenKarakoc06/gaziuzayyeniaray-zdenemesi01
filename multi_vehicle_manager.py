from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QPushButton, QLabel, QMenu)
from PyQt6.QtCore import Qt, pyqtSignal

class MultiVehicleManager(QWidget):
    vehicle_selected = pyqtSignal(int)  # Vehicle ID

    def __init__(self):
        super().__init__()
        self.vehicles = {}  # vehicle_id: vehicle_data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Araç listesi
        self.vehicle_table = QTableWidget()
        self.vehicle_table.setColumnCount(6)
        self.vehicle_table.setHorizontalHeaderLabels([
            'ID', 'Tip', 'Mod', 'Batarya', 'GPS', 'Durum'
        ])
        self.vehicle_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.vehicle_table.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.vehicle_table)

        # Özet bilgiler
        info_layout = QHBoxLayout()
        self.total_vehicles = QLabel("Toplam Araç: 0")
        self.armed_vehicles = QLabel("Aktif Araç: 0")
        self.critical_vehicles = QLabel("Kritik Durum: 0")
        info_layout.addWidget(self.total_vehicles)
        info_layout.addWidget(self.armed_vehicles)
        info_layout.addWidget(self.critical_vehicles)
        layout.addLayout(info_layout)

        # Toplu işlem butonları
        button_layout = QHBoxLayout()
        self.arm_all = QPushButton("Tümünü Arm Et")
        self.disarm_all = QPushButton("Tümünü Disarm Et")
        self.rtl_all = QPushButton("Tümünü RTL'e Al")
        button_layout.addWidget(self.arm_all)
        button_layout.addWidget(self.disarm_all)
        button_layout.addWidget(self.rtl_all)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def update_vehicle(self, vehicle_id, data):
        if vehicle_id not in self.vehicles:
            # Yeni araç ekle
            self.vehicles[vehicle_id] = data
            row = self.vehicle_table.rowCount()
            self.vehicle_table.insertRow(row)
        else:
            # Mevcut aracı güncelle
            row = self.find_vehicle_row(vehicle_id)
            self.vehicles[vehicle_id].update(data)

        # Tablo satırını güncelle
        self.update_table_row(row, vehicle_id, self.vehicles[vehicle_id])
        self.update_summary()

    def update_table_row(self, row, vehicle_id, data):
        self.vehicle_table.setItem(row, 0, QTableWidgetItem(str(vehicle_id)))
        self.vehicle_table.setItem(row, 1, QTableWidgetItem(data.get('type', 'Unknown')))
        self.vehicle_table.setItem(row, 2, QTableWidgetItem(data.get('mode', 'Unknown')))
        self.vehicle_table.setItem(row, 3, QTableWidgetItem(f"{data.get('battery', 0)}%"))
        self.vehicle_table.setItem(row, 4, QTableWidgetItem(f"{data.get('gps_fix', 0)}"))
        
        # Durum hücresini renklendir
        status_item = QTableWidgetItem(data.get('status', 'Unknown'))
        if data.get('status') == 'Critical':
            status_item.setBackground(Qt.GlobalColor.red)
        elif data.get('status') == 'Warning':
            status_item.setBackground(Qt.GlobalColor.yellow)
        else:
            status_item.setBackground(Qt.GlobalColor.green)
        self.vehicle_table.setItem(row, 5, status_item)

    def find_vehicle_row(self, vehicle_id):
        for row in range(self.vehicle_table.rowCount()):
            if self.vehicle_table.item(row, 0).text() == str(vehicle_id):
                return row
        return -1

    def update_summary(self):
        total = len(self.vehicles)
        armed = sum(1 for v in self.vehicles.values() if v.get('armed', False))
        critical = sum(1 for v in self.vehicles.values() if v.get('status') == 'Critical')

        self.total_vehicles.setText(f"Toplam Araç: {total}")
        self.armed_vehicles.setText(f"Aktif Araç: {armed}")
        self.critical_vehicles.setText(f"Kritik Durum: {critical}")

    def show_context_menu(self, position):
        menu = QMenu()
        selected_row = self.vehicle_table.currentRow()
        if selected_row >= 0:
            vehicle_id = int(self.vehicle_table.item(selected_row, 0).text())
            
            arm_action = menu.addAction("Arm Et")
            disarm_action = menu.addAction("Disarm Et")
            rtl_action = menu.addAction("RTL'e Al")
            menu.addSeparator()
            remove_action = menu.addAction("Listeden Kaldır")

            action = menu.exec(self.vehicle_table.mapToGlobal(position))
            if action == arm_action:
                self.arm_vehicle(vehicle_id)
            elif action == disarm_action:
                self.disarm_vehicle(vehicle_id)
            elif action == rtl_action:
                self.rtl_vehicle(vehicle_id)
            elif action == remove_action:
                self.remove_vehicle(vehicle_id)

    def arm_vehicle(self, vehicle_id):
        # TODO: MAVLink arm komutu gönder
        pass

    def disarm_vehicle(self, vehicle_id):
        # TODO: MAVLink disarm komutu gönder
        pass

    def rtl_vehicle(self, vehicle_id):
        # TODO: MAVLink RTL komutu gönder
        pass

    def remove_vehicle(self, vehicle_id):
        row = self.find_vehicle_row(vehicle_id)
        if row >= 0:
            self.vehicle_table.removeRow(row)
            del self.vehicles[vehicle_id]
            self.update_summary()