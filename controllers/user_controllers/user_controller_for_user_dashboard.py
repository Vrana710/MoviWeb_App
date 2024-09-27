from flask import render_template
from models import User, Movie, Favorite
from controllers.common_fun import (user_logged_in,
                                    handle_invalid_user,
                                    handle_not_logged_in)


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
