"""
user.py

This module handles user-related routes and functionalities for the MoviWeb application.
It includes operations such as adding, editing, and deleting movies, as well as user authentication
and session management. The routes defined in this module ensure that users can manage their
favorite movies while enforcing access control and data validation.

Routes:
- user_add_movie: Allows users to add a new movie.
- user_edit_movie: Enables users to edit their existing movies.
- delete_movie: Handles the deletion of a user's movie.
- Other user-related functionalities as needed.
"""

import os
from datetime import datetime
from flask import (Blueprint,
                   render_template,
                   request,
                   redirect,
                   url_for,
                   flash,
                   current_app)
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, OperationalError
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from models import db, User, Movie, Favorite, Genre
from blueprints.common_fun import (user_logged_in,
                                   handle_invalid_user,
                                   handle_not_logged_in,
                                   allowed_file,
                                   handle_post_request,
                                   handle_movie_update)

user_bp = Blueprint('user_bp', __name__,
                    template_folder=os.path.join(os.path.dirname(__file__),
                                                 '../templates/user'))


@user_bp.route('/dashboard')
def user_dashboard():
    """
    Display the user's dashboard with their profile information, 
    latest movies added,
    favorite movies, and a count of their movies.
    Parameters:
    None
    Returns:
    render_template: A rendered HTML template with 
    the user's information, latest movies,
    favorite movies, and a count of their movies.
    """
    if not user_logged_in():
        return handle_not_logged_in()  # Handle case where user is not logged in

    user = user_logged_in()

    if user is None:
        return handle_invalid_user()

    user = User.query.get_or_404(user.id)  # Ensure user exists or raise 404

    # Fetch the latest movies added by the current user (limit to 5 for display purposes)
    latest_movies = (
        Movie.query.filter_by(user_id=user.id)
        .order_by(Movie.id.desc())
        .limit(5)
        .all()
    )

    # Query to get the favorite movies of the user
    user_favorites_query = (
        Movie.query.join(Favorite)
        .filter(Favorite.user_id == user.id,
                Favorite.movie_id == Movie.id)
    )

    # Count the total number of favorite movies
    num_favorites = user_favorites_query.count()
    num_movies = Movie.query.filter_by(user_id=user.id).count()

    movies = user_favorites_query.filter_by(user_id=user.id)
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
    """
    Display the list of movies added by the current user, 
    excluding their favorite movies.
    Parameters:
    None
    Returns:
    render_template: A rendered HTML template with 
    the list of movies and pagination details.
    """
    if not user_logged_in():
        return handle_not_logged_in()  # Handle case where user is not logged in

    user = user_logged_in()

    if user is None:
        return handle_invalid_user()
    # Get the current page from query parameters, default to 1
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Number of movies per page

    # Query to get the favorite movies of the user
    favorite_movie_ids = [f.movie_id for f in Favorite.query.filter_by(user_id=user.id).all()]

    # Query to get all movies added by the current user,
    # excluding the user's favorite movies
    movies_query = (
        Movie.query
        .filter(Movie.user_id == user.id)
        .filter(Movie.id.notin_(favorite_movie_ids))
    )
    # Count the total number of movies after filtering
    num_movies = movies_query.count()

    # Paginate the filtered query
    movies = movies_query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('my_movies.html', num_movies=num_movies, movies=movies)


@user_bp.route('/movie/<int:movie_id>', methods=['GET'])
def view_movie_details(movie_id):
    """
    View details of a specific movie added by the user.

    Parameters:
    - movie_id (int): The ID of the movie to display details for.

    Returns:
    - render_template: A rendered HTML template displaying the movie details.
    """
    if not user_logged_in():
        return handle_not_logged_in()  # Redirect if the user is not logged in

    user = user_logged_in()
    if user is None:
        return handle_invalid_user()

    # Query the movie to ensure it belongs to the current user
    movie = Movie.query.filter_by(id=movie_id, user_id=user.id).first()

    if movie is None:
        flash("Movie not found or you do not have permission to view it.", "error")
        return redirect(url_for('user_bp.my_movies'))  # Redirect back to movie list if not found

    # Render the movie details page
    return render_template('view_movie_details.html', movie=movie)


@user_bp.route('/user_favorites')
def user_favorites():
    """
    This function handles the user's favorite movies page. 
    It retrieves the favorite movies of the user
    from the database and paginates the results.

    Parameters:
    None

    Returns:
    render_template: A rendered HTML template for 
    the user's favorite movies page.
    """
    if not user_logged_in():
        return handle_not_logged_in()  # Handle case where user is not logged in

    user = user_logged_in()

    if user is None:
        return handle_invalid_user()
    # Get the current page from query parameters, default to 1
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Number of movies per page

    # Query to get the favorite movies of the user with pagination
    user_favorites_query = (
        Movie.query.join(Favorite)
        .filter(Favorite.user_id == user.id, Favorite.movie_id == Movie.id)
    )

    # Count the total number of favorite movies
    num_favorites = user_favorites_query.count()

    # Paginate the query
    movies = user_favorites_query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('user_favorites.html', num_favorites=num_favorites, movies=movies)


@user_bp.route('/add_to_favorites/<int:movie_id>', methods=['POST'])
def add_to_favorites(movie_id):
    """
    Adds a movie to the user's favorites.
    Parameters:
    movie_id (int): The ID of the movie to be added to favorites.
    Returns:
    Redirects to the user's favorites page with 
    a success message if the movie is successfully added.
    Redirects to the user's movies page with 
    an error message if the movie is already in favorites.
    Redirects to the login page if the user is not logged in.
    """
    if not user_logged_in():
        return handle_not_logged_in()  # Handle case where user is not logged in

    user = user_logged_in()

    if user is None:
        return handle_invalid_user()

    movie = Movie.query.get(movie_id)

    if not movie:
        flash('Movie not found.', 'error')
        return redirect(url_for('user_bp.my_movies'))

    # Check if the movie is already a favorite
    existing_favorite = Favorite.query.filter_by(user_id=user.id, movie_id=movie_id).first()
    if existing_favorite:
        flash('Movie is already in your favorites.', 'info')
        return redirect(url_for('user_bp.my_movies'))

    # Add movie to favorites
    new_favorite = Favorite(user_id=user.id, movie_id=movie_id)
    db.session.add(new_favorite)
    db.session.commit()
    flash('Movie added to favorites!', 'success')

    # Get the updated number of favorite movies
    num_favorites = Favorite.query.filter_by(user_id=user.id).count()

    # Redirect to the same page after adding to favorites
    return redirect(
        url_for('user_bp.user_favorites',
                page=request.args.get('page', 1, type=int),
                num_favorites=num_favorites))


@user_bp.route('/remove_from_favorites/<int:movie_id>', methods=['POST'])
def remove_from_favorites(movie_id):
    """
    Remove a movie from the user's favorites.
    Parameters:
    movie_id (int): The ID of the movie to be removed.
    Returns:
    Redirects to the user's favorite movies page with 
    a success message or an error message.
    """
    if not user_logged_in():
        return handle_not_logged_in()  # Handle case where user is not logged in

    user = user_logged_in()

    if user is None:
        return handle_invalid_user()

    movie = Movie.query.get(movie_id)

    if not movie:
        flash('Movie not found.', 'error')
        return redirect(url_for('user_bp.my_movies'))

    # Find the favorite entry
    favorite = Favorite.query.filter_by(user_id=user.id, movie_id=movie_id).first()
    if not favorite:
        flash('Movie is not in your favorites.', 'info')
        return redirect(url_for('user_bp.my_movies'))

    # Remove movie from favorites
    db.session.delete(favorite)
    db.session.commit()
    flash('Movie removed from favorites!', 'success')

    # Get the updated number of favorite movies
    num_favorites = Favorite.query.filter_by(user_id=user.id).count()

    # Redirect to the same page after removing from favorites
    return redirect(
        url_for('user_bp.user_favorites',
                page=request.args.get('page', 1, type=int),
                num_favorites=num_favorites))


@user_bp.route('/user_add_movie', methods=['GET', 'POST'])
def user_add_movie():
    """
    Handles the addition of a new movie by a user.
    """
    if not user_logged_in():
        return handle_not_logged_in()  # Handle case where user is not logged in

    user = user_logged_in()

    if user is None:
        return handle_invalid_user()

    if request.method == 'POST':
        return handle_post_request()

    # For GET request, prepare the list of genres
    genres = Genre.query.all()
    return render_template('user_add_movie.html', genres=genres)


@user_bp.route('/edit_movie/<int:movie_id>', methods=['GET', 'POST'])
def user_edit_movie(movie_id):
    """
    Handles the editing of a movie by a user.
    """
    if not user_logged_in():
        return handle_not_logged_in()  # Handle case where user is not logged in

    user = user_logged_in()

    if user is None:
        return handle_invalid_user()

    movie = Movie.query.get_or_404(movie_id)

    if movie.user_id != user.id:
        flash('You are not authorized to edit this movie.', 'warning')
        return redirect(url_for('user_bp.my_movies'))

    if request.method == 'POST':
        return handle_movie_update(movie)

    genres = Genre.query.all()  # To display available genres
    return render_template('user_edit_movie.html', movie=movie, genres=genres, user=user)


@user_bp.route('/delete_movie/<int:movie_id>', methods=['POST'])
def delete_movie(movie_id):
    """
    Deletes a movie from the database.
    Parameters:
    movie_id (int): The ID of the movie to be deleted.
    Returns:
    - If the movie belongs to the current user,
      it deletes the movie and redirects to the 'my_movies' page.
    - If the movie does not belong to the current user,
      it redirects to the 'my_movies' page with a warning message.
    - If an error occurs during the deletion process,
      it rolls back the changes and displays an error message.
    """
    if not user_logged_in():
        return handle_not_logged_in()  # Handle case where user is not logged in

    user = user_logged_in()

    if user is None:
        return handle_invalid_user()

    # Get the movie and check if it belongs to the current user
    movie = Movie.query.filter_by(id=movie_id, user_id=user.id).first_or_404()

    try:
        # Remove associations from the movie_genre association table
        movie.genres.clear()

        # Now delete the movie
        db.session.delete(movie)
        db.session.commit()
        flash('Movie deleted successfully!', 'success')
    except IntegrityError:
        db.session.rollback()  # Rollback on integrity error
        flash('Error deleting movie: Integrity error occurred.', 'danger')
    except OperationalError:
        db.session.rollback()  # Rollback on operational error
        flash('Error deleting movie: A database operational error occurred.', 'danger')
    except SQLAlchemyError:
        db.session.rollback()  # Rollback on SQLAlchemy-related errors
        flash('Error deleting movie: A database error occurred.', 'danger')

    return redirect(url_for('user_bp.my_movies'))


@user_bp.route('/user_profile')
def user_profile():
    """
    This function handles the user profile page.
    It checks if the user is logged in, 
    fetches the user's data from the database,
    and renders the 'user_profile.html' 
    template with the user's information.
    Parameters:
    None
    Returns:
    - If the user is logged in, it returns the 'user_profile.html' template
      with the user's information.
    - If the user is not logged in, it redirects to the 'login' page.
    """
    if not user_logged_in():
        return handle_not_logged_in()  # Handle case where user is not logged in

    user = user_logged_in()

    if user is None:
        return handle_invalid_user()  # Handle case where user is not valid

    user_id = User.query.get(user.id)

    return render_template('user_profile.html', user=user_id)


@user_bp.route('/edit_user_profile/<int:user_id>', methods=['GET', 'POST'])
def edit_user_profile(user_id):
    """
    This function handles the editing of a user's profile.
    It checks if the user is logged in, 
    fetches the user's data from the database,
    validates the data, and updates the user object.
    Parameters:
    user_id (int): The ID of the user whose profile is being edited.
    Returns:
    - If the request method is POST, it returns 
      a redirect to the 'user_profile' page
      if the user's profile is successfully updated.
      Otherwise, it returns the 'edit_user_profile.html'
      template with the user's information.
    - If the request method is GET, it returns
      the 'edit_user_profile.html' template
      with the user's information.
    """
    if not user_logged_in():
        return handle_not_logged_in()  # Handle case where user is not logged in

    user = user_logged_in()

    if user is None:
        return handle_invalid_user()  # Handle case where user is not valid

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
        # Ensure the password is not blank
        if new_password and new_password.strip():
            user.password = generate_password_hash(new_password)
            # Optional timestamp for tracking password updates
            user.password_update_date = datetime.now()

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
