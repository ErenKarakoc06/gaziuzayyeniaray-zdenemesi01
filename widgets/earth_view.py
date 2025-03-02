from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
import json
import os

class GoogleEarthView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.flight_path = []

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Web view widget'ı
        self.web_view = QWebEngineView()
        self.web_view.setMinimumHeight(400)
        
        # HTML template'ini yükle
        html_content = self.get_earth_html()
        self.web_view.setHtml(html_content)
        
        layout.addWidget(self.web_view)
        self.setLayout(layout)

    def get_earth_html(self):
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://www.google.com/jsapi"></script>
            <script>
                google.load("earth", "1");
                
                var ge;
                var placemark;
                var flightPath;
                
                function init() {
                    google.earth.createInstance('map3d', initCallback, failureCallback);
                }
                
                function initCallback(instance) {
                    ge = instance;
                    ge.getWindow().setVisibility(true);
                    
                    // Varsayılan görünüm ayarları
                    var lookAt = ge.createLookAt('');
                    lookAt.setLatitude(0);
                    lookAt.setLongitude(0);
                    lookAt.setRange(1000000);
                    ge.getView().setAbstractView(lookAt);
                    
                    // Katmanları ayarla
                    ge.getLayerRoot().enableLayerById(ge.LAYER_BORDERS, true);
                    ge.getLayerRoot().enableLayerById(ge.LAYER_ROADS, true);
                    
                    // Araç konumu için placemark oluştur
                    placemark = ge.createPlacemark('');
                    var point = ge.createPoint('');
                    placemark.setGeometry(point);
                    ge.getFeatures().appendChild(placemark);
                    
                    // Uçuş yolu için
                    flightPath = ge.createPlacemark('');
                    var lineString = ge.createLineString('');
                    lineString.setExtrude(true);
                    lineString.setAltitudeMode(ge.ALTITUDE_RELATIVE_TO_GROUND);
                    flightPath.setGeometry(lineString);
                    ge.getFeatures().appendChild(flightPath);
                }
                
                function failureCallback(errorCode) {
                    console.error("Google Earth yüklenemedi: " + errorCode);
                }
                
                function updateVehiclePosition(lat, lon, alt) {
                    if (ge && placemark) {
                        var point = placemark.getGeometry();
                        point.setLatitude(lat);
                        point.setLongitude(lon);
                        point.setAltitude(alt);
                        
                        // Kamerayı aracı takip edecek şekilde ayarla
                        var lookAt = ge.getView().copyAsLookAt(ge.ALTITUDE_RELATIVE_TO_GROUND);
                        lookAt.setLatitude(lat);
                        lookAt.setLongitude(lon);
                        lookAt.setRange(1000);  // Kamera mesafesi
                        lookAt.setTilt(45);     // Kamera açısı
                        ge.getView().setAbstractView(lookAt);
                    }
                }
                
                function updateFlightPath(pathData) {
                    if (ge && flightPath) {
                        var lineString = flightPath.getGeometry();
                        lineString.getCoordinates().clear();
                        
                        for (var i = 0; i < pathData.length; i++) {
                            var point = pathData[i];
                            lineString.getCoordinates().pushLatLngAlt(
                                point.lat, point.lon, point.alt
                            );
                        }
                    }
                }
            </script>
        </head>
        <body onload="init()" style="margin:0;padding:0;">
            <div id="map3d" style="height:100%;width:100%;"></div>
        </body>
        </html>
        """

    def update_vehicle_position(self, lat, lon, alt):
        js_code = f"updateVehiclePosition({lat}, {lon}, {alt});"
        self.web_view.page().runJavaScript(js_code)
        
        # Uçuş yolunu güncelle
        self.flight_path.append({'lat': lat, 'lon': lon, 'alt': alt})
        self.update_flight_path()

    def update_flight_path(self):
        js_code = f"updateFlightPath({json.dumps(self.flight_path)});"
        self.web_view.page().runJavaScript(js_code)

    def clear_flight_path(self):
        self.flight_path = []
        self.update_flight_path()