from flask import Flask
from flask_mail import Mail
from auth import login_manager, auth_blueprint  # Absolute import
from tool import tools_blueprint
from firebase_admin import credentials
from routes import main_routes
from image import image_blueprint
import firebase_admin
import logging
from firebase_admin import credentials, auth, db,firestore

app = Flask(__name__)

# Flask app configurations
app.secret_key = 'your_secret_key'
app.config['MAIL_SERVER'] = 'smtp.example.com'  
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'dhanapooja1211@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-email-password'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEBUG'] = True

mail = Mail(app)

cred = credentials.Certificate("serviceAccountKey.json")

logging.basicConfig(level=logging.DEBUG)
 
# firebase_admin.initialize_app(cred,{
#     'databaseURL': 'https://holygrail07-default-rtdb.firebaseio.com/'
# })

# firebase_db = firestore.client()
# ref = db.reference('/')


login_manager.init_app(app)
login_manager.login_view = 'login'



app.register_blueprint(auth_blueprint)
app.register_blueprint(tools_blueprint)
app.register_blueprint(main_routes)
app.register_blueprint(image_blueprint)

if __name__ == "__main__":
    app.run(debug=True)
