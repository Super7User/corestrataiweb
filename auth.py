from flask import Blueprint, request, render_template, jsonify, redirect, session, url_for,current_app
from flask_mail import Mail, Message
from flask_login import LoginManager, login_user, UserMixin, current_user, login_required, logout_user
from firebase_admin import auth as firebase_auth, db
from datetime import timedelta
import logging
import requests
import time
import pandas as pd

auth_blueprint = Blueprint('auth_blueprint', __name__)

login_manager = LoginManager()


class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email

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


@login_manager.user_loader
def load_user(user_id):
    # Implement your user loader logic here
    # For demonstration, we'll return a dummy user
    return User(user_id, "example@example.com")

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

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['login_email'].strip().lower()  # Strip any whitespace and convert to lowercase
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
                session.permanent = keep_logged_in  

                try:
                    plan_data = pd.read_csv('plan.csv')
                    plan_data['mail_Id'] = plan_data['mail_Id'].str.strip().str.lower()
                   
                    matching_rows = plan_data[plan_data['mail_Id'] == email]
                    print(matching_rows, plan_data['mail_Id'],email,"matching_rows") 

                    if not matching_rows.empty:
                        
                        plan = matching_rows['Plan'].values[0]  
                        session['email'] = email  
                        session['plan'] = plan    
                        print(plan,"plan")
                        unique_id = db.reference('generated_streams').push().key
                        session['firebase_unique_id'] = unique_id  # Store this ID in session

                        ref = db.reference(f'generated_streams/{unique_id}')
                        ref.update({
                            'plan': plan,
                        })


                        return jsonify({"status": "success", "message": f"Login successful. Plan: {plan}"})
                    else:
                        return jsonify({"status": "error", "message": "No plan associated with this user."})

                except Exception as e:
                    return jsonify({"status": "error", "message": f"Error reading plan data: {str(e)}"})
            else:
                return jsonify({"status": "error", "message": response_data.get("error", {}).get("message", "Invalid login credentials.")})

        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
 
    return render_template('login.html',plan=plan)

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

@auth_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('auth_blueprint.login'))

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
    user_emailId = session.get('email')
    user_plan = session.get('plan')
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
        return render_template('repository.html', data=formatted_data,plan=user_plan)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


logging.basicConfig(level=logging.DEBUG)
