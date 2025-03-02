from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QTreeWidget, QTreeWidgetItem, QPushButton)
from PyQt6.QtCore import Qt

class FlightPlanTab(QWidget):
    def __init__(self, vehicle_connection):
        super().__init__()
        self.vehicle_connection = vehicle_connection
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()

        # Sol panel - Görev ağacı
        mission_layout = QVBoxLayout()
        
        # Görev listesi
        self.mission_tree = QTreeWidget()
        self.mission_tree.setHeaderLabels(['#', 'Command', 'P1', 'P2', 'P3', 'P4', 'Lat', 'Lon', 'Alt'])
        mission_layout.addWidget(self.mission_tree)
        
        # Görev düzenleme butonları
        button_layout = QHBoxLayout()
        self.add_wp_button = QPushButton("Add WP")
        self.del_wp_button = QPushButton("Delete WP")
        self.up_button = QPushButton("Up")
        self.down_button = QPushButton("Down")
        
        button_layout.addWidget(self.add_wp_button)
        button_layout.addWidget(self.del_wp_button)
        button_layout.addWidget(self.up_button)
        button_layout.addWidget(self.down_button)
        
        mission_layout.addLayout(button_layout)
        
        mission_widget = QWidget()
        mission_widget.setLayout(mission_layout)
        layout.addWidget(mission_widget)

        # Sağ panel - Harita
        map_widget = QWidget()
        # Harita implementasyonu eklenecek
        layout.addWidget(map_widget)
        
        self.setLayout(layout)