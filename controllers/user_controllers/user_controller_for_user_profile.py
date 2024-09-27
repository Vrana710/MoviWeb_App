from flask import render_template
from models import User
from controllers.common_fun import (user_logged_in,
                                    handle_invalid_user,
                                    handle_not_logged_in
                                    )


def user_profile():
    """
    This function handles the user profile page.
    It checks if the user is logged in,
    fetches the user's data from the database,
    and renders the 'user_profile.html'
    template with the user's information.
    Parameters:
    None
    Returns:
    - If the user is logged in, it returns the 'user_profile.html' template
      with the user's information.
    - If the user is not logged in, it redirects to the 'login' page.
    """
    if not user_logged_in():
        return handle_not_logged_in()  # Handle case where user is not logged in

    user = user_logged_in()

    if user is None:
        return handle_invalid_user()  # Handle case where user is not valid

    user_id = User.query.get(user.id)

    return render_template('user_profile.html', user=user_id)
