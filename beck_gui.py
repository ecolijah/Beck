import tkinter as tk
import speech_recognition as sr
import os
import openai
import tempfile
import pyttsx3

# loading environment variables from .env file.
from dotenv import load_dotenv
load_dotenv()

# constants
green_color = "#00EE00"
red_color = "#EE6363"
i = 0 # finding voice


# function that sends message to API and returns text response.
####### need to add memory of past conversations somehow
def chat(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant named Beck, who is helpful but not enthusiastic. You are concise with your answers and do not say more than you need to."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content.strip()


# function that turns text to speech and speaks it.
def text_to_speech(ai_text):
    engine = pyttsx3.init()
    engine.setProperty("voice", "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0")

    engine.setProperty("rate", 200)  # You can adjust the speech rate here
    engine.say(ai_text)
    engine.runAndWait()


# Beck class representing the tkinter application.
class Beck:
    def __init__(self):
        self.is_listening = False
        self.root = tk.Tk()
        self.root.geometry("400x400")  # sets dimensions of window.
        self.root.resizable(False, False)  # Prevents window from being resizable.
        self.root.title("Beck")

        self.button = tk.Button(self.root, text="", bg=green_color, fg=red_color, width=100, height=100,
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
        self.button.config(bg=red_color)
        self.root.update_idletasks()  # Force the update of the button appearance.
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.listen_for_audio()

    def stop_listening(self):
        self.is_listening = False
        self.button.config(bg=green_color)
        self.root.update_idletasks()  # Force the update of the button appearance.
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
                ai_response = chat(text)
                print("Beck:", ai_response)

                # Convert the AI response to speech.
                text_to_speech(ai_response)

                # Terminate the application
                if text in ["bye-bye", "bye", "goodbye"]:
                    self.root.destroy()

            except sr.UnknownValueError:
                print("Sorry, I could not understand audio.")
                text_to_speech("Sorry, I could not understand audio.")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))
                text_to_speech("Could not request results from Google Speech Recognition service")

        self.stop_listening()


if __name__ == "__main__":
    openai.api_key = os.getenv("OPENAI_API_KEY")
    app = Beck()
