from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem

class MissionTree(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setHeaderLabel('Görevler')
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)