from flask import Flask ,render_template, request, jsonify
from flask_mail import Mail
from auth import login_manager, auth_blueprint  # Absolute import
from tool import tools_blueprint
from firebase_admin import credentials
from routes import main_routes
from image import image_blueprint
from payment import stripe_blueprint
from media import media_blueprint
import logging
from firebase_admin import credentials
import requests

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

PEXELS_API_KEY = 'PqAQtx1BrCZMtcFOPcufLNW0OE6jXkMd2lUPFl2Ck4g4K1cvRdGC3qme'
PEXELS_VIDEO_API_BASE = "https://api.pexels.com/videos/videos/"


# Function to fetch photos from Pexels API
def fetch_photos(query, per_page=1):
    url = f"https://api.pexels.com/v1/search?query={query}&per_page={per_page}"
    headers = {
        "Authorization": PEXELS_API_KEY
    }
    response = requests.get(url, headers=headers)
    return response.json()

@app.route('/photoPexels')
def photoPexels():
    return render_template('photoPexels.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    data = fetch_photos(query)
    return jsonify(data)

# PEXELS_VIDEO_API = "https://api.pexels.com/videos/search"

@app.route('/videoPexels')
def videoPexels():
    return render_template('videoPexels.html')

# @app.route('/get_video')
# def get_video():
#     query = request.args.get('query', 'nature')  # Default to 'nature' if no query is provided
#     headers = {
#         'Authorization': PEXELS_API_KEY
#     }
#     params = {
#         'query': query,
#         'per_page': 1
#     }
#     response = requests.get(PEXELS_VIDEO_API, headers=headers, params=params)
#     if response.status_code == 200 and response.json()['videos']:
#         video_data = response.json()['videos'][0]
#         return jsonify({
#             'video_url': video_data['video_files'][0]['link'],  # SD quality link
#             'author_name': video_data['user']['name'],
#             'author_url': video_data['user']['url']
#         })
#     return jsonify({'error': 'No video found for the given query'}), 404

@app.route('/get_video', methods=['POST'])
def get_video():
    video_id = request.json.get('video_id')
    if not video_id:
        return jsonify({'error': 'No video ID provided'}), 400

    headers = {
        'Authorization': PEXELS_API_KEY
    }
    # Fetch video details using the provided video ID
    response = requests.get(f"{PEXELS_VIDEO_API_BASE}{video_id}", headers=headers)
    if response.status_code == 200:
        video_data = response.json()
        return jsonify({
            'video_url': video_data['video_files'][0]['link'],  # SD/HD video link
            'author_name': video_data['user']['name'],
            'author_url': video_data['user']['url'],
            'thumbnails': [picture['picture'] for picture in video_data['video_pictures']]
        })
    return jsonify({'error': 'Unable to fetch video data'}), 404


def get_videos(n):
    url = f"https://api.pexels.com/videos/popular?per_page={n}"
    headers = {
        "Authorization": PEXELS_API_KEY
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('videos', [])
    else:
        return []
    

def get_images(n):
    url = f"https://api.pexels.com/v1/curated?per_page={n}"
    headers = {
        "Authorization": PEXELS_API_KEY
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('photos', [])
    else:
        return []   

@app.route('/media')
def media():
    n = 25  # Number of videos to display, you can modify this as per your need
    videos = get_videos(n)
    images = get_images(n)
    return render_template('media.html', videos=videos, images=images)


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
