from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from .models import *
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from datetime import datetime
from sqlalchemy import update
auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        # checks everything is good before registering
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
            new_user = User(email=email, name=name, password=generate_password_hash(password1, method='pbkdf2:sha256'),projects=[])
            
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            print("Logged in!")
            flash('Success! Your account has been created', category='success')
            return redirect(url_for('views.home'))
            
            
    return render_template("register.html", user=current_user)
# checks everything is good before allowing user to login
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
                print("Logged in!")
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
    projects = Project.query.filter(Project.users.any(id=current_user.id)).all()
    # projects = Project.query.all()
    return render_template("projectManager.html", user=current_user, projects=projects)


@auth.route('/newtask', methods=['GET', 'POST'])
def new_task():
    if request.method == 'POST':
        name = request.form.get('name')
        assignee = request.form.get('assignee')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        use_deadline = request.form.get('use-deadline')
        deadline = request.form.get('deadline') if use_deadline else None
        project_id = request.form.get('project_id')  # Retrieve project_id from the form

        if not name:
            flash('Task name is required', category='error')
        elif not start_date:
            flash('Start date is required', category='error')
        elif deadline and start_date >= deadline:
            flash('Start date must be before the deadline', category='error')
        else:
            # Convert date strings to datetime objects
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            deadline = datetime.strptime(deadline, '%Y-%m-%d') if deadline else datetime.strptime('9999-12-31','%Y-%m-%d')

            # Check if project_id is provided
            if project_id:
                # If project_id is provided, associate the task with the specified project
                project = Project.query.get(int(project_id))
                if project and current_user in project.users:
                    new_task = Task(
                        name=name,
                        assignee=assignee,
                        description=description,
                        start_date=start_date,
                        deadline=deadline,
                        project_id=int(project_id)
                    )
                    db.session.add(new_task)
                    db.session.commit()
                    flash(f'New task "{name}" assigned to project "{project.name}" successfully', category='success')
                    return redirect(url_for('auth.project', project_id=project_id))
                else:
                    flash('Invalid project selection or access denied', category='error')
            else:
                # If project_id is not provided, create a standalone task without associating it with any project
                new_task = Task(
                    name=name,
                    assignee=assignee,
                    description=description,
                    start_date=start_date,
                    deadline=deadline
                )
                db.session.add(new_task)
                db.session.commit()
                flash(f'New task "{name}" created successfully', category='success')
                return redirect(url_for('auth.taskManager'))

    # Provide the project_id to the template for creating the form
    project_id = request.args.get('project_id')
    return render_template("newTask.html", user=current_user, project_id=project_id)



@auth.route('/newproject', methods=['GET', 'POST'])
def new_project():
    if request.method == 'POST':
        name = request.form.get('name')
        start_date = request.form.get('sdate')
        use_deadline = request.form.get('use-deadline')
        deadline = request.form.get('deadline') if use_deadline else None
        description = request.form.get('description')

        if not name:
            flash('Project name is required', category='error')
        elif not start_date:
            flash('Start date is required', category='error')
        elif deadline:
            if start_date >= deadline:
                flash('Start date must be before the deadline', category='error')
        else:
            # Convert date strings to datetime objects (sql will only accept like this)
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            deadline = datetime.strptime(deadline, '%Y-%m-%d') if deadline else datetime.strptime('9999-12-31','%Y-%m-%d')

            new_project = Project(
                name=name,
                start_date=start_date,
                deadline=deadline,
                description=description,
                users=[current_user],  # Assuming you use Flask-Login to get the current user
                tasks=[]  # You can set task_id as needed
            )

            db.session.add(new_project)
            db.session.commit()

            flash(f'New Project "{name}" created successfully', category='success')
            return redirect(url_for('auth.projectManager'))

    return render_template("newProject.html", user=current_user)

@auth.route('/editproject/<project_id>', methods=['GET','POST'])
@login_required
def edit_project(project_id):
    edit_project = Project.query.filter_by(id=project_id).first()
    if request.method == 'POST':
        name = request.form.get('name')
        start_date = request.form.get('sdate')
        use_deadline = request.form.get('use-deadline')
        deadline = request.form.get('deadline')
        description = request.form.get('description')
    db.session.commit()
    return render_template('editProject.html', user = current_user, project_id = project_id)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    print("Logged Out")
    return redirect(url_for('auth.login'))

@auth.route('/project/<project_id>', methods=['GET', 'POST'])
def project(project_id):
    # for inviting new users
    if request.method == 'POST':
        new_user_email = request.form.get('new_user_email')
        new_user = User.query.filter(User.email == new_user_email).first()
        if new_user:
            project = Project.query.filter(Project.id == project_id,).first()
            project.users.append(new_user)
            db.session.commit()
            flash(f"Invited {new_user.name} to {project.name}", category="success")
            print(f"Invited {new_user.name} to {project.name}")
        else:
            flash("User not found", category='error')
    
    # query project with the project_id and where current_user.id is in the project.users list
    project = Project.query.filter(Project.id == project_id,).first()
    if not project:
        # project not found
        return "Page Not Found", 404
    elif not any(user.id == current_user.id for user in project.users):
        # user doesn't have access
        return "Access Denied", 403
    else:
        # return page
        return render_template('project.html', user=current_user, project=project)
    
@auth.route('project/<project_id>/task_manager')
def task_manager(project_id):
    # query project with the project_id and where current_user.id is in the project.users list
    project = Project.query.filter(Project.id == project_id,).first()
    if not project:
        # project not found
        return "Page Not Found", 404
    elif not any(user.id == current_user.id for user in project.users):
        # user doesn't have access
        return "Access Denied", 403
    else:
        # return page
        return render_template('taskManager.html', user=current_user, project=project)

@auth.route('/view_users')
def view_users():
    users = User.query.all()
    projects = Project.query.all()
    return render_template('view_users.html', user=current_user, users=users, projects=projects)
