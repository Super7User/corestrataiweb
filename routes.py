from flask import Blueprint, render_template,session, request, redirect, url_for, jsonify
from flask_login import login_required, logout_user, login_user
import pandas as pd

main_routes = Blueprint('main_routes', __name__)

# @main_routes.route('/media')
# def media():
#     return render_template('media.html')


@main_routes.route('/sampleData')
def sampleData():
    return render_template('sampleData.html')

@main_routes.route('/')
def index_dark():
    return render_template('index.html')

@main_routes.route('/about')
def about():
    return render_template('about.html')

@main_routes.route('/password')
def password_reset():
    return render_template('password.html')

@main_routes.route('/sam')
def sam():
    return render_template('sample.html')

@main_routes.route('/sam1')
def sam1():
    return render_template('sample1.html')

@main_routes.route('/title')
def title():
    return render_template('title.html')

@main_routes.route('/theme')
def theme():
    return render_template('theme.html')

@main_routes.route('/trendy')
def trendy():
    return render_template('trendy_blog_template.html')

@main_routes.route('/casual')
def casual():
    return render_template('casual_template.html')

@main_routes.route('/bold')
def bold():
    return render_template('bold_template.html')

@main_routes.route('/elegant')
def elegant():
    return render_template('elegant_template.html')

@main_routes.route('/minimalist')
def minimalist():
    return render_template('minimalist_template.html')

@main_routes.route('/formal')
def formal():
    return render_template('formal_template.html')

@main_routes.route('/vintage')
def vintage():
    return render_template('vintage_template.html')

@main_routes.route('/gif')
def index():
    user_emailId = session.get('email')
    user_plan = session.get('plan')
    return render_template('gifgeneration.html',plan=user_plan)

@main_routes.route('/newlogin')
def newlogin():
    return render_template('new_login.html')

@main_routes.route('/newblog')
def newblog():
    user_emailId = session.get('email')
    user_plan = session.get('plan')
    return render_template('new_blog.html',plan=user_plan)

@main_routes.route('/landingpage')
def landing():
    user_emailId = session.get('email')
    user_plan = session.get('plan')
    return render_template('landing_page.html',plan=user_plan)

@main_routes.route('/imageLanding')
def imageLanding():
    user_emailId = session.get('email')
    user_plan = session.get('plan')
    return render_template('image_landingPage.html',plan=user_plan)

@main_routes.route('/header')
def header():
     user_emailId = session.get('email')
     user_plan = session.get('plan')
     return render_template('header.html',plan=user_plan)



