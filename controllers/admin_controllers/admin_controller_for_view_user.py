from flask import render_template
from models import User
from controllers.common_fun import (admin_logged_in,
                                    handle_invalid_admin,
                                    handle_not_logged_in
                                    )


def view_user(user_id):
    """
    This function handles the user profile page.
    Parameters:
    None
    Returns:
    - view_user_profile.html' template with the user's information.
    - If the admin is not logged in, it redirects to the 'login' page.
    """
    if not admin_logged_in():
        return handle_not_logged_in()

    admin = admin_logged_in()

    if admin is None:
        return handle_invalid_admin()  # Handle case where admin is not logged in

    # user = User.query.filter_by(id=user_id, admin_id=admin_id).first_or_404()
    user = User.query.filter_by(id=user_id).first_or_404()

    return render_template('view_user.html', user=user)
