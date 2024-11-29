from flask import Flask ,render_template, request, jsonify,session, url_for, redirect
from flask_mail import Mail
from flask_login import login_required, current_user
from auth import login_manager, auth_blueprint 
from tool import tools_blueprint
from firebase_admin import credentials
from routes import main_routes
from image import image_blueprint
from payment import stripe_blueprint
from media import media_blueprint
import logging
from firebase_admin import credentials
import requests
import redis
import holygrailutils

app = Flask(__name__)


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
redis_client = redis.Redis(host='localhost', port=6379, db=0)
redis_client = holygrailutils.get_redis_client()

 
# firebase_admin.initialize_app(cred,{
#     'databaseURL': 'https://holygrail07-default-rtdb.firebaseio.com/'
# })

# firebase_db = firestore.client()
# ref = db.reference('/')

@app.route('/pricingModal')
def pricing_modal():
    user_id = current_user.get_id()

    current_plan = redis_client.hget(user_id, "plan")
    print(current_plan,"plannnn")

    if current_plan:
        current_plan = current_plan.decode('utf-8')

    app.logger.info(f"Current plan for user {user_id}: {current_plan}")
    
    return render_template('pricingModal.html', current_plan=current_plan)



@app.route('/create-checkout', methods=['POST'])
def create_checkout_session():
    price_id = request.form.get('price_id')
    connected_account_id = request.form.get('connected_account_id')

    session['plan'] = 'personal' if price_id == 'price_0000' else 'other'
    user_id = current_user.get_id()
    current_plan = redis_client.hget(user_id, "plan")
    print(current_plan,"plannnn")

    return redirect(url_for('pricingModal'),current_plan=current_plan) 


login_manager.init_app(app)
login_manager.login_view = 'login'


app.register_blueprint(auth_blueprint)
app.register_blueprint(tools_blueprint)
app.register_blueprint(main_routes)
app.register_blueprint(image_blueprint)
app.register_blueprint(stripe_blueprint)
app.register_blueprint(media_blueprint)

if __name__ == "__main__":
    app.run(debug=True)