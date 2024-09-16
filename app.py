import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from models import db, User, Admin, Contact, Movie
from blueprints.admin import admin_bp
from blueprints.user import user_bp
from flask_caching import Cache
from flask_migrate import Migrate
import logging

logging.basicConfig(level=logging.DEBUG)

# Set up the cache configuration
cache = Cache()

db_directory = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'db')
if not os.path.exists(db_directory):
    os.makedirs(db_directory)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(db_directory, "moviwebapp.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = 'vrana@2024MSchool'
app.config['CACHE_TYPE'] = 'simple'  # Simple in-memory cache for development
app.config['UPLOAD_FOLDER'] = './static/images/upload/profile_image'

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db.init_app(app)
migrate = Migrate(app, db)

# Initialize cache
cache.init_app(app)

# Register Blueprints
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(user_bp, url_prefix='/user')


@app.route('/')
def index():
    movie = Movie.query.all()
    return render_template('index.html', movies=movie)


@app.route('/home')
def home():
    movie = Movie.query.all()
    return render_template('index.html', movies=movie)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/favorites')
def favorites():
    return render_template('favorites.html')


@app.route('/movies')
def movies():
    movie = Movie.query.all()
    return render_template('movies.html', movies=movie)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        new_contact = Contact(name=name, email=email, message=message)
        db.session.add(new_contact)
        db.session.commit()

        flash('Your message has been sent!', 'success')
        return redirect(url_for('contact'))

    return render_template('contact.html')


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/signup_user', methods=['GET', 'POST'])
def signup_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        gender = request.form.get('gender')  # Optional field

        # Handle password hashing
        hashed_password = generate_password_hash(password)

        # Handle profile picture upload
        profile_picture_filename = None
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and allowed_file(file.filename):
                # Save the file and get the filename
                profile_picture_filename = secure_filename(file.filename)
                profile_picture_path = os.path.join(app.config['UPLOAD_FOLDER'], profile_picture_filename)
                file.save(profile_picture_path)

        # Create new user with gender and profile picture filename
        new_user = User(
            name=name,
            email=email,
            password=hashed_password,
            gender=gender,
            profile_picture=profile_picture_filename  # Save only the filename
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('User registration successful!', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('User with this email already exists.', 'danger')

    return render_template('signup.html')


@app.route('/signup_admin', methods=['GET', 'POST'])
def signup_admin():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        new_admin = Admin(name=name, email=email, password=hashed_password)
        try:
            db.session.add(new_admin)
            db.session.commit()
            flash('Admin registration successful!', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('Admin with this email already exists.', 'danger')

    return render_template('signup_admin.html')


# Single login route for both users and admins
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Try to find the email in the Admin table first
        admin = Admin.query.filter_by(email=email).first()
        if admin and admin.check_password(password):
            session['admin_id'] = admin.id  # Store admin ID in session
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_bp.admin_dashboard'))  # Example admin dashboard

        # If no admin found, check the User table
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id  # Store user ID in session
            flash('User login successful!', 'success')
            return redirect(url_for('user_bp.user_dashboard'))  # Redirect user dashboard

        # If neither admin nor user is found
        flash('Invalid email or password', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    # Remove user or admin session data
    session.pop('admin_id', None)
    session.pop('user_id', None)

    # Set headers to prevent browser caching
    response = make_response(redirect(url_for('login')))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    flash('You have been logged out successfully.', 'success')
    return response


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# Clear the cache route
@app.route('/clear_cache')
def clear_cache():
    if hasattr(cache, 'clear'):
        cache.clear()
        flash('Cache cleared successfully!', 'success')
    else:
        flash('Cache clearing functionality not available.', 'warning')
    return redirect(url_for('index'))  # Redirect to a suitable page


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
