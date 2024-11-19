import spidev
import time

class AnalogSensor:
    def __init__(self, channel, bus=0, device=0):
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = 50000
        self.channel = channel
        self._last_error_time = 0
        self.error_cooldown = 5

    def read_adc(self):
        if self.channel < 0 or self.channel > 7:
            return -1
        try:
            r = self.spi.xfer2([1, (8 + self.channel) << 4, 0])
            data = ((r[1] & 3) << 8) + r[2]
            return data
        except Exception as e:
            current_time = time.time()
            if current_time - self._last_error_time >= self.error_cooldown:
                print(f"Analog sensor error: {e}")
                self._last_error_time = current_time
            return -1

    def read(self):
        value = self.read_adc()
        if value == -1:
            return None
        return (value / 1023.0) * 100
    
    def close(self):
        try:
            self.spi.close()
        except:
            pass

class SoilMoistureSensor(AnalogSensor):
    def __init__(self, ch=0):
        super().__init__(channel=ch)
        self.name = "Soil Moisture Sensor"

    def read(self):
        value = super().read()
        if value is None:
            return None
        # 토양 수분 센서는 값이 반전되어 있으므로 보정
        return 100 - value

class LightSensor(AnalogSensor):
    def __init__(self, ch=7):
        super().__init__(channel=ch)
        self.name = "Light Sensor"
