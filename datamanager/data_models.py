from .database import db
from datetime import datetime

class User(db.Model):
    """User model for the database"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    trivia_scores = db.relationship('TriviaScore', back_populates= 'user', lazy=True)
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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'title', 'year', name='unique_user_movie'),
    )

    trivia_scores = db.relationship('TriviaScore', back_populates='movie', lazy=True)
    reviews = db.relationship('Review', backref='movie', lazy=True, cascade='all, delete-orphan')

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


class TriviaScore(db.Model):
    """Model for tracking trivia scores and leaderboards"""
    __tablename__ = 'trivia_scores'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trivia_type = db.Column(db.String(20), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=True)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Integer, nullable=False)
    completion_time = db.Column(db.Integer, nullable=True)  # Time in seconds
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', back_populates='trivia_scores')
    movie = db.relationship('Movie', back_populates='trivia_scores')

    def to_dict(self):
        """Convert trivia score to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'trivia_type': self.trivia_type,
            'movie_id': self.movie_id,
            'score': self.score,
            'total_questions': self.total_questions,
            'percentage': self.percentage,
            'completion_time': self.completion_time,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<TriviaScore {self.user_id}: {self.score}/{self.total_questions} ({self.percentage}%)>'