from flask import Blueprint, render_template, request, flash
from flask_login import current_user
from .models import *
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        name = request.form.get('name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if len(email) < 3:
            flash('Email must contain more than three characters', category ='error')
        elif len(name) < 2:
            flash('Name must contain more than two characters', category ='error')
        elif password1 != password2:
            flash('Passwords do not match', category ='error')
        elif len(password1) < 6:
            flash('Password must contain more than six characters', category ='error')

        else:
            flash('Success! Your account has been created', category='success')
            #add user to db
            user = User(id=0,email=email,name=name,password=password1)
            db.session.add(user)
            db.session.commit()
            
            
    return render_template("register.html", user=current_user)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("login.html", user=current_user)

@auth.route('/taskmanager')
def taskManager():
    return render_template("taskManager.html", user=current_user)

@auth.route('/projectmanager')
def projectManager():
    return render_template("projectManager.html", user=current_user)

@auth.route('/newtask')
def newTask():
    return render_template("newTask.html", user=current_user)

@auth.route('/newproject')
def newProject():
    return render_template("newProject.html", user=current_user)


@auth.route('/logout')
def logout():
    return "<p>Logout</p>"