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
from firebase_admin import credentials, auth, db
from firebase_admin.exceptions import FirebaseError
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
from flask_login import LoginManager, login_user, UserMixin, current_user, login_required, logout_user
from datetime import timedelta
import logging
from groq import Groq
import time
from PIL import Image
import csv
 
app = Flask(__name__)
 
 
 
# Get user data based on the logged-in user id
 
class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email
 
# Load environment variables
 
load_dotenv(find_dotenv())
# client = OpenAI(api_key="sk-proj-jJllTB6aYWrrwO7DLLm9T3BlbkFJO7PocWpToNQ1rD77LXWf")
client = Groq(api_key='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')
 
 
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
firebase_admin.initialize_app(cred,{
    'databaseURL': 'https://holygrail07-3bc90-default-rtdb.firebaseio.com/'
})
 
ref = db.reference('/')
 
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
    # For demonstration, we're just using the user ID. You might want to fetch user details here.
    if 'userId' in session:
        return User(id=session['userId'], email=session['user_email'])
    return None
 
@app.route('/get_user_data')
def get_user_data():
    if 'user_email' not in session:
        return jsonify({"error": "User not logged in"}), 401
 
    email = session['user_email']
   
    # Fetch user data and headers from CSV
    headers, user_data = fetch_user_data_from_csv(email)
    if user_data:
        return jsonify({
            "headers": headers,
            "user_data": user_data
        })
    else:
        return jsonify({"error": "User not found"}), 404
 
def fetch_user_data_from_csv(email):
    with open('demotools.csv', mode='r') as file:
        csv_reader = csv.DictReader(file)
        headers = csv_reader.fieldnames  # Get CSV headers
        for row in csv_reader:
            if row['Email'] == email:
                return headers, row  # Return headers and user data
    return headers, None  # Return headers and None if user not found
 
 
 
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
     # Fetch the user from session, database, or any source
    return render_template('index.html')
 
 
@app.route('/about')
def about():
    return render_template('about.html')
 
# @app.route('/repository')
# def repository():
#     user_id = session.get('userId')
#     print(user_id,"repository")
#     return render_template('repository.html')
 
@app.route('/repository', methods=['GET'])
def repository():
    user_id = session.get('userId')
   
    if not user_id:
        return jsonify({'error': 'User ID not found in session'}), 400
   
    try:
        # Query the database to find all entries with the matching user_id
        ref = db.reference('generated_streams')
        query = ref.order_by_child('user_id').equal_to(user_id)
        result = query.get()
 
        if not result:
            return jsonify({'error': 'Data not found'}), 404
 
        # Convert timestamps to readable format and collect all data
        formatted_data = []
        for key, value in result.items():
            value['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(value['timestamp'] / 1000))
            formatted_data.append(value)
 
        # Render the data in the HTML template
        return render_template('repository.html', data=formatted_data)
   
    except Exception as e:
        return jsonify({'error': str(e)}), 500
 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['login_email']
        password = request.form['login_password']
        keep_logged_in = 'keep_logged_in' in request.form
 
        try:
            # Firebase Authentication REST API request
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={firebaseConfig['apiKey']}"
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            response = requests.post(url, json=payload)
            response_data = response.json()
 
            if response.status_code == 200:
                user_id = response_data['localId']
                user = User(id=user_id, email=email)
                login_user(user, remember=keep_logged_in)
 
                # Store user info in session
                session['userId'] = user_id
                session['user_email'] = email
 
                # Set session lifetime based on 'keep_logged_in'
                if keep_logged_in:
                    session.permanent = True
                    app.permanent_session_lifetime = timedelta(hours=1)
                else:
                    session.permanent = False
 
       
                return jsonify({"status": "success", "message": f"User {email} logged in successfully."})
 
            else:
                return jsonify({"status": "error", "message": response_data.get("error", {}).get("message", "Invalid login credentials.")})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
 
    return render_template('login.html')
 
@app.route('/header')
@login_required
def header():
    email = current_user.email
    user_data = fetch_user_data_from_csv(email)
 
    if user_data:
        return render_template('header.html', user_data=user_data)
    else:
        flash("User data not found.")
        return redirect(url_for('login'))
 
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
            return jsonify({"status": "success", "message": f"User {email} registered successfully.", "redirect_url":'/newlogin'})
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
    data = pd.read_csv('alltools.csv')
 
    user_id = session.get('userId')
    print(user_id,"userId")
 
    if category and category != "All":
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
        session['tool_id'] = tool_id
    except ValueError:
        return "Invalid Tool ID", 400
   
    # session['current_tool_id'] = tool_id
    # current_tool_id = session.get('current_tool_id')
    # print(current_tool_id,"current")
 
    data = pd.read_csv('alltools.csv')
    tool_details = data.to_dict(orient='records')
 
    tool = next((item for item in tool_details if item['ID'] == tool_id), None)
    if tool is None:
        return "Tool not found", 404
 
    tool['Fields'] = ast.literal_eval(tool['Fields']) if pd.notna(tool['Fields']) else []
    font_family = tool.get('Font')
    print(font_family,"tool")
    titleName = tool.get('Title')
    print(titleName,"titleName")
    user_id = session.get('userId')
    # if user_id:
    #     title = tool.get('Title')
    #     if title:
    #         ref.child('users').child(user_id).child('tools').child(str(tool_id)).set({
    #             'title': title,
    #             'user_id':user_id,
    #             'timestamp': {"timestamp": "TIMESTAMP"}
    #         })
    #         print(f"Saved tool {title} for user {user_id} in Firebase")
 
   
    return render_template('tool_details.html', tool=tool, tool_id=tool_id,fontDynamic=font_family,titleName=titleName)
 
@app.route('/generate-content', methods=['POST'])
def generate_content():
    data = request.get_json()
    prompt = data['prompt']
   
    response_message = "I am available"
 
    return jsonify(message=response_message)
 
 
# @app.route('/generate-stream', methods=['POST'])
# def generate_stream():
#     data = request.get_json()
#     prompt = data.get('prompt')
#     user_id = session.get('userId')
   
#     if not prompt:
#         return jsonify({'error': 'Prompt is missing'}), 400
   
#     tool_id = session.get('tool_id')  # Retrieve tool_id from session
 
#     # Read the CSV and fetch the PromptSystem
#     try:
#         df = pd.read_csv('alltools.csv')  # Update the path to where the file is stored
#         tool_details = df[df['ID'] == int(tool_id)]
#         if tool_details.empty:
#             return jsonify({'error': 'Tool not found'}), 404
 
#         system_prompt = tool_details.iloc[0]['PromptSystem']
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
 
#     # Call to OpenAI with the custom system prompt
#     try:
#         response = client.chat.completions.create(
#             model="llama3-8b-8192",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": system_prompt
#                 },
#                 {
#                     "role": "user",
#                     "content": prompt
#                 },
#             ],
#             stream=True,
#             temperature=1,
#             max_tokens=512,
#             top_p=1,
#         )
 
#         # Initialize an empty string to store the entire response
#         complete_response = ""
 
#         def generate():
#             nonlocal complete_response
#             content_generated = False
 
#             for chunk in response:
#                 if chunk.choices[0].delta.content:
#                     content = chunk.choices[0].delta.content
#                     complete_response += content
#                     yield content
#                     content_generated = True
#                 else:
#                     print("No content in chunk or malformed chunk:", chunk)
           
#             # If content was generated, store it in Realtime Database
#             if content_generated:
#                 ref = db.reference('generated_streams').push()  # Auto-generate a new key for the document
#                 ref.set({
#                     'user_id': user_id,
#                     'tool_id': tool_id,
#                     'prompt': prompt,
#                     'response': complete_response,
#                     'timestamp': int(time.time() * 1000)  # Store timestamp in milliseconds
#                 })
 
#         return Response(generate(), mimetype='text/plain')
   
#     except Exception as e:
#         print("Error during streaming:", str(e))
#         return jsonify({'error': str(e)}), 500
 
 
@app.route('/generate-stream', methods=['POST'])
def generate_stream():
    data = request.get_json()
    prompt = data.get('prompt')
    user_id = session.get('userId')
   
    if not prompt:
        return jsonify({'error': 'Prompt is missing'}), 400
   
    tool_id = session.get('tool_id')  # Retrieve tool_id from session
 
    # Read the CSV and fetch the PromptSystem and Title
    try:
        df = pd.read_csv('alltools.csv')  # Update the path to where the file is stored
        tool_details = df[df['ID'] == int(tool_id)]
        if tool_details.empty:
            return jsonify({'error': 'Tool not found'}), 404
 
        system_prompt = tool_details.iloc[0]['PromptSystem']
        tool_title = tool_details.iloc[0]['Title']  # Get the title of the tool
    except Exception as e:
        return jsonify({'error': str(e)}), 500
 
    # Call to OpenAI with the custom system prompt
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                },
            ],
            stream=True,
            temperature=1,
            max_tokens=512,
            top_p=1,
        )
 
        # Initialize an empty string to store the entire response
        complete_response = ""
 
        def generate():
            nonlocal complete_response
            content_generated = False
 
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    complete_response += content
                    yield content
                    content_generated = True
                else:
                    print("No content in chunk or malformed chunk:", chunk)
           
            # If content was generated, store it in Realtime Database
            if content_generated:
                ref = db.reference('generated_streams').push()  # Auto-generate a new key for the document
                ref.set({
                    'user_id': user_id,
                    'tool_id': tool_id,
                    'tool_title': tool_title,  # Store the tool title
                    'prompt': prompt,
                    'response': complete_response,
                    'timestamp': int(time.time() * 1000)  # Store timestamp in milliseconds
                })
 
        return Response(generate(), mimetype='text/plain')
   
    except Exception as e:
        print("Error during streaming:", str(e))
        return jsonify({'error': str(e)}), 500
 
 
 
@app.route('/tooldetailoutput/<int:tool_id>', methods=['GET'])
def tool_details_output(tool_id):
    user_id = session.get('userId')
   
    if not user_id:
        return jsonify({'error': 'User ID not found in session'}), 400
   
    try:
        # Query the database to find the entries with the matching user_id and tool_id
        ref = db.reference('generated_streams')
        query = ref.order_by_child('user_id').equal_to(user_id)
        result = query.get()
 
        last_entry = None
        for key, value in result.items():
            if value['tool_id'] == tool_id:
                last_entry = value
                break  # Assuming you want the first matching entry
 
        if not last_entry:
            return jsonify({'error': 'Data not found for this tool'}), 404
 
        # Convert timestamp to readable format
        last_entry['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_entry['timestamp'] / 1000))
 
        # Render the data in the HTML template
        return render_template('tooldetail_Ouput.html', data=last_entry)
   
    except Exception as e:
        return jsonify({'error': str(e)}), 500
   
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
    datacsv = pd.read_csv('alltools.csv')
     #titles = datacsv['Title'].tolist()
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