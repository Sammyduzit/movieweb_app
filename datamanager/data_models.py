from .database import db
from datetime import datetime

class User(db.Model):
    """User model for the database"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    movies = db.relationship('Movie', backref='user', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email
        }

    def __repr__(self):
        return f'<User {self.name}>'


class Movie(db.Model):
    """Movie model for the database"""
    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    director = db.Column(db.String(100), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    rating = db.Column(db.Float, nullable=True)
    genre = db.Column(db.String(100), nullable=True)
    poster = db.Column(db.String(500), nullable=True)
    reviews = db.relationship('Review', backref='movie', lazy=True, cascade='all, delete-orphan')

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def to_dict(self):
        """Convert movie object to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'director': self.director,
            'year': self.year,
            'rating': self.rating,
            'genre': self.genre,
            'poster': self.poster,
            'user_id': self.user_id
        }

    def __repr__(self):
        return f'<Movie {self.title} ({self.year})>'


class Review(db.Model):
    """Review model for movie reviews"""
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    reviewer_rating = db.Column(db.Integer, nullable=True)
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)

    def to_dict(self):
        """Convert review object to dictionary"""
        return {
            'id': self.id,
            'content': self.content,
            'reviewer_rating': self.reviewer_rating,
            'likes': self.likes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'movie_id': self.movie_id
        }

    def __repr__(self):
        return f'<Review {self.id} for Movie {self.movie_id}>'

