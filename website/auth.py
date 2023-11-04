from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from .models import User, Task, Project
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from datetime import datetime

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
            new_user = User(email=email, name=name, password=generate_password_hash(password1, method='pbkdf2:sha256'))
            
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Success! Your account has been created', category='success')
            return redirect(url_for('views.home'))
            
            
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

@auth.route('/newtask', methods=['GET', 'POST'])
def new_task():
    if request.method == 'POST':
        name = request.form.get('name')
        assignee = request.form.get('assignee')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        deadline = request.form.get('deadline')

        if not name:
            flash('Task name is required', category='error')
        elif not start_date:
            flash('Start date is required', category='error')
        elif not deadline:
            flash('Deadline is required', category='error')
        else:
            # Convert date strings to datetime objects (sql will only accept like this)
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            deadline = datetime.strptime(deadline, '%Y-%m-%d')
            new_task = Task(
                name=name,
                assignee=assignee,
                description=description,
                start_date=start_date,
                deadline=deadline,
                user_id=current_user.id
            )

            db.session.add(new_task)
            db.session.commit()

            flash(f'New task "{name}" created successfully', category='success')
            return redirect(url_for('auth.taskManager'))

    return render_template("newTask.html", user=current_user)

@auth.route('/newproject', methods=['GET', 'POST'])
def new_project():
    if request.method == 'POST':
        name = request.form.get('name')
        start_date = request.form.get('start_date')
        deadline = request.form.get('deadline')
        description = request.form.get('description')

        if not name:
            flash('Project name is required', category='error')
        elif not start_date:
            flash('Start date is required', category='error')
        elif not deadline:
            flash('Deadline is required', category='error')
        else:
            # Convert date strings to datetime objects (sql will only accept like this)
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            deadline = datetime.strptime(deadline, '%Y-%m-%d')

            new_project = Project(
                name=name,
                start_date=start_date,
                deadline=deadline,
                description=description,
                user_id=current_user.id,  # Assuming you use Flask-Login to get the current user
                task_id=None  # You can set task_id as needed
            )

            db.session.add(new_project)
            db.session.commit()

            flash(f'New project "{name}" created successfully', category='success')
            return redirect(url_for('auth.projectManager'))

    return render_template("newProject.html", user=current_user)
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/view_users')
def view_users():
    users = User.query.all()
    return render_template('view_users.html', user=current_user, users=users)