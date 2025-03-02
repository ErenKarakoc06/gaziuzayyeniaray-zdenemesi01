from PyQt6.QtCore import QObject, pyqtSignal
from typing import Dict, Any
import json

class ParameterManager(QObject):
    parameter_updated = pyqtSignal(str, object)
    
    def __init__(self):
        super().__init__()
        self.parameters: Dict[str, Any] = {}
        self.parameter_descriptions: Dict[str, str] = {}
        
    def update_parameter(self, name: str, value: Any):
        self.parameters[name] = value
        self.parameter_updated.emit(name, value)
        
    def load_parameter_descriptions(self, filename: str):
        with open(filename, 'r') as f:
            self.parameter_descriptions = json.load(f)
            
    def get_parameter_description(self, name: str) -> str:
        return self.parameter_descriptions.get(name, "No description available")
        
    def save_parameters(self, filename: str):
        with open(filename, 'w') as f:
            json.dump(self.parameters, f)
            
    def load_parameters(self, filename: str):
        with open(filename, 'r') as f:
            self.parameters = json.load(f)
        for name, value in self.parameters.items():
            self.parameter_updated.emit(name, value)