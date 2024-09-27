from flask import render_template, request
from models import User, Movie
from controllers.common_fun import (admin_logged_in,
                                    handle_invalid_admin,
                                    handle_not_logged_in
                                    )


# admin_controller_for_details_view_of_movies_added_by_user_of_current_admin_report
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
