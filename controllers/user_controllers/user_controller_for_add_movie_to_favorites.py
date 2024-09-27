

from flask import (request,
                   redirect,
                   url_for,
                   flash)
from models import db, Movie, Favorite
from controllers.common_fun import (user_logged_in,
                                    handle_invalid_user,
                                    handle_not_logged_in
                                    )


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
