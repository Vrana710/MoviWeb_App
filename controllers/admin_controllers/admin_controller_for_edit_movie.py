from sqlalchemy.exc import IntegrityError
from flask import (render_template,
                   request,
                   redirect,
                   url_for,
                   flash)
from models import db, User, Movie, Genre
from controllers.common_fun import (admin_logged_in,
                                    handle_invalid_admin,
                                    handle_genres_for_movie,
                                    handle_not_logged_in,
                                    extract_movie_form_data,
                                    find_or_create_director,
                                    update_movie)


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
