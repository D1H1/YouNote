import requests
import json
import time


class TextAnalysis:
    def __init__(self, openai_api_key):
        self.api_key = openai_api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.api_url = "https://api.openai.com/v1/chat/completions"

    def analyze_text(self, text):
        """Uses OpenAI's GPT-3.5 Turbo to generate a title and extract 3-4 keywords from the given text."""
        prompt = (
            "Provide a short simple title (2-3 words) for the following text and 3-4 keywords (1 word-length). Example format: "
            "[\"Title\"], [\"Keyword1\", \"Keyword2\", \"Keyword3\"]:")
        payload = {
            "model": "gpt-3.5-turbo",  # Adjust if a different model is used
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ],
            "temperature": 0.5
        }

        max_retries = 3  # Maximum number of retries
        retry_delay = 5  # Delay in seconds between retries

        for attempt in range(max_retries):
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            if response.status_code == 200:
                # Extract the first response from the completion
                text_response = response.json()['choices'][0]['message']['content']

                # Attempt to parse text response into JSON structure
                try:
                    # The expected format is: ["Title"], ["Keyword1", "Keyword2", "Keyword3"]
                    # Strip brackets and quotes
                    parsed_response = text_response.replace('[', '').replace(']', '').replace('"', '').split(',')
                    title = parsed_response[0].strip()
                    keywords = [keyword.strip() for keyword in parsed_response[1:] if keyword.strip()]

                    result = {"title": title, "keywords": keywords}
                    return json.dumps(result, indent=4)
                except Exception as e:
                    print(f"Error parsing response: {e}")
            else:
                print(f"Error (attempt {attempt + 1}): {response.text}")
                time.sleep(retry_delay)

        return json.dumps({"error": "Failed to process text after several attempts"}, indent=4)


# Example usage:
if __name__ == '__main__':
    doc_text = "Practice playing guitar for 30 minutes daily. This regular practice helps in improving muscle memory and overall skill. It is part of a broader strategy to become proficient in guitar playing within the next year."

    with open('config.json') as f:
        config = json.load(f)
    openai_api_key = config['openai_api_key']

    # Initialize text analysis processor
    text_analyzer = TextAnalysis(openai_api_key=openai_api_key)

    # Analyze text and output JSON
    analysis_result = text_analyzer.analyze_text(doc_text)
    print("Analysis Result:", analysis_result)
