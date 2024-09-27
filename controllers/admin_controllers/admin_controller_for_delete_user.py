from flask import (redirect,
                   url_for,
                   flash)
from models import db, User
from controllers.common_fun import (admin_logged_in,
                                    handle_invalid_admin,
                                    handle_not_logged_in)


def delete_user(user_id):
    """
    Deletes a user from the database.
    Parameters:
    user_id (int): The unique identifier of the user to be deleted.
    Returns:
    Redirects to the 'manage_users' page with a success flash message.
    """
    if not admin_logged_in():
        return handle_not_logged_in()

    admin = admin_logged_in()

    if admin is None:
        return handle_invalid_admin()  # Handle case where admin is not logged in

    # Ensure the user belongs to the current admin (if applicable)
    user = User.query.filter_by(id=user_id).first_or_404()

    # Delete the user if it belongs to the current admin
    db.session.delete(user)
    db.session.commit()

    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin_bp.manage_users', admin=admin))
