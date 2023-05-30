from flask_restful import Resource, reqparse
from flask import jsonify, abort
from ..models import db, Teams, Players
from ..authorization import token_required


team_post_arguments = reqparse.RequestParser()
team_post_arguments.add_argument('name', type=str, help='Name of the team', required=True, location='json')
team_post_arguments.add_argument('coach_id', type=int, help="Id of the teams coach", required=True, location='json')

team_put_arguments = reqparse.RequestParser()
team_put_arguments.add_argument('name', type=str, help='Name of the team', location='json')
team_put_arguments.add_argument('coach_id', type=int, help="Id of the teams coach", location='json')

class Team(Resource):
    method_decorators=[token_required]

    def get(self, current_user, team_id):
        result = Teams.query.filter_by(id=team_id).first()

        if not result:
            abort(404, 'There is no team with that Id!')

        if current_user.admin:
            team_info = {}
            team_info['name'] = result.name
            team_info['coach'] = result.coach_id
            team_info['players'] =[f'{player.name} {player.surname}' for player in result.players]            
            return jsonify(team_info)
        
        else:
            abort(401, 'You are not authorized to see this info!')
        
    def post(self, current_user, team_id):

        if not current_user.admin:
            abort(401, 'Only coaches are autorized to add teams!')
        
        team = Teams.query.filter_by(id=team_id).first()
        if team:
            abort(409, 'There is already team with that ID!')
        
        args = team_post_arguments.parse_args()
        
        if current_user.head_admin:
            team = Teams(id=team_id, name=args['name'], coach_id=args['coach_id'])
            db.session.add(team)
            db.session.commit()
            team_info = {}
            team_info['name'] = team.name
            team_info['coach'] = team.coach_id          
            return jsonify(team_info)
        
        else:
            team = Teams(id=team_id, name=args['name'], coach_id=current_user.id)
            db.session.add(team)
            db.session.commit()
            team_info = {}
            team_info['name'] = team.name
            team_info['coach'] = team.coach_id
            return jsonify(team_info) 
        
    def put(self, current_user, team_id):

        if not current_user.admin:
            abort(401, 'Only coaches are allowed to change team info!')

        result = Teams.query.filter_by(id=team_id).first()

        if not result:
            abort(404, 'There is no team with given ID!')
        
        args = team_put_arguments.parse_args()
        if current_user.head_admin:
            if args['name']:
                result.name = args['name']
            if args['coach_id']:
                result.coach_id = args['coach_id']
            db.session.add(result)
            db.session.commit()
            team_info = {}
            team_info['name'] = result.name
            team_info['coach'] = result.coach_id
            team_info['players'] = [player.as_dict() for player in result.players]
            return jsonify(team_info) 
        
        else:
            if not current_user.id == result.coach_id:
                abort(401, 'You can only make changes on your own team!')
            if args['name']:
                result.name = args['name']
            db.session.add(result)
            db.session.commit()
            team_info = {}
            team_info['name'] = result.name
            team_info['coach'] = result.coach_id
            team_info['players'] = [player.as_dict() for player in result.players]
            return jsonify(team_info) 

    def delete(self, current_user, team_id):

        if not current_user.head_admin:
            abort(401, 'You are not authorized for this action!')
        
        result = Teams.query.filter_by(id = team_id).first()
        if not result:
            abort(404, 'There is no team with that Id!')

        db.session.delete(result)
        db.session.commit()
        return jsonify({'message' : 'Team deleted'})

add_team_players_arguments = reqparse.RequestParser()
add_team_players_arguments.add_argument('player_id', type=int, help='Id of the wanted player', required=True, location='json')

class TeamPlayers(Resource):
    method_decorators=[token_required]

    def get(self, current_user, team_id):
        team = Teams.query.filter_by(id=team_id).first()
        if not team:
            abort(404, 'There is no team with that ID!')
        
        elif current_user.admin:
            info = {}
            info['name'] = team.name
            info['coach'] = team.coach_id
            info['players'] = []
            for player in team.players:
                player_info = f'{player.name} {player.surname}, {player.month_of_birth}/{player.year_of_birth}'
                info['players'].append(player_info)
            return jsonify(info)
        
        else:
            abort(401, 'You are not authorized to see this info!')

    def put(self, current_user, team_id):
        
        if not current_user.admin:
            abort(401, 'Only coaches can add players to team!')
        
        args = add_team_players_arguments.parse_args()
        team = Teams.query.filter_by(id=team_id).first()
        if not team:
            abort(404, 'There is no team with that Id!')
        
        player = Players.query.filter_by(id=args['player_id']).first()
        if not player:
            abort(404, 'There is no player with that ID!')
        
        if current_user.head_admin:
            player.team_id = team_id
            player.coach_id = team.coach_id
            db.session.add(player)
            db.session.commit()
            info = {}
            info['name'] = team.name
            info['player_added'] = player.id
            return jsonify(info)
        else:
            if not player in current_user.players:
                abort(401, 'You can only change teams of your own players!')

            player.team_id = team_id
            player.coach_id = team.coach_id
            db.session.add(player)
            db.session.commit()
            info = {}
            info['name'] = team.name
            info['player_added'] = player.id
            return jsonify(info)
        

class TeamSessions(Resource):
    method_decorators = [token_required]

    def get(self, current_user, team_id):
        team = Teams.query.filter_by(id=team_id).first()
        if not team:
            abort(404, 'There is no team with given ID!')

        if current_user.head_admin or team.coach_id == current_user.id:     
            output = {}
            output['team'] = team.name
            output['sessions'] =[f'num:{session.id}, date:{session.date}, description:{session.description}' for session in team.sessions]
            return jsonify(output)
        
        else:
            abort(401, 'You are not authorized to see this info')
        

class AllTeams(Resource):
    method_decorators = [token_required]

    def get(self, current_user):
        
        if not current_user.admin:
            abort(401, 'You are not authorized for this action!')
        
        teams = Teams.query.all()
        for team in teams:
            team_info = {}
            team_info['name'] = team.name
            team_info['coach_id'] = team.coach_id

        return jsonify({'info': team_info})
    



    
            

            
        

            
            






