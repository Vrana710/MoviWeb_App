from flask import (redirect,
                   url_for,
                   flash
                   )
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, OperationalError
from models import db, Movie
from controllers.common_fun import (user_logged_in,
                                    handle_invalid_user,
                                    handle_not_logged_in
                                    )


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
