
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
from controllers.common_fun import (user_logged_in,
                                    handle_invalid_user,
                                    handle_not_logged_in,
                                    allowed_file)


def edit_user_profile(user_id):
    """
    This function handles the editing of a user's profile.
    It checks if the user is logged in,
    fetches the user's data from the database,
    validates the data, and updates the user object.
    Parameters:
    user_id (int): The ID of the user whose profile is being edited.
    Returns:
    - If the request method is POST, it returns
      a redirect to the 'user_profile' page
      if the user's profile is successfully updated.
      Otherwise, it returns the 'edit_user_profile.html'
      template with the user's information.
    - If the request method is GET, it returns
      the 'edit_user_profile.html' template
      with the user's information.
    """
    if not user_logged_in():
        return handle_not_logged_in()  # Handle case where user is not logged in

    user = user_logged_in()

    if user is None:
        return handle_invalid_user()  # Handle case where user is not valid

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        new_name = request.form.get('name', user.name)
        new_email = request.form.get('email', user.email)
        new_gender = request.form.get('gender', user.gender)  # Optional gender field
        new_password = request.form.get('password', None)

        # Check if name has changed
        if new_name and user.name != new_name:
            user.name = new_name

        # Check if email has changed
        if new_email and user.email != new_email:
            user.email = new_email

        # Update the password only if a new password was provided
        # Ensure the password is not blank
        if new_password and new_password.strip():
            user.password = generate_password_hash(new_password)
            # Optional timestamp for tracking password updates
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

        db.session.commit()
        flash('Your profile updated successfully!', 'success')
        return redirect(url_for('user_bp.user_profile'))

    return render_template('edit_user_profile.html', user=user)
