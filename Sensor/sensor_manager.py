from collections import defaultdict
from statistics import mean
from typing import Dict, Optional
import time

class SensorManager:
    def __init__(self, dht_sensor, soil_sensor, light_sensor):
        self.dht_sensor = dht_sensor
        self.soil_sensor = soil_sensor
        self.light_sensor = light_sensor
        self.measurements = defaultdict(list)
        self.averages = {}
        self.retry_count = 3
        self.retry_delay = 2
        self._last_error_time = 0
        self.error_cooldown = 5

    def read_sensors(self) -> Dict[str, Optional[float]]:
        current_time = time.time()
        data = {
            'temperature': None,
            'humidity': None,
            'soil_moisture': None,
            'light': None
        }
        
        # DHT11 센서 읽기
        dht_result = self.dht_sensor.read()
        if dht_result:
            data['temperature'], data['humidity'] = dht_result

        # 토양 습도 센서 읽기
        soil_value = self.soil_sensor.read()
        if soil_value is not None:
            data['soil_moisture'] = soil_value

        # 조도 센서 읽기
        light_value = self.light_sensor.read()
        if light_value is not None:
            data['light'] = light_value

        return data

    def collect_data(self) -> Optional[Dict[str, float]]:
        data = self.read_sensors()
        valid_data = {k: v for k, v in data.items() if v is not None}
        
        if valid_data:
            for key, value in valid_data.items():
                self.measurements[key].append(value)
        
        return valid_data if valid_data else None

    def calculate_averages(self) -> Dict[str, float]:
        """측정값 평균 계산"""
        try:
            self.averages = {
                sensor: mean(values) for sensor, values in self.measurements.items()
                if values  # Only calculate if there are values
            }
            self.measurements.clear()  # Reset measurements after calculating averages
            return self.averages
        except Exception as e:
            print(f"Error calculating averages: {e}")
            return {}

    def close(self):
        """센서 리소스 정리"""
        try:
            self.dht_sensor.close()
            self.soil_sensor.close()
            self.light_sensor.close()
        except Exception as e:
            print(f"Error closing sensors: {e}")
