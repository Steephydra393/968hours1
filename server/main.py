from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import json
from datetime import datetime


app = Flask(__name__, template_folder=r'C:\Users\Cromi\Code\ROBOTICS\RAWC Hours Site\client\templates', static_folder=r'C:\Users\Cromi\Code\ROBOTICS\RAWC Hours Site\client\static')


app.secret_key = 'your_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.route('/welcome', methods=['GET'])
@app.route('/', methods=['GET'])
def welcome():
    print(session.get('logged_in'))
    return render_template('home.html', logged_in=session.get('logged_in', False))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        schoole = request.form['schoolEmail']
        personale = request.form['personalEmail']
        phonenumber = request.form['phoneNumber']
        id = request.form['schoolid']

        print(name, password, confirm_password)

        if password != confirm_password:
            flash('Passwords do not match. Please try again.')
            return redirect(url_for('register'))

        # Load existing users
        users = load_json_file(r'C:\Users\Cromi\Code\ROBOTICS\RAWC Hours Site\server\users.json')

        # Check if username already exists
        if any(user['username'] == name for user in users):
            flash('Username already exists. Please choose a different one.')
            print(5)
            return redirect(url_for('register'))
        
        if any(user['schoole'] == schoole for user in users):
            flash('School email already in use, contact a mentor to gain access.')
            print(4)
            return redirect(url_for('register'))
        
        if any(user['personale'] == personale for user in users):
            flash('Personal email already in use, contact a mentor to gain access.')
            print(3)
            return redirect(url_for('register')) 

        if any(user['phonenumber'] == phonenumber for user in users):
            flash('Phone number already in use, contact a mentor to gain access.')
            print(2)
            return redirect(url_for('register'))
        
        if any(user['school_id'] == id for user in users):
            flash('School ID already in use, contact a mentor to gain access.')
            print(1)
            return redirect(url_for('register'))
        
        # Hash the password and save the new user
        hashed_password = generate_password_hash(password)
        new_user = {
            "id": len(users) + 1,
            "username": name,
            "school_id": id,
            "password_hash": hashed_password,
            "schoole": schoole,
            "personale": personale,
            "phonenumber": phonenumber,
            "role": "student"  # Default role; adjust as needed
        }
        users.append(new_user)
        save_json_file(r'C:\Users\Cromi\Code\ROBOTICS\RAWC Hours Site\server\users.json', users)
        
        flash('User created successfully! Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html')


# Load JSON Data
def load_json_file(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

# Save JSON Data
def save_json_file(filepath, data):
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=4)

# Define User Class
class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

# User loader callback
@login_manager.user_loader
def load_user(user_id):
    users = load_json_file(r'C:\Users\Cromi\Code\ROBOTICS\RAWC Hours Site\server\users.json')
    for user in users:
        if user['id'] == int(user_id):
            return User(user['id'], user['username'], user['role'])
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_json_file(r'C:\Users\Cromi\Code\ROBOTICS\RAWC Hours Site\server\users.json')
        user = next((u for u in users if u['username'] == username), None)

        if user and check_password_hash(user['password_hash'], password):
            user_obj = User(user['id'], user['username'], user['role'])
            login_user(user_obj)
            flash('Logged in successfully.')
            session['logged_in'] = True
            return redirect(url_for('mentor_hub')) if user['role'] == 'mentor' else redirect(url_for('welcome'))
        else:
            flash('Invalid credentials, please try again.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('logged_in', None)
    flash('You have been logged out.')
    return redirect(url_for('welcome'))

@app.route('/mentor_hub')
@login_required
def mentor_hub():
    if current_user.role != 'mentor':
        flash('Access denied.')
        return redirect(url_for('welcome'))

    # Fetch all stats from the JSON file
    stats_data = load_json_file(r'C:\Users\Cromi\Code\ROBOTICS\RAWC Hours Site\server\stats.json')
    users_data = load_json_file(r'C:\Users\Cromi\Code\ROBOTICS\RAWC Hours Site\server\users.json')

    # Enrich stats data with usernames
    enriched_stats = [
        {
            'username': next((u['username'] for u in users_data if u['id'] == stat['user_id']), 'Unknown'),
            'hours_logged': stat['hours_logged'],
            'activities_completed': stat['activities_completed'],
            'last_updated': stat['last_updated']
        }
        for stat in stats_data
    ]

    return render_template('mentor_hub.html', stats=enriched_stats)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
