from flask import Flask,Blueprint ,render_template, request, jsonify
from flask_login import LoginManager
import requests
import logging


login_manager = LoginManager()

media_blueprint = Blueprint('media_blueprint', __name__)


PEXELS_API_KEY = 'PqAQtx1BrCZMtcFOPcufLNW0OE6jXkMd2lUPFl2Ck4g4K1cvRdGC3qme'
PEXELS_VIDEO_API_BASE = "https://api.pexels.com/videos/videos/"


def fetch_photos(query, per_page=1):
    url = f"https://api.pexels.com/v1/search?query={query}&per_page={per_page}"
    headers = {
        "Authorization": PEXELS_API_KEY
    }
    response = requests.get(url, headers=headers)
    print(response,url)
    return response.json()

@media_blueprint.route('/photoPexels')
def photoPexels():
    return render_template('photoPexels.html')

@media_blueprint.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    data = fetch_photos(query)
    return jsonify(data)

# PEXELS_VIDEO_API = "https://api.pexels.com/videos/search"

@media_blueprint.route('/videoPexels')
def videoPexels():
    return render_template('videoPexels.html')

# @media_blueprint.route('/get_video')
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

@media_blueprint.route('/get_video', methods=['POST'])
def get_video():
    video_id = request.json.get('video_id')
    if not video_id:
        return jsonify({'error': 'No video ID provided'}), 400
    
    query = request.json.get('query', '')  
    orientation = request.json.get('orientation', 'landscape')  
    per_page = request.json.get('per_page', 10) 
    page = request.json.get('page', 1) 

    params = {
        "query": query,
        "orientation": orientation,
        "per_page": per_page,
        "page": page
    }

    headers = {
        'Authorization': PEXELS_API_KEY
    }
    
   
    # response = requests.get(url, headers=headers, params=params)
    
    response = requests.get(f"{PEXELS_VIDEO_API_BASE}{video_id}", headers=headers,params=params)
    print(response)
    if response.status_code == 200:
        video_data = response.json()
        return jsonify({
            'video_url': video_data['video_files'][0]['link'],  
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
    print(response)
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
    print(response)
    if response.status_code == 200:
        return response.json().get('photos', [])
    else:
        return []   

@media_blueprint.route('/media')
def media():
    n = 25 
    videos = get_videos(n)
    images = get_images(n)
    print(videos,images,"video")
    return render_template('media.html', videos=videos, images=images)


logging.basicConfig(level=logging.DEBUG)
