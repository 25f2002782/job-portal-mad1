from models import db, User, Job
from flask import Flask, render_template, request, redirect, session
from models import db, User

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secret'

db.init_app(app)

# ✅ THIS PART IS CRITICAL
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return redirect('/login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user = User(
            name=request.form['name'],
            email=request.form['email'],
            password=request.form['password'],
            role=request.form['role']
        )
        db.session.add(user)
        db.session.commit()
        return redirect('/login')

    return render_template('signup.html')

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

# POST JOB (RECRUITER)
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


# VIEW JOBS (ALL USERS)
@app.route('/view_jobs')
def view_jobs():
    jobs = Job.query.all()
    return render_template('view_jobs.html', jobs=jobs)

if __name__ == '__main__':
    app.run(debug=True)