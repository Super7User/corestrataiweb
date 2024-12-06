from flask import Flask, render_template, request, jsonify, session, redirect, current_app
from flask_mail import Mail, Message
from flask_login import LoginManager, login_user, UserMixin, current_user, login_required, logout_user
from firebase_admin import credentials, firestore, initialize_app, auth as firebase_auth, db
import redis
import logging
import requests
from datetime import datetime, timedelta

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'dhanapooja1211@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-email-password'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEBUG'] = True
mail = Mail(app)

# Initialize Firebase Admin
cred = credentials.Certificate("serviceAccountKey.json")
initialize_app(cred, {'databaseURL': 'https://holygrail07-default-rtdb.firebaseio.com'})
firebase_db = firestore.client()

# Initialize Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User Model for Flask-Login
class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email



@login_manager.user_loader
def load_user(user_id):
    return User(user_id, "example@example.com")

firebaseConfig = {
    "apiKey": "AIzaSyANFurFRRBK-NrZstE1A-LUd9gHM1ODjkY",
    "authDomain": "holygrail07.firebaseapp.com",
    "databaseURL": "https://holygrail07-default-rtdb.firebaseio.com",
    "projectId": "holygrail07",
    "storageBucket": "holygrail07.appspot.com",
    "messagingSenderId": "395680302764",
    "appId": "1:395680302764:web:8a7ac908f4a7f7ceeb0109",
    "measurementId": "G-PVSRW8082S"
}


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/newlogin')
def newlogin():
    return render_template('auth/new_login.html')

@app.route('/newLanding')
def newLanding():
    return render_template('newLanding.html')

@app.route('/password')
def password_reset():
    return render_template('auth/password.html')

@app.route('/send_reset_password', methods=['POST'])
def send_reset_password():
    email = request.form.get('email')
    if not email:
        return jsonify({'status': 'error', 'message': 'Email address is required.'}), 400

    try:
        reset_link = firebase_auth.generate_password_reset_link(email)
        msg = Message('Password Reset Request', sender="your-email@example.com", recipients=[email])
        msg.body = f'Click the following link to reset your password: {reset_link}'
        mail.send(msg)
        return jsonify({'status': 'success', 'message': 'Reset link sent via email.'})
    except firebase_auth.UserNotFoundError:
        return jsonify({'status': 'error', 'message': 'No user found with this email address.'}), 404
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({'status': 'error', 'message': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['login_email'].strip().lower()
        password = request.form['login_password']
        keep_logged_in = 'keep_logged_in' in request.form

        try:
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={firebaseConfig['apiKey']}"
            response = requests.post(url, json={"email": email, "password": password, "returnSecureToken": True})
            response_data = response.json()

            if response.status_code == 200:
                user_id = response_data['localId']
                user = User(id=user_id, email=email)
                login_user(user, remember=keep_logged_in)
                session['is_admin'] = email == "admin@gmail.com"
                redis_client.hset(user_id, mapping={"user_id": user_id, "email": email})
                return jsonify({"status": "success", "message": "Login successful."})
            else:
                return jsonify({"status": "error", "message": response_data.get("error", {}).get("message", "Invalid login credentials.")})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = firebase_auth.create_user(email=email, password=password)
            firebase_db.collection('users').document(user.uid).set({
                'email': email,
                'plan': 'Free',
                'created_at': datetime.utcnow()
            })
            return jsonify({"status": "success", "message": f"User {email} registered successfully."})
        except Exception as e:
            return jsonify({"status": 'error', "message": str(e)})
    return render_template('auth/register.html')

# @app.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     session.clear()
#     return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
