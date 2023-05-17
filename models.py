from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Player(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), index = True, nullable = False)
    surname = db.Column(db.String(50), index = True, nullable = False)
    year_of_birth = db.Column(db.Integer, index = True, nullable = False)
    month_of_birth = db.Column(db.Integer, index = True, nullable = False)
    coach_id = db.Column(db.Integer, db.ForeignKey('coach.id'))

    def __repr__(self):
        return f'{self.name} {self.surname}, coach num: {self.coach_id}'


class Coach(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), index = True, nullable = False)
    surname = db.Column(db.String(50), index = True, nullable = False)
    players = db.relationship('Player', backref = 'player', lazy = 'dynamic')

    def __repr__(self):
        return f'{self.name} {self.surname}, players: {self.players}'