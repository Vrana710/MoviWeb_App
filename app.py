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


# Set up logging
logging.basicConfig(level=logging.DEBUG)


# Create the database directory if it doesn't exist
db_directory = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'db')
if not os.path.exists(db_directory):
    os.makedirs(db_directory)


# Create the Flask app instance and configure the database URI and other settings.
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

# Initialize SQLAlchemy and Flask-Migrate
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
    """
    This function retrieves all movies from the database, 
    removes duplicates based on imdbID,
    and renders the home page with the unique movies.

    Parameters:
    None

    Returns:
    render_template: A Flask function that renders 
    the 'index.html' template with the unique movies.
    """
    movies = Movie.query.all()
    seen_imdb_ids = set()
    unique_movies = []

    for movie in movies:
        if movie.imdbID not in seen_imdb_ids:
            seen_imdb_ids.add(movie.imdbID)
            unique_movies.append(movie)

    return render_template('index.html', movies=unique_movies)


@app.route('/home')
def home():
    """
    This function retrieves all movies from the database, 
    removes duplicates based on imdbID,
    and renders the home page with the unique movies.

    Parameters:
    None

    Returns:
    render_template: A Flask function that renders 
    the 'index.html' template with the unique movies.
    """
    movies = Movie.query.all()
    seen_imdb_ids = set()
    unique_movies = []

    for movie in movies:
        if movie.imdbID not in seen_imdb_ids:
            seen_imdb_ids.add(movie.imdbID)
            unique_movies.append(movie)

    return render_template('index.html', movies=unique_movies)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/favorites')
def favorites():
    return render_template('favorites.html')


@app.route('/movies_home')
def movies_home():
    """
    This function handles the movie home page with pagination, sorting, and filtering.
    It fetches movies from the database, removes duplicates based on imdbID,
    applies sorting and pagination, and renders the 'movies_home.html' template.

    Parameters:
    None

    Returns:
    render_template: A Flask function that renders 
    the 'movies_home.html' template with the paginated unique movies,
    total number of unique movies, sorting information,
    and the original movies query.
    """
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
        .distinct() \
        .outerjoin(Movie.director) \
        .outerjoin(Movie.genres) \
        .order_by(sort) \
        .all()  # Fetch all movies without pagination first to filter duplicates

    # Logic to filter out duplicate movies by imdbID
    seen_imdb_ids = set()
    unique_movies = []

    for movie in movies_query:
        if movie.imdbID not in seen_imdb_ids:
            seen_imdb_ids.add(movie.imdbID)
            unique_movies.append(movie)

    # Paginate the filtered unique movies list manually
    total_unique_movies = len(unique_movies)
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    paginated_movies = unique_movies[start_index:end_index]

    # Pass movies and sorting information to the template
    return render_template('movies_home.html',
                           num_movies=total_unique_movies,  # Use total number of unique movies
                           movies=paginated_movies,  # Pass the paginated unique movies
                           sort_column=sort_column,
                           sort_order=sort_order,
                           page=page,
                           per_page=per_page,
                           movies_query=unique_movies)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """
    This function handles the contact form submission 
    and saves the contact details to the database.
    It renders the contact form for GET requests 
    and processes the form data for POST requests.

    Parameters:
    None

    Returns:
    render_template: A Flask function that renders 
    the 'contact.html' template for GET requests.
    redirect: A Flask function that redirects to 
    the 'contact' route for POST requests.
    """
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Create a new Contact object with the form data
        new_contact = Contact(name=name, email=email, message=message)

        # Add the new contact to the database session and commit the changes
        db.session.add(new_contact)
        db.session.commit()

        # Display a success flash message and redirect to the contact page
        flash('Your message has been sent!', 'success')
        return redirect(url_for('contact'))

    # Render the contact form for GET requests
    return render_template('contact.html')


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    """
    Check if a filename is allowed based on its extension.

    Parameters:
    filename (str): The name of the file to check.

    Returns:
    bool: True if the filename has a valid extension (allowed by ALLOWED_EXTENSIONS), 
          False otherwise.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/signup_user', methods=['GET', 'POST'])
def signup_user():
    """
    This function handles the user signup process. It processes the signup form data 
    for both GET and POST requests. For POST requests, it validates the form data, 
    hashes the password, handles profile picture upload, creates a new User object, 
    and saves it to the database.

    Parameters:
    None

    Returns:
    render_template: A Flask function that renders the 'signup.html' template for GET requests.
    redirect: A Flask function that redirects to the 'login' route for successful POST requests.
    """
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        gender = request.form.get('gender')  # Optional field

        if not email:
            flash('E-mail is required to create a user.', 'error')
            return redirect(url_for('signup_user'))

        if User.query.filter_by(email=email).first():
            flash('User is already exists with this E-mail Id. Please use a different email.', 'error')
            return redirect(url_for('signup_user'))

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
    """
    This function handles the admin signup process. It processes the signup form data 
    for both GET and POST requests. For POST requests, it validates the form data, 
    hashes the password, creates a new Admin object, and saves it to the database.

    Parameters:
    request (flask.Request): The request object containing form data.

    Returns:
    render_template: A Flask function that renders the 'signup_admin.html' template for GET requests.
    redirect: A Flask function that redirects to the 'login' route for successful POST requests.
    """
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if not email:
            flash('E-mail is required to create a user.', 'error')
            return redirect(url_for('signup_admin'))

        if Admin.query.filter_by(email=email).first():
            flash('Admin is already exists with this E-mail Id. Please use a different email.', 'error')
            return redirect(url_for('signup_admin'))

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
    """
    This function handles the login process for both admin and user.
    It checks the email and password against the database records.
    If a match is found, it clears any previous session data,
    stores the user or admin ID in the session, and redirects to the appropriate dashboard.
    If no match is found, it displays an error message and redirects back to the login page.

    Parameters:
    None

    Returns:
    render_template: A Flask function that renders the 'login.html' template for GET requests.
    redirect: A Flask function that redirects to the 'admin_bp.admin_dashboard' or 'user_bp.user_dashboard' for successful POST requests.
    """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Print the email being attempted for login
        print(f"Attempting to log in with email: {email}")
        # Check for Admin first
        admin = Admin.query.filter_by(email=email).first()

        print(f"Admin found: {admin}")  # Print the admin object or None
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

        print(f"User found: {user}")  # Print the user object or None
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
    """
    Clears the cache if it is available.

    This function checks if the cache object has a 'clear' method. If it does,
    it clears the cache and displays a success flash message. If the cache object
    does not have a 'clear' method, it displays a warning flash message.
    Finally, it redirects the user to the home page.

    Parameters:
    None

    Returns:
    redirect: A Flask function that redirects to the 'home' route.
    """
    if hasattr(cache, 'clear'):
        cache.clear()
        flash('Cache cleared successfully!', 'success')
    else:
        flash('Cache clearing functionality not available.', 'warning')
    return redirect(url_for('home'))  # Redirect to a suitable page


@app.route('/logout')
def logout():
    """
    This function handles the logout process for both admin and user.
    It checks the session data for admin and user IDs, clears the session data,
    and redirects to the login page.

    Parameters:
    None

    Returns:
    redirect: A Flask function that redirects to the 'login' route.
    """
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
    """
    This function handles the 404 Not Found error. It renders a custom 404 error page.

    Parameters:
    e (Exception): The exception object that caused the 404 error. This parameter is not used in the function.

    Returns:
    render_template: A Flask function that renders the '404.html' template.
    int: The HTTP status code 404, indicating that the requested resource could not be found.
    """
    return render_template('404.html'), 404


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
