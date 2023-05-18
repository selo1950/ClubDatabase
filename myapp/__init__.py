from flask import Flask
from flask_restful import Api
import os
from .api import main
from .models import db

def create_app():
    
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.register_blueprint(main)
    db.init_app(app)

    return(app)
    
   