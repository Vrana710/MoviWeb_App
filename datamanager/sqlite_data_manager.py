from models import User, Movie, Director, Admin, Genre, db
from datamanager.data_manager_interface import DataManagerInterface

class SQLiteDataManager(DataManagerInterface):

    def __init__(self, app):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/moviwebapp.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)
        self.db = db

    def get_all_users(self):
        return User.query.all()

    def get_all_admins(self):
        return Admin.query.all()

    def get_all_genres(self):
        return Genre.query.all()

    def get_user_movies(self, user_id):
        return Movie.query.filter_by(user_id=user_id).all()

    def get_admin_movies(self, admin_id):
        return Movie.query.filter_by(admin_id=admin_id).all()

    def add_user(self, user_name, user_email, user_password):
        new_user = User(name=user_name, email=user_email)
        new_user.set_password(user_password)  # Set hashed password
        self.db.session.add(new_user)
        self.db.session.commit()

    def add_admin(self, admin_name, admin_email, admin_password):
        new_admin = Admin(name=admin_name, email=admin_email)
        new_admin.set_password(admin_password)  # Set hashed password
        self.db.session.add(new_admin)
        self.db.session.commit()

    def add_movie(self, movie_data):
        director_name = movie_data.get('director')
        director = Director.query.filter_by(name=director_name).first()

        if not director:
            director = Director(name=director_name)
            self.db.session.add(director)
            self.db.session.commit()

        # Create the movie object
        new_movie = Movie(
            user_id=movie_data.get('user_id'),  # Optional: may be None
            admin_id=movie_data.get('admin_id'),  # Optional: may be None
            title=movie_data.get('title'),
            director_id=director.id,
            year=movie_data.get('year'),
            rating=movie_data.get('rating'),
            plot=movie_data.get('plot', ''),
            poster=movie_data.get('poster', ''),
            imdbID=movie_data.get('imdbID')  # Added IMDb ID if provided
        )
        self.db.session.add(new_movie)
        self.db.session.commit()

        # Handle genres if provided
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
            movie.admin_id = new_data.get('admin_id')  # Optionally re-assign to an admin
            movie.imdbID = new_data.get('imdbID')  # Update IMDb ID if provided

            # Clear existing genres and add new ones
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
        movie = Movie.query.get(movie_id)
        if movie:
            self.db.session.delete(movie)
            self.db.session.commit()

    def delete_user(self, user_id):
        user = User.query.get(user_id)
        if user:
            self.db.session.delete(user)
            self.db.session.commit()

    def get_reports(self):
        num_users = User.query.count()
        num_movies = Movie.query.count()
        return {'num_users': num_users, 'num_movies': num_movies}
