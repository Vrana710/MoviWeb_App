from abc import ABC, abstractmethod


class DataManagerInterface(ABC):
    @abstractmethod
    def get_all_users(self):
        pass

    @abstractmethod
    def get_all_admins(self):
        pass

    @abstractmethod
    def get_all_genres(self):
        pass

    @abstractmethod
    def get_user_movies(self, user_id):
        pass

    @abstractmethod
    def get_admin_movies(self, admin_id):
        pass

    @abstractmethod
    def add_user(self, user_name, user_email, user_password):
        pass

    @abstractmethod
    def add_admin(self, admin_name, admin_email, admin_password):
        pass

    @abstractmethod
    def add_movie(self, movie_data):
        pass

    @abstractmethod
    def update_movie(self, movie_id, new_data):
        pass

    @abstractmethod
    def delete_movie(self, movie_id):
        pass

    @abstractmethod
    def delete_user(self, user_id):
        pass

    @abstractmethod
    def get_reports(self):
        pass
