from models import User, Movie, Director, Admin, Genre, db
from datamanager.data_manager_interface import DataManagerInterface


class SQLiteDataManager(DataManagerInterface):
    """
    Data Manager class to handle database operations with SQLite using SQLAlchemy.

    Attributes:
        db (SQLAlchemy): The SQLAlchemy instance to interact with the SQLite database.
    """

    def __init__(self, app):
        """
        Initializes the SQLiteDataManager with a Flask app and configures the database.

        Args:
            app (Flask): The Flask application instance.
        """
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/moviwebapp.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)
        self.db = db

    def get_all_users(self):
        """
        Fetches all users from the database.

        Returns:
            List[User]: A list of all user objects.
        """
        return User.query.all()

    def get_all_admins(self):
        """
        Fetches all admins from the database.

        Returns:
            List[Admin]: A list of all admin objects.
        """
        return Admin.query.all()

    def get_all_genres(self):
        """
        Fetches all genres from the database.

        Returns:
            List[Genre]: A list of all genre objects.
        """
        return Genre.query.all()

    def get_user_movies(self, user_id):
        """
        Fetches all movies associated with a specific user.

        Args:
            user_id (int): The user's ID.

        Returns:
            List[Movie]: A list of movie objects associated with the user.
        """
        return Movie.query.filter_by(user_id=user_id).all()

    def get_admin_movies(self, admin_id):
        """
        Fetches all movies added by a specific admin.

        Args:
            admin_id (int): The admin's ID.

        Returns:
            List[Movie]: A list of movie objects added by the admin.
        """
        return Movie.query.filter_by(admin_id=admin_id).all()

    def add_user(self, user_name, user_email, user_password):
        """
        Adds a new user to the database.

        Args:
            user_name (str): The name of the user.
            user_email (str): The email of the user.
            user_password (str): The password of the user (hashed).
        """
        new_user = User(name=user_name, email=user_email)
        new_user.set_password(user_password)
        self.db.session.add(new_user)
        self.db.session.commit()

    def add_admin(self, admin_name, admin_email, admin_password):
        """
        Adds a new admin to the database.

        Args:
            admin_name (str): The name of the admin.
            admin_email (str): The email of the admin.
            admin_password (str): The password of the admin (hashed).
        """
        new_admin = Admin(name=admin_name, email=admin_email)
        new_admin.set_password(admin_password)
        self.db.session.add(new_admin)
        self.db.session.commit()

    def add_movie(self, movie_data):
        """
        Adds a new movie to the database and handles associated genres and director.

        Args:
            movie_data (dict): A dictionary containing movie details 
            like title, director, year, genres, etc.
        """
        director_name = movie_data.get('director')
        director = Director.query.filter_by(name=director_name).first()

        if not director:
            director = Director(name=director_name)
            self.db.session.add(director)
            self.db.session.commit()

        new_movie = Movie(
            user_id=movie_data.get('user_id'),
            admin_id=movie_data.get('admin_id'),
            title=movie_data.get('title'),
            director_id=director.id,
            year=movie_data.get('year'),
            rating=movie_data.get('rating'),
            plot=movie_data.get('plot', ''),
            poster=movie_data.get('poster', ''),
            imdbID=movie_data.get('imdbID')
        )
        self.db.session.add(new_movie)
        self.db.session.commit()

        # Handle genres
        genres = movie_data.get('genres', [])
        for genre_name in genres:
            genre = Genre.query.filter_by(name=genre_name).first()
            if not genre:
                genre = Genre(name=genre_name)
                self.db.session.add(genre)
                self.db.session.commit()
            new_movie.genres.append(genre)
        self.db.session.commit()

    def update_movie(self, movie_id, new_data):
        """
        Updates the details of an existing movie.

        Args:
            movie_id (int): The ID of the movie to be updated.
            new_data (dict): A dictionary containing updated movie details like title, 
            director, year, genres, etc.
        """
        movie = Movie.query.get(movie_id)
        if movie:
            director_name = new_data.get('director')
            director = Director.query.filter_by(name=director_name).first()

            if not director:
                director = Director(name=director_name)
                self.db.session.add(director)
                self.db.session.commit()

            movie.title = new_data.get('title')
            movie.director_id = director.id
            movie.year = new_data.get('year')
            movie.rating = new_data.get('rating')
            movie.admin_id = new_data.get('admin_id')
            movie.imdbID = new_data.get('imdbID')

            # Update genres
            movie.genres = []
            genres = new_data.get('genres', [])
            for genre_name in genres:
                genre = Genre.query.filter_by(name=genre_name).first()
                if not genre:
                    genre = Genre(name=genre_name)
                    self.db.session.add(genre)
                    self.db.session.commit()
                movie.genres.append(genre)
            self.db.session.commit()

    def delete_movie(self, movie_id):
        """
        Deletes a movie from the database.

        Args:
            movie_id (int): The ID of the movie to be deleted.
        """
        movie = Movie.query.get(movie_id)
        if movie:
            self.db.session.delete(movie)
            self.db.session.commit()

    def delete_user(self, user_id):
        """
        Deletes a user from the database.

        Args:
            user_id (int): The ID of the user to be deleted.
        """
        user = User.query.get(user_id)
        if user:
            self.db.session.delete(user)
            self.db.session.commit()

    def get_reports(self):
        """
        Generates a report of the total number of users and movies.

        Returns:
            dict: A dictionary containing the number of users and movies.
        """
        num_users = User.query.count()
        num_movies = Movie.query.count()
        return {'num_users': num_users, 'num_movies': num_movies}
