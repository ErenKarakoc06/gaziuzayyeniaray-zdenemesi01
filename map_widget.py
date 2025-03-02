from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
import folium

class MapWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Web view oluştur
        self.web_view = QWebEngineView()
        
        # Folium haritası oluştur
        self.map = folium.Map(
            location=[39.925533, 32.866287],  # Ankara merkezi
            zoom_start=10
        )
        
        # Haritayı HTML olarak kaydet ve web view'da göster
        self.map.save('temp_map.html')
        self.web_view.setUrl(QUrl.fromLocalFile(os.path.abspath('temp_map.html')))
        
        layout.addWidget(self.web_view)
        self.setLayout(layout)