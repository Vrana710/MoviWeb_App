from flask import redirect, url_for, flash
from models import db, Movie, Favorite
from controllers.common_fun import (admin_logged_in,
                                    handle_invalid_admin,
                                    handle_not_logged_in)


def delete_any_movie(movie_id):
    """
    Deletes a movie from the database, regardless of who added it.
    First, it deletes all related favorites from the favorites table.
    Then, it deletes the movie itself.
    If the movie is found in the database, it is deleted and a success message is flashed.
    If the movie is not found, a message indicating that the movie was not found is flashed.
    Parameters:
    movie_id (int): The ID of the movie to be deleted.
    Returns:
    redirect: A redirect to the 'manage_all_movies' route.
    """
    if not admin_logged_in():
        return handle_not_logged_in()

    admin = admin_logged_in()

    if admin is None:
        return handle_invalid_admin()  # Handle case where admin is not logged in

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
