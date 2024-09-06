# auth/__init__.py

from flask import Blueprint
from flask_login import LoginManager

# Initialize the login manager
login_manager = LoginManager()

# Create the auth blueprint
auth_blueprint = Blueprint('auth_blueprint', __name__)

# Import the routes from auth.py so they are registered with the blueprint
from . import routes

# You could also set the login view here if needed
login_manager.login_view = 'auth_blueprint.login'
