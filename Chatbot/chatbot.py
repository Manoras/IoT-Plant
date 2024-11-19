import openai
import os
from dotenv import load_dotenv

load_dotenv()

class ChatBot:
    def __init__(self, stt, tts, model="gpt-3.5-turbo"):
        self.stt = stt
        self.tts = tts
        self.model = model
        self.message_history = []

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("API key not found. Please check your .env file")
        
        openai.api_key = api_key

    def ask_openai(self, question):
        if len(self.message_history) == 0:
            self.message_history.append({
                "role": "system",
                "content": "You are a helpful assistant. You must answer in Korean.",
            })

        self.message_history.append({"role": "user", "content": question})

        try:
            completion = openai.ChatCompletion.create(
                model=self.model,
                messages=self.message_history,
            )

            answer = completion.choices[0].message.content
            self.message_history.append({"role": "assistant", "content": answer})

            return answer
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return "죄송합니다. 응답을 받는 중에 오류가 발생했습니다."

    def chat(self):
        print("Listening...")
        user_text = self.stt.transcribe_audio()
        if not user_text:
            return

        print("User:", user_text)
        print("Asking OpenAI API...")
        response_text = self.ask_openai(user_text)
        print("Assistant:", response_text)

        print("Converting response to speech...")
        self.tts.speak(response_text)

    def reset_message_history(self):
        self.message_history.clear()
