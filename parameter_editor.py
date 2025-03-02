from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, 
                            QTreeWidgetItem, QLineEdit, QPushButton, QLabel,
                            QProgressBar, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal

class ParameterEditor(QWidget):
    parameter_changed = pyqtSignal(str, float)

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.parameters = {}

    def init_ui(self):
        layout = QVBoxLayout()

        # Üst kısım - Arama ve yenileme
        top_layout = QHBoxLayout()
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Parametre ara...")
        self.search_box.textChanged.connect(self.filter_parameters)
        
        self.refresh_btn = QPushButton("Yenile")
        self.refresh_btn.clicked.connect(self.refresh_parameters)
        
        self.write_btn = QPushButton("Tümünü Yaz")
        self.write_btn.clicked.connect(self.write_all_parameters)
        
        top_layout.addWidget(self.search_box)
        top_layout.addWidget(self.refresh_btn)
        top_layout.addWidget(self.write_btn)
        
        layout.addLayout(top_layout)

        # Parametre ağacı
        self.param_tree = QTreeWidget()
        self.param_tree.setHeaderLabels(['Parametre', 'Değer', 'Birim', 'Açıklama'])
        self.param_tree.itemChanged.connect(self.on_parameter_changed)
        layout.addWidget(self.param_tree)

        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def add_parameter(self, name, value, unit="", description=""):
        # Parametre gruplarını ayır (örn: SERVO_1_MIN -> SERVO grubu)
        group = name.split('_')[0]
        
        # Grup için kök öğeyi bul veya oluştur
        root = None
        for i in range(self.param_tree.topLevelItemCount()):
            if self.param_tree.topLevelItem(i).text(0) == group:
                root = self.param_tree.topLevelItem(i)
                break
        
        if root is None:
            root = QTreeWidgetItem(self.param_tree)
            root.setText(0, group)
            root.setExpanded(True)

        # Parametre öğesini oluştur
        item = QTreeWidgetItem(root)
        item.setText(0, name)
        item.setText(1, str(value))
        item.setText(2, unit)
        item.setText(3, description)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        
        self.parameters[name] = value

    def filter_parameters(self):
        search_text = self.search_box.text().lower()
        
        # Tüm öğeleri kontrol et
        for i in range(self.param_tree.topLevelItemCount()):
            group = self.param_tree.topLevelItem(i)
            visible_children = False
            
            # Grup içindeki parametreleri kontrol et
            for j in range(group.childCount()):
                param = group.child(j)
                matches = (search_text in param.text(0).lower() or 
                          search_text in param.text(3).lower())
                param.setHidden(not matches)
                visible_children = visible_children or matches
            
            # Grubu, içinde görünür parametre varsa göster
            group.setHidden(not visible_children)

    def refresh_parameters(self):
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        
        # TODO: MAVLink üzerinden parametreleri al
        # Örnek parametreler:
        example_params = {
            'SERVO_1_MIN': {'value': 1000, 'unit': 'us', 'desc': 'Minimum PWM'},
            'SERVO_1_MAX': {'value': 2000, 'unit': 'us', 'desc': 'Maximum PWM'},
            'BATT_CAPACITY': {'value': 3000, 'unit': 'mAh', 'desc': 'Battery capacity'},
        }
        
        self.param_tree.clear()
        self.parameters.clear()
        
        for i, (name, data) in enumerate(example_params.items()):
            self.add_parameter(name, data['value'], data['unit'], data['desc'])
            self.progress_bar.setValue((i + 1) * 100 // len(example_params))
        
        self.progress_bar.hide()

    def on_parameter_changed(self, item, column):
        if column == 1 and item.parent():  # Değer sütunu ve alt öğe
            try:
                name = item.text(0)
                value = float(item.text(1))
                self.parameters[name] = value
                self.parameter_changed.emit(name, value)
            except ValueError:
                QMessageBox.warning(self, "Hata", "Geçersiz değer!")
                item.setText(1, str(self.parameters[name]))

    def write_all_parameters(self):
        # TODO: Tüm parametreleri araca gönder
        pass