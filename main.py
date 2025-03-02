import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from datetime import datetime

def main():
    app = QApplication(sys.argv)
    
    # Uygulama meta verileri
    app.setApplicationName("Gazi Uzay Arayüz")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Gazi Üniversitesi")
    app.setOrganizationDomain("gazi.edu.tr")
    
    # Ana pencereyi oluştur
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()