from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from .models import *
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
        # checks everything is good before registering
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already in database', category='error')
        elif '@' not in email:
            flash('Invalid email address', category='error')
        elif len(email) <= 3:
            flash('Email must contain more than three characters', category ='error')
        elif len(name) <= 2:
            flash('Name must contain more than two characters', category ='error')
        elif password1 != password2:
            flash('Passwords do not match', category ='error')
        elif len(password1) < 6:
            flash('Password must contain more than six characters', category ='error')

        else:
            new_user = User(email=email, name=name, password=generate_password_hash(password1, method='pbkdf2:sha256'),projects=[])
            default_project = Project(name=f"{name}'s Default Project", start_date=datetime.now(), deadline=datetime.now(), is_default=True)
            default_project.users.append(new_user)
            new_user.def_project = default_project
            
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
@login_required
def taskManager():
    return render_template("taskManager.html", user=current_user)

@auth.route('/projectmanager')
@login_required
def projectManager():
    projects = Project.query.filter(Project.users.any(id=current_user.id), ~Project.is_default).all()
    # projects = Project.query.all()
    print(projects)
    return render_template("projectManager.html", user=current_user, projects=projects)

@auth.route('/newproject', methods=['GET', 'POST'])
@login_required
def new_project():
    if request.method == 'POST':
        name = request.form.get('name')
        start_date = request.form.get('sdate')
        use_deadline = request.form.get('use-deadline')
        deadline = request.form.get('deadline')
        description = request.form.get('description')

        if not name:
            flash('Project name is required', category='error')
        elif not start_date:
            flash('Start date is required', category='error')
        elif use_deadline and not deadline:
            flash('No deadline given', category='error')
        elif use_deadline and start_date >= deadline:
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
                tasks=[] 
            )

            db.session.add(new_project)
            db.session.commit()
            flash(f"New Project [{name}] created successfully", category='success')
            return redirect(url_for('auth.project', project_id=new_project.id))

    return render_template("newProject.html", user=current_user)

@auth.route('/editproject/<project_id>', methods=['GET','POST'])
@login_required
def edit_project(project_id):
    edit_project = Project.query.filter_by(id=project_id).first()
    if request.method == 'POST':
        name = request.form.get('name')
        start_date = request.form.get('sdate')
        deadline = request.form.get('deadline')
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

            
            edit_project.name=name,
            edit_project.start_date=start_date,
            edit_project.deadline=deadline,
            edit_project.description=description,
            edit_project.users=[current_user],  # Assuming you use Flask-Login to get the current user

        db.session.commit()
    return render_template('editProject.html', user = current_user, project_id = project_id)

@auth.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    print("Logged Out")
    return redirect(url_for('auth.login'))

@auth.route('/project/<project_id>', methods=['GET', 'POST'])
@login_required
def project(project_id):

    # see if project is default project
    def_project = get_default_project()
    if str(def_project.id) == project_id:
        return redirect(url_for('auth.tasks'))
    
    # query project with the project_id and where current_user.id is in the project.users list
    project = Project.query.filter(Project.id == project_id,).first()
    if not project:
        # project not found
        return "Page Not Found", 404
    elif not any(user.id == current_user.id for user in project.users):
        # user doesn't have access
        return "Access Denied", 403
    
    
    # get tasks
    tasks = Task.query.filter(Task.project_id == project_id).all()
    
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
    
    tasks.sort(key=lambda t: (not t.completed, t.id)) # sort tasks by 1: completion, 2: id
    print(tasks)
    # get progress percentage
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task.completed)
    progress_percentage = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
    return render_template('project.html', user=current_user, project=project, tasks=tasks, progress_percentage=progress_percentage)
    
@auth.route('project/<project_id>/newtask', methods=['GET', 'POST'])
@auth.route('/tasks/newtask', methods=['GET', 'POST'], defaults={'project_id': None})
@login_required
def new_task(project_id):

    def_project = get_default_project()
    if not project_id:
        project_id = def_project.id # Assume defualt project

    # query project with the project_id and where current_user.id is in the project.users list
    project = Project.query.filter(Project.id == project_id).first()
    if not project:
        # project not found
        return "Page Not Found", 404
    elif not any(user.id == current_user.id for user in project.users):
        # user doesn't have access
        return "Access Denied", 403
    if request.method == 'POST':
        assignee = request.form.get('assignee')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        use_deadline = request.form.get('use-deadline')
        deadline = request.form.get('deadline')

        if not description:
            flash('Task description is required', category='error')
        elif not start_date:
            flash('Start date is required', category='error')
        elif use_deadline and not deadline:
            flash('No deadline given', category='error')
        elif use_deadline and start_date >= deadline:
            flash('Start date must be before the deadline', category='error')
        else:
            # Convert date strings to datetime objects (sql will only accept like this)
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            deadline = datetime.strptime(deadline, '%Y-%m-%d') if deadline else datetime.strptime('9999-12-31','%Y-%m-%d')
            new_task = Task(
                assignee=assignee,
                description=description,
                start_date=start_date,
                deadline=deadline,
                project_id=project_id
            )

            db.session.add(new_task)
            db.session.commit()
            flash(f'New task created successfully', category='success')
            return redirect(url_for('auth.project', project_id=project_id))
        
    return render_template('newTask.html', user=current_user, project=project)

@auth.route('/tasks')
@login_required
def tasks():
    def_project = get_default_project()
    tasks = def_project.tasks
    tasks.sort(key=lambda t: (not t.completed, t.id)) # sort tasks by 1: completion, 2: id
    # get progress percentage
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task.completed)
    progress_percentage = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
    return render_template('tasks.html', user=current_user, project=def_project, tasks=tasks, progress_percentage=progress_percentage)

@auth.route('/delete_task/<project_id>/<task_id>', methods=['POST'])
def delete_task(project_id, task_id):
    task = Task.query.filter(Task.id == task_id).first()
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('auth.project', project_id=project_id))

@auth.route('/delete_project/<project_id>', methods=['POST'])
def delete_project(project_id):
    project = Project.query.filter(Project.id == project_id).first()
    db.session.delete(project)
    db.session.commit()
    flash(f'Project [{project.name}] was deleted', category='warning')
    return redirect(url_for('auth.projectManager'))

@auth.route('/complete_task/<project_id>/<task_id>', methods=['POST'])
def complete_task(project_id, task_id):
    task = Task.query.filter(Task.id == task_id).first()
    task.completed = True if not task.completed else False
    db.session.commit()
    return redirect(url_for('auth.project', project_id=project_id))

@auth.route('/complete_project/<project_id>', methods=['POST'])
def complete_project(project_id):
    project = Project.query.filter(Project.id == project_id).first()
    tasks = project.tasks
    project_completed = False
    if tasks:
        project_completed = True
        for task in tasks:
            if not task.completed:
                project_completed = False
    project.completed = project_completed
    db.session.commit()
    return redirect(url_for('auth.project', project_id=project_id, project_completed=project_completed))

@auth.route('/database')
def view_users():
    users = User.query.all()
    projects = Project.query.all()
    tasks  = Task.query.all()
    return render_template('database.html', user=current_user, users=users, projects=projects, tasks=tasks)



def get_default_project():
    return Project.query.filter(Project.users.any(id=current_user.id), Project.is_default).first()