from datetime import datetime
from flask_restful import reqparse, fields, marshal_with, Resource
from flask import jsonify, abort
import uuid
from werkzeug.security import generate_password_hash
from ..models import db, Players, MembershipPayments, Teams
from ..authorization import token_required
    
#args parser za provjeru i izvlačenje podataka iz requesta
player_post_args = reqparse.RequestParser()
player_post_args.add_argument('name', type= str, help='Players name', required=True, location='json')
player_post_args.add_argument('surname', type=str, help='Players surname', required=True, location='json')
player_post_args.add_argument('year_of_birth', type=int, help='Players birth year', required=True,location='json')
player_post_args.add_argument('month_of_birth', type=int, help='Payers birth month', required=True, location='json')
player_post_args.add_argument('coach_id', type=int, help='ID num of players coach', location='json')
player_post_args.add_argument('password', type=str, help='account password', required=True, location='json')
player_post_args.add_argument('team_id', type=int, help='Team Id', required=True, location='json')

player_update_args = reqparse.RequestParser()
player_update_args.add_argument('name', type=str, help='Players name', location='json')
player_update_args.add_argument('surname', type=str, help='Players surname', location='json')
player_update_args.add_argument('year_of_birth', type=int, help='Players birth year', location='json')
player_update_args.add_argument('month_of_birth', type=int, help='Payers birth month', location='json')
player_update_args.add_argument('coach_id', type=int, help='ID num of players coach', location='json')
player_update_args.add_argument('password', type=str, help ='account password', location ='json')

resource_fields_player = {
    'id' : fields.Integer,
    'name': fields.String,
    'surname': fields.String,
    'year_of_birth' : fields.Integer,
    'month_of_birth' : fields.Integer,
    'coach_id': fields.Integer
}


class Player(Resource):
    method_decorators = [token_required]
 
    @marshal_with(resource_fields_player)
    def get(self, current_user, player_id):
        result = Players.query.filter_by(id=player_id).first()
        if not result:
            abort(404, 'There is no player with that ID')

        elif current_user.admin:
            return result

        elif not current_user.admin:
            result = Players.query.filter_by(id=current_user.id).first()
            return result

    @marshal_with(resource_fields_player)
    def post(self, current_user, player_id):
        if not current_user.admin:
            abort(401, 'You are not authorized for this action!')

        result = Players.query.filter_by(id=player_id).first()
        if result:
            abort(409, 'Player ID taken') 

        args = player_post_args.parse_args()
        
        team = Teams.query.filter_by(id = args['team_id']).first()

        if not team:
            abort(404, 'There is no team with given ID!')

        hashed_password = generate_password_hash(args['password'])
        
        if current_user.head_admin:
            player = Players(public_id=str(uuid.uuid4()), id=player_id, name=args['name'], surname=args['surname'], year_of_birth=args['year_of_birth'], month_of_birth=args['month_of_birth'], coach_id=team.coach_id, team_id=args['team_id'], username=(args['name'].lower()+args['surname'].lower()), password=hashed_password)
            db.session.add(player)
            db.session.commit()
            return player
        
        elif current_user.admin:

            if not current_user.id == team.coach_id:
                abort(401, 'You can only add players to your own team!')

            player = Players(public_id=str(uuid.uuid4()), id=player_id, name=args['name'], surname=args['surname'], year_of_birth=args['year_of_birth'], month_of_birth=args['month_of_birth'], coach_id=current_user.id, team_id=args['team_id'], username=(args['name'].lower()+args['surname'].lower()), password=hashed_password)
            db.session.add(player)
            db.session.commit()
            return player
               
    @marshal_with(resource_fields_player)
    def put(self, current_user, player_id):
        
        if not current_user.admin:
            abort(401, 'You are not authorized for this action!')

        args = player_update_args.parse_args()
        result = Players.query.filter_by(id=player_id).first()

        if not result:
            abort(404, 'There is no player with given ID!')
        if current_user.head_admin:
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
        
        elif current_user.admin:
            if result in current_user.players:
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
        
            else:
                abort(401, 'You are not authorized for this action!')
                
    def delete(self, current_user, player_id):

        if not current_user.admin:
            abort(401, 'You are not authorized for this action!')

        delete_player = Players.query.filter_by(id=player_id).first()
        if not delete_player:
            abort(404, 'There is no player with given ID!')

        if current_user.head_admin:
            db.session.delete(delete_player)
            db.session.commit()
            return '{message : deleted}'
        
        elif current_user.admin:
            if delete_player in current_user.players:
                db.session.delete(delete_player)
                db.session.commit()
                return '{message : deleted}'
            
            else:
                abort(401, 'You are not authorized for this action!')


resource_player_membership = {
    'id':fields.Integer,
    'name': fields.String,
    'surname': fields.String,
    'memberships': fields.List(fields.String)
}   


class PlayerMembership(Resource):
    method_decorators=[token_required]

    @marshal_with(resource_player_membership)
    def get(self, current_user, player_id):

        if current_user.head_admin:
            player = Players.query.filter_by(id=player_id).first()

            if not player:
                abort(404, 'There is no player with that ID')

            return player
        
        elif current_user.admin:
            player = Players.query.filter_by(id=player_id).first()

            if not player:
                abort(404, 'There is no player with that ID')
            
            elif player in current_user.players:
                return player
            
            else:
                abort(401, 'You can only see payments of your own players!')

        else:
            player = Players.query.filter_by(id=current_user.id).first()
            return player


player_paid_membership = reqparse.RequestParser()
player_paid_membership.add_argument('player_id', type=int, help='Id required', required=True, location='json')
player_paid_membership.add_argument('month',type=int, help='month required', required=True, location='json')
player_paid_membership.add_argument('year', type=int, help='year required', required=True, location='json')

player_paid_membership_put = reqparse.RequestParser()
player_paid_membership_put.add_argument('coach_id', type=int, help='Coach Id required', location='json')
player_paid_membership_put.add_argument('player_id', type=int, help='Id required',location='json')
player_paid_membership_put.add_argument('month',type=int, help='month required',location='json')
player_paid_membership_put.add_argument('year', type=int, help='year required',location='json')

resuorce_field_payments={
    'player_id':fields.Integer,
    'coach_id':fields.Integer,
    'month':fields.Integer,
    'year':fields.Integer,
    'date_of_payment':fields.String
}        


class MembershipPayment(Resource):
    method_decorators=[token_required]

    @marshal_with(resuorce_field_payments)
    def get(self, current_user, membership_id):
        
        if not current_user.admin:
            abort(401, 'Only coaches can see this information! You can see your own payments in "My payments" section.')

        payment = MembershipPayments.query.filter_by(id=membership_id).first()

        if not payment:
            abort(404, 'There is no payment with that ID')

        elif current_user.head_admin:
            return payment
        
        elif current_user.admin:
            player_id = payment.player_id
            player = Players.query.filter_by(id=player_id).first()
            if player in current_user.players:
                return payment
            else:
                abort(401, 'You can only see payments of your own players')
            
    @marshal_with(resuorce_field_payments)
    def post(self, current_user, membership_id):
        
        if not current_user.admin:
            abort(401, 'You are not authorized for this action')
        
        payment = MembershipPayments.query.filter_by(id=membership_id).first()
        if payment:
            abort(409, 'There already is a payment with that ID!')
        
        args = player_paid_membership.parse_args()
        player = Players.query.filter_by(id=args['player_id']).first()

        if not player:
            abort(404, 'There is no player with that ID')
        
        else:
            if player in current_user.players:
                payment = MembershipPayments(id=membership_id, player_id=args['player_id'], coach_id=current_user.id, month=args['month'], year=args['year'], date_of_payment=datetime.now().date())
                db.session.add(payment)
                db.session.commit()
                return payment
            else:
                abort(401, 'You can only add payments for your own players!')
        
    @marshal_with(resuorce_field_payments)   
    def put(self, current_user, membership_id):

        if not current_user.head_admin:
            abort(401, 'You are not authorized for this action')
        
        payment = MembershipPayments.query.filter_by(id=membership_id).first()

        if not payment:
            abort(404, 'There is no payment with that ID')
        
        args = player_paid_membership_put.parse_args()
        
        if args['player_id']:
            payment.player_id = args['player_id']
        if args['coach_id']:
            payment.coach_id = args['coach_id']
        if args['month']:
            payment.month = args['month']
        if args['year']:
            payment.year = args['year']
        
        db.session.add(payment)
        db.session.commit()
        return payment
    
    def delete(self, current_user, membership_id):

        if not current_user.head_admin:
            abort(401, 'You are not authorized for this action')

        payment = MembershipPayments.query.filter_by(id=membership_id).first()
        if not payment:
            abort(404, 'There is no payment with given ID!')

        db.session.delete(payment)
        db.session.commit()
        return jsonify({'message':'Payment deleted'})
    

class PlayerSessions(Resource):
    method_decorators = [token_required]

    def get(self, current_user, player_id):
        player = Players.query.filter_by(id=player_id).first()
        if not player:
            abort(404, 'There is no player with that ID!')
        
        if  not current_user.admin:
            player = Players.query.filter_by(id=current_user.id).first()
            output={}
            output['player_name'] = player.name + ' ' + player.surname
            output['sessions'] = [f'sessio number:{session.id}, team:{session.team_id}, coach:{session.coach_id}, date:{session.date}' for session in player.sessions]
            return jsonify(output)
            
        elif current_user.head_admin or player in current_user.players:
            output={}
            output['player_name'] = player.name + ' ' + player.surname
            output['sessions'] = [f'session number:{session.id}, team:{session.team_id}, coach:{session.coach_id}, date:{session.date}' for session in player.sessions]
            return jsonify(output)
        
        elif current_user.admin and not player in current_user.players:
            abort(401, 'You can only see your own players!')
        
        else:
            player = Players.query.filter_by(id=current_user.id).players
            output={}
            output['player_name'] = player.name + ' ' + player.surname
            output['sessions'] = [f'sessio number:{session.id}, team:{session.team_id}, coach:{session.coach_id}, date:{session.date}' for session in player.sessions]
            return jsonify(output)
        

class AllPlayers(Resource):
    method_decorators=[token_required]
    
    def get(self, current_user):

        if not current_user.admin:
            abort(401, 'You are not authorized for this action')

        players = Players.query.order_by(Players.year_of_birth)
        output = []
        
        for player in players:
            player_info={}
            player_info['full_name'] = (player.name + ' ' + player.surname)
            player_info['birth_date'] = (str(player.month_of_birth) +'/'+ str(player.year_of_birth))
            player_info['coach_id'] = player.coach_id
            player_info['team_id'] = player.team_id
            output.append(player_info)
        
        return jsonify({'players': output})

        
            
            



        


    


    



    