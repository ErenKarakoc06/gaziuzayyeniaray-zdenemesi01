from PyQt6.QtCore import QThread, pyqtSignal
import serial
import time

class FirmwareUploadThread(QThread):
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    finished = pyqtSignal(bool)

    def __init__(self, port, firmware_path):
        super().__init__()
        self.port = port
        self.firmware_path = firmware_path

    def run(self):
        try:
            # Seri port bağlantısı
            self.status_updated.emit("Port açılıyor...")
            ser = serial.Serial(self.port, 57600, timeout=1)
            
            # Bootloader modu için reset
            self.status_updated.emit("Cihaz reset atılıyor...")
            ser.setDTR(False)
            time.sleep(0.1)
            ser.setDTR(True)
            time.sleep(0.5)

            # Firmware dosyasını oku
            self.status_updated.emit("Firmware okunuyor...")
            with open(self.firmware_path, 'rb') as f:
                firmware_data = f.read()

            # Firmware yükleme
            self.status_updated.emit("Firmware yükleniyor...")
            total_size = len(firmware_data)
            chunk_size = 256
            uploaded = 0

            for i in range(0, total_size, chunk_size):
                chunk = firmware_data[i:i + chunk_size]
                ser.write(chunk)
                uploaded += len(chunk)
                progress = int((uploaded / total_size) * 100)
                self.progress_updated.emit(progress)
                time.sleep(0.01)  # Yükleme hızını kontrol et

            # Tamamlandı
            ser.close()
            self.status_updated.emit("Yükleme tamamlandı!")
            self.finished.emit(True)

        except Exception as e:
            self.status_updated.emit(f"Hata: {str(e)}")
            self.finished.emit(False)