import os
from flask import render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from models import db, User
from controllers.common_fun import (admin_logged_in, handle_invalid_admin, handle_not_logged_in, allowed_file)


def add_user():
    """
    This function handles user registration.
    It checks if the user is logged in as an admin, validates the user input,
    and saves the user's information to the database.
    Parameters:
    None
    Returns:
    - If the user is not logged in as an admin, it redirects to the login page.
    - If the user input is invalid, it displays an error message and
    redirects to the registration page.
    - If the user registration is successful,
    it displays a success message and redirects to the manage users page.
    """
    if not admin_logged_in():
        return handle_not_logged_in()

    admin = admin_logged_in()

    if admin is None:
        return handle_invalid_admin()  # Handle case where admin is not logged in

    if not admin:
        flash('You must be logged in as an admin to add a movie.', 'warning')
        return redirect(url_for('admin_bp.login'))

    if request.method == 'POST':
        user_name = request.form['name']
        user_email = request.form['email']
        user_password = request.form['password']
        user_gender = request.form.get('gender')  # Optional gender field

        if not user_email:
            flash('Email is required to create a user.', 'error')
            return redirect(url_for('admin_bp.add_user'))

        if User.query.filter_by(email=user_email).first():
            flash('Email address already exists. Please use a different email.', 'error')
            return redirect(url_for('admin_bp.add_user'))

        hashed_password = generate_password_hash(user_password)

        # Handle profile picture upload
        profile_picture_filename = None
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                profile_picture_filename = filename
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        new_user = User(
            name=user_name,
            email=user_email,
            password=hashed_password,
            gender=user_gender,
            profile_picture=profile_picture_filename,  # Save only filename
            admin_id=admin.id  # Admin who is adding the user
        )
        db.session.add(new_user)
        db.session.commit()
        flash('User registration successful!', 'success')
        return redirect(url_for('admin_bp.manage_users', admin=admin))

    return render_template('add_user.html', admin=admin)
