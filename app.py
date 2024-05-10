from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
from datetime import datetime
import json
from process_inputs import TextAnalysis
from process_images import ImageTitleGenerator
from copilot import  ChatGPTNoteResponder
app = Flask(__name__)

# Load configuration and initialize services
with open('config.json') as f:
    config = json.load(f)

OPENAI_API_KEY = config['openai_api_key']
GOOGLE_CREDENTIALS_PATH = config['GOOGLE_CREDENTIALS_PATH']
MONGO_URI = config['mongo_uri']  # Assuming this is added to your config

client = MongoClient(MONGO_URI)
db = client['Cluster0']  # You can name your database as you like
notes_collection = db['notes']
questions_collection = db['questions']

text_analysis = TextAnalysis(OPENAI_API_KEY)
image_title_generator = ImageTitleGenerator(OPENAI_API_KEY, GOOGLE_CREDENTIALS_PATH)


@app.route('/submit_question', methods=['POST'])
def submit_question():
    question = request.form['question']
    index_name = "default"  # Adjust to your actual index name

    try:
        query = {
            "$search": {
                "index": index_name,
                "text": {
                    "query": question,
                    "path": {
                        "wildcard": "*"
                    }
                }
            }
        }

        results = notes_collection.aggregate([{"$search": query["$search"]}])

        matched_notes = []
        for note in results:
            formatted_note = (
                f"Title: {note.get('title', 'N/A')}\n"
                f"Content: {note.get('content', 'N/A')}\n"
                f"Tags: {note.get('tags', [])}\n"
                f"Created At: {note.get('createdAt', 'N/A')}\n"
                f"Updated At: {note.get('updatedAt', 'N/A')}\n"
                f"ID: {note.get('_id', 'N/A')}\n"
            )
            matched_notes.append(formatted_note)

        print("Query used:", json.dumps(query))
        print("Search Results:", matched_notes)

    except Exception as e:
        print("Error during text search:", e)
        matched_notes = []

    # Generate response from ChatGPT
    responder = ChatGPTNoteResponder(openai_api_key=config['openai_api_key'])
    response = responder.generate_response(matched_notes, question)
    print("Generated Response:", response)

    return render_template('index.html', notes=matched_notes, question=question, response=response)


@app.route('/')
def index():
    notes = list(notes_collection.find().sort("createdAt", -1).limit(5))
    return render_template('index.html', notes=notes)


@app.route('/add_note', methods=['POST'])
def add_note():
    text = request.form['note_text']
    image = request.files['image'] if 'image' in request.files else None
    image_filename = image.filename if image else ''

    # Generate title and keywords based on the text or image
    if image:
        image_path = f'./static/{image_filename}'  # Construct a file path
        image.save(image_path)  # Save the image to a directory within the project
        keywords = image_title_generator.get_image_labels(image_path)
        title_data = image_title_generator.generate_title(keywords)
        print(keywords, type(keywords), type(title_data))
        title = title_data.get('title', 'Default Title') if isinstance(title_data, dict) else 'Default Title'
    else:
        title_data = text_analysis.analyze_text(text)
        if isinstance(title_data, str):
            try:
                title_data = json.loads(title_data)  # Only parse if it's a string
            except json.JSONDecodeError as e:
                print(f"Error parsing title data: {e}")
                title_data = {"title": "Default Title", "keywords": []}

        title = title_data.get('title', 'Default Title')
        keywords = title_data.get('keywords', [])

    # Log received data
    print("Received Note:")
    print(f"Title: {title}")
    print(f"Text: {text}")
    print(f"Image: {image_filename}")
    print(f"Keywords: {keywords}")

    # Save the note to MongoDB instead of CSV (modification if MongoDB is integrated)
    notes_collection.insert_one({
        "title": title,
        "text": text,
        "image": image_filename,
        "keywords": keywords,
        "createdAt": datetime.now()
    })

    # Redirect to the homepage
    return redirect(url_for('index'))


@app.route('/update_notes')
def update_notes():
    note_count = int(request.args.get('noteCount', 5))
    notes = list(notes_collection.find().sort("createdAt", -1).limit(note_count))

    # Print the update request
    print(f"Updating notes display, Count: {note_count}")

    # Build HTML using safe access to dictionary keys
    html = ''.join([
        f"<div class='note'><h3>{note.get('title', 'No Title')}</h3><p>{note.get('text', 'No content available')}</p>"
        f"<img src='static/{note.get('image', '')}' alt='Image' style='display:{'block' if note.get('image') else 'none'}'>"
        f"<p>Keywords: {', '.join(note.get('keywords', []))}</p><p>Date Created: {note.get('createdAt', 'Unknown').strftime('%Y-%m-%d %H:%M:%S')}</p></div>"
        for note in notes
    ])
    return jsonify({'html': html})


if __name__ == '__main__':
    app.run(debug=True)
