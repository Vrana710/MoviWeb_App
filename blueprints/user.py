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
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from models import db, User, Movie, Director, Favorite, Genre
from blueprints.utils import _fetch_movie_data

user_bp = Blueprint('user_bp', __name__,
                    template_folder=os.path.join(os.path.dirname(__file__),
                                                 '../templates/user'))


@user_bp.route('/dashboard')
def user_dashboard():
    if 'user_id' not in session:
        session.clear()

        # Access cache through current_app
        current_cache = current_app.extensions['cache']

        # Clear cache if it exists
        if current_cache and hasattr(current_cache, 'clear'):
            current_cache.clear()

        return redirect(url_for('login'))  # Redirect to login page if not authenticated

    user_id = session['user_id']
    user = User.query.get_or_404(user_id)  # Ensure user exists or raise 404

    # Fetch the latest movies added by the current user (limit to 5 for display purposes)
    latest_movies = (
        Movie.query.filter_by(user_id=user_id)
        .order_by(Movie.id.desc())
        .limit(5)
        .all()
    )

    # Query to get the favorite movies of the user
    user_favorites_query = (
        Movie.query.join(Favorite)
        .filter(Favorite.user_id == user_id,
                Favorite.movie_id == Movie.id)
    )

    # Count the total number of favorite movies
    num_favorites = user_favorites_query.count()
    num_movies = Movie.query.filter_by(user_id=user_id).count()

    movies = user_favorites_query.filter_by(user_id=user_id)
    seen_imdb_ids = set()
    unique_movies = []

    for movie in movies:
        if movie.imdbID not in seen_imdb_ids:
            seen_imdb_ids.add(movie.imdbID)
            unique_movies.append(movie)

    return render_template('dashboard.html',
                           user=user,
                           latest_movies=latest_movies,
                           num_favorites=num_favorites,
                           movies=unique_movies,
                           num_movies=num_movies
                           )


@user_bp.route('/my_movies')
def my_movies():
    if 'user_id' not in session:
        session.clear()

        # Access cache through current_app
        current_cache = current_app.extensions['cache']

        # Clear cache if it exists
        if current_cache and hasattr(current_cache, 'clear'):
            current_cache.clear()

        return redirect(url_for('login'))

    user_id = session['user_id']
    page = request.args.get('page', 1, type=int)  # Get the current page from query parameters, default to 1
    per_page = 5  # Number of movies per page

    # Query to get the favorite movies of the user
    favorite_movie_ids = [f.movie_id for f in Favorite.query.filter_by(user_id=user_id).all()]

    # Query to get all movies added by the current user, excluding the user's favorite movies
    movies_query = Movie.query.filter(Movie.user_id == user_id).filter(Movie.id.notin_(favorite_movie_ids))

    # Count the total number of movies after filtering
    num_movies = movies_query.count()

    # Paginate the filtered query
    movies = movies_query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('my_movies.html', num_movies=num_movies, movies=movies)


@user_bp.route('/user_favorites')
def user_favorites():
    if 'user_id' not in session:
        session.clear()

        # Access cache through current_app
        current_cache = current_app.extensions['cache']

        # Clear cache if it exists
        if current_cache and hasattr(current_cache, 'clear'):
            current_cache.clear()

        return redirect(url_for('login'))

    user_id = session['user_id']
    page = request.args.get('page', 1, type=int)  # Get the current page from query parameters, default to 1
    per_page = 5  # Number of movies per page

    # Query to get the favorite movies of the user with pagination
    user_favorites_query = (
        Movie.query.join(Favorite)
        .filter(Favorite.user_id == user_id, Favorite.movie_id == Movie.id)
    )

    # Count the total number of favorite movies
    num_favorites = user_favorites_query.count()

    # Paginate the query
    movies = user_favorites_query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('user_favorites.html', num_favorites=num_favorites, movies=movies)


@user_bp.route('/add_to_favorites/<int:movie_id>', methods=['POST'])
def add_to_favorites(movie_id):
    if 'user_id' not in session:
        session.clear()

        # Access cache through current_app
        current_cache = current_app.extensions['cache']

        # Clear cache if it exists
        if current_cache and hasattr(current_cache, 'clear'):
            current_cache.clear()

        return redirect(url_for('login'))

    user_id = session['user_id']
    movie = Movie.query.get(movie_id)

    if not movie:
        flash('Movie not found.', 'error')
        return redirect(url_for('user_bp.my_movies'))

    # Check if the movie is already a favorite
    existing_favorite = Favorite.query.filter_by(user_id=user_id, movie_id=movie_id).first()
    if existing_favorite:
        flash('Movie is already in your favorites.', 'info')
        return redirect(url_for('user_bp.my_movies'))

    # Add movie to favorites
    new_favorite = Favorite(user_id=user_id, movie_id=movie_id)
    db.session.add(new_favorite)
    db.session.commit()
    flash('Movie added to favorites!', 'success')

    # Get the updated number of favorite movies
    num_favorites = Favorite.query.filter_by(user_id=user_id).count()

    # Redirect to the same page after adding to favorites
    return redirect(
        url_for('user_bp.user_favorites', page=request.args.get('page', 1, type=int), num_favorites=num_favorites))


@user_bp.route('/remove_from_favorites/<int:movie_id>', methods=['POST'])
def remove_from_favorites(movie_id):
    if 'user_id' not in session:
        session.clear()

        # Access cache through current_app
        current_cache = current_app.extensions['cache']

        # Clear cache if it exists
        if current_cache and hasattr(current_cache, 'clear'):
            current_cache.clear()

        return redirect(url_for('login'))

    user_id = session['user_id']
    movie = Movie.query.get(movie_id)

    if not movie:
        flash('Movie not found.', 'error')
        return redirect(url_for('user_bp.my_movies'))

    # Find the favorite entry
    favorite = Favorite.query.filter_by(user_id=user_id, movie_id=movie_id).first()
    if not favorite:
        flash('Movie is not in your favorites.', 'info')
        return redirect(url_for('user_bp.my_movies'))

    # Remove movie from favorites
    db.session.delete(favorite)
    db.session.commit()
    flash('Movie removed from favorites!', 'success')

    # Get the updated number of favorite movies
    num_favorites = Favorite.query.filter_by(user_id=user_id).count()

    # Redirect to the same page after removing from favorites
    return redirect(
        url_for('user_bp.user_favorites', page=request.args.get('page', 1, type=int), num_favorites=num_favorites))


@user_bp.route('/user_add_movie', methods=['GET', 'POST'])
def user_add_movie():
    if 'user_id' not in session:
        session.clear()
        current_cache = current_app.extensions.get('cache')
        if current_cache and hasattr(current_cache, 'clear'):
            current_cache.clear()
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_id = session['user_id']
        movie_title = request.form.get('title')

        if not movie_title:
            flash('Title is required to fetch movie details.', 'error')
            return redirect(url_for('user_bp.user_add_movie'))

        # Check if the movie already exists for the current admin
        existing_movie = Movie.query.filter_by(title=movie_title, user_id=user_id).first()
        if existing_movie:
            flash('Movie with this title already exists.', 'warning')
            return redirect(url_for('admin_bp.manage_movies'))

        # Fetch movie data from an external source (API or other service)
        movie_data = _fetch_movie_data(movie_title)

        if movie_data:
            # Validate the essential fields
            title = movie_data.get('Title')
            if not title:
                flash('Movie title not found in the fetched data.', 'error')
                return redirect(url_for('user_bp.user_add_movie'))

            director_name = movie_data.get('Director')
            if not director_name:
                flash('Director not found in the fetched data.', 'error')
                return redirect(url_for('user_bp.user_add_movie'))

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
                title=title,
                director_id=director.id,
                year=movie_data.get('Year') or None,
                rating=rating,
                poster=movie_data.get('Poster')
                if movie_data.get('Poster') and movie_data.get('Poster') != 'N/A'
                else url_for('static', filename='images/default_movie_poster.jpg'),
                imdbID=movie_data.get('imdbID') or '',  # IMDb ID or link
                plot=movie_data.get('Plot') or '',
                user_id=user_id,  # The user who is adding the movie
                admin_id=request.form.get('admin_id') or None  # Optional: admin ID
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
                return redirect(url_for('user_bp.my_movies'))
            except IntegrityError as e:
                db.session.rollback()  # Rollback in case of error
                flash(f"Database error: {str(e)}", 'error')
                return redirect(url_for('user_bp.user_add_movie'))
        else:
            flash('Movie not found in the API.', 'error')
            return redirect(url_for('user_bp.user_add_movie'))

    # For GET request, prepare the list of genres
    genres = Genre.query.all()

    return render_template('user_add_movie.html', genres=genres)


@user_bp.route('/edit_movie/<int:movie_id>', methods=['GET', 'POST'])
def user_edit_movie(movie_id):
    if 'user_id' not in session:
        session.clear()
        current_cache = current_app.extensions.get('cache')
        if current_cache and hasattr(current_cache, 'clear'):
            current_cache.clear()
        return redirect(url_for('login'))

    user_id = session['user_id']  # Fetch the current user from session

    if not user_id:
        flash('You must be logged in to edit a movie.', 'warning')
        return redirect(url_for('user_bp.login'))

    movie = Movie.query.get_or_404(movie_id)

    # Ensure that only the user who added the movie can edit it
    if movie.user_id != user_id:
        flash('You are not authorized to edit this movie.', 'warning')
        return redirect(url_for('user_bp.my_movies'))

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

        # Handle genres if provided
        genre_string = request.form.get('genres', '')
        # Set of genre names from input
        genre_names = {name.strip() for name in genre_string.split(',') if name.strip()}

        current_genres = {genre.name: genre for genre in movie.genres}  # Map of current genre names to Genre objects
        existing_genre_names = set(current_genres.keys())  # Set of current genre names

        genres_to_add = genre_names - existing_genre_names  # New genres not already associated with the movie
        genres_to_remove = existing_genre_names - genre_names  # Genres to remove

        # Add new genres
        for genre_name in genres_to_add:
            genre = Genre.query.filter_by(name=genre_name).first()
            if not genre:
                genre = Genre(name=genre_name)
                db.session.add(genre)
                db.session.commit()
            movie.genres.append(genre)

        # Remove genres that are no longer associated with the movie
        for genre_name in genres_to_remove:
            genre_to_remove = current_genres[genre_name]
            movie.genres.remove(genre_to_remove)

        try:
            db.session.commit()
            flash('Movie updated successfully!', 'success')
            return redirect(url_for('user_bp.my_movies'))
        except IntegrityError as e:
            db.session.rollback()  # Rollback in case of error
            flash(f"Database error: {str(e)}", 'error')
            return redirect(url_for('user_bp.user_edit_movie', movie_id=movie_id))

    genres = Genre.query.all()  # To display available genres

    return render_template('user_edit_movie.html', movie=movie, genres=genres, user=user_id)


@user_bp.route('/delete_movie/<int:movie_id>', methods=['POST'])
def delete_movie(movie_id):
    if 'user_id' not in session:
        session.clear()

        # Access cache through current_app
        current_cache = current_app.extensions.get('cache')

        # Clear cache if it exists
        if current_cache and hasattr(current_cache, 'clear'):
            current_cache.clear()

        return redirect(url_for('login'))

    user_id = session['user_id']
    user = User.query.get(user_id)

    # Get the movie and check if it belongs to the current user
    movie = Movie.query.filter_by(id=movie_id, user_id=user_id).first_or_404()

    # Delete the movie if it belongs to the current admin
    try:
        # Remove associations from the movie_genre association table
        movie.genres.clear()

        # Now delete the movie
        db.session.delete(movie)
        db.session.commit()
        flash('Movie deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()  # Rollback on error
        flash(f'Error deleting movie: {str(e)}', 'danger')

    return redirect(url_for('user_bp.my_movies', user=user))


@user_bp.route('/user_profile')
def user_profile():
    if 'user_id' not in session:
        session.clear()

        # Access cache through current_app
        current_cache = current_app.extensions['cache']

        # Clear cache if it exists
        if current_cache and hasattr(current_cache, 'clear'):
            current_cache.clear()

        return redirect(url_for('login'))

    user_id = session['user_id']
    user = User.query.get(user_id)

    return render_template('user_profile.html', user=user)


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@user_bp.route('/edit_user_profile/<int:user_id>', methods=['GET', 'POST'])
def edit_user_profile(user_id):
    if 'user_id' not in session:
        session.clear()

        # Access cache through current_app
        current_cache = current_app.extensions['cache']

        # Clear cache if it exists
        if current_cache and hasattr(current_cache, 'clear'):
            current_cache.clear()

        return redirect(url_for('login'))

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        new_name = request.form.get('name', user.name)
        new_email = request.form.get('email', user.email)
        new_gender = request.form.get('gender', user.gender)  # Optional gender field
        new_password = request.form.get('password', None)

        # Check if name has changed
        if new_name and user.name != new_name:
            user.name = new_name

        # Check if email has changed
        if new_email and user.email != new_email:
            user.email = new_email

        # Update the password only if a new password was provided
        if new_password and new_password.strip():  # Ensure the password is not blank
            user.password = generate_password_hash(new_password)
            user.password_update_date = datetime.now()  # Optional timestamp for tracking password updates

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

        db.session.commit()
        flash('Your profile updated successfully!', 'success')
        return redirect(url_for('user_bp.user_profile'))

    return render_template('edit_user_profile.html', user=user)
