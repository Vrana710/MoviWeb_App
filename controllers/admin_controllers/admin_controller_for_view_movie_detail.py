from flask import (render_template,
                   redirect,
                   url_for,
                   flash)
from models import Movie
from controllers.common_fun import (admin_logged_in,
                                    handle_invalid_admin,
                                    handle_not_logged_in
                                    )


def view_movie_details(movie_id):
    """
    View details of a specific movie added by the user.

    Parameters:
    - movie_id (int): The ID of the movie to display details for.

    Returns:
    - render_template: A rendered HTML template displaying the movie details.
    """
    if not admin_logged_in():
        return handle_not_logged_in()  # Redirect if the user is not logged in

    admin = admin_logged_in()
    if admin is None:
        return handle_invalid_admin()

    # Query the movie to ensure it belongs to the current user
    movie = Movie.query.filter_by(id=movie_id).first()

    if movie is None:
        flash("Movie not found or you do not have permission to view it.", "error")
        return redirect(url_for('admin_bp.manage_movies'))  # Redirect back to movie list if not found

    # Render the movie details page
    return render_template('view_movie_details.html', movie=movie)
