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
from models import db, User, Movie, Director, Favorite, Genre
from blueprints.utils import _fetch_movie_data


user_bp = Blueprint('user_bp', __name__,
                    template_folder=os.path.join(os.path.dirname(__file__),
                                                 '../templates/user'))


@user_bp.route('/dashboard')
def user_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login page if not authenticated

    user_id = session['user_id']
    user = User.query.get(user_id)
    latest_movies = Movie.query.order_by(Movie.id.desc()).limit(5).all()  # Latest movies

    return render_template('dashboard.html', user=user, latest_movies=latest_movies)


@user_bp.route('/my_movies')
def my_movies():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    # Query to get all movies
    all_movies = Movie.query.all()
    # Query to get the favorite movies of the user
    favorite_movie_ids = [f.movie_id for f in Favorite.query.filter_by(user_id=user_id).all()]
    # Filter out favorite movies from the list of all movies
    movies_to_display = [movie for movie in all_movies if movie.id not in favorite_movie_ids]

    return render_template('my_movies.html', movies=movies_to_display)


@user_bp.route('/user_favorites')
def user_favorites():
    if 'user_id' not in session:
        return redirect(url_for('user_bp.login'))

    user_id = session['user_id']
    # Query to get the favorite movies of the user
    user_favorite = Movie.query.join(Favorite).filter(Favorite.user_id == user_id, Favorite.movie_id == Movie.id).all()

    return render_template('user_favorites.html', movies=user_favorite)


@user_bp.route('/add_to_favorites/<int:movie_id>', methods=['POST'])
def add_to_favorites(movie_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    movie = Movie.query.get(movie_id)

    if not movie:
        flash('Movie not found.', 'error')
        return redirect(url_for('user_bp.my_movies'))

    # Check if the movie is already a favorite
    existing_favorite = Favorite.query.filter_by(user_id=user_id, movie_id=movie_id).first()
    if existing_favorite:
        flash('Movie is already in your favorites.', 'info')
        return redirect(url_for('user_bp.my_movies'))

    # Add movie to favorites
    new_favorite = Favorite(user_id=user_id, movie_id=movie_id)
    db.session.add(new_favorite)
    db.session.commit()
    flash('Movie added to favorites!', 'success')

    return redirect(url_for('user_bp.my_movies'))


@user_bp.route('/remove_from_favorites/<int:movie_id>', methods=['POST'])
def remove_from_favorites(movie_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    movie = Movie.query.get(movie_id)

    if not movie:
        flash('Movie not found.', 'error')
        return redirect(url_for('user_bp.my_movies'))

    # Find the favorite entry
    favorite = Favorite.query.filter_by(user_id=user_id, movie_id=movie_id).first()
    if not favorite:
        flash('Movie is not in your favorites.', 'info')
        return redirect(url_for('user_bp.my_movies'))

    # Remove movie from favorites
    db.session.delete(favorite)
    db.session.commit()
    flash('Movie removed from favorites!', 'success')

    return redirect(url_for('user_bp.my_movies'))


@user_bp.route('/user_add_movie', methods=['GET', 'POST'])
def user_add_movie():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_id = session['user_id']
        movie_title = request.form.get('title')

        if not movie_title:
            flash('Title is required to fetch movie details.', 'error')
            return redirect(url_for('user_bp.user_add_movie'))

        # Fetch movie data from an external source (API or other service)
        movie_data = _fetch_movie_data(movie_title)

        if movie_data:
            # Validate the essential fields
            title = movie_data.get('Title')
            if not title:
                flash('Movie title not found in the fetched data.', 'error')
                return redirect(url_for('user_bp.user_add_movie'))

            director_name = movie_data.get('Director')
            if not director_name:
                flash('Director not found in the fetched data.', 'error')
                return redirect(url_for('user_bp.user_add_movie'))

            # Find or create the director
            director = Director.query.filter_by(name=director_name).first()
            if not director:
                director = Director(name=director_name)
                db.session.add(director)
                db.session.commit()

            # Create the movie object with the director's ID
            new_movie = Movie(
                title=title,
                director_id=director.id,
                year=movie_data.get('Year') or None,
                rating=float(movie_data.get('imdbRating', 0)) if movie_data.get('imdbRating') else 0,
                poster=movie_data.get('Poster') or '',
                imdbID=movie_data.get('imdbID') or '',  # IMDb ID or link
                plot=movie_data.get('Plot') or '',
                admin_id=request.form.get('admin_id') or None,  # Optional: user ID
                user_id=user_id  # The user who is adding the movie
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
                return redirect(url_for('user_bp.my_movies'))
            except IntegrityError as e:
                db.session.rollback()  # Rollback in case of error
                flash(f"Database error: {str(e)}", 'error')
                return redirect(url_for('user_bp.user_add_movie'))
        else:
            flash('Movie not found in the API.', 'error')
            return redirect(url_for('user_bp.user_add_movie'))

    # For GET request, prepare the list of genres
    genres = Genre.query.all()

    return render_template('user_add_movie.html', genres=genres)


@user_bp.route('/user_profile')
def user_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = User.query.get(user_id)

    return render_template('user_profile.html', user=user)


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@user_bp.route('/edit_user_profile/<int:user_id>', methods=['GET', 'POST'])
def edit_user_profile(user_id):
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

        db.session.commit()
        flash('Your profile updated successfully!', 'success')
        return redirect(url_for('user_bp.user_profile'))

    return render_template('edit_user_profile.html', user=user)
