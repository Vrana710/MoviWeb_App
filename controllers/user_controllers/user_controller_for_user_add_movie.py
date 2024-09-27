
from flask import (render_template,
                   request)
from models import Genre
from controllers.common_fun import (user_logged_in,
                                    handle_invalid_user,
                                    handle_not_logged_in,
                                    handle_post_request_add_movie_by_user
                                    )


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
        return handle_post_request_add_movie_by_user()

    # For GET request, prepare the list of genres
    genres = Genre.query.all()
    return render_template('user_add_movie.html', genres=genres)
