import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from models import db, User, Admin, Contact, Movie, Director, Genre
from blueprints.admin import admin_bp
from blueprints.user import user_bp
from flask_caching import Cache
from flask_migrate import Migrate
import logging

logging.basicConfig(level=logging.DEBUG)

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

# Configure and initialize cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
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


@app.route('/movies_home')
def movies_home():
    # Fetch pagination and sorting parameters
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Items per page
    sort_column = request.args.get('sort', 'title')  # Default sorting by title
    sort_order = request.args.get('order', 'asc')  # Default order ascending

    # Define sorting columns
    sort_options = {
        'title': Movie.title,
        'director': Director.name,
        'year': Movie.year,
        'rating': Movie.rating,
        'genre': Genre.name  # This will require proper joining with Genre
    }

    # Get the sort key, default to Movie.title
    sort = sort_options.get(sort_column, Movie.title)

    # Apply sorting order
    if sort_order == 'desc':
        sort = sort.desc()
    else:
        sort = sort.asc()

    # Use left outer joins for Director and Genre relationships
    movies_query = Movie.query \
        .outerjoin(Movie.director) \
        .outerjoin(Movie.genres) \
        .order_by(sort) \
        .paginate(page=page, per_page=per_page)

    # Get total number of movies
    num_movies = movies_query.total

    # Pass movies and sorting information to the template
    return render_template('movies_home.html',
                           num_movies=num_movies,
                           movies=movies_query,
                           sort_column=sort_column,
                           sort_order=sort_order)


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

        # Check for Admin first
        admin = Admin.query.filter_by(email=email).first()
        if admin:
            if admin.check_password(password):
                # Assuming `check_password` is a method that verifies the hashed password
                session.clear()  # Clear any previous session data
                session['admin_id'] = admin.id  # Store admin ID in session
                flash('Admin login successful!', 'success')
                return redirect(url_for('admin_bp.admin_dashboard'))  # Redirect to the admin dashboard
            else:
                flash('Invalid password for admin', 'danger')  # Password doesn't match for admin
                return redirect(url_for('login'))  # Redirect back to login page

        # If no admin found, check for the user
        user = User.query.filter_by(email=email).first()
        if user:
            if user.check_password(password):
                # Assuming `check_password` is a method that verifies the hashed password
                session.clear()  # Clear any previous session data
                session['user_id'] = user.id  # Store user ID in session
                flash('User login successful!', 'success')
                return redirect(url_for('user_bp.user_dashboard'))  # Redirect to the user dashboard
            else:
                flash('Invalid password for user', 'danger')  # Password doesn't match for user
                return redirect(url_for('login'))  # Redirect back to login page

        # If neither an admin nor user is found with the email
        flash('Invalid email or password', 'danger')

    return render_template('login.html')


# Clear the cache
def clear_cache():
    if hasattr(cache, 'clear'):
        cache.clear()
        flash('Cache cleared successfully!', 'success')
    else:
        flash('Cache clearing functionality not available.', 'warning')
    return redirect(url_for('home'))  # Redirect to a suitable page


@app.route('/logout')
def logout():
    # Check if there is an admin session
    if 'admin_id' in session:
        session.pop('admin_id', None)
        session.clear()
        # flash('Admin session has been cleared.', 'info')

    # Check if there is a user session
    if 'user_id' in session:
        session.pop('user_id', None)
        session.clear()
        # flash('User session has been cleared.', 'info')

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


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
