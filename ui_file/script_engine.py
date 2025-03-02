        cancel_btn = QPushButton("İptal")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)
        
        layout.addLayout(buttons)
        self.setLayout(layout)
        self.setWindowTitle("Örnek Scriptler")

    def get_selected_example(self):
        return self.list_widget.currentItem().text() if self.list_widget.currentItem() else None

class DocumentationDialog(QDialog):
    def __init__(self, docs, parent=None):
        super().__init__(parent)
        self.docs = docs
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setMarkdown(self.docs)
        layout.addWidget(text_edit)
        
        close_btn = QPushButton("Kapat")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        self.setWindowTitle("DroneKit API Dokümantasyonu")
        self.resize(800, 600)