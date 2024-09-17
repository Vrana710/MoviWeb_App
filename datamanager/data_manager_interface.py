from abc import ABC, abstractmethod


class DataManagerInterface(ABC):

    @abstractmethod
    def get_all_users(self):
        """Retrieve a list of all users."""
        pass

    @abstractmethod
    def get_all_admins(self):
        """Retrieve a list of all admins."""
        pass

    @abstractmethod
    def get_all_genres(self):
        """Retrieve a list of all genres."""
        pass

    @abstractmethod
    def get_user_movies(self, user_id):
        """Retrieve a list of movies associated with a specific user."""
        pass

    @abstractmethod
    def get_admin_movies(self, admin_id):
        """Retrieve a list of movies associated with a specific admin."""
        pass

    @abstractmethod
    def add_user(self, user_name, user_email, user_password):
        """Add a new user with the provided name, email, and password."""
        pass

    @abstractmethod
    def add_admin(self, admin_name, admin_email, admin_password):
        """Add a new admin with the provided name, email, and password."""
        pass

    @abstractmethod
    def add_movie(self, movie_data):
        """Add a new movie with the provided data."""
        pass

    @abstractmethod
    def update_movie(self, movie_id, new_data):
        """Update an existing movie with new data based on its ID."""
        pass

    @abstractmethod
    def delete_movie(self, movie_id):
        """Delete a movie based on its ID."""
        pass

    @abstractmethod
    def delete_user(self, user_id):
        """Delete a user based on their ID."""
        pass

    @abstractmethod
    def get_reports(self):
        """Generate and retrieve reports with relevant data."""
        pass
