from flask import render_template, request
from models import User
from controllers.common_fun import (admin_logged_in,
                                    handle_invalid_admin,
                                    handle_not_logged_in)


def manage_all_users():
    """
    This function handles the management of all users in the application.
    It checks if the user is logged in, clears the cache if necessary,
    and redirects to the login page if not.
    It then fetches the total number of users and all users,
    paginates the users for display, and renders
    the appropriate template based on the request type.
    Parameters:
    None
    Returns:
    render_template: A rendered template displaying all users
    if the request is not AJAX.
    render_template: A rendered template containing only
    the table and pagination controls for AJAX requests.
    """
    if not admin_logged_in():
        return handle_not_logged_in()

    admin = admin_logged_in()

    if admin is None:
        return handle_invalid_admin()  # Handle case where admin is not logged in

    # Count users and movies for display purposes, filtering by admin_id
    num_users = User.query.count()

    page = request.args.get('page', 1, type=int)
    per_page = 5  # Set how many users to display per page

    # Paginate users, filtering by admin_id
    users = User.query.paginate(page=page, per_page=per_page)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Render and return only the table and pagination controls for AJAX requests
        return render_template('partials/manage_all_users_content.html', users=users)

    return render_template('manage_all_users.html',
                           num_users=num_users,
                           users=users,
                           admin=admin)
