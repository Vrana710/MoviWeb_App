
from flask import render_template, request
from models import Movie, Favorite
from controllers.common_fun import (user_logged_in,
                                    handle_invalid_user,
                                    handle_not_logged_in,
                                    )


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
