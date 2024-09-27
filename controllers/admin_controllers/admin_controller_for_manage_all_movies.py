from flask import render_template, request
from models import Movie
from controllers.common_fun import (admin_logged_in,
                                    handle_invalid_admin,
                                    handle_not_logged_in,
                                    )


def manage_all_movies():
    """
    This function handles the management of all movies.
    It checks if the user is logged in, clears the cache if necessary,
    and redirects to the login page if not.
    It then fetches the total number of movies,
    paginates the movies for display,
    and renders the appropriate template based on the request type.
    Parameters:
    None
    Returns:
    render_template: A rendered template displaying the movies.
    """
    if not admin_logged_in():
        return handle_not_logged_in()

    admin = admin_logged_in()

    if admin is None:
        return handle_invalid_admin()  # Handle case where admin is not logged in

    total_num_movies = Movie.query.count()

    # Pagination for admin's movies
    page = request.args.get('page', 1, type=int)
    per_page = 5
    movies = Movie.query.paginate(page=page, per_page=per_page)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Render and return only the table and pagination controls for AJAX requests
        return render_template('partials/manage_all_movies_content.html',
                               total_num_movies=total_num_movies,
                               all_movies=movies)  # Ensure consistent naming

    return render_template('manage_all_movies.html',
                           movies=movies,
                           admin=admin,
                           total_num_movies=total_num_movies)
