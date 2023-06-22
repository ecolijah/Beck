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
voiceid ="HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0"
# make changes so that while app is running we use variable memory, and before it closes it writes latest copy to messages log.
rolling_messages = []
rolling_messages_count = 10
messages_filepath = 'rolling_messages.txt'
proompt_filepath = 'prompt.txt'

# function that sends message to API and returns text response.
####### need to add memory of past conversations somehow
# for this version we will go with a rolling memory of the past 10 or so chats back and forth. 
def append_to_rolling_messages(user_text, ai_text):
        # append
    global rolling_messages
    tmpstr = "USER: " + user_text + "\n" + "BECK: " + ai_text
    tmp_rolling_messages = []
    if len(rolling_messages) < rolling_messages_count:
        # Read the file and convert its contents into a list
        with open(messages_filepath, 'r') as file:
            lines = file.readlines()
        tmp_rolling_messages = [line.strip() for line in lines if line.strip()]
        tmp_rolling_messages.append(tmpstr)
        # updates global list
        rolling_messages = tmp_rolling_messages
        write_to_file(messages_filepath, tmp_rolling_messages)  

    else:
        # delete oldest append newest
        # Read the file and retrieve the last 9 lines
        with open(messages_filepath, 'r') as file:
            lines = file.readlines()[-rolling_messages_count-1:]
        tmp_rolling_messages = [line.strip() for line in lines if line.strip()]
        # appends newest convo
        tmp_rolling_messages.append(tmpstr)
        # updates global list
        rolling_messages = tmp_rolling_messages 
        write_to_file(messages_filepath, tmp_rolling_messages)  

    return

def write_to_file(filename, lines):
    # Clear the file
    with open(filename, 'w') as file:
        file.write('')

    # Write the lines to the file
    with open(filename, 'a') as file:
        for line in lines:
            file.write(line + '\n')

def chat(prompt_):
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt_,
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.7
    )
    #append to rolling messages
    return response.choices[0].text.strip()

def load_conversation(file_path):
    # Read the file and return its content as a string
    with open(file_path, 'r') as file:
        file_content = file.read()
    return file_content

def generate_prompt(user_recent_text):
    # TODO: add previous conversation, and most recent user query to prompt
    conversation = load_conversation(messages_filepath)
    prompt = open_file_edit_contents(proompt_filepath, "<<CONVERSATION>>", conversation, "<<USER_RECENT_QUERY>>", user_recent_text)
    print(prompt + '\n')
    return prompt
def open_file_edit_contents(file_path, old_str_1, new_str_1, old_str_2, new_str_2):
    # Read the file
    with open(file_path, 'r') as file:
        content = file.read()
        content = content.replace(old_str_1, new_str_1)
        content = content.replace(old_str_2, new_str_2)
    
    # Return the replace_and_save method as a dot method
    return content

# function that turns text to speech and speaks it.
def text_to_speech(ai_text):
    engine = pyttsx3.init()
    engine.setProperty("voice", voiceid)

    engine.setProperty("rate", 190)  # You can adjust the speech rate here
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
                #generate prompt
                prompt = generate_prompt(text)
                ai_response = chat(prompt)
                print("BECK:", ai_response)

                # Convert the AI response to speech.
                ## TODO: add to rolling messages
                
                text_to_speech(ai_response)
                append_to_rolling_messages(text, ai_response)
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
