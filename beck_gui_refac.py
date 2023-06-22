import tkinter as tk
import speech_recognition as sr
import os
import openai
import pyttsx3
from dotenv import load_dotenv

load_dotenv()

GREEN_COLOR = "#00EE00"
RED_COLOR = "#EE6363"
VOICE_ID = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0"
ROLLING_MESSAGES_COUNT = 7
MESSAGES_FILEPATH = 'rolling_messages.txt'
PROMPT_FILEPATH = 'prompt.txt'


class RollingMessages:
    def __init__(self, filepath, count):
        self.filepath = filepath
        self.count = count
        self.messages = []

    def load(self):
        if os.path.isfile(self.filepath):
            with open(self.filepath, 'r') as file:
                self.messages = [line.strip() for line in file.readlines() if line.strip()]

    def append(self, user_text, ai_text):
        message = f"USER: {user_text}\nBECK: {ai_text}"
        if len(self.messages) >= self.count:
            self.messages.pop(0)
        self.messages.append(message)
        self.write_to_file()

    def write_to_file(self):
        with open(self.filepath, 'w') as file:
            file.write('\n'.join(self.messages))


class ChatBot:
    def __init__(self, openai_api_key):
        self.openai_api_key = openai_api_key
        self.openai_engine = 'text-davinci-003'
        self.messages = RollingMessages(MESSAGES_FILEPATH, ROLLING_MESSAGES_COUNT)
        self.load_messages()
        self.openai_prompt = self.load_prompt()

    def load_messages(self):
        self.messages.load()

    def load_prompt(self):
        with open(PROMPT_FILEPATH, 'r') as file:
            return file.read()

    def chat(self, prompt):
        response = openai.Completion.create(
            engine=self.openai_engine,
            prompt=prompt,
            max_tokens=1000,
            n=1,
            stop=None,
            temperature=0.7
        )
        return response.choices[0].text.strip()

    def generate_prompt(self, user_recent_text):
        conversation = '\n'.join(self.messages.messages)
        prompt = self.openai_prompt.replace("<<CONVERSATION>>", conversation).replace("<<USER_RECENT_QUERY>>",
                                                                                     user_recent_text)
        return prompt


class TextToSpeech:
    def __init__(self, voice_id):
        self.engine = pyttsx3.init()
        self.engine.setProperty("voice", voice_id)
        self.engine.setProperty("rate", 190)

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()


class BeckApp:
    def __init__(self, chatbot, text_to_speech):
        self.chatbot = chatbot
        self.text_to_speech = text_to_speech
        self.is_listening = False
        self.root = tk.Tk()
        self.root.geometry("400x400")
        self.root.resizable(False, False)
        self.root.title("Beck")

        self.button = tk.Button(self.root, text="", bg=GREEN_COLOR, fg=RED_COLOR, width=100, height=100,
                                command=self.toggle_listening, relief='flat')
        self.button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.root.mainloop()

    def toggle_listening(self):
        if self.is_listening:
            self.stop_listening()
        else:
            self.start_listening()

    def start_listening(self):
        self.is_listening = True
        self.button.config(bg=RED_COLOR)
        self.root.update_idletasks()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.listen_for_audio()

    def stop_listening(self):
        self.is_listening = False
        self.button.config(bg=GREEN_COLOR)
        self.root.update_idletasks()
        self.microphone = None
        self.recognizer = None

    def listen_for_audio(self):
        with self.microphone as source:
            print("Listening...")
            audio = self.recognizer.listen(source)
            print("Recognizing...")
            try:
                text = self.recognizer.recognize_google(audio)
                print("User:", text)
                # Send call to OpenAI API key.
                prompt = self.chatbot.generate_prompt(text)
                ai_response = self.chatbot.chat(prompt)
                print("BECK:", ai_response)

                self.text_to_speech.speak(ai_response)
                self.chatbot.messages.append(text, ai_response)

                if text in ["bye-bye", "bye", "goodbye"]:
                    self.root.destroy()

            except sr.UnknownValueError:
                print("Sorry, I could not understand audio.")
                self.text_to_speech.speak("Sorry, I could not understand audio.")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service: {0}".format(e))
                self.text_to_speech.speak("Could not request results from Google Speech Recognition service")

        self.stop_listening()


if __name__ == "__main__":
    openai.api_key = os.getenv("OPENAI_API_KEY")
    chatbot = ChatBot(openai.api_key)
    tts = TextToSpeech(VOICE_ID)
    app = BeckApp(chatbot, tts)
