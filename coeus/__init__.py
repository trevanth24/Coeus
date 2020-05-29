import os
import secrets
import random
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from coeus.config import Config
import googlemaps

# template_dir = os.path.abspath('./templates')

# #Secrets.token_hex(16) to generate a secret key
# SECRET_KEY = secrets.token_hex(16)
db = SQLAlchemy() #created a database
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login' #this line of code talks to routes and i
login_manager.login_message_category = 'info'
mail = Mail()
gmaps = googlemaps.Client(key='AIzaSyBklQLjM95vzJ7HRX0Z-5Eq2pQc5SEBbU8')




def create_app(config_class = Config):
    #We dont want the extentions to be moved into this funtion (but still need to be intialized)
    #This is so the extention object does not tied for one app

    app = Flask(__name__)
    app.config.from_object(Config)

    from coeus.users.routes import users #users is the instance of the blueprint
    from coeus.posts.routes import posts
    from coeus.main.routes import main
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    return app

