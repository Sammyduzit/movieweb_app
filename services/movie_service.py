"""
Movie Service - Business logic for movie operations.
Handles movie CRUD operations, validation, and external API integration.
"""
import re

from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from config import ValidationConfig
from datamanager import SQLiteDataManager
from services.omdb_service import OMDbService
from exceptions import (
    UserNotFoundError, MovieNotFoundError, ValidationError,
    DatabaseError, ExternalAPIError, DuplicateMovieError
)


class MovieService:
    """Service class for handling movie-related business logic"""

    def __init__(self):
        """Initialize movie service with data manager and OMDb service."""
        self.data_manager = SQLiteDataManager()
        self.omdb_service = OMDbService()

        # ==================== VALIDATION METHODS ====================

    def validate_movie_data(self, movie_data):
        """
        Validate movie input data according to business rules.

        :param movie_data: Dictionary containing movie data to validate
        :return: Dictionary with validated and cleaned movie data
        """
        # Extract and validate individual fields
        title = self._validate_title(movie_data.get('title', ''))
        director = self._validate_director(movie_data.get('director', ''))
        year = self._validate_year(movie_data.get('year'))
        genre = self._validate_genre(movie_data.get('genre', ''))
        rating = self._validate_rating(movie_data.get('rating'))

        return {
            'title': title,
            'director': director,
            'year': year,
            'genre': genre,
            'rating': rating
        }

    def _validate_title(self, title):
        """
        Validate movie title.

        :param title: Movie title to validate
        :return: Cleaned title string
        """
        title = title.strip()
        if not title:
            raise ValidationError('title', 'Movie title is required')

        if len(title) > ValidationConfig.MOVIE_TITLE_MAX:
            raise ValidationError('title', 'Title must be less than 200 characters')

        return title

    def _validate_director(self, director):
        """
        Validate director name.

        :param director: Director name to validate
        :return: Cleaned director string or None
        """
        if not director:
            return None

        director = director.strip()
        if len(director) > ValidationConfig.DIRECTOR_NAME_MAX:
            raise ValidationError('director',
                                  'Director name must be less than 100 characters')

        return director

    def _validate_year(self, year):
        """
        Validate movie year.

        :param year: Year to validate
        :return: Integer year or None
        """
        if not year:
            return None

        try:
            year = int(year)
            if year < ValidationConfig.YEAR_MIN or year > ValidationConfig.YEAR_MAX:
                raise ValidationError('year',
                                      'Year must be between 1800 and 2050')
            return year
        except (ValueError, TypeError):
            raise ValidationError('year',
                                  'Year must be a valid number')

    def _validate_genre(self, genre):
        """
        Validate movie genre.

        :param genre: Genre to validate
        :return: Cleaned genre string or None
        """
        if not genre:
            return None

        genre = genre.strip()
        if len(genre) > ValidationConfig.GENRE_MAX:
            raise ValidationError('genre',
                                  'Genre must be less than 100 characters')

        return genre

    def _validate_rating(self, rating):
        """
        Validate movie rating.

        :param rating: Rating to validate
        :return: Float rating or None
        """
        if not rating:
            return None

        try:
            rating = float(rating)
            if not (ValidationConfig.RATING_MIN <= rating <= ValidationConfig.RATING_MAX):
                raise ValidationError('rating',
                                      'Rating must be between 1 and 10')
            return rating
        except (ValueError, TypeError):
            raise ValidationError('rating',
                                  'Rating must be a valid number')

    # ==================== EXTERNAL API INTEGRATION ====================

    def enhance_movie_with_omdb(self, movie_data):
        """
        Enhance movie data with OMDb API information.

        :param movie_data: Dictionary containing basic movie data
        :return: Enhanced movie data dictionary
        """
        try:
            enhanced_data = self.omdb_service.enhance_movie_data(movie_data)
            return enhanced_data
        except Exception as e:
            print(f"Warning: Failed to enhance movie data with OMDb: {e}")
            return movie_data

    # ==================== DATA RETRIEVAL METHODS ====================

    def get_user_movies(self, user_id):
        """
        Get all movies for a specific user.

        :param user_id: ID of the user
        :return: List of movie dictionaries
        """
        try:
            return self.data_manager.get_user_movies(user_id)
        except SQLAlchemyError as e:
            raise DatabaseError('fetching user movies', e)

    def get_movie_by_id(self, movie_id):
        """
        Get movie by ID across all users.

        :param movie_id: ID of the movie to retrieve
        :return: Tuple of (movie_dict, user_id)
        """
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
        """
        Get specific movie for a specific user.

        :param user_id: ID of the user
        :param movie_id: ID of the movie
        :return: Movie dictionary
        """
        movies = self.get_user_movies(user_id)
        movie = next((m for m in movies if m['id'] == movie_id), None)
        if not movie:
            raise MovieNotFoundError(movie_id)
        return movie

    # ==================== MOVIE CREATION AND MODIFICATION ====================

    def create_movie_for_user(self, user_id, movie_data):
        """
        Create new movie for a user with validation and enhancement.

        :param user_id: ID of the user
        :param movie_data: Dictionary containing movie data
        :return: Dictionary representation of created movie
        """
        validated_data = self.validate_movie_data(movie_data)
        enhanced_data = self.enhance_movie_with_omdb(validated_data)

        self._check_duplicate_movie(user_id, enhanced_data)

        try:
            return self.data_manager.add_user_movie(user_id, enhanced_data)
        except IntegrityError as e:
            if 'unique_user_movie' in str(e):
                raise DuplicateMovieError(user_id,
                                          enhanced_data['title'],
                                          enhanced_data.get('year'))
            raise DatabaseError('creating movie', e)
        except ValueError as e:
            if 'not found' in str(e):
                raise UserNotFoundError(user_id)
            raise ValidationError('user_id', str(e))
        except SQLAlchemyError as e:
            raise DatabaseError('creating movie', e)

    def update_movie(self, movie_id, movie_data):
        """
        Update existing movie with validation.

        :param movie_id: ID of the movie to update
        :param movie_data: Dictionary containing updated movie data
        :return: Dictionary representation of updated movie
        """
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

    # ==================== HELPER METHODS ====================

    def _check_duplicate_movie(self, user_id, movie_data, exclude_movie_id=None):
        """
        Check for duplicate movies in user's collection.

        :param user_id: ID of the user
        :param movie_data: Movie data to check
        :param exclude_movie_id: Movie ID to exclude from check (for updates)
        :return: None (raises exception if duplicate found)
        """
        existing_movies = self.get_user_movies(user_id)
        title = movie_data['title'].lower()
        year = movie_data.get('year')

        for movie in existing_movies:
            # Skip the movie being updated
            if exclude_movie_id and movie['id'] == exclude_movie_id:
                continue

            if (movie['title'].lower() == title and
                    movie.get('year') == year):
                raise DuplicateMovieError(user_id, movie_data['title'], year)