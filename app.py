from flask import Flask, render_template, request, redirect, session
from models import db, User, Job, Application

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secret'

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return redirect('/login')


# SIGNUP
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None

    if request.method == 'POST':
        existing_user = User.query.filter_by(email=request.form['email']).first()

        if existing_user:
            error = "Email already exists"
        else:
            user = User(
                name=request.form['name'],
                email=request.form['email'],
                password=request.form['password'],
                role=request.form['role']
            )
            db.session.add(user)
            db.session.commit()
            return redirect('/login')

    return render_template('signup.html', error=error)

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        user = User.query.filter_by(
            email=request.form['email'],
            password=request.form['password']
        ).first()

        if user:
            session['user_id'] = user.id
            return redirect('/dashboard')
        else:
            error = "Invalid email or password"

    return render_template('login.html', error=error)


# DASHBOARD
@app.route('/dashboard')
def dashboard():
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)


# PROFILE
@app.route('/profile')
def profile():
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)


# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# POST JOB
@app.route('/post_job', methods=['GET', 'POST'])
def post_job():
    if request.method == 'POST':
        job = Job(
            title=request.form['title'],
            description=request.form['description'],
            skills=request.form['skills'],
            recruiter_id=session['user_id']
        )
        db.session.add(job)
        db.session.commit()
        return redirect('/dashboard')

    return render_template('post_job.html')


# VIEW JOBS
@app.route('/view_jobs')
def view_jobs():
    jobs = Job.query.all()
    return render_template('view_jobs.html', jobs=jobs)


# APPLY FOR JOB
@app.route('/apply/<int:job_id>')
def apply(job_id):
    user_id = session.get('user_id')

    new_app = Application(
        student_id=user_id,
        job_id=job_id
    )

    db.session.add(new_app)
    db.session.commit()

    return redirect('/my_applications')


# STUDENT VIEW APPLICATIONS
@app.route('/my_applications')
def my_applications():
    user_id = session.get('user_id')

    apps = Application.query.filter_by(student_id=user_id).all()

    return render_template('my_applications.html', applications=apps)


# RECRUITER VIEW APPLICATIONS
@app.route('/view_applicants')
def view_applicants():
    user_id = session.get('user_id')

    # Only show applications for jobs posted by this recruiter
    apps = Application.query.join(Job).filter(Job.recruiter_id == user_id).all()

    return render_template('view_applicants.html', applications=apps)

@app.route('/student/<int:id>')
def view_student(id):
    student = User.query.get(id)
    return render_template('student_profile.html', student=student)

if __name__ == '__main__':
    app.run(debug=True)