from flask import Flask, request, render_template, jsonify, Response, flash, redirect, session, url_for, send_file
from dotenv import load_dotenv, find_dotenv
import pandas as pd
import requests
from openai import OpenAI
import os
import ast
import json
from io import BytesIO
import firebase_admin
from firebase_admin import credentials, auth
from firebase_admin.exceptions import FirebaseError
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
from flask_login import LoginManager, login_user, UserMixin, current_user, login_required, logout_user
from datetime import timedelta
import logging

app = Flask(__name__)

class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email

# Load environment variables

load_dotenv(find_dotenv())
client = OpenAI(api_key="sk-proj-jJllTB6aYWrrwO7DLLm9T3BlbkFJO7PocWpToNQ1rD77LXWf")


# OpenAI configuration
# openai.api_key = os.getenv("OPENAI_API_KEY")


app.secret_key = 'your_secret_key'
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'your_email@example.com'
app.config['MAIL_PASSWORD'] = 'your_email_password'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

# Firebase configuration
cred = credentials.Certificate("serviceAccountKey.json")  
firebase_admin.initialize_app(cred)

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

firebaseConfig = {
    "apiKey": "AIzaSyDQ9Ym9NRCPiC-wLNsmg7PozMA7xedfwfA",
    "authDomain": "holygrail07-3bc90.firebaseapp.com",
    "projectId": "holygrail07-3bc90",
    "storageBucket": "holygrail07-3bc90.appspot.com",
    "messagingSenderId": "1007986562323",
    "appId": "1:1007986562323:web:5a670e323b70f710d9b6e6"
}

@login_manager.user_loader
def load_user(user_id):
    # Implement your user loader logic here
    # For demonstration, we'll return a dummy user
    return User(user_id, "example@example.com")

def get_completion(prompt, model="gpt-4"):
    messages = [{"role": "user", "content": prompt}]
    try:
        response =client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,
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

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form['login_email']
#         password = request.form['login_password']
#         keep_logged_in = 'keep_logged_in' in request.form
#         print(request,request.form,"rrrrr") 
#         try:
#             # Verify the user's email and password using Firebase Authentication REST API
#             url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={firebaseConfig['apiKey']}"
#             payload = {
#                 "email": email,
#                 "password": password,
#                 "returnSecureToken": True
#             }
#             response = requests.post(url, json=payload)
#             response_data = response.json()

#             if response.status_code == 200:
#                 user_id = response_data['localId']
#                 user = User(id=user_id, email=email)
#                 login_user(user, remember=keep_logged_in)

#                 if keep_logged_in:
#                     session.permanent = True
#                     app.permanent_session_lifetime = timedelta(hours=1)
#                 else:
#                     session.permanent = False

#                 return jsonify({"status": "success", "message": f"User {email} logged in successfully."})
#             else:
#                 return jsonify({"status": "error", "message": response_data.get("error", {}).get("message", "Invalid login credentials.")})
#         except Exception as e:
#             return jsonify({"status": "error", "message": str(e)})

#     return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['login_email']
        password = request.form['login_password']
        keep_logged_in = 'keep_logged_in' in request.form

        try:
            # Verify the user's email and password using Firebase Authentication REST API
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={firebaseConfig['apiKey']}"
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            response = requests.post(url, json=payload)
            response_data = response.json()
            
            # Print the response data
            print(response_data)
            
            if response.status_code == 200:
                user_id = response_data['localId']
                user = User(id=user_id, email=email)
                login_user(user, remember=keep_logged_in)

                if keep_logged_in:
                    session.permanent = True
                    app.permanent_session_lifetime = timedelta(hours=1)  # Keep logged in for 24 hours
                else:
                    session.permanent = False

                return jsonify({"status": "success", "message": f"User {email} logged in successfully."})
            else:
                return jsonify({"status": "error", "message": response_data.get("error", {}).get("message", "Invalid login credentials.")})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            user = auth.create_user(
                email=email,
                password=password
            )
            auth.set_custom_user_claims(user.uid, {'signed_in': True})
            return jsonify({"status": "success", "message": f"User {email} registered successfully."})
        except firebase_admin.auth.AuthError as e:
            return jsonify({"status": "error", "message": str(e)})

    return render_template('register.html')

@app.route('/password-reset', methods=['GET', 'POST'])
def send_password_reset():
    if request.method == 'POST':
        email = request.form.get('email')
        app.logger.debug(f"Received email: {email}")
        if email:
            try:
                app.logger.debug("Attempting to generate password reset link")
                link = auth.generate_password_reset_link(email)
                app.logger.debug(f"Password reset link generated: {link}")
                send_reset_email(email, link)
                flash('Password reset email sent!', 'success')
                return redirect(url_for('send_password_reset'))
            except FirebaseError as e:
                app.logger.error(f'Firebase error: {e}')
                flash('Failed to generate password reset link. Please try again later.', 'error')
                return redirect(url_for('send_password_reset'))
            except Exception as e:
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

@app.route('/tools')
@login_required
def tools():
    category = request.args.get('category', None)
    search_query = request.args.get('search', None)
    data = pd.read_csv('alltools1.csv')

    if category:
        data = data[data['Category'] == category]

    if search_query:
        data = data[data['PromptSystem'].str.contains(search_query, case=False, na=False)]

    tools_data = data.to_dict(orient='records')
    categories = data['Category'].dropna().unique().tolist()
 
    session['tool_ids'] = data['ID'].tolist()

    user_email = current_user.email if current_user.is_authenticated else None
  
    return render_template('tools2.html', tools_data=tools_data, categories=categories, user_email=user_email)

@app.route('/tool-detail/<string:tool_id_str>')
def tool_detail(tool_id_str):
    try:
        tool_id = int(float(tool_id_str))
    except ValueError:
        return "Invalid Tool ID", 400
    
    session['current_tool_id'] = tool_id
    current_tool_id = session.get('current_tool_id')
    print(current_tool_id,"current")

    data = pd.read_csv('alltools1.csv')
    tool_details = data.to_dict(orient='records')

    tool = next((item for item in tool_details if item['ID'] == tool_id), None)
    if tool is None:
        return "Tool not found", 404

    tool['Fields'] = ast.literal_eval(tool['Fields']) if pd.notna(tool['Fields']) else []

    return render_template('tool_details.html', tool=tool, tool_id=tool_id)

@app.route('/generate-content', methods=['POST'])
def generate_content():
    data = request.get_json()
    prompt = data['prompt']
    
    response_message = "I am available"

    return jsonify(message=response_message)

@app.route('/generate-stream', methods=['POST'])
def generate_stream():
    data = request.get_json()
    prompt = data['prompt']
    textarea = data['textareaInput']

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Write a compelling product page copy for my [product/service] that clearly communicates the features and benefits of the product, engages my [target persona], and motivates them to take action."},
                {"role": "user", "content": prompt},
                {"role": "user", "content": textarea}
            ],
            stream=True,
            temperature=1,
            max_tokens=256,
            top_p=1,
        )
        
        def generate():
            for chunk in response:
                yield chunk.choices[0].delta.content
        
        return Response(generate(), mimetype='text/plain')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-description', methods=['POST'])
def generate_description():
    data = request.get_json()
    # dropdownPrompt = data.get('dropdownPrompt')
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
    print(response_data,"response")
    if 'output' in response_data and len(response_data['output']) > 0:
        image_url = response_data['output'][0]

        image_response = requests.get(image_url)

        print(image_response,"image")
        if image_response.status_code == 200:
            image_buffer = BytesIO(image_response.content)
            image_buffer.seek(0)

            return send_file(image_buffer, mimetype='image/png', as_attachment=True, download_name='generated_image.png')
        else:
            return jsonify({'status': 'error', 'message': 'Failed to download the image'})
    else:
        return jsonify({'status': 'error', 'message': 'No image URL found'})

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

@app.route('/login1', methods=['POST'])
def log_in():
    username = request.form['username']
    password = request.form['password']
    return redirect(url_for('tools'))

@app.route('/image')
def image():
    datacsv = pd.read_csv('alltools1.csv')
    # titles = datacsv['Title'].tolist()
    other_titles = datacsv[datacsv['Category'] != 'image']['Title'].tolist()
    datacsv['Category'] = datacsv['Category'].str.strip().str.title()
    negative_prompts = datacsv.set_index('Title')['Negativeprompt'].dropna().to_dict()
    image_titles = datacsv[datacsv['Category'] == 'Image']['Title'].tolist()

    print(image_titles,"title")
    return render_template('image_gen.html',tools_data=image_titles, negative_prompts=negative_prompts)

@app.route('/generate-headers', methods=['POST'])
def generate_headers_old():
    data = request.get_json()
    topic = data['topic']
    headers = [f"Header {i} for {topic}" for i in range(1, 11)]
    return jsonify({'headers': headers})

logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    app.run(debug=True)
