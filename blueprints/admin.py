# admin.py

import os
from datetime import datetime
from flask import (Blueprint,
                   render_template,
                   request,
                   redirect,
                   url_for,
                   session,
                   flash,
                   current_app)
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from models import db, User, Movie, Director, Admin, Genre
from blueprints.utils import _fetch_movie_data


admin_bp = Blueprint('admin_bp', __name__,
                     template_folder=os.path.join(os.path.dirname(__file__),
                                                  '../templates/admin'))


@admin_bp.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    return render_template('admin_dashboard.html')


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Add this function to fetch the current admin
def get_current_admin():
    if 'admin_id' in session:
        return Admin.query.get(session['admin_id'])
    return None


@admin_bp.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    admin = get_current_admin()  # Fetch the current admin from session

    if not admin:
        flash('You must be logged in as an admin to add a movie.', 'warning')
        return redirect(url_for('admin_bp.login'))

    if request.method == 'POST':
        user_name = request.form['name']
        user_email = request.form['email']
        user_password = request.form['password']
        user_gender = request.form.get('gender')  # Optional gender field
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
            admin_id=admin.id  # Admin who is adding the movie

        )
        db.session.add(new_user)
        db.session.commit()
        flash('User registration successful!', 'success')
        return redirect(url_for('admin_bp.manage_users'))

    return render_template('add_user.html')


@admin_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get_or_404(user_id)
    admin = get_current_admin()  # Fetch the current admin from session

    if not admin:
        flash('You must be logged in as an admin to add a movie.', 'warning')
        return redirect(url_for('admin_bp.login'))

    if request.method == 'POST':
        new_name = request.form.get('name', user.name)
        new_email = request.form.get('email', user.email)
        new_gender = request.form.get('gender', user.gender)  # Optional gender field
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
            user.password_update_date = datetime.now()  # Update password change timestamp

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

    return render_template('edit_user.html', user=user)


@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin_bp.manage_users'))


@admin_bp.route('/manage_users')
def manage_users():
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    users = User.query.all()
    return render_template('manage_users.html', users=users)


@admin_bp.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    admin = get_current_admin()  # Fetch the current admin from session

    if not admin:
        flash('You must be logged in as an admin to add a movie.', 'warning')
        return redirect(url_for('admin_bp.login'))

    if request.method == 'POST':
        title = request.form.get('title')

        if not title:
            flash('Title is required to fetch movie details.', 'error')
            return redirect(url_for('admin_bp.add_movie'))

        # Fetch the movie data using the title
        movie_data = _fetch_movie_data(title)

        if movie_data:
            # Validate the essential fields
            movie_title = movie_data.get('Title')
            if not movie_title:
                flash('Movie title not found in the fetched data.', 'error')
                return redirect(url_for('admin_bp.add_movie'))

            director_name = movie_data.get('Director')
            if not director_name:
                flash('Director not found in the fetched data.', 'error')
                return redirect(url_for('admin_bp.add_movie'))

            # Find or create the director
            director = Director.query.filter_by(name=director_name).first()
            if not director:
                director = Director(name=director_name)
                db.session.add(director)
                db.session.commit()

            # Create the movie object with the director's ID
            new_movie = Movie(
                title=movie_title,
                director_id=director.id,
                year=movie_data.get('Year') or None,
                rating=float(movie_data.get('imdbRating', 0)) if movie_data.get('imdbRating') else 0,
                poster=movie_data.get('Poster') or '',
                imdbID=movie_data.get('imdbID') or '',  # IMDb ID or link
                plot=movie_data.get('Plot') or '',
                user_id=request.form.get('user_id') or None,  # Optional: user ID
                admin_id=admin.id  # Admin who is adding the movie
            )

            # Handle genres if provided
            genres = movie_data.getlist('genres')
            for genre_name in genres:
                genre = Genre.query.filter_by(name=genre_name).first()
                if not genre:
                    genre = Genre(name=genre_name)
                    db.session.add(genre)
                    db.session.commit()
                new_movie.genres.append(genre)

            try:
                db.session.add(new_movie)
                db.session.commit()
                flash('Movie added successfully!', 'success')
                return redirect(url_for('admin_bp.manage_movies'))
            except IntegrityError as e:
                db.session.rollback()  # Rollback in case of error
                flash(f"Database error: {str(e)}", 'error')
                return redirect(url_for('admin_bp.add_movie'))
        else:
            flash('Movie not found in the API.', 'error')
            return redirect(url_for('admin_bp.add_movie'))

    users = User.query.all()  # To optionally assign a movie to a user
    genres = Genre.query.all()  # To display available genres

    return render_template('add_movie.html', users=users, genres=genres, admin=admin)


@admin_bp.route('/edit_movie/<int:movie_id>', methods=['GET', 'POST'])
def edit_movie(movie_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    admin = get_current_admin()  # Fetch the current admin from session

    if not admin:
        flash('You must be logged in as an admin to edit a movie.', 'warning')
        return redirect(url_for('admin_bp.login'))

    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':
        movie.title = request.form.get('title')
        director_name = request.form.get('director')

        # Find or create the director
        director = Director.query.filter_by(name=director_name).first()
        if not director:
            director = Director(name=director_name)
            db.session.add(director)
            db.session.commit()

        movie.director_id = director.id
        movie.year = int(request.form.get('year', movie.year))
        movie.rating = float(request.form.get('rating', movie.rating))
        movie.admin_id = admin.id  # Update admin ID to current admin

        # Handle genres if provided
        movie.genres = []
        genres = request.form.getlist('genres')
        for genre_name in genres:
            genre = Genre.query.filter_by(name=genre_name).first()
            if not genre:
                genre = Genre(name=genre_name)
                db.session.add(genre)
                db.session.commit()
            movie.genres.append(genre)

        try:
            db.session.commit()
            flash('Movie updated successfully!', 'success')
            return redirect(url_for('admin_bp.manage_movies'))
        except IntegrityError as e:
            db.session.rollback()  # Rollback in case of error
            flash(f"Database error: {str(e)}", 'error')
            return redirect(url_for('admin_bp.edit_movie', movie_id=movie_id))

    users = User.query.all()  # To assign movie to a user
    genres = Genre.query.all()  # To display available genres

    return render_template('edit_movie.html', movie=movie, users=users, genres=genres, admin=admin)


@admin_bp.route('/delete_movie/<int:movie_id>', methods=['POST'])
def delete_movie(movie_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('admin_bp.manage_movies'))


@admin_bp.route('/manage_movies')
def manage_movies():
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    movies = Movie.query.all()
    return render_template('manage_movies.html', movies=movies)


@admin_bp.route('/reports')
def reports():
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    num_users = User.query.count()
    num_movies = Movie.query.count()
    return render_template('reports.html', num_users=num_users, num_movies=num_movies)
