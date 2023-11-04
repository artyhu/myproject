<<<<<<< Updated upstream
from flask import Blueprint, render_template, request, flash
from flask_login import current_user
from .models import *
=======
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
>>>>>>> Stashed changes
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already in database', category='error')
        elif len(email) < 3:
            flash('Email must contain more than three characters', category ='error')
        elif len(name) < 2:
            flash('Name must contain more than two characters', category ='error')
        elif password1 != password2:
            flash('Passwords do not match', category ='error')
        elif len(password1) < 6:
            flash('Password must contain more than six characters', category ='error')

        else:
            new_user = User(email=email, name=name, password=generate_password_hash(password1, method='sha256'))
            
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Success! Your account has been created', category='success')
<<<<<<< Updated upstream
            #add user to db
            user = User(id=0,email=email,name=name,password=password1)
            db.session.add(user)
            db.session.commit()
=======
            return redirect(url_for('views.home'))
>>>>>>> Stashed changes
            
            
    return render_template("register.html", user=current_user)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method =='POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                flash('Login Successful!', category='success')
                return redirect(url_for('views.home'))
            else:
                flash('Login Failed!', category='error')
        else:
            flash('Email not found', category = 'error')
    
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
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))