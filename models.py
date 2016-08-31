"""Database models for MBMT.

The database is structured by sponsor. Sponsors register teams, which
are composed of students.
"""

from mbmt import db

SUBJECTS = ["Algebra", "Number Theory", "Geometry", "Combinatorics"]


class Sponsor(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Sponsor: %s>" % self.name


class Team(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'))
    school = db.relationship('School', backref=db.backref('teams', lazy='dynamic'))

    def __init__(self, name, school):
        self.name = name
        self.school = school

    def __repr__(self):
        return "<Team: %s, Sponsor: %s>" % (self.name, self.school.name)


class Student(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    team = db.relationship('Team', backref=db.backref('members', lazy='dynamic'))

    subject1 = db.Column(db.Integer)
    subject2 = db.Column(db.Integer)

    def __init__(self, name, team):
        self.name = name
        self.team = team

    def __repr__(self):
        return "<Student: %s, Team: %s, Sponsor: %s>" % (self.name, self.team.name, self.team.school.name)
