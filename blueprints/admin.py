# admin.py
"""
This module defines the routes and functionality for the admin section of the application.
It includes routes for managing movies, users, and viewing reports, ensuring only admins
with valid sessions can access and modify the data.
"""
import os
from datetime import datetime
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, OperationalError
from flask import (Blueprint,
                   render_template,
                   request,
                   redirect,
                   url_for,
                   flash,
                   current_app)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from models import db, User, Movie, Genre, Favorite
from blueprints.common_fun import (admin_logged_in,
                                   handle_invalid_admin,
                                   handle_add_movie_post,
                                   handle_genres_for_movie,
                                   handle_not_logged_in,
                                   extract_movie_form_data,
                                   find_or_create_director,
                                   update_movie,
                                   allowed_file)

admin_bp = Blueprint('admin_bp', __name__,
                     template_folder=os.path.join(os.path.dirname(__file__),
                                                  '../templates/admin'))


@admin_bp.route('/admin_dashboard')
def admin_dashboard():
    """
    Admin dashboard page. Displays admin statistics, user and movie data.
    Parameters:
    None
    Returns:
    render_template: A rendered HTML template for the admin dashboard page.
    """
    if not admin_logged_in():
        return handle_not_logged_in()

    admin = admin_logged_in()

    if admin is None:
        return handle_invalid_admin()  # Handle case where admin is not logged in

    # Log the current admin ID
    print(f"Current admin ID: {admin}")

    # Fetch counts for users and movies
    counts = {
        'num_users': User.query.filter_by(admin_id=admin.id).count(),
        'num_movies': Movie.query.filter_by(admin_id=admin.id).count(),
        'num_users_total': User.query.count(),
        'num_movies_total': Movie.query.count(),
    }

    # Fetch users and their associated movie counts
    user_query = User.query.filter_by(admin_id=admin.id)
    users_with_movies = [
        {
            'user': user,
            'movies_count': Movie.query.filter_by(user_id=user.id).count()
        }
        for user in user_query
    ]

    # Get unique movies by IMDb ID
    unique_movies = []
    seen_imdb_ids = set()
    for movie in Movie.query.filter_by(admin_id=admin.id):
        if movie.imdbID not in seen_imdb_ids:
            seen_imdb_ids.add(movie.imdbID)
            unique_movies.append(movie)

    # Render the full page
    return render_template('admin_dashboard.html',
                           admin=admin,
                           users_with_movies=users_with_movies,
                           unique_movies=unique_movies,
                           **counts)  # Unpack counts dictionary into template variables


@admin_bp.route('/add_user', methods=['GET', 'POST'])
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


@admin_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
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


@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
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


@admin_bp.route('/view_user/<int:user_id>', methods=['GET', 'POST'])
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


@admin_bp.route('/manage_users')
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


@admin_bp.route('/manage_all_users')
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


@admin_bp.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    """
    Route for admins to add a movie to the database.
    Fetches movie data using the provided title, checks for existing movies, 
    and adds a new movie entry if all necessary fields are present. This route 
    also handles director and genre associations and assigns the movie to the 
    currently logged-in admin.
    Returns:
        - On success, redirects to the movie management page.
        - On failure, displays a flash message and redirects to the add movie form.
    """
    if not admin_logged_in():
        return handle_not_logged_in()

    admin = admin_logged_in()
    if not admin:
        return handle_invalid_admin()

    if request.method == 'POST':
        return handle_add_movie_post(admin)

    users = User.query.all()
    genres = Genre.query.all()

    return render_template('add_movie.html', users=users, genres=genres, admin=admin)


@admin_bp.route('/edit_movie/<int:movie_id>', methods=['GET', 'POST'])
def edit_movie(movie_id):
    """
    This function handles the editing of a movie.
    It checks if the user is logged in, clears the cache if necessary,
    and redirects to the login page if not.
    It then fetches the movie to be edited, updates its details based on
    the form data, and commits the changes to the database.
    If the request method is POST, it handles the form
    submission and updates the movie's details.
    If the request method is GET, it renders the edit movie template
    with the movie's details.
    Parameters:
    movie_id (int): The ID of the movie to be edited.
    Returns:
    redirect: A redirect to the 'manage_movies' route if
    the movie is successfully updated.
    render_template: A rendered template displaying
    the edit movie form if the request method is GET.
    """
    if not admin_logged_in():
        return handle_not_logged_in()

    admin = admin_logged_in()

    if admin is None:
        return handle_invalid_admin()  # Handle case where admin is not logged in

    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':
        form_data = extract_movie_form_data(request.form)
        director = find_or_create_director(form_data['director_name'])
        update_movie(movie, form_data, director, admin)

        # Handle genres
        handle_genres_for_movie(movie, form_data['genre_string'])

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
    """
    Deletes a movie from the database if it belongs to the current admin.
    First, it removes all associations from the movie_genre association table.
    Then, it removes any associated favorites.
    Finally, it deletes the movie itself.
    If the movie is found in the database but
    does not belong to the current admin,
    it redirects to the 'manage_movies' route with a
    flash message indicating an error.
    Parameters:
    movie_id (int): The ID of the movie to be deleted.
    Returns:
    redirect: A redirect to the 'manage_movies' route.
    """
    if not admin_logged_in():
        return handle_not_logged_in()

    admin = admin_logged_in()

    if admin is None:
        return handle_invalid_admin()  # Handle case where admin is not logged in

    # Get the movie and check if it belongs to the current admin
    movie = Movie.query.filter_by(id=movie_id, admin_id=admin.id).first_or_404()

    try:
        # Remove associations from the movie_genre association table
        movie.genres.clear()
        # Remove any associated favorites
        Favorite.query.filter_by(movie_id=movie_id).delete()
        # Now delete the movie
        db.session.delete(movie)
        db.session.commit()
        flash('Movie deleted successfully!', 'success')

    except IntegrityError as integrity_error:
        db.session.rollback()  # Rollback on integrity constraint violations
        flash(f'Integrity error while deleting movie: {str(integrity_error)}', 'danger')

    except OperationalError as operational_error:
        db.session.rollback()  # Rollback on operational errors
        flash(f'Operational error while deleting movie: {str(operational_error)}', 'danger')

    except SQLAlchemyError as db_error:
        db.session.rollback()  # Rollback on other SQLAlchemy-related errors
        flash(f'Database error while deleting movie: {str(db_error)}', 'danger')

    return redirect(url_for('admin_bp.manage_movies', admin=admin))


@admin_bp.route('/delete_any_movie/<int:movie_id>', methods=['POST'])
def delete_any_movie(movie_id):
    """
    Deletes a movie from the database, regardless of who added it.
    First, it deletes all related favorites from the favorites table.
    Then, it deletes the movie itself.
    If the movie is found in the database, it is deleted and a success message is flashed.
    If the movie is not found, a message indicating that the movie was not found is flashed.
    Parameters:
    movie_id (int): The ID of the movie to be deleted.
    Returns:
    redirect: A redirect to the 'manage_all_movies' route.
    """
    if not admin_logged_in():
        return handle_not_logged_in()

    admin = admin_logged_in()

    if admin is None:
        return handle_invalid_admin()  # Handle case where admin is not logged in

    # First, delete related favorites
    Favorite.query.filter_by(movie_id=movie_id).delete()
    # Then, delete the movie
    movie = Movie.query.get(movie_id)
    if movie:
        db.session.delete(movie)
        db.session.commit()
        flash('Movie deleted successfully.')
    else:
        flash('Movie not found.')

    return redirect(url_for('admin_bp.manage_all_movies'))


@admin_bp.route('/manage_movies')
def manage_movies():
    """
    This function handles the management of movies for the current admin.
    It checks if the user is logged in, clears the cache if necessary, 
    and redirects to the login page if not.
    It then fetches the total number of movies added by the current admin 
    and all movies,
    paginates the admin's movies for display, and renders 
    the appropriate template based on the request type.
    Parameters:
    None
    Returns:
    render_template: A rendered template displaying the admin's movies.
    """
    if not admin_logged_in():
        return handle_not_logged_in()

    admin = admin_logged_in()

    if admin is None:
        return handle_invalid_admin()  # Handle case where admin is not logged in

    # Filter movies by the current admin's ID
    num_movies = Movie.query.filter_by(admin_id=admin.id).count()
    total_num_movies = Movie.query.count()

    # Pagination for admin's movies
    page = request.args.get('page', 1, type=int)
    per_page = 5
    movies = Movie.query.filter_by(admin_id=admin.id).paginate(page=page, per_page=per_page)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Render and return only the table and pagination controls for AJAX requests
        return render_template('partials/manage_movies_content.html',
                               num_movies=num_movies,
                               movies=movies,
                               admin=admin)

    return render_template('manage_movies.html',
                           num_movies=num_movies,
                           movies=movies,
                           admin=admin,
                           total_num_movies=total_num_movies
                           )


@admin_bp.route('/manage_all_movies')
def manage_all_movies():
    """
    This function handles the management of all movies.
    It checks if the user is logged in, clears the cache if necessary,
    and redirects to the login page if not. 
    It then fetches the total number of movies,
    paginates the movies for display, 
    and renders the appropriate template based on the request type.
    Parameters:
    None
    Returns:
    render_template: A rendered template displaying the movies.
    """
    if not admin_logged_in():
        return handle_not_logged_in()

    admin = admin_logged_in()

    if admin is None:
        return handle_invalid_admin()  # Handle case where admin is not logged in

    total_num_movies = Movie.query.count()

    # Pagination for admin's movies
    page = request.args.get('page', 1, type=int)
    per_page = 5
    movies = Movie.query.paginate(page=page, per_page=per_page)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Render and return only the table and pagination controls for AJAX requests
        return render_template('partials/manage_all_movies_content.html',
                               total_num_movies=total_num_movies,
                               all_movies=movies)  # Ensure consistent naming

    return render_template('manage_all_movies.html',
                           movies=movies,
                           admin=admin,
                           total_num_movies=total_num_movies)


@admin_bp.route('/reports')
def reports():
    """
    Render the reports page for the currently logged-in admin.
    This route checks if an admin is logged in. If not, it clears the session
    and any cache, then redirects to the login page. If an admin is logged in,
    it fetches and counts the number of users and movies associated with the
    admin, as well as the total number of users and movies in the database.
    Returns:
        - Rendered HTML page with reports data if admin is logged in.
        - Redirects to login page if admin is not logged in.
    """
    if not admin_logged_in():
        return handle_not_logged_in()

    admin = admin_logged_in()

    if admin is None:
        return handle_invalid_admin()  # Handle case where admin is not logged in

    # Filter movies by the current admin's ID
    num_users = User.query.filter_by(admin_id=admin.id).count()
    # Filter movies by the current admin's ID
    num_movies = Movie.query.filter_by(admin_id=admin.id).count()

    # Count all users and movies for display purposes
    num_users_total = User.query.count()
    num_movies_total = Movie.query.count()

    # Render the full page
    return render_template('reports.html',
                           num_users=num_users,
                           num_movies=num_movies,
                           admin=admin,
                           num_users_total=num_users_total,
                           num_movies_total=num_movies_total
                           )


@admin_bp.route('/all_movies_added_by_user_of_current_admin_report')
def all_movies_added_by_user_of_current_admin_report():
    """
    This function handles the report of movies added by
    users under the current admin.
    It fetches the users, counts the movies they added,
    and paginates them for display.
    It also checks if the request is an AJAX request and
    renders the appropriate template accordingly.

    Parameters:
    None

    Returns:
    render_template: A rendered template displaying the users and
    their associated movies.
    """
    if not admin_logged_in():
        return handle_not_logged_in()

    admin = admin_logged_in()

    if admin is None:
        return handle_invalid_admin()  # Handle case where admin is not logged in

    # Set the page number from the request args or default to 1
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Set how many users to display per page

    # Get users filtered by admin_id with pagination
    paginated_users = User.query.filter_by(admin_id=admin.id).paginate(page=page, per_page=per_page)

    # Prepare the list of users with their movie counts
    users_with_movies = [{
        'user': user,
        'movies_count': Movie.query.filter_by(user_id=user.id).count()
    } for user in paginated_users.items]

    # Get all movies added by users under the current admin (optional)
    movies = Movie.query.filter_by(admin_id=admin.id).all()  # Consider using .all() if you need all movies

    # Check if the request is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Render only the table and pagination
        return render_template('partials/all_movies_added_by_user_of_current_admin_content.html',
                               users_with_movies=users_with_movies,
                               admin=admin,
                               movies=movies,
                               pagination=paginated_users
                               )

    # Render the full page
    return render_template('all_movies_added_by_user_of_current_admin_report.html',
                           users_with_movies=users_with_movies,
                           admin=admin,
                           movies=movies,
                           pagination=paginated_users)  # Pass the pagination object if needed


@admin_bp.route('/details_view_of_movies_added_by_user_of_current_admin_report/<int:user_id>')
def details_view_of_movies_added_by_user_of_current_admin_report(user_id):
    """
    This function handles the details view of movies 
    added by a specific user under the current admin.
    It fetches the movies, counts them, and paginates them for display.
    It also checks if the request is an AJAX request 
    and renders the appropriate template accordingly.
    Parameters:
    user_id (int): The ID of the user whose movies are to be displayed.
    Returns:
    render_template: A rendered template displaying 
    the movies added by the specified user.
    """
    if not admin_logged_in():
        return handle_not_logged_in()

    admin = admin_logged_in()

    if admin is None:
        return handle_invalid_admin()  # Handle case where admin is not logged in

    print(f"Admin ID: {admin}, User ID: {user_id}")

    num_movies = Movie.query.filter_by(user_id=user_id).count()
    # Set the page number from the request args or default to 1
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Set how many movies to display per page

    # Fetch movies for the specified user with pagination,
    # filtered by the admin's ID
    movies = (
        Movie.query.filter_by(user_id=user_id)
        .order_by(Movie.title.asc())
        .paginate(page=page, per_page=per_page)
    )
    # Check if the request is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Render only the table and pagination
        return render_template(
            'partials/details_view_of_movies_added_by_user_of_current_admin_content.html',
            num_movies=num_movies,
            movies=movies,  # Pass movies for rendering
            user=User.query.get(user_id),  # Pass the specific user
            admin=admin
        )

    # Render the full page
    return render_template(
        'details_view_of_movies_added_by_user_of_current_admin_report.html',
        num_movies=num_movies,
        movies=movies,  # Pass movies for rendering
        user=User.query.get(user_id),  # Pass the specific user
        admin=admin
    )
