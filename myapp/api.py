from flask import Flask, request, Blueprint
from flask_restful import Api,Resource, reqparse, abort, fields, marshal_with
import json
import datetime
from .models import db, Player, Coach
from .resources import Coaches, Players
import os



main = Blueprint('main', __name__)
#main.app_context().push()
#db.init_app(main)
#db.create_all()
api = Api(main)

@main.route('/')
def home():
    return {'message': 'Welcome to club database manager'}

api.add_resource(Players, '/players/<int:player_id>')
api.add_resource(Coaches, '/coaches/<int:coach_id>')




#$env:DATABASE_URL='postgres://clubdatabase_user:NQdcNkMwGGqAGxIkCAHT7Arnjjl4n6SH@dpg-chitk23hp8ufsbla8r3g-a.frankfurt-postgres.render.com/clubdatabase'