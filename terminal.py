from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, 
                            QLineEdit, QHBoxLayout, QPushButton)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QTextCursor, QColor, QTextCharFormat

class TerminalConsole(QWidget):
    command_sent = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.command_history = []
        self.history_index = 0

    def init_ui(self):
        layout = QVBoxLayout()

        # Terminal çıktı alanı
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #FFFFFF;
                font-family: 'Courier New';
                font-size: 12px;
            }
        """)
        layout.addWidget(self.terminal_output)

        # Komut girişi
        input_layout = QHBoxLayout()
        self.command_input = QLineEdit()
        self.command_input.setStyleSheet("""
            QLineEdit {
                background-color: #2D2D2D;
                color: #FFFFFF;
                font-family: 'Courier New';
                font-size: 12px;
                padding: 5px;
            }
        """)
        self.command_input.returnPressed.connect(self.send_command)
        input_layout.addWidget(self.command_input)

        # Gönder butonu
        self.send_button = QPushButton("Gönder")
        self.send_button.clicked.connect(self.send_command)
        input_layout.addWidget(self.send_button)

        # Temizle butonu
        self.clear_button = QPushButton("Temizle")
        self.clear_button.clicked.connect(self.clear_terminal)
        input_layout.addWidget(self.clear_button)

        layout.addLayout(input_layout)
        self.setLayout(layout)

        # Komut geçmişi için tuş olayları
        self.command_input.installEventFilter(self)

    def send_command(self):
        command = self.command_input.text().strip()
        if command:
            self.command_history.append(command)
            self.history_index = len(self.command_history)
            self.add_output(f">>> {command}", "command")
            self.command_sent.emit(command)
            self.command_input.clear()

    def add_output(self, text, type="normal"):
        cursor = self.terminal_output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        format = QTextCharFormat()
        if type == "command":
            format.setForeground(QColor("#4EC9B0"))
        elif type == "error":
            format.setForeground(QColor("#F44747"))
        elif type == "success":
            format.setForeground(QColor("#6A9955"))
        else:
            format.setForeground(QColor("#FFFFFF"))

        cursor.insertText(f"{text}\n", format)
        self.terminal_output.setTextCursor(cursor)
        self.terminal_output.ensureCursorVisible()

    def clear_terminal(self):
        self.terminal_output.clear()

    def eventFilter(self, obj, event):
        if obj is self.command_input and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Up:
                self.show_previous_command()
                return True
            elif event.key() == Qt.Key.Key_Down:
                self.show_next_command()
                return True
        return super().eventFilter(obj, event)

    def show_previous_command(self):
        if self.command_history and self.history_index > 0:
            self.history_index -= 1
            self.command_input.setText(self.command_history[self.history_index])

    def show_next_command(self):
        if self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.command_input.setText(self.command_history[self.history_index])
        elif self.history_index == len(self.command_history) - 1:
            self.history_index = len(self.command_history)
            self.command_input.clear()