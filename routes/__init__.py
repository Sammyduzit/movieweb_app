from .user_routes import user_bp
from .movie_routes import movie_bp
from .review_routes import review_bp
from .api_routes import api_bp
from .trivia_routes import trivia_bp

__all__ = ['user_bp', 'movie_bp', 'review_bp', 'api_bp', 'trivia_bp']