from flask import Flask,Blueprint,render_template, request, jsonify, send_file
import pandas as pd
import requests
import logging
from openai import OpenAI
from io import BytesIO
from PIL import Image

app = Flask(__name__)

@app.route('/generate-description', methods=['POST'])
def generate_description():
    data = request.get_json()
    prompt = data.get('prompt')
    negative_prompt = data.get('negativePrompt')

    # Optionally accept width and height from the client
    image_width = data.get('width', 850)
    image_height = data.get('height', 420)

    client1 = OpenAI(api_key="sk-proj-jJllTB6aYWrrwO7DLLm9T3BlbkFJO7PocWpToNQ1rD77LXWf")

    try:
        # Generate the image using OpenAI API
        response = client1.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",  # Default size to work with
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        print("image url==", image_url)
        image_response = requests.get(image_url)

        if image_response.status_code == 200:
            image_buffer = BytesIO(image_response.content)
            image = Image.open(image_buffer)

            # Resize image based on frontend dimensions
            resized_image = image.resize((image_width, image_height))
            resized_image_buffer = BytesIO()
            
            resized_image.save(resized_image_buffer, format='PNG')
            resized_image_buffer.seek(0)

            return send_file(resized_image_buffer, mimetype='image/png', as_attachment=True, download_name='generated_image.png')
        else:
            return jsonify({'status': 'error', 'message': 'Failed to download the image'}), 500
    except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    


@app.route('/image')
def image():
    datacsv = pd.read_csv('alltools.csv')
     #titles = datacsv['Title'].tolist()
    other_titles = datacsv[datacsv['Category'] != 'image']['Title'].tolist()
    datacsv['Category'] = datacsv['Category'].str.strip().str.title()
    negative_prompts = datacsv.set_index('Title')['Negativeprompt'].dropna().to_dict()
    image_titles = datacsv[datacsv['Category'] == 'Image']['Title'].tolist()

    print(image_titles,"title")
    return render_template('image_gen.html',tools_data=image_titles, negative_prompts=negative_prompts)

logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':
    app.run(debug=True)