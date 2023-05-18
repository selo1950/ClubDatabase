from .models import db, Player, Coach
from flask_restful import reqparse, fields, marshal_with, abort, Resource
from flask_sqlalchemy import SQLAlchemy

coach_post_args = reqparse.RequestParser()
coach_post_args.add_argument('name', type = str, help = 'Players name', required = True)
coach_post_args.add_argument('surname', type = str, help = 'Players surname', required = True)


coach_update_args = reqparse.RequestParser()
coach_update_args.add_argument('name', type = str, help = 'Players name')
coach_update_args.add_argument('surname', type = str, help = 'Players surname')


resource_fields_coach = {
    'id' : fields.Integer,
    'name': fields.String,
    'surname': fields.String,
    'players': fields.List(fields.String)
}

class Coaches(Resource):
    
    @marshal_with(resource_fields_coach)
    def get(self,coach_id):
        result = Coach.query.filter_by(id = coach_id).first()
        return result
    
    @marshal_with(resource_fields_coach)
    def put(self,coach_id):
        args = coach_post_args.parse_args()
        result = Coach.query.filter_by(id =coach_id).first()
        if result:
            abort(409, message = 'Coach ID taken')
        
        player = Player(id =coach_id,  name = args['name'], surname = args['surname'], year_of_birth = args['year_of_birth'], month_of_birth = args['month_of_birth'], coach_id = args['coach_id'])
        db.session.add(player)
        db.session.commit()
        return player
    
    @marshal_with(resource_fields_coach)
    def patch(self,coach_id):
        args = coach_update_args.parse_args()
        result = Coach.query.filter_by(id =coach_id).first()
        if not result:
            abort(message = 'Coach does not exist')
        if args['name']:
            result.name = args['name']
        if args['surname']:
            result.surname = args['surname']
        db.session.add(result)
        db.session.commit()
        return result
    
    def delete(self,coach_id):
        delete_coach = Coach.query.filter_by(id =coach_id).first()
        db.session.delete(delete_coach)
        db.session.commit()
        return '{message : deleted}'
    
#args parser za provjeru i izvlačenje podataka iz requesta
player_post_args = reqparse.RequestParser()
player_post_args.add_argument('name', type = str, help = 'Players name', required = True)
player_post_args.add_argument('surname', type = str, help = 'Players surname', required = True)
player_post_args.add_argument('year_of_birth', type = int, help = 'Players birth year', required = True)
player_post_args.add_argument('month_of_birth', type = int, help = 'Payers birth month', required = True)
player_post_args.add_argument('coach_id', type = int, help = 'ID num of players coach', required = True)

player_update_args = reqparse.RequestParser()
player_update_args.add_argument('name', type = str, help = 'Players name')
player_update_args.add_argument('surname', type = str, help = 'Players surname')
player_update_args.add_argument('year_of_birth', type = int, help = 'Players birth year')
player_update_args.add_argument('month_of_birth', type = int, help = 'Payers birth month')
player_update_args.add_argument('coach_id', type = int, help = 'ID num of players coach')

resource_fields_player = {
    'id' : fields.Integer,
    'name': fields.String,
    'surname': fields.String,
    'year_of_birth' : fields.Integer,
    'month_of_birth' : fields.Integer,
    'coach_id': fields.Integer
}

class Players(Resource):
    
    @marshal_with(resource_fields_player)
    def get(self,player_id):
        result = Player.query.filter_by(id = player_id).first()
        if not result:
            abort(404, message = 'There is no player with that ID')
        return result
    
    @marshal_with(resource_fields_player)
    def put(self,player_id):
        args = player_post_args.parse_args()
        result = Player.query.filter_by(id = player_id).first()
        if result:
            abort(409, message = 'Player ID taken')
        
        player = Player(id = player_id,  name = args['name'], surname = args['surname'], year_of_birth = args['year_of_birth'], month_of_birth = args['month_of_birth'], coach_id = args['coach_id'])
        db.session.add(player)
        db.session.commit()
        return player
    
    @marshal_with(resource_fields_player)
    def patch(self, player_id):
        args = player_update_args.parse_args()
        result = Player.query.filter_by(id = player_id).first()
        if not result:
            abort(message = 'Player does not exist')
        if args['name']:
            result.name = args['name']
        if args['surname']:
            result.surname = args['surname']
        if args['year_of_birth']:
            result.year_of_birth = args['year_of_birth']
        if args['month_of_birth']:
            result.month_of_birth = args['month_of_birth']
        if args['coach_id']:
            result.coach_id = args['coach_id']
        db.session.add(result)
        db.session.commit()
        return result
    
    def delete(self,player_id):
        delete_player = Player.query.filter_by(id = player_id).first()
        db.session.delete(delete_player)
        db.session.commit()
        return '{message : deleted}'