from flask import Flask, request
from flask_restful import Api,Resource, reqparse, abort, fields, marshal_with
import json
import datetime
from models import db, Player, Coach
from resources import Coaches, Players
import os


app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.app_context().push()
db.init_app(app)
#db.create_all()


api.add_resource(Players, '/players/<int:player_id>')
api.add_resource(Coaches, '/coaches/<int:coach_id>')

if __name__  == '__main__':
    
    app.run(debug=True)



#$env:DATABASE_URL='postgres://clubdatabase_user:NQdcNkMwGGqAGxIkCAHT7Arnjjl4n6SH@dpg-chitk23hp8ufsbla8r3g-a.frankfurt-postgres.render.com/clubdatabase'