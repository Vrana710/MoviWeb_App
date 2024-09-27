

from flask import (
                   render_template,
                   request,
                   redirect,
                   url_for,
                   flash
                   )
from models import Movie, Genre
from controllers.common_fun import (user_logged_in,
                                    handle_invalid_user,
                                    handle_not_logged_in,
                                    handle_movie_update)


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
