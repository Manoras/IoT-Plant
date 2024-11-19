import asyncio
import threading
import time
import signal
from Sensor import DHT11, SoilMoistureSensor, LightSensor, SensorManager
from Database import PlantDatabase
from Monitor import PlantMonitor
from STT import SpeechToText
from TTS import TextToSpeech
from Chatbot import ChatBot

class IoTPlantSystem:
    def __init__(self):
        self.running = True
        self.monitor_thread = None
        self.voice_thread = None
        
        try:
            self.init_components()
        except Exception as e:
            print(f"Error initializing components: {e}")
            self.running = False
            return

    def init_components(self):
        # Initialize sensors
        self.dht_sensor = DHT11()
        self.soil_sensor = SoilMoistureSensor()
        self.light_sensor = LightSensor()

        # Initialize database
        self.db = PlantDatabase()
        self.db.create_tables()

        # Initialize voice interface
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.chatbot = ChatBot(self.stt, self.tts)

        # Initialize managers
        self.sensor_manager = SensorManager(self.dht_sensor, self.soil_sensor, self.light_sensor)
        self.plant_monitor = PlantMonitor(self.sensor_manager, self.db, self.chatbot)

    async def monitor_task(self):
        while self.running:
            try:
                await self.plant_monitor.monitor_cycle()
            except Exception as e:
                print(f"Monitoring error: {e}")
                await asyncio.sleep(10)  # Wait before retrying

    def voice_assistant_task(self):
        while self.running:
            try:
                text = self.stt.transcribe_audio()
                if text:
                    if self.stt.detect_keyword(text):
                        print("Keyword detected! Starting chat...")
                        self.chatbot.chat()
            except Exception as e:
                print(f"Voice assistant error: {e}")
                time.sleep(1)  # Wait before retrying

    def start(self):
        """Start all system components"""
        if not self.running:
            print("System initialization failed. Cannot start.")
            return

        try:
            # Create event loop for the monitor thread
            self.monitor_thread = threading.Thread(
                target=lambda: asyncio.run(self.monitor_task())
            )
            self.monitor_thread.daemon = True

            # Create voice assistant thread
            self.voice_thread = threading.Thread(
                target=self.voice_assistant_task
            )
            self.voice_thread.daemon = True

            # Start threads
            self.monitor_thread.start()
            self.voice_thread.start()

            # Keep main thread alive
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nReceived shutdown signal...")
            finally:
                self.stop()

        except Exception as e:
            print(f"System error: {e}")
            self.stop()

    def stop(self):
        """Stop all system components"""
        if not self.running:
            return
            
        print("\nShutting down system...")
        self.running = False
        
        # Wait for threads to finish
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)
        if self.voice_thread and self.voice_thread.is_alive():
            self.voice_thread.join(timeout=2)

        # Clean up resources
        try:
            self.sensor_manager.close()
        except:
            pass

        try:
            self.db.close()
        except:
            pass

        print("System shutdown complete")
