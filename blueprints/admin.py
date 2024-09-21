# admin.py

import os
from datetime import datetime
from flask import (Blueprint,
                   render_template,
                   request,
                   redirect,
                   url_for,
                   session,
                   flash,
                   current_app)
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from models import db, User, Movie, Director, Admin, Genre, Favorite
from blueprints.utils import _fetch_movie_data

admin_bp = Blueprint('admin_bp', __name__,
                     template_folder=os.path.join(os.path.dirname(__file__),
                                                  '../templates/admin'))


@admin_bp.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        session.clear()

        # Access cache through current_app
        current_cache = current_app.extensions['cache']

        # Clear cache if it exists
        if current_cache and hasattr(current_cache, 'clear'):
            current_cache.clear()

        return redirect(url_for('login'))

    admin_id = session['admin_id']
    admin = Admin.query.get(admin_id)

    # Count users and movies for display purposes, filtering by admin_id
    num_users = User.query.filter_by(admin_id=admin_id).count()
    num_movies = Movie.query.filter_by(admin_id=admin_id).count()

    # Count all users and movies for display purposes
    num_users_total = User.query.count()
    num_movies_total = Movie.query.count()

    # Set the page number from the request args or default to 1
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Set how many users to display per page

    # Paginate the query, filtering by admin_id
    users_with_movies = (
        db.session.query(User, func.count(Movie.id).label('movies_count'))
        .outerjoin(Movie, Movie.user_id == User.id)
        .filter(User.admin_id == admin_id)
        .group_by(User.id)
        .paginate(page=page, per_page=per_page)
    )
    movies = Movie.query.filter_by(admin_id=admin_id)
    seen_imdb_ids = set()
    unique_movies = []

    for movie in movies:

        if movie.imdbID not in seen_imdb_ids:
            seen_imdb_ids.add(movie.imdbID)
            unique_movies.append(movie)

    # Render the full page
    return render_template('admin_dashboard.html',
                           num_users=num_users,
                           num_movies=num_movies,
                           users_with_movies=users_with_movies,
                           admin=admin,
                           num_users_total=num_users_total,
                           num_movies_total=num_movies_total,
                           movies=unique_movies,
                           )


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Add this function to fetch the current admin
def get_current_admin():
    if 'admin_id' in session:
        return Admin.query.get(session['admin_id'])
    return None


@admin_bp.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if 'admin_id' not in session:
        session.clear()

        # Access cache through current_app
        current_cache = current_app.extensions['cache']

        # Clear cache if it exists
        if current_cache and hasattr(current_cache, 'clear'):
            current_cache.clear()

        return redirect(url_for('login'))

    admin = get_current_admin()  # Fetch the current admin from session

    if not admin:
        flash('You must be logged in as an admin to add a movie.', 'warning')
        return redirect(url_for('admin_bp.login'))

    if request.method == 'POST':
        user_name = request.form['name']
        user_email = request.form['email']
        user_password = request.form['password']
        user_gender = request.form.get('gender')  # Optional gender field

        if not user_email:
            flash('Email is required to create a user.', 'error')
            return redirect(url_for('admin_bp.add_user'))

        if User.query.filter_by(email=user_email).first():
            flash('Email address already exists. Please use a different email.', 'error')
            return redirect(url_for('admin_bp.add_user'))

        hashed_password = generate_password_hash(user_password)

        # Handle profile picture upload
        profile_picture_filename = None
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                profile_picture_filename = filename
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        new_user = User(
            name=user_name,
            email=user_email,
            password=hashed_password,
            gender=user_gender,
            profile_picture=profile_picture_filename,  # Save only filename
            admin_id=admin.id  # Admin who is adding the user

        )
        db.session.add(new_user)
        db.session.commit()
        flash('User registration successful!', 'success')
        return redirect(url_for('admin_bp.manage_users', admin=admin))

    return render_template('add_user.html', admin=admin)


@admin_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'admin_id' not in session:
        session.clear()

        # Access cache through current_app
        current_cache = current_app.extensions['cache']

        # Clear cache if it exists
        if current_cache and hasattr(current_cache, 'clear'):
            current_cache.clear()

        return redirect(url_for('login'))

    admin_id = session['admin_id']
    admin = Admin.query.get(admin_id)

    if not admin:
        flash('You must be logged in as an admin to add a movie.', 'warning')
        return redirect(url_for('admin_bp.login'))

    # user = User.query.filter_by(id=user_id, admin_id=admin_id).first_or_404()
    user = User.query.filter_by(id=user_id).first_or_404()

    if request.method == 'POST':
        new_name = request.form.get('name', user.name)
        new_email = request.form.get('email', user.email)
        new_gender = request.form.get('gender', user.gender)  # Optional gender field
        new_password = request.form.get('password', None)

        # Debugging: Print old and new passwords
        if new_password:
            print(f"Old Password Hash: {user.password}")
            print(f"New Password: {generate_password_hash(new_password)}")

        # Check if name has changed
        if new_name and user.name != new_name:
            user.name = new_name

        # Check if email has changed
        if new_email and user.email != new_email:
            user.email = new_email

        # Check if password has changed
        if new_password:
            user.password = generate_password_hash(new_password)
            user.password_update_date = datetime.now()  # Update password change timestamp

        # Check if gender has changed
        if new_gender and user.gender != new_gender:
            user.gender = new_gender

        # Handle profile picture upload (optional)
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                profile_picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(profile_picture_path)
                user.profile_picture = filename  # Save only the filename

                # Debugging: Print profile picture details
                print(f"Profile Picture Filename: {filename}")
                print(f"Profile Picture Path: {profile_picture_path}")

        user.admin_id = admin.id  # Admin who is Updating the user

        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin_bp.manage_users'))

    return render_template('edit_user.html', user=user, admin=admin)


@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'admin_id' not in session:
        session.clear()

        # Access cache through current_app
        current_cache = current_app.extensions['cache']

        # Clear cache if it exists
        if current_cache and hasattr(current_cache, 'clear'):
            current_cache.clear()

        return redirect(url_for('login'))

    admin_id = session['admin_id']
    admin = Admin.query.get(admin_id)

    # Ensure the user belongs to the current admin (if applicable)
    user = User.query.filter_by(id=user_id).first_or_404()

    # Delete the user if it belongs to the current admin
    db.session.delete(user)
    db.session.commit()

    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin_bp.manage_users', admin=admin))


@admin_bp.route('/manage_users')
def manage_users():
    if 'admin_id' not in session:
        session.clear()

        # Access cache through current_app
        current_cache = current_app.extensions['cache']

        # Clear cache if it exists
        if current_cache and hasattr(current_cache, 'clear'):
            current_cache.clear()

        return redirect(url_for('login'))

    admin_id = session['admin_id']
    admin = Admin.query.get(admin_id)

    # Count users and movies for display purposes, filtering by admin_id
    num_users = User.query.filter_by(admin_id=admin_id).count()
    num_movies = Movie.query.filter_by(admin_id=admin_id).count()

    page = request.args.get('page', 1, type=int)
    per_page = 5  # Set how many users to display per page

    # Paginate users, filtering by admin_id
    users = User.query.filter_by(admin_id=admin_id).paginate(page=page, per_page=per_page)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Render and return only the table and pagination controls for AJAX requests
        return render_template('partials/manage_users_content.html', users=users)

    return render_template('manage_users.html',
                           num_users=num_users,
                           num_movies=num_movies,
                           users=users,
                           admin=admin)


@admin_bp.route('/manage_all_users')
def manage_all_users():
    if 'admin_id' not in session:
        session.clear()

        # Access cache through current_app
        current_cache = current_app.extensions['cache']

        # Clear cache if it exists
        if current_cache and hasattr(current_cache, 'clear'):
            current_cache.clear()

        return redirect(url_for('login'))

    admin_id = session['admin_id']
    admin = Admin.query.get(admin_id)

    # Count users and movies for display purposes, filtering by admin_id
    num_users = User.query.count()

    page = request.args.get('page', 1, type=int)
    per_page = 5  # Set how many users to display per page

    # Paginate users, filtering by admin_id
    users = User.query.paginate(page=page, per_page=per_page)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Render and return only the table and pagination controls for AJAX requests
        return render_template('partials/manage_all_users_content.html', users=users)

    return render_template('manage_all_users.html',
                           num_users=num_users,
                           users=users,
                           admin=admin)


@admin_bp.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    if 'admin_id' not in session:
        session.clear()
        current_cache = current_app.extensions.get('cache')
        if current_cache and hasattr(current_cache, 'clear'):
            current_cache.clear()
        return redirect(url_for('login'))

    admin = get_current_admin()  # Fetch the current admin from session

    if not admin:
        flash('You must be logged in as an admin to add a movie.', 'warning')
        return redirect(url_for('admin_bp.login'))

    if request.method == 'POST':
        title = request.form.get('title')

        if not title:
            flash('Title is required to fetch movie details.', 'error')
            return redirect(url_for('admin_bp.add_movie'))

        # Check if the movie already exists for the current admin
        existing_movie = Movie.query.filter_by(title=title, admin_id=admin.id).first()
        if existing_movie:
            flash('Movie with this title already exists.', 'warning')
            return redirect(url_for('admin_bp.manage_movies'))

        # Fetch the movie data using the title
        movie_data = _fetch_movie_data(title)

        if movie_data:
            # Validate the essential fields
            movie_title = movie_data.get('Title')
            if not movie_title:
                flash('Movie title not found in the fetched data.', 'error')
                return redirect(url_for('admin_bp.add_movie'))

            director_name = movie_data.get('Director')
            if not director_name:
                flash('Director not found in the fetched data.', 'error')
                return redirect(url_for('admin_bp.add_movie'))

            # Find or create the director
            director = Director.query.filter_by(name=director_name).first()
            if not director:
                director = Director(name=director_name)
                db.session.add(director)
                db.session.commit()

            # Handle rating conversion with error handling
            try:
                rating = float(movie_data.get('imdbRating', 0))
            except ValueError:
                rating = 0  # Default to 0 if conversion fails

            # Create the movie object with the director's ID
            new_movie = Movie(
                title=movie_title,
                director_id=director.id,
                year=movie_data.get('Year') or None,
                rating=rating,
                poster=movie_data.get('Poster')
                if movie_data.get('Poster') and movie_data.get('Poster') != 'N/A'
                else url_for('static', filename='images/default_movie_poster.jpg'),
                imdbID=movie_data.get('imdbID') or '',  # IMDb ID or link
                plot=movie_data.get('Plot') or '',
                user_id=request.form.get('user_id') or None,  # Optional: user ID
                admin_id=admin.id  # Admin who is adding the movie
            )

            # Handle genres if provided
            genre_string = movie_data.get('Genre', '')
            genre_names = [name.strip() for name in genre_string.split(',') if name.strip()]

            existing_genres = {genre.id for genre in new_movie.genres}  # Get existing genre IDs for the movie
            for genre_name in genre_names:
                genre = Genre.query.filter_by(name=genre_name).first()
                if not genre:
                    genre = Genre(name=genre_name)
                    db.session.add(genre)
                    db.session.commit()
                if genre.id not in existing_genres:
                    new_movie.genres.append(genre)
                    existing_genres.add(genre.id)  # Update the existing genre IDs set

            try:
                db.session.add(new_movie)
                db.session.commit()
                flash('Movie added successfully!', 'success')
                return redirect(url_for('admin_bp.manage_movies'))
            except IntegrityError as e:
                db.session.rollback()  # Rollback in case of error
                flash(f"Database error: {str(e)}", 'error')
                return redirect(url_for('admin_bp.add_movie'))
        else:
            flash('Movie not found in the API.', 'error')
            return redirect(url_for('admin_bp.add_movie'))

    users = User.query.all()  # To optionally assign a movie to a user
    genres = Genre.query.all()  # To display available genres

    return render_template('add_movie.html', users=users, genres=genres, admin=admin)


@admin_bp.route('/edit_movie/<int:movie_id>', methods=['GET', 'POST'])
def edit_movie(movie_id):
    if 'admin_id' not in session:
        session.clear()
        current_cache = current_app.extensions.get('cache')
        if current_cache and hasattr(current_cache, 'clear'):
            current_cache.clear()
        return redirect(url_for('login'))

    admin = get_current_admin()  # Fetch the current admin from session

    if not admin:
        flash('You must be logged in as an admin to edit a movie.', 'warning')
        return redirect(url_for('admin_bp.login'))

    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':
        movie.title = request.form.get('title')
        director_name = request.form.get('director')

        # Find or create the director
        director = Director.query.filter_by(name=director_name).first()
        if not director:
            director = Director(name=director_name)
            db.session.add(director)
            db.session.commit()

        movie.director_id = director.id
        movie.year = int(request.form.get('year', movie.year))
        movie.rating = float(request.form.get('rating', movie.rating))
        movie.admin_id = admin.id  # Update admin ID to current admin

        # Handle genres if provided
        genre_string = request.form.get('genres', '')
        # Set of genre names from input
        genre_names = {name.strip() for name in genre_string.split(',') if name.strip()}

        # Get current genres associated with the movie
        current_genres = {genre.name: genre for genre in movie.genres}  # Map of current genre names to Genre objects
        existing_genre_names = set(current_genres.keys())  # Set of current genre names

        # Determine genres to add and remove
        genres_to_add = genre_names - existing_genre_names  # New genres to add
        genres_to_remove = existing_genre_names - genre_names  # Existing genres to remove

        # Add new genres
        for genre_name in genres_to_add:
            genre = Genre.query.filter_by(name=genre_name).first()
            if not genre:
                genre = Genre(name=genre_name)
                db.session.add(genre)
                db.session.commit()
            movie.genres.append(genre)

        # Remove old genres
        for genre_name in genres_to_remove:
            genre_to_remove = current_genres[genre_name]
            movie.genres.remove(genre_to_remove)

        try:
            db.session.commit()
            flash('Movie updated successfully!', 'success')
            return redirect(url_for('admin_bp.manage_movies'))
        except IntegrityError as e:
            db.session.rollback()  # Rollback in case of error
            flash(f"Database error: {str(e)}", 'error')
            return redirect(url_for('admin_bp.edit_movie', movie_id=movie_id))

    users = User.query.all()  # To assign movie to a user
    genres = Genre.query.all()  # To display available genres

    return render_template('edit_movie.html', movie=movie, users=users, genres=genres, admin=admin)


@admin_bp.route('/delete_movie/<int:movie_id>', methods=['POST'])
def delete_movie(movie_id):
    if 'admin_id' not in session:
        session.clear()
        current_cache = current_app.extensions.get('cache')
        if current_cache and hasattr(current_cache, 'clear'):
            current_cache.clear()
        return redirect(url_for('login'))

    admin_id = session['admin_id']
    admin = Admin.query.get(admin_id)

    # Get the movie and check if it belongs to the current admin
    movie = Movie.query.filter_by(id=movie_id, admin_id=admin_id).first_or_404()

    # Delete the movie if it belongs to the current admin
    try:
        # Remove associations from the movie_genre association table
        movie.genres.clear()

        # Remove any associated favorites
        Favorite.query.filter_by(movie_id=movie_id).delete()

        # Now delete the movie
        db.session.delete(movie)
        db.session.commit()
        flash('Movie deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()  # Rollback on error
        flash(f'Error deleting movie: {str(e)}', 'danger')

    return redirect(url_for('admin_bp.manage_movies', admin=admin))


@admin_bp.route('/delete_any_movie/<int:movie_id>', methods=['POST'])
def delete_any_movie(movie_id):
    # First, delete related favorites
    Favorite.query.filter_by(movie_id=movie_id).delete()

    # Then, delete the movie
    movie = Movie.query.get(movie_id)
    if movie:
        db.session.delete(movie)
        db.session.commit()
        flash('Movie deleted successfully.')
    else:
        flash('Movie not found.')

    return redirect(url_for('admin_bp.manage_all_movies'))


@admin_bp.route('/manage_movies')
def manage_movies():
    if 'admin_id' not in session:
        session.clear()

        # Access cache through current_app
        current_cache = current_app.extensions['cache']

        # Clear cache if it exists
        if current_cache and hasattr(current_cache, 'clear'):
            current_cache.clear()

        return redirect(url_for('login'))

    admin_id = session['admin_id']
    admin = Admin.query.get(admin_id)

    # Filter movies by the current admin's ID
    num_movies = Movie.query.filter_by(admin_id=admin_id).count()
    total_num_movies = Movie.query.count()

    # Pagination for admin's movies
    page = request.args.get('page', 1, type=int)
    per_page = 5
    movies = Movie.query.filter_by(admin_id=admin_id).paginate(page=page, per_page=per_page)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Render and return only the table and pagination controls for AJAX requests
        return render_template('partials/manage_movies_content.html',
                               num_movies=num_movies,
                               movies=movies,
                               admin=admin)

    return render_template('manage_movies.html',
                           num_movies=num_movies,
                           movies=movies,
                           admin=admin,
                           total_num_movies=total_num_movies
                           )


@admin_bp.route('/manage_all_movies')
def manage_all_movies():
    if 'admin_id' not in session:
        session.clear()

        # Access cache through current_app
        current_cache = current_app.extensions.get('cache')

        # Clear cache if it exists
        if current_cache and hasattr(current_cache, 'clear'):
            current_cache.clear()

        return redirect(url_for('login'))

    admin_id = session['admin_id']
    admin = Admin.query.get(admin_id)

    total_num_movies = Movie.query.count()

    # Pagination for admin's movies
    page = request.args.get('page', 1, type=int)
    per_page = 5
    movies = Movie.query.paginate(page=page, per_page=per_page)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Render and return only the table and pagination controls for AJAX requests
        return render_template('partials/manage_all_movies_content.html',
                               total_num_movies=total_num_movies,
                               all_movies=movies)  # Ensure consistent naming

    return render_template('manage_all_movies.html',
                           movies=movies,
                           admin=admin,
                           total_num_movies=total_num_movies)


@admin_bp.route('/reports')
def reports():
    if 'admin_id' not in session:
        session.clear()

        # Access cache through current_app
        current_cache = current_app.extensions['cache']

        # Clear cache if it exists
        if current_cache and hasattr(current_cache, 'clear'):
            current_cache.clear()

        return redirect(url_for('login'))

    admin_id = session['admin_id']
    admin = Admin.query.get(admin_id)

    # Filter movies by the current admin's ID
    num_users = User.query.filter_by(admin_id=admin_id).count()
    # Filter movies by the current admin's ID
    num_movies = Movie.query.filter_by(admin_id=admin_id).count()

    # Count all users and movies for display purposes
    num_users_total = User.query.count()
    num_movies_total = Movie.query.count()

    # Render the full page
    return render_template('reports.html',
                           num_users=num_users,
                           num_movies=num_movies,
                           admin=admin,
                           num_users_total=num_users_total,
                           num_movies_total=num_movies_total
                           )


@admin_bp.route('/all_movies_added_by_user_of_current_admin_report')
def all_movies_added_by_user_of_current_admin_report():
    if 'admin_id' not in session:
        session.clear()

        # Access cache through current_app
        current_cache = current_app.extensions['cache']

        # Clear cache if it exists
        if current_cache and hasattr(current_cache, 'clear'):
            current_cache.clear()

        return redirect(url_for('login'))

    admin_id = session['admin_id']
    admin = Admin.query.get(admin_id)

    # Set the page number from the request args or default to 1
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Set how many users to display per page

    # Paginate users with their associated movies, filtered by admin_id
    users_with_movies = (
        db.session.query(User, func.count(Movie.id).label('movies_count'))
        .outerjoin(Movie, Movie.user_id == User.id)
        .filter(User.admin_id == admin_id)  # Ensure we only get users for the current admin
        .group_by(User.id)
        .paginate(page=page, per_page=per_page)
    )

    # Get all movies added by users under the current admin
    movies = Movie.query.filter_by(admin_id=admin_id)

    # Check if the request is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Render only the table and pagination
        return render_template('partials/all_movies_added_by_user_of_current_admin_content.html',
                               users_with_movies=users_with_movies,
                               admin=admin,
                               movies=movies
                               )

    # Render the full page
    return render_template('all_movies_added_by_user_of_current_admin_report.html',
                           users_with_movies=users_with_movies,
                           admin=admin,
                           movies=movies
                           )


@admin_bp.route('/details_view_of_movies_added_by_user_of_current_admin_report/<int:user_id>')
def details_view_of_movies_added_by_user_of_current_admin_report(user_id):
    if 'admin_id' not in session:
        session.clear()

        # Access cache through current_app
        current_cache = current_app.extensions.get('cache')

        # Clear cache if it exists
        if current_cache and hasattr(current_cache, 'clear'):
            current_cache.clear()

        return redirect(url_for('login'))

    admin_id = session['admin_id']
    admin = Admin.query.get(admin_id)

    print(f"Admin ID: {admin_id}, User ID: {user_id}")

    num_movies = Movie.query.filter_by(user_id=user_id).count()

    # Set the page number from the request args or default to 1
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Set how many movies to display per page

    # Fetch movies for the specified user with pagination, filtered by the admin's ID
    movies = (
        Movie.query.filter_by(user_id=user_id)
        .order_by(Movie.title.asc())
        .paginate(page=page, per_page=per_page)
    )

    # Check if the request is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Render only the table and pagination
        return render_template('partials/details_view_of_movies_added_by_user_of_current_admin_content.html',
                               num_movies=num_movies,
                               movies=movies,  # Pass movies for rendering
                               user=User.query.get(user_id),  # Pass the specific user
                               admin=admin
                               )

    # Render the full page
    return render_template('details_view_of_movies_added_by_user_of_current_admin_report.html',
                           num_movies=num_movies,
                           movies=movies,  # Pass movies for rendering
                           user=User.query.get(user_id),  # Pass the specific user
                           admin=admin
                           )
