from . import db 
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique = True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(50))
    tasks = db.relationship('Task')
    projects = db.relationship('Project')
    
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    assignee = db.Column(db.String(120))
    description = db.Column(db.String(9999))
    start_date = db.Column(db.DateTime(timezone=True), default=func.now)
    deadline = db.Column(db.DateTime(timezone=True), default=func.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    start_date = db.Column(db.DateTime(timezone=True), default=func.now)
    deadline = db.Column(db.DateTime(timezone=True), default=func.now)
    description = db.Column(db.String(9999))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
