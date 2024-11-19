import time
import asyncio
from typing import Dict, Optional

class PlantMonitor:
    def __init__(self, sensor_manager, plant_db, chatbot):
        self.sensor_manager = sensor_manager
        self.plant_db = plant_db
        self.chatbot = chatbot
        self.current_plant = "스킨답서스"  # Default plant
        self._monitoring_active = True

    def set_plant(self, plant_name: str):
        self.current_plant = plant_name

    def generate_status_prompt(self, sensor_data: Dict[str, float], comparisons: Dict[str, str]) -> str:
        status_texts = []
        sensors_kr = {
            'temperature': '온도',
            'humidity': '습도',
            'soil_moisture': '토양 수분',
            'light': '조도'
        }
        
        for sensor, status in comparisons.items():
            if status == "no_data":
                continue
                
            value = sensor_data.get(sensor)
            kr_name = sensors_kr.get(sensor, sensor)
            
            if status == "below_minimum":
                status_texts.append(f"{kr_name}가 너무 낮습니다 (현재: {value:.1f})")
            elif status == "above_maximum":
                status_texts.append(f"{kr_name}가 너무 높습니다 (현재: {value:.1f})")
        
        if not status_texts:
            return f"{self.current_plant}의 모든 환경이 적정 범위 내에 있습니다."
        
        status_summary = ", ".join(status_texts)
        prompt = f"""
        {self.current_plant}의 현재 상태:
        {status_summary}
        
        이러한 상황에서 {self.current_plant}를 위해 어떤 조치가 필요한지 설명해주세요.
        """
        return prompt.strip()

    async def monitor_cycle(self):
        print("센서 데이터 수집 시작...")
        measurement_count = 0
        
        try:
            # 2분 동안 10초마다 데이터 수집 (12회)
            while measurement_count < 12 and self._monitoring_active:
                data = self.sensor_manager.collect_data()
                if data:
                    measurement_count += 1
                await asyncio.sleep(10)
            
            if not self._monitoring_active:
                return
            
            # 평균 계산
            averages = self.sensor_manager.calculate_averages()
            if not averages:
                print("No valid sensor data collected")
                return
            
            # DB와 비교
            comparisons = self.plant_db.compare_sensor_data(self.current_plant, averages)
            if not comparisons:
                print("Could not compare sensor data")
                return
            
            # 상태가 이상적이지 않은 경우 ChatGPT에 물어보고 TTS로 출력
            prompt = self.generate_status_prompt(averages, comparisons)
            response = self.chatbot.ask_openai(prompt)
            if response:
                self.chatbot.tts.speak(response)
        
        except Exception as e:
            print(f"Monitoring cycle error: {e}")

    def stop_monitoring(self):
        self._monitoring_active = False
