from flask import render_template, request
from models import User, Movie
from controllers.common_fun import (admin_logged_in,
                                    handle_invalid_admin,
                                    handle_not_logged_in
                                    )


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
