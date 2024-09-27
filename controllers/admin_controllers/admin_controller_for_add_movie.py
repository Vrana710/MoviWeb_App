from flask import render_template, request
from models import User, Genre
from controllers.common_fun import (admin_logged_in,
                                    handle_invalid_admin,
                                    handle_add_movie_post,
                                    handle_not_logged_in)


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
