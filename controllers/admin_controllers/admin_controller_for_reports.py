from flask import render_template
from models import User, Movie
from controllers.common_fun import (admin_logged_in,
                                    handle_invalid_admin,
                                    handle_not_logged_in
                                    )


def reports():
    """
    Render the reports page for the currently logged-in admin.
    This route checks if an admin is logged in. If not, it clears the session
    and any cache, then redirects to the login page. If an admin is logged in,
    it fetches and counts the number of users and movies associated with the
    admin, as well as the total number of users and movies in the database.
    Returns:
        - Rendered HTML page with reports data if admin is logged in.
        - Redirects to login page if admin is not logged in.
    """
    if not admin_logged_in():
        return handle_not_logged_in()

    admin = admin_logged_in()

    if admin is None:
        return handle_invalid_admin()  # Handle case where admin is not logged in

    # Filter movies by the current admin's ID
    num_users = User.query.filter_by(admin_id=admin.id).count()
    # Filter movies by the current admin's ID
    num_movies = Movie.query.filter_by(admin_id=admin.id).count()

    # Count all users and movies for display purposes
    num_users_total = User.query.count()
    num_movies_total = Movie.query.count()

    # Render the full page
    return render_template('reports.html',
                           num_users=num_users,
                           num_movies=num_movies,
                           admin=admin,
                           num_users_total=num_users_total,
                           num_movies_total=num_movies_total
                           )
