"""
API Routes - RESTful API endpoints for MovieWeb application.
Provides JSON API for all core functionality including users, movies, and reviews.
"""
from flask import Blueprint, jsonify, request
from services.user_service import UserService
from services.movie_service import MovieService
from services.review_service import ReviewService
from exceptions import (
    UserNotFoundError, MovieNotFoundError, ReviewNotFoundError,
    ValidationError, DatabaseError, ExternalAPIError, DuplicateMovieError
)

api_bp = Blueprint('api', __name__, url_prefix='/api')

user_service = UserService()
movie_service = MovieService()
review_service = ReviewService()


def error_response(message, status_code=400):
    """
    Create standardized error response.

    :param message: Error message to return
    :param status_code: HTTP status code
    :return: Flask JSON response tuple
    """
    return jsonify({'error': message, 'success': False}), status_code


def success_response(data=None, message=None):
    """
    Create standardized success response.

    :param data: Data to include in response
    :param message: Success message
    :return: Flask JSON response
    """
    response = {'success': True}
    if data is not None:
        response['data'] = data
    if message:
        response['message'] = message
    return jsonify(response)


def clean_string_data(data, fields):
    """
    Clean and validate string fields from request data.

    :param data: Dictionary containing request data
    :param fields: List of field names to clean
    :return: Dictionary with cleaned string fields
    """
    cleaned = {}
    for field in fields:
        value = data.get(field)
        if value is not None:
            cleaned[field] = str(value).strip()
        else:
            cleaned[field] = ''
    return cleaned


def handle_service_exceptions(func):
    """
    Decorator to handle common service exceptions in API routes.

    :param func: Function to wrap
    :return: Wrapped function with exception handling
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except UserNotFoundError as e:
            return error_response('User not found', 404)
        except MovieNotFoundError as e:
            return error_response('Movie not found', 404)
        except ReviewNotFoundError as e:
            return error_response('Review not found', 404)
        except ValidationError as e:
            return error_response(e.message, 400)
        except DatabaseError as e:
            return error_response(f'Database error: {e.message}', 500)
        except DuplicateMovieError as e:
            return error_response(e.message, 409)
        except ExternalAPIError as e:
            return error_response(f'External API error: {e.message}', 503)
        except Exception as e:
            return error_response(f'Unexpected error: {str(e)}', 500)

    wrapper.__name__ = func.__name__
    return wrapper


# ==================== USER ENDPOINTS ====================

@api_bp.route('/users', methods=['GET'])
@handle_service_exceptions
def api_get_users():
    """
    Get all users.

    :return: JSON response with list of all users
    """
    users = user_service.get_all_users()
    return success_response(users)


@api_bp.route('/users', methods=['POST'])
@handle_service_exceptions
def api_create_user():
    """
    Create a new user.

    :return: JSON response with created user data and 201 status
    """
    data = request.get_json()
    if not data:
        return error_response('No JSON data provided')

    clean_data = clean_string_data(data, ['name', 'email'])
    new_user = user_service.create_user(clean_data)
    return success_response(new_user, 'User created successfully'), 201


@api_bp.route('/users/<int:user_id>', methods=['GET'])
@handle_service_exceptions
def api_get_user(user_id):
    """
    Get specific user by ID.

    :param user_id: ID of the user to retrieve
    :return: JSON response with user data
    """
    user = user_service.get_user_by_id(user_id)
    return success_response(user)


# ==================== MOVIE ENDPOINTS ====================

@api_bp.route('/users/<int:user_id>/movies', methods=['GET'])
@handle_service_exceptions
def api_get_user_movies(user_id):
    """
    Get all movies for a specific user.

    :param user_id: ID of the user
    :return: JSON response with list of user's movies
    """
    user_service.get_user_by_id(user_id)
    movies = movie_service.get_user_movies(user_id)
    return success_response(movies)


@api_bp.route('/users/<int:user_id>/movies', methods=['POST'])
@handle_service_exceptions
def api_create_movie(user_id):
    """
    Add a movie to a user's collection.

    :param user_id: ID of the user
    :return: JSON response with created movie data and 201 status
    """
    data = request.get_json()
    if not data:
        return error_response('No JSON data provided')

    user_service.get_user_by_id(user_id)

    clean_data = clean_string_data(data, ['title', 'director', 'genre'])
    clean_data.update({
        'year': data.get('year'),
        'rating': data.get('rating')
    })

    new_movie = movie_service.create_movie_for_user(user_id, clean_data)
    return success_response(new_movie, 'Movie added successfully'), 201


@api_bp.route('/movies/<int:movie_id>', methods=['GET'])
@handle_service_exceptions
def api_get_movie(movie_id):
    """
    Get specific movie with its reviews.

    :param movie_id: ID of the movie to retrieve
    :return: JSON response with movie data and reviews
    """
    movie, user_id = movie_service.get_movie_by_id(movie_id)
    reviews = review_service.get_movie_reviews(movie_id)

    response_data = {
        'movie': movie,
        'reviews': reviews,
        'user_id': user_id
    }

    return success_response(response_data)


@api_bp.route('/movies/<int:movie_id>', methods=['PUT'])
@handle_service_exceptions
def api_update_movie(movie_id):
    """
    Update a movie's details.

    :param movie_id: ID of the movie to update
    :return: JSON response with updated movie data
    """
    data = request.get_json()
    if not data:
        return error_response('No JSON data provided')

    string_fields = ['title', 'director', 'year', 'genre', 'rating']
    clean_data = {}

    for field in string_fields:
        if field in data:
            value = data[field]
            clean_data[field] = str(value).strip() if value is not None else ''

    result = movie_service.update_movie(movie_id, clean_data)
    return success_response(result, 'Movie updated successfully')


@api_bp.route('/movies/<int:movie_id>', methods=['DELETE'])
@handle_service_exceptions
def api_delete_movie(movie_id):
    """
    Delete a movie.

    :param movie_id: ID of the movie to delete
    :return: JSON response confirming deletion
    """
    movie_service.delete_movie(movie_id)
    return success_response(message='Movie deleted successfully')


# ==================== REVIEW ENDPOINTS ====================

@api_bp.route('/movies/<int:movie_id>/reviews', methods=['GET'])
@handle_service_exceptions
def api_get_movie_reviews(movie_id):
    """
    Get all reviews for a specific movie.

    :param movie_id: ID of the movie
    :return: JSON response with list of reviews
    """
    reviews = review_service.get_movie_reviews(movie_id)
    return success_response(reviews)


@api_bp.route('/movies/<int:movie_id>/reviews', methods=['POST'])
@handle_service_exceptions
def api_create_review(movie_id):
    """
    Add a review to a movie.

    :param movie_id: ID of the movie to review
    :return: JSON response with created review data and 201 status
    """
    data = request.get_json()
    if not data:
        return error_response('No JSON data provided')

    new_review = review_service.create_review(movie_id, data)
    return success_response(new_review, 'Review added successfully'), 201


@api_bp.route('/reviews/<int:review_id>', methods=['PUT'])
@handle_service_exceptions
def api_update_review(review_id):
    """
    Update a review.

    :param review_id: ID of the review to update
    :return: JSON response with updated review data
    """
    data = request.get_json()
    if not data:
        return error_response('No JSON data provided')

    clean_data = {}
    if 'content' in data:
        clean_data['content'] = str(data['content']).strip() \
                                if data['content'] is not None else ''

    if 'reviewer_rating' in data:
        clean_data['reviewer_rating'] = str(data['reviewer_rating']).strip() \
                                        if data['reviewer_rating'] is not None \
                                        else ''

    result = review_service.update_review(review_id, clean_data)
    return success_response(result, 'Review updated successfully')


@api_bp.route('/reviews/<int:review_id>', methods=['DELETE'])
@handle_service_exceptions
def api_delete_review(review_id):
    """
    Delete a review.

    :param review_id: ID of the review to delete
    :return: JSON response confirming deletion
    """
    review_service.delete_review(review_id)
    return success_response(message='Review deleted successfully')


@api_bp.route('/reviews/<int:review_id>/like', methods=['POST'])
@handle_service_exceptions
def api_like_review(review_id):
    """
    Like a review (increment like count).

    :param review_id: ID of the review to like
    :return: JSON response with updated review data
    """
    result = review_service.like_review(review_id)
    return success_response(result, 'Review liked successfully')


@api_bp.route('/usage', methods=['GET'])
def api_usage_stats():
    """
    Get API usage statistics.

    :return: JSON response with current API usage statistics
    """
    try:
        from services.rapidapi_service import RapidAPIService
        rapidapi_service = RapidAPIService()
        stats = rapidapi_service.usage_tracker.get_usage_stats()

        return success_response({
            'api_usage': stats,
            'status': 'available' if stats['remaining'] > 0 else 'limit_reached'
        })
    except Exception as e:
        return error_response(f'Error getting usage stats: {str(e)}', 500)


@api_bp.route('/usage/reset', methods=['POST'])
def reset_api_usage():
    """
    Manually reset API usage counter (for testing).

    :return: JSON response confirming usage reset
    """
    try:
        from services.rapidapi_service import RapidAPIService
        rapidapi_service = RapidAPIService()
        rapidapi_service.usage_tracker.force_reset()

        return success_response(message='API usage counter reset successfully')
    except Exception as e:
        return error_response(f'Error resetting usage: {str(e)}', 500)


@api_bp.route('/test-apis', methods=['GET'])
def test_apis():
    """
    Test both RapidAPI and OpenAI connections.

    :return: JSON response with API connection test results
    """
    try:
        from services.trivia_service import TriviaService
        trivia_service = TriviaService()
        test_results = trivia_service.test_apis()

        status_msg = []
        if test_results['rapidapi']:
            status_msg.append("RapidAPI: ✅ Working")
        else:
            status_msg.append("RapidAPI: ❌ Failed")

        if test_results['openai']:
            status_msg.append("OpenAI: ✅ Working")
        else:
            status_msg.append("OpenAI: ❌ Failed")

        return success_response({
            'api_tests': test_results,
            'status_summary': status_msg,
            'fallback_ready': test_results['fallback_available']
        })
    except Exception as e:
        return error_response(f'Error testing APIs: {str(e)}', 500)

# ==================== API INFO ENDPOINT ====================

@api_bp.route('/', methods=['GET'])
def api_info():
    """
    Get API information and available endpoints.

    :return: JSON response with API documentation
    """
    endpoints = {
        'users': {
            'GET /api/users': 'Get all users',
            'POST /api/users': 'Create new user',
            'GET /api/users/{id}': 'Get specific user',
            'GET /api/users/{id}/movies': 'Get user movies'
        },
        'movies': {
            'POST /api/users/{id}/movies': 'Add movie to user',
            'GET /api/movies/{id}': 'Get movie details with reviews',
            'PUT /api/movies/{id}': 'Update movie',
            'DELETE /api/movies/{id}': 'Delete movie'
        },
        'reviews': {
            'GET /api/movies/{id}/reviews': 'Get movie reviews',
            'POST /api/movies/{id}/reviews': 'Add review to movie',
            'PUT /api/reviews/{id}': 'Update review',
            'DELETE /api/reviews/{id}': 'Delete review',
            'POST /api/reviews/{id}/like': 'Like a review'
        }
    }

    return success_response(endpoints, 'MovieWeb API v1.0')