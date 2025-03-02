from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QSplitter
from PyQt6.QtCore import Qt
from .widgets.earth_view import GoogleEarthView
from .widgets.dashboard import Dashboard
from .widgets.three_d_view import ThreeDView

class FlightDataTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Yatay splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Sol panel
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        
        # Dashboard
        self.dashboard = Dashboard()
        dashboard_group = QGroupBox("System Status")
        dashboard_layout = QVBoxLayout()
        dashboard_layout.addWidget(self.dashboard)
        dashboard_group.setLayout(dashboard_layout)
        left_layout.addWidget(dashboard_group)
        
        # 3D görünüm
        self.three_d_view = ThreeDView()
        model_group = QGroupBox("3D Vehicle View")
        model_layout = QVBoxLayout()
        model_layout.addWidget(self.three_d_view)
        model_group.setLayout(model_layout)
        left_layout.addWidget(model_group)
        
        left_widget.setLayout(left_layout)
        splitter.addWidget(left_widget)
        
        # Sağ panel - Google Earth
        self.earth_view = GoogleEarthView()
        earth_group = QGroupBox("Mission Map")
        earth_layout = QVBoxLayout()
        earth_layout.addWidget(self.earth_view)
        earth_group.setLayout(earth_layout)
        splitter.addWidget(earth_group)
        
        # Splitter'ı ana layout'a ekle
        layout.addWidget(splitter)
        
        self.setLayout(layout)

    def update_vehicle_data(self, data):
        # Dashboard güncellemesi
        if 'battery' in data:
            self.dashboard.update_battery(data['battery'])
        if 'signal' in data:
            self.dashboard.update_signal(data['signal'])
        if 'gps_hdop' in data:
            self.dashboard.update_gps(data['gps_hdop'])
        if 'motor' in data:
            self.dashboard.update_motor(data['motor'])
            
        # 3D görünüm güncellemesi
        if all(k in data for k in ['roll', 'pitch', 'yaw']):
            self.three_d_view.update_attitude(
                data['roll'],
                data['pitch'],
                data['yaw']
            )
            
        # Harita güncellemesi
        if all(k in data for k in ['lat', 'lon', 'alt']):
            self.earth_view.update_vehicle_position(
                data['lat'],
                data['lon'],
                data['alt']
            )