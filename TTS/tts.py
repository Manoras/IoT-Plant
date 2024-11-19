from gtts import gTTS
import os
import time

class TextToSpeech:
    def __init__(self, lang="ko"):
        self.lang = lang
        self._last_speech_time = 0
        self.min_interval = 1  # 최소 발화 간격 (초)

    def text_to_speech(self, text, output_file="output.mp3"):
        try:
            tts = gTTS(text=text, lang=self.lang)
            tts.save(output_file)
            return True
        except Exception as e:
            print(f"Error generating speech: {e}")
            return False

    def play_audio(self, output_file="output.mp3"):
        try:
            current_time = time.time()
            if current_time - self._last_speech_time < self.min_interval:
                time.sleep(self.min_interval)
            
            os.system(f"mpg321 {output_file}")
            self._last_speech_time = time.time()
            return True
        except Exception as e:
            print(f"Error playing audio: {e}")
            return False

    def speak(self, text, output_file="output.mp3"):
        if self.text_to_speech(text, output_file):
            if self.play_audio(output_file):
                try:
                    os.remove(output_file)
                except:
                    pass
