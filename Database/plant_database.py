import sqlite3
import threading
from contextlib import contextmanager

class PlantDatabase:
    def __init__(self, db_name="plant_data.db"):
        self.db_name = db_name
        self.thread_local = threading.local()

    @contextmanager
    def get_connection(self):
        if not hasattr(self.thread_local, "connection"):
            self.thread_local.connection = sqlite3.connect(self.db_name)
        try:
            yield self.thread_local.connection
        except Exception as e:
            print(f"Database error: {e}")
            if hasattr(self.thread_local, "connection"):
                self.thread_local.connection.close()
                delattr(self.thread_local, "connection")
            raise

    def create_tables(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS plants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    ideal_temperature_min REAL,
                    ideal_temperature_max REAL,
                    ideal_humidity_min REAL,
                    ideal_humidity_max REAL,
                    ideal_soil_moisture_min REAL,
                    ideal_soil_moisture_max REAL,
                    ideal_light_min REAL,
                    ideal_light_max REAL
                )
            """)
            
            plants_data = [
                ("스킨답서스", 18, 27, 40, 70, 40, 60, 500, 2500),
                ("몬스테라", 20, 30, 50, 80, 45, 65, 1000, 3000),
                ("산세베리아", 15, 30, 30, 50, 20, 40, 1500, 4000)
            ]
            
            cursor.executemany("""
                INSERT OR IGNORE INTO plants (
                    name, ideal_temperature_min, ideal_temperature_max, 
                    ideal_humidity_min, ideal_humidity_max, 
                    ideal_soil_moisture_min, ideal_soil_moisture_max, 
                    ideal_light_min, ideal_light_max
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, plants_data)
            
            conn.commit()

    def fetch_all_data(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM plants")
            return cursor.fetchall()

    def fetch_specific_columns(self, plant_name, columns):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            col_names = ", ".join(columns)
            cursor.execute(f"SELECT {col_names} FROM plants WHERE name = ?", (plant_name,))
            return cursor.fetchone()

    def compare_sensor_data(self, plant_name, sensor_data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                ideal_values = self.fetch_specific_columns(
                    plant_name,
                    [
                        "ideal_temperature_min", "ideal_temperature_max",
                        "ideal_humidity_min", "ideal_humidity_max",
                        "ideal_soil_moisture_min", "ideal_soil_moisture_max",
                        "ideal_light_min", "ideal_light_max"
                    ]
                )
                
                if ideal_values:
                    comparisons = {}
                    temp_min, temp_max, hum_min, hum_max, soil_min, soil_max, light_min, light_max = ideal_values
                    
                    comparisons['temperature'] = self._compare(sensor_data.get('temperature'), temp_min, temp_max)
                    comparisons['humidity'] = self._compare(sensor_data.get('humidity'), hum_min, hum_max)
                    comparisons['soil_moisture'] = self._compare(sensor_data.get('soil_moisture'), soil_min, soil_max)
                    comparisons['light'] = self._compare(sensor_data.get('light'), light_min, light_max)
                    
                    return comparisons
                return None
            except Exception as e:
                print(f"Error comparing sensor data: {e}")
                return None

    def _compare(self, sensor_value, min_val, max_val):
        if sensor_value is None:
            return "no_data"
        if sensor_value < min_val:
            return "below_minimum"
        elif min_val <= sensor_value <= max_val:
            return "within_range"
        else:
            return "above_maximum"

    def close(self):
        if hasattr(self.thread_local, "connection"):
            self.thread_local.connection.close()
            delattr(self.thread_local, "connection")
