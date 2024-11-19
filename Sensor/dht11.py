import board
import adafruit_dht
import time

class DHT11:
    def __init__(self, pin=board.D17):
        self.pin = pin
        self.dht_device = None
        self.init_sensor()
        self._last_error_time = 0
        self.error_cooldown = 5
        self._consecutive_errors = 0
        self.max_consecutive_errors = 3

    def init_sensor(self):
        try:
            if self.dht_device:
                self.dht_device.exit()
            self.dht_device = adafruit_dht.DHT11(self.pin)
        except Exception as e:
            print(f"DHT11 initialization error: {e}")

    def read(self):
        if self.dht_device is None:
            self.init_sensor()
            return None

        try:
            temperature_c = self.dht_device.temperature
            humidity = self.dht_device.humidity
            self._consecutive_errors = 0  # 성공적인 읽기 후 에러 카운트 리셋
            return temperature_c, humidity
        
        except RuntimeError as err:
            current_time = time.time()
            self._consecutive_errors += 1
            
            if self._consecutive_errors >= self.max_consecutive_errors:
                if current_time - self._last_error_time >= self.error_cooldown:
                    print(f"DHT11 Error: {err.args[0]}")
                    self._last_error_time = current_time
                self.init_sensor()  # 센서 재초기화
                self._consecutive_errors = 0
            
            return None

        except Exception as err:
            print(f"Critical DHT11 error: {err}")
            self.close()
            time.sleep(2)  # 에러 발생 시 잠시 대기
            self.init_sensor()
            return None
        
    def close(self):
        try:
            if self.dht_device:
                self.dht_device.exit()
                self.dht_device = None
        except:
            pass
