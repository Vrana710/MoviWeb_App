"""
user.py

This module handles user-related routes and functionalities for the MoviWeb application.
It includes operations such as adding, editing, and deleting movies, as well as user authentication
and session management. The routes defined in this module ensure that users can manage their
favorite movies while enforcing access control and data validation.

Routes:
- user_add_movie: Allows users to add a new movie.
- user_edit_movie: Enables users to edit their existing movies.
- delete_movie: Handles the deletion of a user's movie.
- Other user-related functionalities as needed.
"""

import os
from flask import Blueprint
from controllers.user_controllers.user_controller_for_user_dashboard import user_dashboard
from controllers.user_controllers.user_controller_for_my_movies import my_movies
from controllers.user_controllers.user_controller_for_user_favorites import user_favorites
from controllers.user_controllers.user_controller_for_add_movie_to_favorites import add_to_favorites
from controllers.user_controllers.user_controller_for_remove_movie_from_favorites import (
    remove_from_favorites
)
from controllers.user_controllers.user_controller_for_view_movie_details import view_movie_details
from controllers.user_controllers.user_controller_for_user_add_movie import user_add_movie
from controllers.user_controllers.user_controller_for_user_delete_movie import delete_movie
from controllers.user_controllers.user_controller_for_user_edit_movie import user_edit_movie
from controllers.user_controllers.user_controller_for_user_profile import user_profile
from controllers.user_controllers.user_controller_for_user_edit_profile import edit_user_profile

user_bp = Blueprint('user_bp', __name__,
                    template_folder=os.path.join(os.path.dirname(__file__),
                                                 '../templates/user'))


user_bp.route('/dashboard')(user_dashboard)
user_bp.route('/my_movies')(my_movies)
user_bp.route('/movie/<int:movie_id>', methods=['GET'])(view_movie_details)
user_bp.route('/user_favorites')(user_favorites)
user_bp.route('/add_to_favorites/<int:movie_id>', methods=['POST'])(add_to_favorites)
user_bp.route('/remove_from_favorites/<int:movie_id>', methods=['POST'])(remove_from_favorites)
user_bp.route('/user_add_movie', methods=['GET', 'POST'])(user_add_movie)
user_bp.route('/edit_movie/<int:movie_id>', methods=['GET', 'POST'])(user_edit_movie)
user_bp.route('/delete_movie/<int:movie_id>', methods=['POST'])(delete_movie)
user_bp.route('/user_profile')(user_profile)
user_bp.route('/edit_user_profile/<int:user_id>', methods=['GET', 'POST'])(edit_user_profile)
