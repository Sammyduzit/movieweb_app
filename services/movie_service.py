"""
Movie Service - Business logic for movie operations.
"""
from datamanager import SQLiteDataManager
from services.omdb_service import OMDbService
from exceptions import (
    UserNotFoundError, MovieNotFoundError, ValidationError,
    DatabaseError, ExternalAPIError, DuplicateMovieError
)
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import re


class MovieService:
    """Service class for handling movie-related business logic"""

    def __init__(self):
        self.data_manager = SQLiteDataManager()
        self.omdb_service = OMDbService()

    def validate_movie_data(self, movie_data):
        """Validate movie input data"""
        title = movie_data.get('title', '').strip()
        director = movie_data.get('director', '').strip() or None
        year = movie_data.get('year')
        genre = movie_data.get('genre', '').strip() or None
        rating = movie_data.get('rating')

        if not title:
            raise ValidationError('title', 'Movie title is required')

        if len(title) > 200:
            raise ValidationError('title', 'Title must be less than 200 characters')

        if year:
            try:
                year = int(year)
                if year < 1800 or year > 2050:
                    raise ValidationError('year', 'Year must be between 1800 and 2050')
            except (ValueError, TypeError):
                raise ValidationError('year', 'Year must be a valid number')
        else:
            year = None

        if rating:
            try:
                rating = float(rating)
                if not (1 <= rating <= 10):
                    raise ValidationError('rating', 'Rating must be between 1 and 10')
            except (ValueError, TypeError):
                raise ValidationError('rating', 'Rating must be a valid number')
        else:
            rating = None

        if director and len(director) > 100:
            raise ValidationError('director', 'Director name must be less than 100 characters')

        if genre and len(genre) > 100:
            raise ValidationError('genre', 'Genre must be less than 100 characters')

        return {
            'title': title,
            'director': director,
            'year': year,
            'genre': genre,
            'rating': rating
        }

    def enhance_movie_with_omdb(self, movie_data):
        """Enhance movie data with OMDb API information"""
        try:
            enhanced_data = self.omdb_service.enhance_movie_data(movie_data)
            return enhanced_data
        except Exception as e:
            print(f"Warning: Failed to enhance movie data with OMDb: {e}")
            return movie_data

    def get_user_movies(self, user_id):
        """Get all movies for a user"""
        try:
            return self.data_manager.get_user_movies(user_id)
        except SQLAlchemyError as e:
            raise DatabaseError('fetching user movies', e)

    def get_movie_by_id(self, movie_id):
        """Get movie by ID across all users"""
        try:
            all_users = self.data_manager.get_all_users()
            for user in all_users:
                movies = self.data_manager.get_user_movies(user['id'])
                movie = next((m for m in movies if m['id'] == movie_id), None)
                if movie:
                    return movie, user['id']
            raise MovieNotFoundError(movie_id)
        except SQLAlchemyError as e:
            raise DatabaseError('fetching movie', e)

    def get_movie_for_user(self, user_id, movie_id):
        """Get specific movie for a specific user"""
        movies = self.get_user_movies(user_id)
        movie = next((m for m in movies if m['id'] == movie_id), None)
        if not movie:
            raise MovieNotFoundError(movie_id)
        return movie

    def create_movie_for_user(self, user_id, movie_data):
        """Create new movie for a user with validation and enhancement"""
        validated_data = self.validate_movie_data(movie_data)

        enhanced_data = self.enhance_movie_with_omdb(validated_data)

        existing_movies = self.get_user_movies(user_id)
        title = enhanced_data['title'].lower()
        year = enhanced_data.get('year')

        for movie in existing_movies:
            if (movie['title'].lower() == title and
                    movie.get('year') == year):
                raise DuplicateMovieError(user_id, enhanced_data['title'], year)

        try:
            return self.data_manager.add_user_movie(user_id, enhanced_data)
        except IntegrityError as e:
            if 'unique_user_movie' in str(e):
                raise DuplicateMovieError(user_id, enhanced_data['title'], year)
            raise DatabaseError('creating movie', e)
        except ValueError as e:
            if 'not found' in str(e):
                raise UserNotFoundError(user_id)
            raise ValidationError('user_id', str(e))
        except SQLAlchemyError as e:
            raise DatabaseError('creating movie', e)

    def update_movie(self, movie_id, movie_data):
        """Update existing movie with validation"""
        validated_data = self.validate_movie_data(movie_data)

        try:
            current_movie, user_id = self.get_movie_by_id(movie_id)
        except MovieNotFoundError:
            raise MovieNotFoundError(movie_id)

        existing_movies = self.get_user_movies(user_id)
        title = validated_data['title'].lower()
        year = validated_data.get('year')

        for movie in existing_movies:
            if movie['id'] == movie_id:
                continue

            if (movie['title'].lower() == title and
                    movie.get('year') == year):
                raise DuplicateMovieError(user_id, validated_data['title'], year)

        try:
            result = self.data_manager.update_movie(movie_id, validated_data)
            if not result:
                raise MovieNotFoundError(movie_id)
            return result
        except IntegrityError as e:
            # Database constraint backup
            if 'unique_user_movie' in str(e):
                raise DuplicateMovieError(user_id, validated_data['title'], year)
            raise DatabaseError('updating movie', e)
        except SQLAlchemyError as e:
            raise DatabaseError('updating movie', e)

    def delete_movie(self, movie_id):
        """Delete movie by ID"""
        try:
            success = self.data_manager.delete_movie(movie_id)
            if not success:
                raise MovieNotFoundError(movie_id)
            return True
        except SQLAlchemyError as e:
            raise DatabaseError('deleting movie', e)