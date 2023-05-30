from datetime import datetime
from flask_restful import Resource, reqparse
from flask import abort, jsonify
from ..models import Trainings, Teams, db, Players, PlayerSessionAssociation
from ..authorization import token_required


add_session_arguments = reqparse.RequestParser()
add_session_arguments.add_argument('team_id', type=int, help='Team ID', required=True, location='json')
add_session_arguments.add_argument('description',type=str, help='Session description', required=True, location='json')
add_session_arguments.add_argument('date', help='Date of the session', required=True, location='json')

put_session_arguments = reqparse.RequestParser()
put_session_arguments.add_argument('team_id', type=int, help='Team ID', location='json')
put_session_arguments.add_argument('description',type=str, help='Session description', location='json')


class Training(Resource):
    method_decorators = [token_required]

    def get(self, current_user, session_id):

        if not current_user.admin:
            abort(401, 'You are not authorized for this action!')

        session = Trainings.query.filter_by(id=session_id).first()
        if not session:
            abort(404, 'There is no session with that ID!')
        
        elif current_user.head_admin or session.coach_id == current_user.id:
            session_info = {}
            session_info['team'] = session.team_id
            session_info['coach'] = session.coach_id
            session_info['players'] = [player.to_dict() for player in session.players]
            session_info['description'] = session.description
            session_info['date'] = session.date
            return jsonify(session_info)
    
        
        else:
            abort(401, 'You can only see your own sessions!')

    def post(self, current_user, session_id):

        if not current_user.admin:
            abort(401, 'You are not authorized for this action!')
        
        session = Trainings.query.filter_by(id=session_id).first()
        if session:
            abort(409, 'There is already session with that ID!')

        args = add_session_arguments.parse_args()
        team = Teams.query.filter_by(id=args['team_id']).first()
        if not team:
            abort(404, 'There is no team with that ID!')
        elif not team in current_user.teams:
            abort(401, 'You can only add session for your own team!')
        
        datetime_object = datetime.strptime(args['date'], '%d-%m-%y')
        session = Trainings(id=session_id, team_id=args['team_id'], coach_id=current_user.id, date=datetime_object.date(), description=args['description'])
        db.session.add(session)
        db.session.commit()
        session_info = {}
        session_info['team'] = session.team_id
        session_info['coach'] = session.coach_id
        session_info['players'] = [player.to_dict() for player in session.players]
        session_info['description'] = session.description
        session_info['date'] = session.date
        return jsonify(session_info)
    
    def put(self, current_user, session_id):

        if not current_user.admin:
            abort(401, 'You are not authorized for this action!')
        
        session = Trainings.query.filter_by(id=session_id).first()
        if not session:
            abort(404, 'There is no session with that ID!')

        args = put_session_arguments.parse_args()
        team = Teams.query.filter_by(id=args['team_id']).first()
        if not session.coach_id == current_user.id:
            abort(401, 'You can only change session for your own team!')

        if args['team_id']:
            session.team_id = args['team_id']
        if args['description']:
            session.description = args['description']
        db.session.add(session)
        db.session.commit()
        session_info = {}
        session_info['team'] = session.team_id
        session_info['coach'] = session.coach_id
        session_info['players'] = [f'{player.name} {player.surname}' for player in session.players]
        session_info['description'] = session.description
        session_info['date'] = session.date
        return jsonify(session_info)
    
    def delete(self, current_user, session_id):
        session = Trainings.query.filter_by(id=session_id).first()
        if not session:
            abort(404, 'There is no session with given ID!')

        elif not current_user.admin or not session.coach_id == current_user.id:
            abort(401, 'You are not authorized for this action!')
        
        db.session.delete(session)
        db.session.commit()
        return jsonify({'message':'deleted'})

add_session_player_args = reqparse.RequestParser()
add_session_player_args.add_argument('player_id', type=int, help='Player ID', required=True, location='json')  

class SessionPlayers(Resource):
    method_decorators=[token_required]

    def get(self, current_user, session_id):

        if not current_user.admin:
            abort(401, 'Only coaches can seet this info!')
        
        session = Trainings.query.filter_by(id=session_id).first()
        if not session:
            abort(404, 'There is no session with given ID!')

        elif current_user.head_admin or current_user.id == session.coach_id:
            output = {}
            output['session_id'] = session.id
            output['date'] = session.date
            output['team'] = session.team_id
            output['players'] = [{
                'name':player.name + ' ' + player.surname,
            } for player in session.players]
            return jsonify(output)
        
        else:
            abort(401, 'You can only see your own sessions!')

    def post(self, current_user, session_id):
        session = Trainings.query.filter_by(id=session_id).first()
        if not session:
            abort(404, 'There is no session with given ID!')

        elif current_user.admin and session.coach_id == current_user.id:
            args = add_session_player_args.parse_args()
            player = Players.query.filter_by(id=args['player_id']).first()
            if not player:
                abort(404, 'There is no player with that ID!')

            elif not player in current_user.players:
                abort(401, 'You can only add your own players to the session!')

            output = {}
            output['session_id'] = session.id
            output['date'] = session.date
            output['team_id'] = session.team_id
            output['players'] = [f'{player.name} {player.surname}' for player in session.players]
            
            player_session = PlayerSessionAssociation(player=player.id, session=session.id)
            db.session.add(player_session)
            db.session.commit()
            return jsonify(output)
        
        else:
            abort(401, 'You are not authorized for this action!')


class AllSession(Resource):
    method_decorators = [token_required]

    def get(self, current_user):

        if not current_user.head_admin:
            abort(401, 'You are not allowed to see this info!')
        
        output = []
        sessions = Trainings.query.all()
        
        for session in sessions:
            info = {}
            info['session_id'] = session.id
            info['date'] = session.date
            info['session_coach'] = session.coach_id
            info['session_team'] = session.team_id
            info['description'] = session.description
            output.append(info)
        
        return jsonify({'sessions': output})
            

        

        

       
       
        
    
        
        
        

        
        
    


        
