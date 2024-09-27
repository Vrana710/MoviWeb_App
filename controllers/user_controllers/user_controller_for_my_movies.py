from flask import render_template, request
from models import Movie, Favorite
from controllers.common_fun import (user_logged_in,
                                    handle_invalid_user,
                                    handle_not_logged_in)


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
