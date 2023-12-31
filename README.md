# Beck Chatbot

Beck is an AI-powered chatbot that uses the OpenAI API, PineConeDB client, and speech recognition to engage in interactive conversations with users. (Supplemented by conversational memory as well as long-term memory enabled through use of a vector database.)

![Example Image](example.png)

## Features

- Long-term memory: Beck can recall details from past conversations, by querying a vector databse for relevant conversations.
- Voice activation: Beck can listen to user queries through the microphone and respond accordingly.
- Text-based interaction: Users can also communicate with Beck by typing their queries.
- Rolling message log: Beck maintains a rolling log of user chats and AI responses for reference during the conversation. in combination with long-term memory supplied by a vector database.
- Text-to-speech conversion: Beck will convert AI responses into speech for a more interactive experience.
- Easy configuration: The chatbot can be customized by adjusting settings and environment variables.
- Customizable experience: By altering the 'prompt.txt', users can easily cuztomize their experience in a variety of ways.
- Tkinter-GUI: simple gui experience.

## Prerequisites

To run the Beck chatbot, ensure you have the following:

- Python 3.9.13 installed
- The required Python packages installed (specified in the `requirements.txt` file)
- An OpenAI API key (set as the `OPENAI_API_KEY` environment variable)
- A PinconeDB API Key (set as the `PINECONE_API_KEY` environment variable)
- Speech recognition dependencies (such as microphone access and appropriate audio drivers)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/beck-chatbot.git
   cd beck-chatbot

2. Install required dependencies (inside venv, if you wish): 

    ```bash
    pip install -r requirements.txt

3. Obtain OpenAI API key, and set environment variable.

4. Obtain PineconeDB API key, and set environment variable.

5. Create PinconeDB Index.

6. Run the program:

    ```bash
    python beck.py

## Usage

The chatbot window will appear, allowing you to interact with Beck either through voice or text. Simply press the green button to speak to Beck or just type your queries, and Beck will respond accordingly.

Whenever the button is red, please be patient for Beck's response. Whenever it turns green again, she is ready to be asked another question.

To exit the chatbot, you can say or type "bye-bye," "bye," or "goodbye." Or simply just exit the window.
