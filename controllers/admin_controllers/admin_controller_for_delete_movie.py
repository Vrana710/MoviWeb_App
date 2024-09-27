from sqlalchemy.exc import IntegrityError, SQLAlchemyError, OperationalError
from flask import redirect, url_for, flash
from models import db, Movie, Favorite
from controllers.common_fun import (admin_logged_in,
                                    handle_invalid_admin,
                                    handle_not_logged_in)


def delete_movie(movie_id):
    """
    Deletes a movie from the database if it belongs to the current admin.
    First, it removes all associations from the movie_genre association table.
    Then, it removes any associated favorites.
    Finally, it deletes the movie itself.
    If the movie is found in the database but
    does not belong to the current admin,
    it redirects to the 'manage_movies' route with a
    flash message indicating an error.
    Parameters:
    movie_id (int): The ID of the movie to be deleted.
    Returns:
    redirect: A redirect to the 'manage_movies' route.
    """
    if not admin_logged_in():
        return handle_not_logged_in()

    admin = admin_logged_in()

    if admin is None:
        return handle_invalid_admin()  # Handle case where admin is not logged in

    # Get the movie and check if it belongs to the current admin
    movie = Movie.query.filter_by(id=movie_id, admin_id=admin.id).first_or_404()

    try:
        # Remove associations from the movie_genre association table
        movie.genres.clear()
        # Remove any associated favorites
        Favorite.query.filter_by(movie_id=movie_id).delete()
        # Now delete the movie
        db.session.delete(movie)
        db.session.commit()
        flash('Movie deleted successfully!', 'success')

    except IntegrityError as integrity_error:
        db.session.rollback()  # Rollback on integrity constraint violations
        flash(f'Integrity error while deleting movie: {str(integrity_error)}', 'danger')

    except OperationalError as operational_error:
        db.session.rollback()  # Rollback on operational errors
        flash(f'Operational error while deleting movie: {str(operational_error)}', 'danger')

    except SQLAlchemyError as db_error:
        db.session.rollback()  # Rollback on other SQLAlchemy-related errors
        flash(f'Database error while deleting movie: {str(db_error)}', 'danger')

    return redirect(url_for('admin_bp.manage_movies', admin=admin))
