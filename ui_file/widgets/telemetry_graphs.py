from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox, 
                            QPushButton, QCheckBox, QGroupBox)
from PyQt6.QtCore import QTimer
import pyqtgraph as pg
import numpy as np
from collections import deque

class TelemetryGraphs(QWidget):
    def __init__(self):
        super().__init__()
        self.data_buffers = {}
        self.plots = {}
        self.init_ui()
        
        # Veri güncelleme zamanlayıcısı
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_plots)
        self.update_timer.start(100)  # 10Hz güncelleme

    def init_ui(self):
        layout = QVBoxLayout()

        # Grafik kontrolleri
        controls_layout = QHBoxLayout()
        
        # Veri seçimi
        self.data_selector = QComboBox()
        self.data_selector.addItems([
            "Yükseklik",
            "Hız",
            "Batarya Voltajı",
            "Akım",
            "GPS HDOP",
            "İvme",
            "Açısal Hız"
        ])
        controls_layout.addWidget(self.data_selector)
        
        # Zaman aralığı seçimi
        self.time_range = QComboBox()
        self.time_range.addItems(["30 sn", "1 dk", "5 dk", "10 dk", "30 dk"])
        controls_layout.addWidget(self.time_range)
        
        # Grafik ekleme butonu
        add_plot_btn = QPushButton("Grafik Ekle")
        add_plot_btn.clicked.connect(self.add_plot)
        controls_layout.addWidget(add_plot_btn)
        
        # Kayıt kontrolü
        self.record_cb = QCheckBox("Kaydet")
        self.record_cb.toggled.connect(self.toggle_recording)
        controls_layout.addWidget(self.record_cb)
        
        layout.addLayout(controls_layout)

        # Grafik alanı
        self.plot_area = QVBoxLayout()
        layout.addLayout(self.plot_area)

        self.setLayout(layout)

    def add_plot(self):
        data_type = self.data_selector.currentText()
        if data_type not in self.plots:
            # Yeni grafik widget'ı oluştur
            plot_widget = pg.PlotWidget(title=data_type)
            plot_widget.showGrid(x=True, y=True)
            plot_widget.setLabel('bottom', 'Zaman', 's')
            plot_widget.setLabel('left', data_type)
            
            # Veri tamponu oluştur
            buffer_size = self.get_buffer_size()
            self.data_buffers[data_type] = {
                'time': deque(maxlen=buffer_size),
                'values': deque(maxlen=buffer_size)
            }
            
            # Çizgi grafiği oluştur
            plot_item = plot_widget.plot(pen='y')
            
            # Grafiği kaydet
            self.plots[data_type] = {
                'widget': plot_widget,
                'plot': plot_item
            }
            
            # Grafik grubunu oluştur
            group = QGroupBox(data_type)
            group_layout = QVBoxLayout()
            group_layout.addWidget(plot_widget)
            
            # Kaldır butonu
            remove_btn = QPushButton("Kaldır")
            remove_btn.clicked.connect(lambda: self.remove_plot(data_type))
            group_layout.addWidget(remove_btn)
            
            group.setLayout(group_layout)
            self.plot_area.addWidget(group)

    def remove_plot(self, data_type):
        if data_type in self.plots:
            # Widget'ı kaldır
            self.plots[data_type]['widget'].parent().deleteLater()
            # Veri tamponunu ve plot referansını temizle
            del self.data_buffers[data_type]
            del self.plots[data_type]

    def update_plots(self):
        current_time = len(next(iter(self.data_buffers.values()))['time']) if self.data_buffers else 0
        
        # Her grafik için yeni veri ekle
        for data_type, plot_data in self.plots.items():
            # Simüle edilmiş veri (gerçek uygulamada telemetri verisi kullanılacak)
            new_value = self.get_simulated_data(data_type, current_time)
            
            # Veri tamponlarını güncelle
            self.data_buffers[data_type]['time'].append(current_time / 10.0)  # saniye cinsinden
            self.data_buffers[data_type]['values'].append(new_value)
            
            # Grafiği güncelle
            plot_data['plot'].setData(
                x=list(self.data_buffers[data_type]['time']),
                y=list(self.data_buffers[data_type]['values'])
            )

    def get_buffer_size(self):
        time_range = self.time_range.currentText()
        if time_range == "30 sn":
            return 300  # 10Hz * 30s
        elif time_range == "1 dk":
            return 600  # 10Hz * 60s
        elif time_range == "5 dk":
            return 3000  # 10Hz * 300s
        elif time_range == "10 dk":
            return 6000  # 10Hz * 600s
        else:  # 30 dk
            return 18000  # 10Hz * 1800s

    def get_simulated_data(self, data_type, t):
        # Test için simüle edilmiş veri
        if data_type == "Yükseklik":
            return 100 + 10 * np.sin(t / 50.0)
        elif data_type == "Hız":
            return 15 + 5 * np.sin(t / 30.0)
        elif data_type == "Batarya Voltajı":
            return 12.6 - (t / 1000.0) % 1.0
        elif data_type == "Akım":
            return 10 + 2 * np.random.randn()
        elif data_type == "GPS HDOP":
            return 1.0 + 0.5 * np.random.randn()
        elif data_type == "İvme":
            return np.random.randn()
        else:  # Açısal Hız
            return 5 * np.sin(t / 20.0)

    def toggle_recording(self, enabled):
        if enabled:
            # Veri kaydetmeye başla
            pass
        else:
            # Veri kaydetmeyi durdur
            pass

    def closeEvent(self, event):
        self.update_timer.stop()
        super().closeEvent(event)