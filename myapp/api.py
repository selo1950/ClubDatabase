from flask import Blueprint
from flask_restful import Api
from .resources.player_resources import Player, PlayerMembership, MembershipPayment, AllPlayers, PlayerSessions
from .resources.coach_resources import Coach, CoachAllPlayers, AllCoaches, CoachTeams, CoachMembership, AllPayments, CoachSessions
from .resources.teams_resources import Team, TeamPlayers, AllTeams, TeamSessions
from .resources.session_resources import Training, SessionPlayers, AllSession
from .authorization import LogInCoach, LogInPlayer



main = Blueprint('main', __name__)

api = Api(main)

@main.route('/')
def home():
    return {'message': 'Welcome to club database manager'}


api.add_resource(LogInPlayer, '/player-login/')

api.add_resource(LogInCoach,'/coach-login/')

api.add_resource(Player, '/player/<int:player_id>/')

api.add_resource(Coach, '/coach/<int:coach_id>')

api.add_resource(Team, '/team/<int:team_id>')

api.add_resource(Training, '/session/<int:session_id>')

api.add_resource(TeamPlayers, '/team-players/<int:team_id>')

api.add_resource(TeamSessions, '/team-sessions/<int:team_id>')

api.add_resource(SessionPlayers, '/session-players/<int:session_id>')

api.add_resource(CoachTeams, '/coach-teams/<int:coach_id>' )

api.add_resource(CoachSessions, '/coach-sessions/<int:coach_id>')

api.add_resource(CoachAllPlayers, '/coach-players/<int:coach_id>')

api.add_resource(MembershipPayment, '/payment/<int:membership_id>')

api.add_resource(PlayerMembership, '/player-payments/<int:player_id>')

api.add_resource(PlayerSessions, '/player-sessions/<int:player_id>')

api.add_resource(CoachMembership, '/coach-payments/<int:coach_id>')

api.add_resource(AllPlayers, '/allplayers/')

api.add_resource(AllCoaches, '/allcoaches/')

api.add_resource(AllTeams, '/allteams/')

api.add_resource(AllPayments, '/allpayments')

api.add_resource(AllSession, '/allsessions/')




#$env:DATABASE_URL='postgresql://clubdatabase_user:NQdcNkMwGGqAGxIkCAHT7Arnjjl4n6SH@dpg-chitk23hp8ufsbla8r3g-a.frankfurt-postgres.render.com/clubdatabase'