from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, send_file, Response
from flask_login import login_required, current_user
from dotenv import load_dotenv, find_dotenv
from groq import Groq
import pandas as pd
import ast
import requests
from io import BytesIO
import time
from firebase_admin import credentials, auth, db
import json
import logging

image_blueprint = Blueprint('image', __name__)

@image_blueprint.route('/image')
def image():
    datacsv = pd.read_csv('alltools.csv')
    # titles = datacsv['Title'].tolist()
    other_titles = datacsv[datacsv['Category'] != 'image']['Title'].tolist()
    datacsv['Category'] = datacsv['Category'].str.strip().str.title()
    negative_prompts = datacsv.set_index('Title')['Negativeprompt'].dropna().to_dict()
    image_titles = datacsv[datacsv['Category'] == 'Image']['Title'].tolist()

    print(image_titles,"title")
    return render_template('image_gen.html',tools_data=image_titles, negative_prompts=negative_prompts)

@image_blueprint.route('/generate-description', methods=['POST'])
def generate_description():
    data = request.get_json()
    prompt = data.get('prompt')
    negative_prompt = data.get('negativePrompt')

    url = "https://modelslab.com/api/v6/realtime/text2img"

    payload = json.dumps({
        "key": "4bwTSqIbyTxTdTUhJxOFFKF1TS3XxqcgrcF1IWtvBOHlKGy636yMhSxUvqc6",
        "prompt": prompt,
        "negative_prompt": "Bad quality" if negative_prompt is None else negative_prompt,
        "width": "512",
        "height": "512",
        "safety_checker": False,
        "seed": None,
        "samples": 1,
        "base64": False,
        "webhook": None,
        "track_id": None
    })

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, data=payload)
    response_data = json.loads(response.text)

    if 'output' in response_data and len(response_data['output']) > 0:
        image_url = response_data['output'][0]

        image_response = requests.get(image_url)

        if image_response.status_code == 200:
            image_buffer = BytesIO(image_response.content)
            image_buffer.seek(0)

            return send_file(image_buffer, mimetype='image/png', as_attachment=True, download_name='generated_image.png')
        else:
            return jsonify({'status': 'error', 'message': 'Failed to download the image'})
    else:
        return jsonify({'status': 'error', 'message': 'No image URL found'})
