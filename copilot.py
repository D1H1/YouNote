import requests
import json
import datetime

class ChatGPTNoteResponder:
    def __init__(self, openai_api_key):
        self.api_key = openai_api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.api_url = "https://api.openai.com/v1/chat/completions"

    def generate_response(self, notes, user_query):
        """Generates a response based on a list of notes and a user query using OpenAI's GPT-3.5 Turbo model."""
        context = "The following notes are given: " + " ".join(notes) + f" Answer the following question based on these notes. Current time: {datetime.datetime.now()}"
        prompt = f"{context} Question: {user_query}"
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": context},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5
        }

        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            text_response = response.json()['choices'][0]['message']['content']
            return text_response
        except requests.RequestException as e:
            return f"Error: {str(e)}"

# Example usage:
if __name__ == '__main__':
    notes = [
        '''"Joyful Toddler Outdoors"
Keywords: ['Skin', 'People in nature', 'Flash photography', 'Happy', 'Gesture', 'Interaction', 'Smile', 'Toddler', 'Sky', 'Baby']
Date Created: 2024-05-10 20:49:53.087944
id: 123''',
        '''Ordering Pizza
How to make pizza: 1. Order at dominos 2. Wait

Keywords: ["Domino's", 'Easy', 'Quick']

Date Created: 2024-05-10 20:49:19.844078
id: 122''',
        '''Joyful Family Outing
Image
Keywords: []
Date Created: 2024-05-10 20:48:16.526000
id: 121'''
    ]
    question = "Show recent notes about pizza"

    # Assuming 'openai_api_key' is loaded from a configuration file or environment variable
    with open('config.json') as f:
        config = json.load(f)
    openai_api_key = config['openai_api_key']

    responder = ChatGPTNoteResponder(openai_api_key=openai_api_key)
    response = responder.generate_response(notes, question)
    print("Generated Response:", response)
