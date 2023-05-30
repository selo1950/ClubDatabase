from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, ForeignKey
from flask import current_app

  
db = SQLAlchemy()

Base = declarative_base()
    

class Players(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50), index=True, nullable=False)
    surname = db.Column(db.String(50), index=True, nullable=False)
    year_of_birth = db.Column(db.Integer, index=True,nullable=False)
    month_of_birth = db.Column(db.Integer, index=True,nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('coaches.id'))
    username = db.Column(db.String(50), index=True, nullable=False)    
    password = db.Column(db.Text, nullable=False)
    admin = db.Column(db.Boolean)
    head_admin = db.Column(db.Boolean)
    memberships = db.relationship('MembershipPayments', backref='memberships_p', lazy='dynamic')
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    sessions = db.relationship('Trainings', secondary='player_session_association',
                               back_populates='players', lazy='dynamic', overlaps="Players,sessions")
                               
    
    def __repr__(self):
        return f'id:{self.id}, {self.name} {self.surname}, year of birth:{self.year_of_birth}, team:{self.team_id}'


class Coaches(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50), index=True, nullable=False)
    surname = db.Column(db.String(50), index=True, nullable=False)
    players = db.relationship('Players', backref='player', lazy = 'dynamic')
    username = db.Column(db.String(50), index=True, nullable=False)
    password = db.Column(db.Text)
    admin = db.Column(db.Boolean)
    head_admin = db.Column(db.Boolean)
    memberships = db.relationship('MembershipPayments', backref='memberships_c', lazy='dynamic')
    teams = db.relationship('Teams', backref='teams', lazy='dynamic')
    sessions = db.relationship('Trainings', backref='sessions_c', lazy='dynamic')

    def __repr__(self):
        return f'{self.name} {self.surname}, players: {self.players}'
    

class MembershipPayments(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.ForeignKey('players.id'))
    coach_id = db.Column(db.ForeignKey('coaches.id'))
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    date_of_payment = db.Column(db.Date, nullable=False, index=True)


    def __repr__(self):
        return f'Membership for :{self.month}, {self.year}, paid on {self.date_of_payment}'
    

class Teams(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), index=True, nullable=False)
    players = db.relationship('Players', backref='players_t', lazy='dynamic')
    coach_id = db.Column(db.ForeignKey('coaches.id'), nullable=False, index=True)
    sessions = db.relationship('Trainings', backref='sessions_t', lazy='dynamic')

    def __repr__(self):
        return f'{self.name}, coach: {self.coach_id}'
        

class Trainings(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.ForeignKey('teams.id'), nullable=False)
    coach_id = db.Column(db.ForeignKey('coaches.id'), nullable=False, index=True)
    players = db.relationship('Players', secondary='player_session_association', back_populates='sessions', lazy='dynamic', overlaps="Players,sessions")
    date = db.Column(db.Date, nullable=False, index=True)
    description = db.Column(db.Text)

    def __repr__(self):
        return f'session number: {self.id} by team: {self.team_id} on: {self.date}'
    

class PlayerSessionAssociation(db.Model):
    __tablename__='player_session_association'

    player = db.Column('player_id', db.Integer, db.ForeignKey('players.id'), primary_key=True)
    session = db.Column('session_id', db.Integer, db.ForeignKey('trainings.id'), primary_key=True)




    

        




    



