"""
Custom exception classes for MovieWeb application.
Provides specific error types for better error handling and debugging.
"""

class MovieWebError(Exception):
    """Base exception class for all MovieWeb errors"""
    def __init__(self, message, status_code=500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class UserNotFoundError(MovieWebError):
    """Raised when a user is not found"""
    def __init__(self, user_id):
        message = f"User with ID {user_id} not found"
        super().__init__(message, status_code=404)
        self.user_id = user_id

class MovieNotFoundError(MovieWebError):
    """Raised when a movie is not found"""
    def __init__(self, movie_id):
        message = f"Movie with ID {movie_id} not found"
        super().__init__(message, status_code=404)
        self.movie_id = movie_id

class ReviewNotFoundError(MovieWebError):
    """Raised when a review is not found"""
    def __init__(self, review_id):
        message = f"Review with ID {review_id} not found"
        super().__init__(message, status_code=404)
        self.review_id = review_id

class ValidationError(MovieWebError):
    """Raised when input validation fails"""
    def __init__(self, field, message):
        full_message = f"Validation error for {field}: {message}"
        super().__init__(full_message, status_code=400)
        self.field = field

class TriviaError(MovieWebError):
    """Raised when trivia operations fail"""
    def __init__(self, message, trivia_type=None):
        super().__init__(message, status_code=503)
        self.trivia_type = trivia_type

class InsufficientMoviesError(MovieWebError):
    """Raised when user doesn't have enough movies for collection trivia"""
    def __init__(self, user_id, movie_count, required_count=3):
        message = f"User {user_id} has only {movie_count} movies, but {required_count} required for collection trivia"
        super().__init__(message, status_code=400)
        self.user_id = user_id
        self.movie_count = movie_count
        self.required_count = required_count

class ExternalAPIError(MovieWebError):
    """Raised when external API calls fail"""
    def __init__(self, service_name, message):
        full_message = f"{service_name} API error: {message}"
        super().__init__(full_message, status_code=503)
        self.service_name = service_name

class DatabaseError(MovieWebError):
    """Raised when database operations fail"""
    def __init__(self, operation, original_error):
        message = f"Database error during {operation}: {str(original_error)}"
        super().__init__(message, status_code=500)
        self.operation = operation
        self.original_error = original_error