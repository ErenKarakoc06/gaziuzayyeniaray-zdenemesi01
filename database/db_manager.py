import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_file='mission_planner.db'):
        self.db_file = db_file
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            # Görevler tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS missions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Waypoint'ler tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS waypoints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mission_id INTEGER,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    altitude REAL,
                    order_index INTEGER,
                    FOREIGN KEY (mission_id) REFERENCES missions (id)
                )
            ''')
            
            conn.commit()