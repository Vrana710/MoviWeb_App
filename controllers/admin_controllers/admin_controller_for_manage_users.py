from flask import render_template, request
from models import User, Movie
from controllers.common_fun import (admin_logged_in,
                                    handle_invalid_admin,
                                    handle_not_logged_in)


def manage_users():
    """
    This function handles the management of users for the current admin.
    If the admin is not logged in, the session is cleared,
    the cache is cleared if it exists,
    and the user is redirected to the login page.
    The function then fetches the admin from the database,
    counts the number of users and movies
    associated with the admin, and paginates the users for display.
    If the request is an AJAX request, the function renders and
    returns only the table and
    pagination controls. Otherwise, it renders
    the 'manage_users.html' template with the necessary
    data.
    Parameters:
    None
    Returns:
    render_template: A rendered template displaying the table and
    pagination controls for AJAX requests.
    render_template: A rendered template displaying the user management page.
    """
    if not admin_logged_in():
        return handle_not_logged_in()

    admin = admin_logged_in()

    if admin is None:
        return handle_invalid_admin()  # Handle case where admin is not logged in

    # Count users and movies for display purposes, filtering by admin_id
    num_users = User.query.filter_by(admin_id=admin.id).count()
    num_movies = Movie.query.filter_by(admin_id=admin.id).count()

    page = request.args.get('page', 1, type=int)
    per_page = 5  # Set how many users to display per page

    # Paginate users, filtering by admin_id
    users = User.query.filter_by(admin_id=admin.id).paginate(page=page, per_page=per_page)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Render and return only the table and pagination controls for AJAX requests
        return render_template('partials/manage_users_content.html', users=users)

    return render_template('manage_users.html',
                           num_users=num_users,
                           num_movies=num_movies,
                           users=users,
                           admin=admin)
