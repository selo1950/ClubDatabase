from flask_restful import reqparse, fields, marshal_with, Resource
import uuid
from werkzeug.security import generate_password_hash
from flask import jsonify, abort
from ..authorization import token_required
from ..models import db, Coaches, Teams, MembershipPayments



coach_post_args = reqparse.RequestParser()
coach_post_args.add_argument('name', type=str, help='Coach name', required=True)
coach_post_args.add_argument('surname', type=str, help='Coach surname', required=True)
coach_post_args.add_argument('password', type=str, help='account password', required=True, location='json')
coach_post_args.add_argument('head_admin', type=bool, location='json')
coach_post_args.add_argument('admin', type=bool, location='json')

coach_update_args = reqparse.RequestParser()
coach_update_args.add_argument('name', type=str, help='Coach name')
coach_update_args.add_argument('surname', type=str, help='Coach surname')
coach_update_args.add_argument('password', type=str, help='account password', location='json')
coach_update_args.add_argument('head_admin', type=bool, location='json')
coach_update_args.add_argument('admin', type=bool, location='json')

resource_fields_coach = {
    'id' : fields.Integer,
    'name': fields.String,
    'surname': fields.String,
    'teams': fields.List(fields.String)
}


class Coach(Resource):
    method_decorators = [token_required]
    
    @marshal_with(resource_fields_coach)
    def get(self, current_user, coach_id):

        if current_user.admin:
            result = Coaches.query.filter_by(id=coach_id).first()

            if not result:
                abort (404,'There is no coach with that ID')

            return result
        
        else:
            abort(401,'You are not authorized for this action')
    
    @marshal_with(resource_fields_coach)
    def post(self,current_user, coach_id):
        if not current_user.head_admin:
            abort(401,'You are not authorized for this action')
        result = Coaches.query.filter_by(id =coach_id).first()

        if result:
            abort(409,'Coach ID taken')
        args = coach_post_args.parse_args()
                   
        hashed_password = generate_password_hash(args['password'])
        coach = Coaches(id = coach_id, public_id=str(uuid.uuid4()), name=args['name'], surname=args['surname'], username=(args['name'].lower()+ args['surname'].lower()), password=hashed_password, admin=args['admin'], head_admin=args['head_admin'])

        db.session.add(coach)
        db.session.commit()
        return coach
       
    @marshal_with(resource_fields_coach)
    def put(self, current_user, coach_id):

        if current_user.head_admin:
            args = coach_update_args.parse_args()
            result = Coaches.query.filter_by(id=coach_id).first()

            if not result:
                abort(404,'There is no coach with given ID!')

            if args['name']:
               result.name = args['name']
            if args['surname']:
                result.surname = args['surname']
            if args['head_admin']:
                result.head_admin = args['head_admin']
            if args['admin']:
                result.admin = args['admin']

            db.session.add(result)
            db.session.commit()
            return result

        else:
            abort(401,'You are not authorized for this action')
    
    def delete(self, current_user, coach_id ):

        if current_user.head_admin: 
            delete_coach = Coaches.query.filter_by(id =coach_id).first()
            if not delete_coach:
                abort(404,'There is no coach with given ID!')

            db.session.delete(delete_coach)
            db.session.commit()
            return '{message : deleted}'
        
        else:
            abort(401,'You are not authorized for this action')


resource_fields_get_player = {
    'id':fields.Integer,
    'surname':fields.String,
    'players':fields.List(fields.String)
}


class CoachAllPlayers(Resource):
    method_decorators=[token_required]

    @marshal_with(resource_fields_get_player)
    def get(self, current_user, coach_id):

        if current_user.head_admin:
            result = Coaches.query.filter_by(id=coach_id).first()
            if not result:
                abort(404, 'There is no coach with given ID!')
            return result
        
        elif current_user.admin:
            result = Coaches.query.filter_by(id=current_user.id).first()
            
            return result
        
        else:
            abort(401,'You are not authorized for this action')


coach_teams_argument = reqparse.RequestParser()
coach_teams_argument.add_argument('team_id', type=int, help='Id of the team', required=True, location='json')


class CoachTeams(Resource):
    method_decorators=[token_required]

    def get(self, current_user, coach_id):

        if not current_user.admin:
            abort(401,'You are not authorized to see this info!')
        
        result = Coaches.query.filter_by(id=coach_id).first()

        if not result:
            abort(404,'There is no coach with given ID')

        return jsonify({
            'name' : f'{result.name} {result.surname}',
            'teams': [team.name for team in result.teams]})
    

    def put(self, current_user, coach_id):

        if not current_user.head_admin:
            abort(401, 'Only head admin can change teams!')

        result = Coaches.query.filter_by(id=coach_id).first()

        if not result:
            abort(404,'There is no coach with given ID')
        
        args = coach_teams_argument.parse_args()
        team = Teams.query.filter_by(id=args['team_id']).first()

        if not team:
            abort(404,'There is no team with that ID')

        team.coach_id =coach_id
        for player in team.players:
            player.coach_id = team.coach_id
            db.session.add(player)
            
        db.session.add(team)
        db.session.commit()
        return jsonify({'team': team.name,
                        'new coach' : team.coach_id })
        

class CoachMembership(Resource):
    method_decorators = [token_required]

    def get(self, current_user, coach_id):

        if not current_user.admin:
            abort(401,'Only coaches can see this info!')
        
        coach = Coaches.query.filter_by(id=coach_id).first()
        
        if not coach:
            abort(404,'There is no coach with given ID!')
        
        output = {}
        if current_user.head_admin or current_user.id == coach.id:
            payments = MembershipPayments.query.filter_by(coach_id=coach_id)
            for payment in payments:
                output['payment num'] = payment.id
                output['player_id'] = payment.player_id
                output['month/year'] = str(payment.month) + '/' + str(payment.year)
                output['paid on'] = payment.date_of_payment
                           
            return jsonify({'coach': coach.name + ' ' + coach.surname,
                            'payments':output})
        
        else:
            abort(401, 'You can only see payments for your own players!')


class CoachSessions(Resource):
    method_decorators = [token_required]

    def get(self, current_user, coach_id):

        if not current_user.admin:
            abort(401,'You are not authorized to see this info')
            
        coach = Coaches.query.filter_by(id=coach_id).first()
        if not coach:
            abort(404,'There is no coach with given ID!')
        
        output = {}
        output['coach'] = coach.name + ' ' + coach.surname
        output['sessions'] = [f'num:{session.id}, date:{session.date}, team:{session.team_id}, description:{session.description}' for session in coach.sessions]
    
        return jsonify(output)


class AllPayments(Resource):
    method_decorators = [token_required]

    def get(self, current_user):

        if not current_user.head_admin:
            abort(401,'You are not authorized for this info!')

        output = []
        payments = MembershipPayments.query.all()
        for payment in payments:
            payment_info = {}
            payment_info['id'] = payment.id
            payment_info['player_id'] = payment.player_id
            payment_info['coach_id'] = payment.coach_id
            payment_info['paid_for'] = str(payment.month) + '/' + str(payment.year)
            payment_info['paid_on'] = payment.date_of_payment
            output.append(payment_info)
        
        return jsonify({'payments':output})


class AllCoaches(Resource):
    method_decorators=[token_required]
    
    def get(self, current_user):

        if not current_user.head_admin:
            abort(401,'You are not authorized for this action')

        coaches = Coaches.query.all()
        output=[]
        
        for coach in coaches:
            coach_info={}
            coach_info['full_name']=(coach.name + ' ' + coach.surname)
            coach_info['birth_date']=coach.id
            output.append(coach_info)
        
        return jsonify({'coaches': output})

    

        


                

        

          


