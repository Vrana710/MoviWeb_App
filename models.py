from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Association table for many-to-many relationship between Movie and Genre
movie_genre = db.Table('movie_genre',
                       db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'), primary_key=True),
                       db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
                       )


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    gender = db.Column(db.String(10), nullable=True)  # Optional field for gender
    profile_picture = db.Column(db.String(200), nullable=True)  # Optional field for profile picture URL
    password_update_date = db.Column(db.DateTime, nullable=True)
    join_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    movies = db.relationship('Movie', backref='user', lazy=True)
    favorites = db.relationship('Favorite', back_populates='user', lazy=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)
        self.password_update_date = datetime.now()  # Update password change timestamp

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Director(db.Model):
    __tablename__ = 'director'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    # Relationships
    movies = db.relationship('Movie', backref='director', lazy=True)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    poster = db.Column(db.String(255))  # Optional field to store movie posters
    plot = db.Column(db.Text)  # Optional field to store the plot
    imdbID = db.Column(db.String(255), nullable=True)  # IMDb ID or link
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
    director_id = db.Column(db.Integer, db.ForeignKey('director.id'), nullable=False)  # Foreign key to Director
    genres = db.relationship('Genre', secondary=movie_genre, backref='movies')
    favorites = db.relationship('Favorite', back_populates='movie', lazy=True)  # Add this line


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)


class Favorite(db.Model):
    __tablename__ = 'favorite'
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', back_populates='favorites')
    movie = db.relationship('Movie', back_populates='favorites')
    # movie = db.relationship('Movie', backref='favorites', lazy=True)


class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Contact(db.Model):
    __tablename__ = 'contact'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
