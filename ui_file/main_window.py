from PyQt6.QtWidgets import QMainWindow, QTabWidget
from ui.hud_customization import HUDCustomization
from ui.hardware_test import HardwareTestModule
from ui.script_engine import ScriptingEngine
from ui.log_analyzer import LogAnalyzer
from ui.rtk_gps_manager import RTKGPSManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Gazi Uzay Arayüz")
        self.setGeometry(100, 100, 1280, 720)
        
        # Ana tab widget
        tabs = QTabWidget()
        tabs.addTab(HUDCustomization(), "HUD")
        tabs.addTab(HardwareTestModule(), "Donanım Testi")
        tabs.addTab(ScriptingEngine(), "Script")
        tabs.addTab(LogAnalyzer(), "Log Analiz")
        tabs.addTab(RTKGPSManager(), "RTK GPS")
        
        self.setCentralWidget(tabs)