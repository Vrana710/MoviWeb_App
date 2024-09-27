from flask import render_template
from models import User, Movie
from controllers.common_fun import (admin_logged_in, handle_invalid_admin, handle_not_logged_in)


def admin_dashboard():
    """
    Admin dashboard page. Displays admin statistics, user and movie data.
    Parameters:
    None
    Returns:
    render_template: A rendered HTML template for the admin dashboard page.
    """
    if not admin_logged_in():
        return handle_not_logged_in()

    admin = admin_logged_in()

    if admin is None:
        return handle_invalid_admin()  # Handle case where admin is not logged in

    # Log the current admin ID
    print(f"Current admin ID: {admin}")

    # Fetch counts for users and movies
    counts = {
        'num_users': User.query.filter_by(admin_id=admin.id).count(),
        'num_movies': Movie.query.filter_by(admin_id=admin.id).count(),
        'num_users_total': User.query.count(),
        'num_movies_total': Movie.query.count(),
    }

    # Fetch users and their associated movie counts
    user_query = User.query.filter_by(admin_id=admin.id)
    users_with_movies = [
        {
            'user': user,
            'movies_count': Movie.query.filter_by(user_id=user.id).count()
        }
        for user in user_query
    ]

    # Get unique movies by IMDb ID
    unique_movies = []
    seen_imdb_ids = set()
    for movie in Movie.query.filter_by(admin_id=admin.id):
        if movie.imdbID not in seen_imdb_ids:
            seen_imdb_ids.add(movie.imdbID)
            unique_movies.append(movie)

    # Render the full page
    return render_template('admin_dashboard.html',
                           admin=admin,
                           users_with_movies=users_with_movies,
                           unique_movies=unique_movies,
                           **counts)  # Unpack counts dictionary into template variables
