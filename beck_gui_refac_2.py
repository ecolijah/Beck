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
ROLLING_MESSAGES_COUNT = 7 #can be increased for larger memory, at the cost of more tokens.
MESSAGES_FILEPATH = 'rolling_messages.txt'
PROMPT_FILEPATH = 'prompt.txt'


class RollingMessages:
    # Represents a rolling messages log.
    def __init__(self, filepath, count):
        self.filepath = filepath
        self.count = count
        self.messages = [] #variable representation of messages log.

    def load(self):
        # Load messages from file into messages list.
        if os.path.isfile(self.filepath):
            with open(self.filepath, 'r') as file:
                self.messages = [line.strip() for line in file.readlines() if line.strip()]

    def append(self, user_text, ai_text):
        # Append a new message to the log.
        message = f"USER: {user_text}\nBECK: {ai_text}"
        if len(self.messages) >= self.count:
            self.messages.pop(0) #pops oldest element
            self.messages.pop(0) #pops 2nd oldest element, they come in pairs
        self.messages.append(message)
        self.write_to_file()

    def write_to_file(self):
        # Write messages to file.
        with open(self.filepath, 'w') as file:
            file.write('\n'.join(self.messages))


class ChatBot:
    # Represents the chatbot using OpenAI API
    def __init__(self, openai_api_key):
        self.openai_api_key = openai_api_key
        self.openai_engine = 'text-davinci-003'
        self.messages = RollingMessages(MESSAGES_FILEPATH, ROLLING_MESSAGES_COUNT) #initializing message log object
        self.load_messages()
        self.openai_prompt = self.load_prompt()

    def load_messages(self):
        # Load the rolling messages log to be associated with chatbot.
        self.messages.load()

    def load_prompt(self):
        # Load the conversation prompt.
        with open(PROMPT_FILEPATH, 'r') as file:
            return file.read()

    def chat(self, prompt):
        # Send chat prompt to OpenAI and get the response.
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
        # Generate the conversation prompt with the latest user query.
        conversation = '\n'.join(self.messages.messages)
        prompt = self.openai_prompt.replace("<<CONVERSATION>>", conversation).replace("<<USER_RECENT_QUERY>>", user_recent_text)
        return prompt


class TextToSpeech:
    # Handles text-to-speech conversion.
    def __init__(self, voice_id):
        self.engine = pyttsx3.init()
        self.engine.setProperty("voice", voice_id)
        self.engine.setProperty("rate", 190)

    def speak(self, text):
        # Convert text to speech and speak it.
        self.engine.say(text)
        self.engine.runAndWait()


class BeckApp:
    """
    Represents the tkinter application for the Beck chatbot.
    """

    def __init__(self, chatbot, text_to_speech):
        self.chatbot = chatbot
        self.text_to_speech = text_to_speech
        self.is_listening = False
        self.root = tk.Tk()
        self.root.geometry("800x400")
        self.root.resizable(False, False)
        self.root.title("Beck")

        self.button = tk.Button(self.root, text="", bg=GREEN_COLOR, fg=RED_COLOR, width=100, height=100,
                                command=self.toggle_listening, relief='flat')
        self.button.place(relx=0.0, rely=0.5, anchor=tk.CENTER)

        self.message_box = tk.Text(self.root, bg="white", fg="black", height=25, width=55, relief='flat')
        self.message_box.place(relx=0.72, rely=0.5, anchor=tk.CENTER)

        self.scrollbar = tk.Scrollbar(self.root, command=self.message_box.yview)
        #self.scrollbar.place(relx=0.98, rely=0.5, anchor=tk.CENTER, relheight=0.8)

        self.message_box.config(yscrollcommand=self.scrollbar.set)
        self.message_box.config(state="disabled")

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
        self.recognizer.pause_threshold = 2  # can be adjusted to the user's preference.
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
                print("USER:", text)
                # Update the message box with user and bot messages
                self.message_box.config(state="normal")
                self.message_box.insert(tk.END, "USER: " + text + "\n", "user")
                self.root.update_idletasks() #force update idle task

                prompt = self.chatbot.generate_prompt(text)
                ai_response = self.chatbot.chat(prompt)
                print("BECK:", ai_response)
                self.message_box.insert(tk.END, "BECK: " + ai_response + "\n", "bot")
                self.message_box.config(state="disabled")
                self.root.update_idletasks() #force update idle task
                # Configure the message tags for color highlighting
                self.message_box.tag_config("user", foreground="blue")
                self.message_box.tag_config("bot", foreground="green")
                self.root.update_idletasks() #force update idle task

                self.text_to_speech.speak(ai_response)
                self.chatbot.messages.append(text, ai_response)

                if text in ["bye-bye", "bye", "goodbye"]:
                    self.root.destroy()

            except sr.UnknownValueError:
                print("Sorry, I could not understand audio.")
                self.text_to_speech.speak("Sorry, I could not understand audio.")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))
                self.text_to_speech.speak("Could not request results from Google Speech Recognition service")

        self.stop_listening()


# Driver code
if __name__ == "__main__":
    openai.api_key = os.getenv("OPENAI_API_KEY")
    chatbot = ChatBot(openai.api_key)
    text_to_speech = TextToSpeech(VOICE_ID)
    app = BeckApp(chatbot, text_to_speech)