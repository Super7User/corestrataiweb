from flask import Flask, request, jsonify, render_template, session,Blueprint
from flask_login import login_user, UserMixin
from datetime import timedelta
from flask_login import login_user, UserMixin
import requests

main_routes = Blueprint('main_routes', __name__)

app = Flask(__name__)


class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email

        
firebaseConfig = {
    "apiKey": "AIzaSyDQ9Ym9NRCPiC-wLNsmg7PozMA7xedfwfA",
    "authDomain": "holygrail07-3bc90.firebaseapp.com",
    "projectId": "holygrail07-3bc90",
    "storageBucket": "holygrail07-3bc90.appspot.com",
    "messagingSenderId": "1007986562323",
    "appId": "1:1007986562323:web:5a670e323b70f710d9b6e6"
}




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
            
            print(response_data)
            
            if response.status_code == 200:
                user_id = response_data['localId']
                user = User(id=user_id, email=email)
                login_user(user, remember=keep_logged_in)

                session['userId'] = user_id

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


if __name__ == '__main__':
    app.run(debug=True)