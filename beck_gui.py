import tkinter as tk
import speech_recognition as sr
from gtts import gTTS
import os
import openai
import tempfile
import pygame

# loading environment variables from .env file.
from dotenv import load_dotenv
load_dotenv() 

# function that sends messaage to api, returns text response.
def chat(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages = [    # calibration for the ai.
            {"role": "system", "content": "You are an assistant named Beck."},
            {"role": "user", "content": "Can you recommend a good movie?"},
            {"role": "assistant", "content": "What genre are you interested in?"},
            {"role": "user", "content": "I like 2000's comedy movies."},
            {"role": "assistant", "content": "In that case, I recommend watching 'Superbad', starring Jonah Hill or 'Tropic-Thunder', starring Ben Stiller."},
            {"role": "user", "content": text}
        ]

    )
    return response.choices[0].message.content.strip()

# function that turns text to speech, returns name of the temporary audio file.
def text_to_speech(ai_text):
    # Create a temporary file to save the audio.
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_filename = temp_file.name

    # Convert the text to speech.
    tts = gTTS(text=ai_text, lang="en")
    tts.save(temp_filename)

    return temp_filename

# function that plays audio file using pygame library.
def play_audio(audio_file_tmp):
    pygame.mixer.init()
    pygame.mixer.music.load(audio_file_tmp)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue
    
    
# Beck class representing the tkinter application.
class Beck:
    def __init__(self):
        self.is_listening = False
        self.root = tk.Tk()
        self.root.geometry("400x400")  # sets dimensions of window.
        self.root.resizable(False, False)  # Prevents window from being resizable.
        self.root.title("Beck")

        self.button = tk.Button(self.root, text="", width=100, bg="green", height=100, command=self.toggle_listening)
        self.button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.root.mainloop()

    def toggle_listening(self):
        if self.is_listening:
            self.stop_listening()
        else:
            self.start_listening()

    def start_listening(self):
        self.is_listening = True
        self.button.config(bg="red")
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.listen_for_audio()

    def stop_listening(self):
        self.is_listening = False
        self.button.config(bg="green")
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
                audio_file = text_to_speech(ai_response)
                # play the generated audio file.
                play_audio(audio_file)

            except sr.UnknownValueError:
                print("Sorry, I could not understand audio.")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))

        self.stop_listening()


if __name__ == "__main__":
    openai.api_key = os.getenv("OPENAI_API_KEY")
    app = Beck()
