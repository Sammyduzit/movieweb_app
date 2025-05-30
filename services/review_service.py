"""
Review Service - Business logic for review operations.
"""

from datamanager import SQLiteDataManager
from exceptions import (
    MovieNotFoundError, ReviewNotFoundError, ValidationError,
    DatabaseError
)
from sqlalchemy.exc import SQLAlchemyError


class ReviewService:
    """Service class for handling review-related business logic"""

    def __init__(self):
        self.data_manager = SQLiteDataManager()

    def validate_review_data(self, review_data):
        """Validate review input data"""
        content = review_data.get('content', '').strip()
        reviewer_rating = review_data.get('reviewer_rating')

        if not content:
            raise ValidationError('content', 'Review content is required')

        if len(content) > 2000:
            raise ValidationError('content', 'Review must be less than 2000 characters')

        if reviewer_rating:
            try:
                reviewer_rating = int(reviewer_rating)
                if not (1 <= reviewer_rating <= 10):
                    raise ValidationError('reviewer_rating', 'Rating must be between 1 and 10')
            except (ValueError, TypeError):
                raise ValidationError('reviewer_rating', 'Rating must be a valid integer')

        return {
            'content': content,
            'reviewer_rating': reviewer_rating
        }

    def create_review(self, movie_id, review_data):
        """Create new review for a movie"""
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
        """Get all reviews for a movie"""
        try:
            return self.data_manager.get_movie_reviews(movie_id)
        except SQLAlchemyError as e:
            raise DatabaseError('fetching reviews', e)

    def update_review(self, review_id, review_data):
        """Update existing review"""
        validated_data = self.validate_review_data(review_data)

        try:
            result = self.data_manager.update_review(review_id, validated_data)
            if not result:
                raise ReviewNotFoundError(review_id)
            return result
        except SQLAlchemyError as e:
            raise DatabaseError('updating review', e)

    def delete_review(self, review_id):
        """Delete review by ID"""
        try:
            success = self.data_manager.delete_review(review_id)
            if not success:
                raise ReviewNotFoundError(review_id)
            return True
        except SQLAlchemyError as e:
            raise DatabaseError('deleting review', e)

    def like_review(self, review_id):
        """Add like to review"""
        try:
            result = self.data_manager.like_review(review_id)
            if not result:
                raise ReviewNotFoundError(review_id)
            return result
        except SQLAlchemyError as e:
            raise DatabaseError('liking review', e)