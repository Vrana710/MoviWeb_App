import os
from datetime import datetime
from flask import (render_template,
                   request,
                   redirect,
                   url_for,
                   flash,
                   current_app)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from models import db, User
from controllers.common_fun import (admin_logged_in,
                                    handle_invalid_admin,
                                    handle_not_logged_in,
                                    allowed_file)


def edit_user(user_id):
    """
    Update user details.
    Parameters:
    user_id (int): The ID of the user to be updated.
    Returns:
    redirect: Redirects to the login page if the user is not
    logged in as an admin.
    redirect: Redirects to the manage users page
    if the user is successfully updated.
    """
    if not admin_logged_in():
        return handle_not_logged_in()

    admin = admin_logged_in()

    if admin is None:
        return handle_invalid_admin()  # Handle case where admin is not logged in

    # user = User.query.filter_by(id=user_id, admin_id=admin_id).first_or_404()
    user = User.query.filter_by(id=user_id).first_or_404()

    if request.method == 'POST':
        new_name = request.form.get('name', user.name)
        new_email = request.form.get('email', user.email)
        # Optional gender field
        new_gender = request.form.get('gender', user.gender)
        new_password = request.form.get('password', None)

        # Debugging: Print old and new passwords
        if new_password:
            print(f"Old Password Hash: {user.password}")
            print(f"New Password: {generate_password_hash(new_password)}")

        # Check if name has changed
        if new_name and user.name != new_name:
            user.name = new_name

        # Check if email has changed
        if new_email and user.email != new_email:
            user.email = new_email

        # Check if password has changed
        if new_password:
            user.password = generate_password_hash(new_password)
            # Update password change timestamp
            user.password_update_date = datetime.now()

        # Check if gender has changed
        if new_gender and user.gender != new_gender:
            user.gender = new_gender

        # Handle profile picture upload (optional)
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                profile_picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(profile_picture_path)
                user.profile_picture = filename  # Save only the filename

                # Debugging: Print profile picture details
                print(f"Profile Picture Filename: {filename}")
                print(f"Profile Picture Path: {profile_picture_path}")

        user.admin_id = admin.id  # Admin who is Updating the user

        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin_bp.manage_users'))

    return render_template('edit_user.html', user=user, admin=admin)
