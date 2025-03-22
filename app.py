# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, User, Event
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///events.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')  # Change for production

db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()
    # Optional: Create a default admin user if needed.
    # if not User.query.filter_by(username="admin").first():
    #     user = User(username="admin")
    #     user.set_password("admin")
    #     db.session.add(user)
    #     db.session.commit()

# --- Authentication Routes ---

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if the username already exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists. Please choose another.", "danger")
            return redirect(url_for('signup'))
        # Create a new user
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully! Please login.", "success")
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash("Logged in successfully", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logged out successfully", "success")
    return redirect(url_for('login'))

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please login to access this page", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Event Management Routes ---

@app.route('/')
@login_required
def index():
    events = Event.query.order_by(Event.date.asc()).all()
    return render_template('index.html', events=events)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_event():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        date_str = request.form['date']
        time_str = request.form['time']
        location = request.form['location']
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            time_obj = datetime.strptime(time_str, '%H:%M').time()
        except ValueError:
            flash("Invalid date or time format", "danger")
            return redirect(url_for('add_event'))
        event = Event(title=title, description=description, date=date_obj, time=time_obj, location=location)
        db.session.add(event)
        db.session.commit()
        flash("Event added successfully", "success")
        return redirect(url_for('index'))
    return render_template('add_event.html')

@app.route('/edit/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    if request.method == 'POST':
        event.title = request.form['title']
        event.description = request.form['description']
        date_str = request.form['date']
        time_str = request.form['time']
        event.location = request.form['location']
        try:
            event.date = datetime.strptime(date_str, '%Y-%m-%d').date()
            event.time = datetime.strptime(time_str, '%H:%M').time()
        except ValueError:
            flash("Invalid date or time format", "danger")
            return redirect(url_for('edit_event', event_id=event.id))
        db.session.commit()
        flash("Event updated successfully", "success")
        return redirect(url_for('index'))
    return render_template('edit_event.html', event=event)

@app.route('/delete/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash("Event deleted successfully", "success")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
