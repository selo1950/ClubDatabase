import datetime
from functools import wraps
import jwt
from flask import jsonify, request, current_app, make_response
from flask_restful import Resource
from werkzeug.security import check_password_hash
from .models import Coaches, Players

def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = (request.headers['x-access-token'])
                
        if not token:
            return jsonify({'message': 'Token is missing!'})
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms="HS256")
            current_user = Coaches.query.filter_by(public_id=data['public_id']).first()

            if not current_user:
                current_user = Players.query.filter_by(public_id=data['public_id']).first()

        except:
            return jsonify({'message':'Token is invalid!'})
        
        return f(current_user, *args, **kwargs )
    
    return decorated


class LogInCoach(Resource):

    def get(self):
        return jsonify({'message':'Log in required'})

    def post(self):
        auth = request.authorization

        if not auth or not auth.username or not auth.password:
            return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
        
        user = Coaches.query.filter_by(username=auth.username).first()

        if not user:
             return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
        
        if check_password_hash (user.password, auth.password):
            token = jwt.encode({'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, current_app.config['SECRET_KEY'])
            return jsonify({'token': token})
        
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
    


class LogInPlayer(Resource):

    def get(self):
        return jsonify({'message':'Log in required'})

    def post(self):
        auth = request.authorization

        if not auth or not auth.username or not auth.password:
            return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
        
        user = Players.query.filter_by(username=auth.username).first()

        if not user:
             return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
        
        if check_password_hash (user.password, auth.password):
            token = jwt.encode({'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, current_app.config['SECRET_KEY'])
            return jsonify({'token': token})
        
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
