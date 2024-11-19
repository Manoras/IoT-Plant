import whisper
import sounddevice as sd
import soundfile as sf
import numpy as np
import os
import warnings
import time

class SpeechToText:
    def __init__(self, model_size="base", duration=5, keyword="지니"):
        self.model = None
        self.model_size = model_size
        self.duration = duration
        self.samplerate = 16000
        self.sound_file = "sound_file.mp3"
        self.keywords = keyword
        self._last_text = None
        warnings.filterwarnings("ignore", category=UserWarning)

    def load_model(self):
        if self.model is None:
            print("모델 로드 중...")
            self.model = whisper.load_model(self.model_size)
            print("모델 로드 완료!")
        return self

    def transcribe_audio(self, audio=None):
        try:
            if self.model is None:
                self.load_model()

            if audio is None:
                print(f"\n{self.duration}초 동안 말씀해주세요...")
                audio = sd.rec(
                    int(self.duration * self.samplerate),
                    samplerate=self.samplerate,
                    channels=1,
                    dtype='float32'
                )
                sd.wait()
                print("녹음 완료!")

            sf.write(self.sound_file, audio, self.samplerate)

            print("음성 인식 중...")
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                result = self.model.transcribe(self.sound_file, language='ko')
            
            text = result["text"].strip() if result and "text" in result else None
            
            # 중복 출력 방지
            if text and text != self._last_text:
                print(f"Recognized text: {text}")
                self._last_text = text
            
            return text

        except Exception as e:
            print(f"음성 인식 오류: {e}")
            return None

        finally:
            if os.path.exists(self.sound_file):
                try:
                    os.remove(self.sound_file)
                except:
                    pass

    def detect_keyword(self, text):
        return bool(text and self.keywords in text)
