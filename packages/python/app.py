from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging
import os
# from hugchat import hugchat
# from hugchat.login import Login
from dotenv import load_dotenv
import easyocr
import numpy as np
from PIL import Image
import re
import pytesseract
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

app = Flask(__name__)
CORS(app, origins="*")

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retrieve EMAIL, PASSWD, NODEJS_SERVICE_URL, and FLASK_PORT from environment variables
EMAIL = os.environ.get('EMAIL')
PASSWD = os.environ.get('PASSWD')
NODEJS_SERVICE_URL = os.environ.get('NODEJS_SERVICE_URL')
FLASK_PORT = os.environ.get('FLASK_PORT', 8000)  # Default port is 8000 if FLASK_PORT is not set

if EMAIL is None or PASSWD is None or NODEJS_SERVICE_URL is None:
    raise ValueError("EMAIL, PASSWD, or NODEJS_SERVICE_URL environment variables are not set.")

# # Initialize HugChat
# cookie_path_dir = "./cookies"
# sign = Login(EMAIL, PASSWD)
# cookies = sign.login(cookie_dir_path=cookie_path_dir, save_cookies=True)
# chatbot = hugchat.ChatBot(cookies=cookies.get_dict())

@app.route('/')
def home():
    return 'Hello, World!'

# # Endpoint to process prompts
# @app.route("/process-prompt", methods=["POST"])
# def process_prompt():
#     try:
#         data = request.json
#         prompt = data['prompt']
#         prompt_id = data['id']

#         # Process prompt with HugChat
#         response = chatbot.chat(prompt)

#         # Trigger Node.js API with response and prompt ID
#         payload = {"promptId": prompt_id, "response": str(response).strip()}
#         expResponse = requests.post(NODEJS_SERVICE_URL+"/api/response", json=payload)
#         expResponse.raise_for_status()

#         return jsonify({"message": "Prompt response updated successfully", "data": str(response).strip()}), 200
#     except Exception as e:
#         logging.error(f"Error processing prompt: {e}")
#         return jsonify({"error": "Internal Server Error"}), 500
    

@app.route("/process-image", methods=["POST"])
def process_image():
    try:
        # Get image file from request
        image_file = request.files['image']
        category = request.form.get('category')

        image = Image.open(image_file)
        image_np = np.array(image)

        reader = easyocr.Reader(['en'])
        # Read text from image using EasyOCR
        result = reader.readtext(image_np)
        # print("EasyOCR Result:", result)

        # Extract text from result
        extracted_text = ' '.join([text[1] for text in result])

        filtered_text = filter_text(extracted_text)

        return jsonify({"text": extracted_text.strip(), "label": category}), 200

    except Exception as e:
        logging.error(f"Error processing image: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    

@app.route("/process-imaget", methods=["POST"])
def process_imaget():
    try:
        # Get image file from request
        image_file = request.files['image']
        category = request.form.get('category')

        image = Image.open(image_file)

        # Convert image to grayscale
        image_gray = image.convert('L')

        # Perform OCR using Pytesseract
        extracted_text = pytesseract.image_to_string(image_gray, config='--psm 6')

        print("Pytesseract Result:", extracted_text)

        # Filter and process extracted text if needed
        # filtered_text = filter_text(extracted_text)

        return jsonify({"text": extracted_text.strip(), "label": category}), 200

    except Exception as e:
        print("Error:", e)  # Print the error for debugging
        logging.error(f"Error processing image: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
def filter_text(text):
    # Convert text to lowercase
    text = text.lower()

    # Define regex pattern to remove non-alphabetic characters
    pattern = r'[^a-z\s]'

    # Apply regex pattern to remove unwanted elements from text
    filtered_text = re.sub(pattern, '', text)

    # Replace multiple spaces with single space
    filtered_text = re.sub(r'\s+', ' ', filtered_text)

    return filtered_text.strip()


categories = [
    "Personal & Lifestyle",
    "Work & Business",
    "Education & Learning",
    "Financial & Legal",
    "Health & Medical",
    "Travel & Leisure",
    "Entertainment & Media",
    "Utilities & Miscellaneous",
]

# Load tokenizer and model
loaded_tokenizer = DistilBertTokenizer.from_pretrained("./ml.models/saved.model/tokenizer")
loaded_model = DistilBertForSequenceClassification.from_pretrained("./ml.models/saved.model")

# API endpoint to predict labels for given sentences
@app.route("/predict-labels", methods=["POST"])
def predict_labels_api():
    try:
        # Get sentences from request data
        data = request.json
        sentences = data["sentences"]

        # Predict labels for sentences
        predicted_labels = predict_labels(loaded_model, loaded_tokenizer, sentences, categories)

        # Create response with sentences and predicted labels
        response = {sentence: label for sentence, label in zip(sentences, predicted_labels)}
        
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Function to predict labels for given sentences
def predict_labels(model, tokenizer, sentences, categories):
    # Encode sentences
    encoded_sentences = tokenizer(sentences, padding=True, truncation=True, max_length=128, return_tensors='pt')

    # Perform inference on the model
    with torch.no_grad():
        outputs = model(**encoded_sentences)
    
    # Get predicted class indices
    predicted_class_indices = torch.argmax(outputs.logits, dim=1).tolist()
    
    # Map indices to labels
    predicted_labels = [categories[index] for index in predicted_class_indices]
    
    return predicted_labels



if __name__ == "__main__":
    app.run(port=int(FLASK_PORT), debug=True)
