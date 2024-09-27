"""
common_fun.py

This module contains utility functions for handling movie data,
admin and user interactions, and genre associations in the movie
management application.
"""

from sqlalchemy.exc import IntegrityError
from flask import (
                   request,
                   redirect,
                   url_for,
                   session,
                   flash,
                   current_app)
from models import db, Movie, Director,  Genre, Admin, User
from blueprints.utils import _fetch_movie_data


def admin_logged_in():
    """Check if the admin is logged in."""
    admin_id = session.get('admin_id')
    if admin_id:
        return Admin.query.get(admin_id)  # This should return the Admin object or None
    return None


def user_logged_in():
    """Check if the user is logged in."""
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)  # This should return the User object or None
    return None


def handle_not_logged_in():
    """Handle case where admin is not logged in."""
    session.clear()
    clear_cache()
    return redirect(url_for('login'))


def clear_cache():
    """Clear cache if it exists."""
    current_cache = current_app.extensions.get('cache')
    if current_cache and hasattr(current_cache, 'clear'):
        current_cache.clear()


def handle_invalid_admin():
    """Handle case where admin is invalid."""
    session.clear()
    clear_cache()
    flash('You must be logged in as an admin.', 'warning')
    return redirect(url_for('login'))


def handle_invalid_user():
    """Handle the case where the user is not valid."""
    session.clear()
    clear_cache()
    flash('Invalid user. Please log in again.', 'error')
    return redirect(url_for('login'))  # Redirect to login page


def handle_add_movie_post(admin):
    """Handle POST request for adding a movie."""
    title = request.form.get('title')
    if not title:
        return handle_missing_title()

    existing_movie = check_existing_movie(title, admin.id)
    if existing_movie:
        return handle_existing_movie()

    movie_data = _fetch_movie_data(title)
    if not movie_data:
        return handle_missing_movie_data()

    new_movie = create_movie_from_data(movie_data, admin)
    if not new_movie:
        return handle_invalid_movie_data()

    return save_new_movie(new_movie)


def handle_missing_title():
    """Handle case where title is missing."""
    flash('Title is required to fetch movie details.', 'error')
    return redirect(url_for('admin_bp.add_movie'))


def check_existing_movie(title, admin_id):
    """Check if a movie with the same title already exists for the current admin."""
    return Movie.query.filter_by(title=title, admin_id=admin_id).first()


def handle_existing_movie():
    """Handle case where the movie already exists."""
    flash('Movie with this title already exists.', 'warning')
    return redirect(url_for('admin_bp.manage_movies'))


def handle_missing_movie_data():
    """Handle case where movie data is missing from the API."""
    flash('Movie not found in the API.', 'error')
    return redirect(url_for('admin_bp.add_movie'))


def create_movie_from_data(movie_data, admin):
    """Create a Movie object from the fetched data."""
    movie_title = movie_data.get('Title')
    director_name = movie_data.get('Director')
    if not movie_title or not director_name:
        return None

    director = find_or_create_director(director_name)
    rating = get_movie_rating(movie_data)

    new_movie = Movie(
        title=movie_title,
        director_id=director.id,
        year=movie_data.get('Year'),
        rating=rating,
        poster=get_movie_poster(movie_data),
        imdbID=movie_data.get('imdbID') or '',
        trailer=movie_data.get('Trailer') or '',  # Include the trailer URL
        plot=movie_data.get('Plot') or '',
        user_id=request.form.get('user_id') or None,
        admin_id=admin.id
    )

    handle_genres(new_movie, movie_data)
    return new_movie


def find_or_create_director(director_name):
    """Find or create a director in the database."""
    director = Director.query.filter_by(name=director_name).first()
    if not director:
        director = Director(name=director_name)
        db.session.add(director)
        db.session.commit()
    return director


def get_movie_rating(movie_data):
    """Convert and return the movie rating."""
    try:
        return float(movie_data.get('imdbRating', 0))
    except ValueError:
        return 0


def get_movie_poster(movie_data):
    """Return the movie poster URL or a default poster if not available."""
    return (
        movie_data.get('Poster')
        if movie_data.get('Poster') and movie_data.get('Poster') != 'N/A'
        else url_for('static', filename='images/default_movie_poster.jpg')
    )


def handle_genres(movie, movie_data):
    """Handle genre add new movie association for the movie."""
    genre_string = movie_data.get('Genre', '')
    genre_names = [name.strip() for name in genre_string.split(',') if name.strip()]
    existing_genres = {genre.id for genre in movie.genres}

    for genre_name in genre_names:
        genre = Genre.query.filter_by(name=genre_name).first()
        if not genre:
            genre = Genre(name=genre_name)
            db.session.add(genre)
            db.session.commit()
        if genre.id not in existing_genres:
            movie.genres.append(genre)


def save_new_movie(movie):
    """Save the new movie to the database."""
    try:
        db.session.add(movie)
        db.session.commit()
        flash('Movie added successfully!', 'success')
        return redirect(url_for('admin_bp.manage_movies'))
    except IntegrityError as e:
        db.session.rollback()
        flash(f"Database error: {str(e)}", 'error')
        return redirect(url_for('admin_bp.add_movie'))


def handle_invalid_movie_data():
    """Handle invalid movie data."""
    flash('Movie title or director is missing.', 'error')
    return redirect(url_for('admin_bp.add_movie'))


def extract_movie_form_data(form):
    """
    Extracts and returns relevant movie data from the form.
    """
    return {
        'title': form.get('title'),
        'director_name': form.get('director'),
        'year': int(form.get('year', 0)),
        'rating': float(form.get('rating', 0)),
        'genre_string': form.get('genres', '')
    }


def update_movie(movie, form_data, director, admin):
    """
    Updates the movie with new data from the form.
    """
    movie.title = form_data['title']
    movie.director_id = director.id
    movie.year = form_data['year']
    movie.rating = form_data['rating']
    movie.admin_id = admin.id


def handle_genres_for_movie(movie, genre_string):
    """
    Handles genre for update movie associations for a movie.
    """
    genre_names = {name.strip() for name in genre_string.split(',') if name.strip()}
    current_genres = {genre.name: genre for genre in movie.genres}
    existing_genre_names = set(current_genres.keys())

    genres_to_add = genre_names - existing_genre_names
    genres_to_remove = existing_genre_names - genre_names

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


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    """
    Check if a filename has a valid extension.
    Parameters:
    filename (str): The name of the file to check.
    Returns:
    bool: True if the filename has a valid extension, False otherwise.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def handle_post_request():
    """handel request for the current user."""
    user_id = session['user_id']
    movie_title = request.form.get('title')

    if not movie_title:
        flash('Title is required to fetch movie details.', 'error')
        return redirect(url_for('user_bp.user_add_movie'))

    if is_movie_exists(movie_title, user_id):
        flash('Movie with this title already exists.', 'warning')
        return redirect(url_for('admin_bp.manage_movies'))

    movie_data = _fetch_movie_data(movie_title)
    if not movie_data:
        flash('Movie not found in the API.', 'error')
        return redirect(url_for('user_bp.user_add_movie'))

    return process_movie_data(movie_data, user_id)


def is_movie_exists(movie_title, user_id):
    """Check if the movie already exists for the current user."""
    return Movie.query.filter_by(title=movie_title, user_id=user_id).first() is not None


def process_movie_data(movie_data, user_id):
    """Process the fetched movie data and add it to the database."""
    title = movie_data.get('Title')
    if not title:
        flash('Movie title not found in the fetched data.', 'error')
        return redirect(url_for('user_bp.user_add_movie'))

    director_name = movie_data.get('Director')
    if not director_name:
        flash('Director not found in the fetched data.', 'error')
        return redirect(url_for('user_bp.user_add_movie'))

    director = find_or_create_director(director_name)

    rating = parse_rating(movie_data.get('imdbRating'))
    new_movie = create_movie_object(movie_data, user_id, director.id, rating)

    handle_genres_for_user(movie_data.get('Genre', ''), new_movie)

    try:
        db.session.add(new_movie)
        db.session.commit()
        flash('Movie added successfully!', 'success')
        return redirect(url_for('user_bp.my_movies'))
    except IntegrityError as e:
        db.session.rollback()  # Rollback in case of error
        flash(f"Database error: {str(e)}", 'error')
        return redirect(url_for('user_bp.user_add_movie'))


def parse_rating(rating_str):
    """Convert the rating to a float, defaulting to 0 on error."""
    try:
        return float(rating_str)
    except ValueError:
        return 0


def create_movie_object(movie_data, user_id, director_id, rating):
    """Create a new Movie object."""
    return Movie(
        title=movie_data.get('Title'),
        director_id=director_id,
        year=movie_data.get('Year') or None,
        rating=rating,
        poster=(
                movie_data.get('Poster')
                or url_for('static', filename='images/default_movie_poster.jpg')
        ),
        imdbID=movie_data.get('imdbID') or '',
        trailer=movie_data.get('Trailer') or '',  # Include the trailer URL
        plot=movie_data.get('Plot') or '',
        user_id=user_id,
        admin_id=request.form.get('admin_id') or None
    )


def handle_genres_for_user(genre_string, new_movie):
    """Handle genre creation and association with the movie."""
    genre_names = [name.strip() for name in genre_string.split(',') if name.strip()]
    existing_genres = {genre.id for genre in new_movie.genres}

    for genre_name in genre_names:
        genre = Genre.query.filter_by(name=genre_name).first()
        if not genre:
            genre = Genre(name=genre_name)
            db.session.add(genre)
            db.session.commit()
        if genre.id not in existing_genres:
            new_movie.genres.append(genre)
            existing_genres.add(genre.id)


def update_movie_genres(movie, genre_string):
    """Update the movie's genres based on the input string."""
    genre_names = {name.strip() for name in genre_string.split(',') if name.strip()}
    current_genres = {genre.name: genre for genre in movie.genres}
    existing_genre_names = set(current_genres.keys())

    genres_to_add = genre_names - existing_genre_names
    genres_to_remove = existing_genre_names - genre_names

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


def handle_movie_update(movie):
    """Process the movie update logic."""
    movie.title = request.form.get('title')
    director_name = request.form.get('director')
    director = find_or_create_director(director_name)

    movie.director_id = director.id
    movie.year = int(request.form.get('year', movie.year))
    movie.rating = float(request.form.get('rating', movie.rating))

    genre_string = request.form.get('genres', '')
    update_movie_genres(movie, genre_string)

    try:
        db.session.commit()
        flash('Movie updated successfully!', 'success')
        return redirect(url_for('user_bp.my_movies'))
    except IntegrityError as e:
        db.session.rollback()  # Rollback in case of error
        flash(f"Database error: {str(e)}", 'error')
        return redirect(url_for('user_bp.user_edit_movie', movie_id=movie.id))
