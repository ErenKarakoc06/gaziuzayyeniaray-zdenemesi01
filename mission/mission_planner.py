from PyQt6.QtCore import QObject, pyqtSignal
from dataclasses import dataclass
from typing import List, Dict
import json

@dataclass
class Waypoint:
    seq: int
    command: int
    param1: float
    param2: float
    param3: float
    param4: float
    latitude: float
    longitude: float
    altitude: float
    frame: int = 0

class MissionPlanner(QObject):
    mission_updated = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.waypoints: List[Waypoint] = []
        self.current_wp_index = 0
        
    def add_waypoint(self, wp: Waypoint):
        self.waypoints.append(wp)
        self._resequence_waypoints()
        self.mission_updated.emit()
        
    def remove_waypoint(self, index: int):
        if 0 <= index < len(self.waypoints):
            del self.waypoints[index]
            self._resequence_waypoints()
            self.mission_updated.emit()
            
    def move_waypoint(self, from_index: int, to_index: int):
        if 0 <= from_index < len(self.waypoints) and 0 <= to_index < len(self.waypoints):
            wp = self.waypoints.pop(from_index)
            self.waypoints.insert(to_index, wp)
            self._resequence_waypoints()
            self.mission_updated.emit()
            
    def _resequence_waypoints(self):
        for i, wp in enumerate(self.waypoints):
            wp.seq = i
            
    def save_mission(self, filename: str):
        mission_data = [vars(wp) for wp in self.waypoints]
        with open(filename, 'w') as f:
            json.dump(mission_data, f)
            
    def load_mission(self, filename: str):
        with open(filename, 'r') as f:
            mission_data = json.load(f)
            self.waypoints = [Waypoint(**wp_data) for wp_data in mission_data]
        self.mission_updated.emit()