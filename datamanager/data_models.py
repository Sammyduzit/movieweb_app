from .database import db

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
    director = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, nullable=True)
    genre = db.Column(db.String(100), nullable=True)

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
            'user_id': self.user_id
        }

    def __repr__(self):
        return f'<Movie {self.title} ({self.year})>'