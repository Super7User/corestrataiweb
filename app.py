from flask import Flask, request, render_template, jsonify, Response, flash, redirect, url_for, send_file
from dotenv import load_dotenv, find_dotenv
import pandas as pd
# from openai import OpenAI
import requests
import openai
import os
import time
import ast
import json
from io import BytesIO
# from flask import Flask, render_template, request, jsonify
import firebase_admin
from firebase_admin import credentials, auth
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature,BadSignature
from flask_mail import Mail, Message
from firebase_admin.exceptions import FirebaseError
import logging


app = Flask(__name__)
 

load_dotenv(find_dotenv())
openai.api_key ='sk-proj-yD1vWVA1mWuSArCSrUqJT3BlbkFJMbhkUHGmr3f3HrgPvpba'

app.secret_key = 'your_secret_key'
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'your_email@example.com'
app.config['MAIL_PASSWORD'] = 'your_email_password'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)
# s = URLSafeTimedSerializer(app.secret_key)

firebaseConfig = {
    "apiKey": "AIzaSyDQ9Ym9NRCPiC-wLNsmg7PozMA7xedfwfA",
    "authDomain": "holygrail07-3bc90.firebaseapp.com",
    "projectId": "holygrail07-3bc90",
    "storageBucket": "holygrail07-3bc90.appspot.com",
    "messagingSenderId": "1007986562323",
    "appId": "1:1007986562323:web:5a670e323b70f710d9b6e6"
}

cred = credentials.Certificate("serviceAccountKey.json")  
firebase_admin.initialize_app(cred)


def get_completion(prompt, model="gpt-4"):
    messages = [{"role": "user", "content": prompt}]
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0,  # this is the degree of randomness of the model's output
        )
        return response.choices[0].message["content"]
    except Exception as e:
        logging.error(f"Error during OpenAI API call: {e}")
        return f"Error: {e}"


@app.route('/sampleData')
def sampleData():
    return render_template('sampleData.html')

@app.route('/get_info', methods=['POST'])
def get_info():
    product_name = request.form['product_name']
    prompt = f"Tell me about {product_name}"
    response = get_completion(prompt)
    return response

@app.route('/')
def index_dark():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login')
def home():
    return render_template('new_login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['login_email']
    password = request.form['login_password']

    try:
        # Verify the user's email and password using Firebase Authentication REST API
        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=" + firebaseConfig["apiKey"]
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        response = requests.post(url, json=payload)
        response_data = response.json()

        if response.status_code == 200:
            return jsonify({"status": "success", "message": f"User {email} logged in successfully."})
        else:
            return jsonify({"status": "error", "message": response_data.get("error", {}).get("message", "Invalid login credentials.")})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/register', methods=['POST'])
def register_user():
    email = request.form['email']
    password = request.form['password']
    
    try:
        user = auth.create_user(
            email=email,
            password=password
        )
              
        # Set custom claims to indicate the user is signed in
        auth.set_custom_user_claims(user.uid, {'signed_in': True})
        return jsonify({"status": "success", "message": f"User {email} registered successfully."})
    except firebase_admin.auth.AuthError as e:
        return jsonify({"status": "error", "message": str(e)})

# @app.route('/password', methods=['GET', 'POST'])
# def password():
#     if request.method == 'POST':
#         email = request.form.get('email')
#         new_password = request.form.get('password')
        
#         if email and new_password:
#             try:
#                 user = auth.get_user_by_email(email)
#                 auth.update_user(user.uid, password=new_password)
#                 return redirect(url_for('password', success=True))
#             except firebase_admin.auth.UserNotFoundError:
#                 return redirect(url_for('password', error=True))
#             except Exception as e:
#                 return redirect(url_for('password', error=True))
    
#     success = request.args.get('success')
#     error = request.args.get('error')
#     return render_template('password.html', success=success, error=error)

logging.basicConfig(level=logging.DEBUG)

@app.route('/password-reset', methods=['GET', 'POST'])
def send_password_reset():
    if request.method == 'POST':
        email = request.form.get('email')
        app.logger.debug(f"Received email: {email}")
        if email:
            try:
                app.logger.debug("Attempting to generate password reset link")
                # Generate the password reset link
                link = auth.generate_password_reset_link(email)
                app.logger.debug(f"Password reset link generated: {link}")
                send_reset_email(email, link)
                flash('Password reset email sent!', 'success')
                return redirect(url_for('send_password_reset'))
            except FirebaseError as e:
                # Log the detailed error and show a user-friendly message
                app.logger.error(f'Firebase error: {e}')
                flash('Failed to generate password reset link. Please try again later.', 'error')
                return redirect(url_for('send_password_reset'))
            except Exception as e:
                # Catch any other errors
                app.logger.error(f'Error sending password reset email: {str(e)}')
                flash('An unexpected error occurred. Please try again later.', 'error')
                return redirect(url_for('send_password_reset'))
    return render_template('password.html')

def send_reset_email(to_email, reset_link):
    msg = Message('Password Reset Request',
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[to_email])
    msg.body = f'Click the link to reset your password: {reset_link}'
    mail.send(msg)
    app.logger.debug(f"Password reset email sent to: {to_email}")

@app.route('/sam')
def sam():
    return render_template('sample.html')

@app.route('/sam1')
def sam1():
    return render_template('sample1.html')

@app.route('/title')
def title():
    return render_template('title.html')

@app.route('/theme')
def theme():
    return render_template('theme.html')

@app.route('/trendy')
def trendy():
    return render_template('trendy_blog_template.html')

@app.route('/casual')
def casual():
    return render_template('casual_template.html')

@app.route('/bold')
def bold():
    return render_template('bold_template.html')

@app.route('/elegant')
def elegant():
    return render_template('elegant_template.html')

@app.route('/minimalist')
def minimalist():
    return render_template('minimalist_template.html')

@app.route('/formal')
def formal():
    return render_template('formal_template.html')

@app.route('/vintage')
def vintage():
    return render_template('vintage_template.html')

@app.route('/gif')
def index():
    return render_template('gifgeneration.html')

@app.route('/newlogin')
def newlogin():
    return render_template('new_login.html')

@app.route('/newblog')
def newblog():
    return render_template('new_blog.html')

@app.route('/landingpage')
def landing():
    return render_template('landing_page.html')

@app.route('/imageLanding')
def imageLanding():
    return render_template('image_landingPage.html')


@app.route('/tools')
def tools():
    category = request.args.get('category', None)
    search_query = request.args.get('search', None)
    data = pd.read_csv('alltools.csv')

    if category:
        data = data[data['Category'] == category]

    if search_query:
        data = data[data['PromptSystem'].str.contains(search_query, case=False, na=False)]

    tools_data = data.to_dict(orient='records')
    categories = data['Category'].dropna().unique().tolist()
    print("It is in tools   1")

    return render_template('tools2.html', tools_data=tools_data, categories=categories)


@app.route('/tool-detail/<string:tool_id_str>')
def tool_detail(tool_id_str):
    # Attempt to convert the tool ID to integer
    try:
        tool_id = int(float(tool_id_str))  # Convert from string to float, then to int
    except ValueError:
        return "Invalid Tool ID", 400  # Return an error for invalid input

    # Read CSV file
    data = pd.read_csv('alltools.csv')
    tool_details = data.to_dict(orient='records')  # Convert data to a list of dictionaries

    # Find the specific tool by ID
    tool = next((item for item in tool_details if item['ID'] == tool_id), None)
    if tool is None:
        return "Tool not found", 404

    # Parse the 'Fields' column
    tool['Fields'] = ast.literal_eval(tool['Fields']) if pd.notna(tool['Fields']) else []

    return render_template('tool_details.html', tool=tool, tool_id=tool_id)



@app.route('/generate-content', methods=['POST'])
def generate_content():
    data = request.get_json()  # Get JSON data sent from the JavaScript fetch
    prompt = data['prompt']
    
    # Placeholder response, you will later replace this with actual content generation logic
    response_message = "I am available"

    return jsonify(message=response_message)


@app.route('/generate-stream', methods=['POST'])
def generate_stream():
    data = request.get_json()  # Get JSON data sent from the JavaScript fetch
    prompt = data['prompt']

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Write a compelling product page copy for my [product/service] that clearly communicates the features and benefits of the product, engages my [target persona], and motivates them to take action."
                },
                {
                    "role": "user",
                    "content": prompt
                },
            ],
            stream=True,
            temperature=1,
            max_tokens=256,
            top_p=1,
        )
        
        # Function to generate the response stream
        def generate():
            for chunk in response:
                yield chunk.choices[0].delta.content
        
        return Response(generate(), mimetype='text/plain')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# @app.route('/generate-stream', methods=['POST'])
# def generate_stream():

#     client = openai(api_key="sk-proj-jJllTB6aYWrrwO7DLLm9T3BlbkFJO7PocWpToNQ1rD77LXWf")
    
#     data = request.get_json()  # Get JSON data sent from the JavaScript fetch
#     prompt = data['prompt']

#     try:
#         response = client.chat.completions.create(
#             model="gpt-4",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": "Write a compelling product page copy for my [product/service] that clearly communicates the features and benefits of the product, engages my [target persona], and motivates them to take action."
#                 },
#                 {
#                     "role": "user",
#                     "content": prompt
#                 },
#             ],
#             stream=True,
#             temperature=1,
#             max_tokens=256,
#             top_p=1,
#             )
#         print("Response ========", response)
#         # Extracting the message from the response
#         #messages = response.get('choices', [])[0].get('message.content', {})

#         # Function to generate the response stream
#         def generate():
#             for chunk in response:
#                 yield chunk.choices[0].delta.content 
#         return Response(generate(), mimetype='text/plain')
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


@app.route('/login1', methods=['POST'])
def log_in():
    username = request.form['username']
    password = request.form['password']
            
    return redirect(url_for('tools'))
    """
    # Here you would validate the credentials, possibly checking against a database
    if username == 'admin' and password == 'admin':  # This is just an example condition
        return redirect(url_for('tools'))
    else:
        flash('Invalid credentials, please try again!')
        return redirect(url_for('login'))  # sRedirect back to the home/login page if credentials are incorrect
    """

#  copied


@app.route('/image')
def image():
    return render_template('image_gen.html')


@app.route('/generate-headers', methods=['POST'])
def generate_headers_old():
    print("In generate headers")
    data = request.get_json()
    topic = data['topic']
    # Dummy data for headers; replace with actual generation logic
    headers = [f"Header {i} for {topic}" for i in range(1, 11)]
    return jsonify({'headers': headers})


@app.route('/generate-description', methods=['POST'])
def generate_description():
    data = request.get_json()
    prompt = data.get('prompt')
    print(prompt)
    negative_prompt = data.get('negativePrompt')
    # Process the prompts to generate an image URL
    # Example: Generate image and return URL


    url = "https://modelslab.com/api/v6/realtime/text2img"

    payload = json.dumps({
        "key" : "4bwTSqIbyTxTdTUhJxOFFKF1TS3XxqcgrcF1IWtvBOHlKGy636yMhSxUvqc6",
        "prompt": prompt,
        "negative_prompt": "Bad quality" if negative_prompt is None else negative_prompt,
        "width": "512",
        "height": "512",
        "safety_checker": False,
        "seed": None,
        "samples":1,
        "base64":False,
        "webhook": None,
        "track_id": None
    })
    print(payload,"data")

    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
    """
    # Convert the string response to a dictionary
    response_data = json.loads(response.text)

    # Check if 'output' is in the response and if it contains at least one URL
    if 'output' in response_data and len(response_data['output']) > 0:
        image_url = response_data['output'][0]  # Get the first image URL from the output array
        print("image url =======",image_url)
        return jsonify({'status': 'success', 'image_url': image_url})
    else:
        return jsonify({'status': 'error', 'message': 'No image URL found'})

    return jsonify({'imageUrl': image_url})
    """
    response_data = json.loads(response.text)

    # Check if 'output' is in the response and if it contains at least one URL
    if 'output' in response_data and len(response_data['output']) > 0:
        image_url = response_data['output'][0]  # Get the first image URL from the output array
        print("Image URL =======", image_url)

        # Retrieve the image from the URL
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            # Save the image to a buffer
            image_buffer = BytesIO(image_response.content)
            image_buffer.seek(0)

            # Serve the image directly
            return send_file(image_buffer, mimetype='image/png', as_attachment=True, download_name='generated_image.png')
        else:
            return jsonify({'status': 'error', 'message': 'Failed to download the image'})

    else:
        return jsonify({'status': 'error', 'message': 'No image URL found'})
def process_generation(prompt, negative_prompt):
    # Dummy function to simulate image generation
    return 'http://example.com/path/to/generated/image.png'


if __name__ == '__main__':
    app.run(debug=True)


