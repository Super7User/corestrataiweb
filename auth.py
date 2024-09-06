from flask import Blueprint, request, render_template, jsonify, redirect, session, url_for,current_app
from flask_mail import Mail, Message
from flask_login import LoginManager, login_user, UserMixin, current_user, login_required, logout_user
from firebase_admin import auth as firebase_auth, db
from datetime import timedelta
import logging
import smtplib
import requests
import time

# Initialize the auth blueprint
auth_blueprint = Blueprint('auth_blueprint', __name__)

# Set up the login manager for user sessions
login_manager = LoginManager()

# Dummy User class for session management
class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email

# Firebase configuration (use actual credentials)
firebaseConfig = {
    "apiKey": "AIzaSyDQ9Ym9NRCPiC-wLNsmg7PozMA7xedfwfA",
    "authDomain": "holygrail07-3bc90.firebaseapp.com",
    "projectId": "holygrail07-3bc90",
    "storageBucket": "holygrail07-3bc90.appspot.com",
    "messagingSenderId": "1007986562323",
    "appId": "1:1007986562323:web:5a670e323b70f710d9b6e6"
}

# Load user function for login manager
@login_manager.user_loader
def load_user(user_id):
    # Implement your user loader logic here
    # For demonstration, we'll return a dummy user
    return User(user_id, "example@example.com")

# Route for sending a password reset email
@auth_blueprint.route('/send_reset_password', methods=['POST'])
def send_reset_password():
    email = request.form.get('email')
    if not email:
        return jsonify({'status': 'error', 'message': 'Email address is required.'}), 400
    
    try:
        reset_link = firebase_auth.generate_password_reset_link(email)
        
        # Get the mail object from the Flask app context
        mail = current_app.extensions.get('mail')

        msg = Message('Password Reset Request', sender="your-email@example.com", recipients=[email])
        msg.body = f'Click the following link to reset your password: {reset_link}'
        
        # Send the email using the mail object
        mail.send(msg)
        return jsonify({'status': 'success', 'message': 'Reset link sent via email.'})
    
    except firebase_auth.UserNotFoundError:
        return jsonify({'status': 'error', 'message': 'No user found with this email address.'}), 404
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({'status': 'error', 'message': f'An unexpected error occurred: {str(e)}'}), 500
# Route for login
@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['login_email']
        password = request.form['login_password']
        keep_logged_in = 'keep_logged_in' in request.form

        try:
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

                session['userId'] = user_id
                session.permanent = keep_logged_in  # Set session based on 'keep_logged_in'

                return jsonify({"status": "success", "message": f"User {email} logged in successfully."})
            else:
                return jsonify({"status": "error", "message": response_data.get("error", {}).get("message", "Invalid login credentials.")})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
    
    return render_template('login.html')

# Route for signup
@auth_blueprint.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    token = data.get('token')

    try:
        decoded_token = firebase_auth.verify_id_token(token)
        uid = decoded_token['uid']

        return jsonify({'success': True, 'uid': uid})
    except firebase_auth.InvalidIdTokenError:
        return jsonify({'success': False, 'error': 'Invalid ID token'}), 401
    except firebase_auth.ExpiredIdTokenError:
        return jsonify({'success': False, 'error': 'Expired ID token'}), 401
    except firebase_auth.RevokedIdTokenError:
        return jsonify({'success': False, 'error': 'Revoked ID token'}), 401
    except Exception as e:
        return jsonify({'success': False, 'error': 'Token verification failed'}), 401

# Route for logout
@auth_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('auth_blueprint.login'))

# Route for registering a new user
@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            user = firebase_auth.create_user(email=email, password=password)
            firebase_auth.set_custom_user_claims(user.uid, {'signed_in': True})
            return jsonify({"status": "success", "message": f"User {email} registered successfully."})
        except firebase_auth.AuthError as e:
            return jsonify({"status": "error", "message": str(e)})

    return render_template('register.html')

@auth_blueprint.route('/repository', methods=['GET'])
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


# Logging configuration
logging.basicConfig(level=logging.DEBUG)
