import io
import requests
import json
from google.cloud import vision
from google.oauth2 import service_account


class ImageTitleGenerator:
    def __init__(self, openai_api_key, google_credentials_path):
        # Set up credentials for both services
        self.vision_client = vision.ImageAnnotatorClient(
            credentials=service_account.Credentials.from_service_account_file(google_credentials_path))
        self.api_key = openai_api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.api_url = "https://api.openai.com/v1/chat/completions"

    def get_image_labels(self, image_path):
        """Detects labels in the image file using Google Cloud Vision API."""
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()
            image = vision.Image(content=content)
            response = self.vision_client.label_detection(image=image)
            labels = response.label_annotations
            return [label.description for label in labels]

    def generate_title(self, labels):
        """Generates a title using OpenAI's GPT-3.5 Turbo based on image labels."""
        text = "Generate a short precise title (2-3 words) for an image containing: " + ', '.join(labels)
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "system", "content": text}],
            "temperature": 0.5
        }

        response = requests.post(self.api_url, headers=self.headers, json=payload)
        if response.status_code == 200:
            response_data = response.json()
            title = response_data['choices'][0]['message']['content']
            return {"title": title}
        else:
            print("Error generating title:", response.text)
            return {"title": "Error in title generation"}


if __name__ == '__main__':
    # Initialize the generator
    with open('config.json') as f:
        config = json.load(f)
    openai_api_key = config['openai_api_key']
    GOOGLE_CREDENTIALS_PATH = config['GOOGLE_CREDENTIALS_PATH']

    image_path = '/home/david/PycharmProjects/YouNote/examples/family.jpg'
    generator = ImageTitleGenerator(openai_api_key, GOOGLE_CREDENTIALS_PATH)

    # Get labels from the image
    labels = generator.get_image_labels(image_path)
    print("Detected Labels:", labels)

    # Generate and print the image title
    title = generator.generate_title(labels)
    print("Generated Title:", title)
