"""
Review Service - Business logic for review operations.
Handles review CRUD operations with comprehensive validation and error handling.
"""
from sqlalchemy.exc import SQLAlchemyError

from config import ValidationConfig
from datamanager import SQLiteDataManager
from exceptions import (
    MovieNotFoundError, ReviewNotFoundError, ValidationError,
    DatabaseError
)


class ReviewService:
    """Service class for handling review-related business logic"""

    def __init__(self):
        self.data_manager = SQLiteDataManager()

    def validate_review_data(self, review_data):
        """
        Validate review input data according to business rules.

        :param review_data: Dictionary containing review data to validate
        :return: Dictionary with validated and cleaned review data
        """
        content = self._validate_content(review_data.get('content', ''))
        reviewer_rating = self._validate_reviewer_rating(
            review_data.get('reviewer_rating')
        )

        return {
            'content': content,
            'reviewer_rating': reviewer_rating
        }

    def _validate_content(self, content):
        """
        Validate review content.

        :param content: Review content to validate
        :return: Cleaned content string
        """
        content = content.strip()
        if not content:
            raise ValidationError('content', 'Review content is required')

        if len(content) > ValidationConfig.REVIEW_CONTENT_MAX:
            raise ValidationError('content',
                                  'Review must be less than 2000 characters')

        return content

    def _validate_reviewer_rating(self, reviewer_rating):
        """
        Validate reviewer rating.

        :param reviewer_rating: Rating to validate
        :return: Integer rating or None
        """
        if not reviewer_rating:
            return None

        try:
            reviewer_rating = int(reviewer_rating)
            min_rating = ValidationConfig.RATING_MIN
            max_rating = ValidationConfig.RATING_MAX

            if not (min_rating <= reviewer_rating <= max_rating):
                raise ValidationError('reviewer_rating',
                                      'Rating must be between 1 and 10')
            return reviewer_rating
        except (ValueError, TypeError):
            raise ValidationError('reviewer_rating',
                                  'Rating must be a valid integer')

    def create_review(self, movie_id, review_data):
        """
        Create new review for a movie with validation.

        :param movie_id: ID of the movie to review
        :param review_data: Dictionary containing review data
        :return: Dictionary representation of created review
        """
        validated_data = self.validate_review_data(review_data)

        try:
            return self.data_manager.add_review(movie_id, validated_data)
        except ValueError as e:
            if 'not found' in str(e):
                raise MovieNotFoundError(movie_id)
            raise ValidationError('movie_id', str(e))
        except SQLAlchemyError as e:
            raise DatabaseError('creating review', e)

    def get_movie_reviews(self, movie_id):
        """
        Get all reviews for a specific movie.

        :param movie_id: ID of the movie
        :return: List of review dictionaries
        """
        try:
            return self.data_manager.get_movie_reviews(movie_id)
        except SQLAlchemyError as e:
            raise DatabaseError('fetching reviews', e)

    def update_review(self, review_id, review_data):
        """
        Update existing review with validation.

        :param review_id: ID of the review to update
        :param review_data: Dictionary containing updated review data
        :return: Dictionary representation of updated review
        """
        validated_data = self.validate_review_data(review_data)

        try:
            result = self.data_manager.update_review(review_id, validated_data)
            if not result:
                raise ReviewNotFoundError(review_id)
            return result
        except SQLAlchemyError as e:
            raise DatabaseError('updating review', e)

    def delete_review(self, review_id):
        """
        Delete review by ID.

        :param review_id: ID of the review to delete
        :return: True if successful
        """
        try:
            success = self.data_manager.delete_review(review_id)
            if not success:
                raise ReviewNotFoundError(review_id)
            return True
        except SQLAlchemyError as e:
            raise DatabaseError('deleting review', e)

    def like_review(self, review_id):
        """
        Add like to review (increment like count).

        :param review_id: ID of the review to like
        :return: Dictionary representation of updated review
        """
        try:
            result = self.data_manager.like_review(review_id)
            if not result:
                raise ReviewNotFoundError(review_id)
            return result
        except SQLAlchemyError as e:
            raise DatabaseError('liking review', e)