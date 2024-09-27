from flask import (request,
                   redirect,
                   url_for,
                   flash
                   )

from models import db, Movie, Favorite
from controllers.common_fun import (user_logged_in,
                                    handle_invalid_user,
                                    handle_not_logged_in
                                    )


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
