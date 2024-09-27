# admin.py
"""
This module defines the routes and functionality for the admin section of the application.
It includes routes for managing movies, users, and viewing reports, ensuring only admins
with valid sessions can access and modify the data.
"""
import os
from flask import Blueprint

from controllers.admin_controllers.admin_controller_dashboard import admin_dashboard
from controllers.admin_controllers.admin_controller_for_add_user import add_user
from controllers.admin_controllers.admin_controller_for_edit_user import edit_user
from controllers.admin_controllers.admin_controller_for_delete_user import delete_user

from controllers.admin_controllers.admin_controller_for_view_user import view_user
from controllers.admin_controllers.admin_controller_for_manage_users import manage_users
from controllers.admin_controllers.admin_controller_for_manage_all_users import manage_all_users

from controllers.admin_controllers.admin_controller_for_add_movie import add_movie
from controllers.admin_controllers.admin_controller_for_edit_movie import edit_movie
from controllers.admin_controllers.admin_controller_for_delete_movie import delete_movie
from controllers.admin_controllers.admin_controller_for_delete_any_movie import delete_any_movie
from controllers.admin_controllers.admin_controller_for_manage_movies import manage_movies
from controllers.admin_controllers.admin_controller_for_manage_all_movies import manage_all_movies
# from controllers.admin_controller_for_view_movie import view_movie
from controllers.admin_controllers.admin_controller_for_reports import reports
from controllers.admin_controllers.admin_controller_for_all_movies_added_by_user_of_current_admin_report import (
    all_movies_added_by_user_of_current_admin_report
)
from controllers.admin_controllers.admin_controller_for_details_view_of_movies_added_by_user_of_current_admin_report \
    import details_view_of_movies_added_by_user_of_current_admin_report
from controllers.admin_controllers.admin_controller_for_admin_view_movie_detail import admin_view_movie_details


admin_bp = Blueprint('admin_bp', __name__,
                     template_folder=os.path.join(os.path.dirname(__file__),
                                                  '../templates/admin'))

# Define routes and assign controller functions
admin_bp.route('/admin_dashboard')(admin_dashboard)
admin_bp.route('/add_user', methods=['GET', 'POST'])(add_user)
admin_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])(edit_user)
admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])(delete_user)

admin_bp.route('/view_user/<int:user_id>', methods=['GET', 'POST'])(view_user)

admin_bp.route('/manage_users')(manage_users)
admin_bp.route('/manage_all_users')(manage_all_users)

admin_bp.route('/add_movie', methods=['GET', 'POST'])(add_movie)
admin_bp.route('/edit_movie/<int:movie_id>', methods=['GET', 'POST'])(edit_movie)

admin_bp.route('/delete_movie/<int:movie_id>', methods=['POST'])(delete_movie)
admin_bp.route('/delete_any_movie/<int:movie_id>', methods=['POST'])(delete_any_movie)

admin_bp.route('/manage_movies')(manage_movies)
admin_bp.route('/manage_all_movies')(manage_all_movies)
admin_bp.route('/movie/<int:movie_id>', methods=['GET'])(admin_view_movie_details)

admin_bp.route('/reports')(reports)
admin_bp.route('/all_movies_added_by_user_of_current_admin_report')(all_movies_added_by_user_of_current_admin_report)
admin_bp.route('/details_view_of_movies_added_by_user_of_current_admin_report/<int:user_id>')(
    details_view_of_movies_added_by_user_of_current_admin_report
)
