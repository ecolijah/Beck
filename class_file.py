import pyttsx3
import os

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

class TextToSpeech:
    # Handles text-to-speech conversion.
    def __init__(self, voice_id):
        self.engine = pyttsx3.init()
        self.engine.setProperty("voice", voice_id)
        self.engine.setProperty("rate", 210)

    def speak(self, text):
        # Convert text to speech and speak it.
        self.engine.say(text)
        self.engine.runAndWait()
