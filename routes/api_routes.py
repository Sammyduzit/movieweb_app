from flask import Blueprint, jsonify, request
from datamanager import SQLiteDataManager, OMDbService
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

api_bp = Blueprint('api', __name__, url_prefix='/api')

data_manager = SQLiteDataManager()
omdb_service = OMDbService()


def error_response(message, status_code=400):
    """Create standardized error response"""
    return jsonify({'error': message, 'success': False}), status_code


def success_response(data=None, message=None):
    """Create standardized success response"""
    response = {'success': True}
    if data is not None:
        response['data'] = data
    if message:
        response['message'] = message
    return jsonify(response)


# ==================== USER ENDPOINTS ====================

@api_bp.route('/users', methods=['GET'])
def api_get_users():
    """GET /api/users - Get all users"""
    try:
        users = data_manager.get_all_users()
        return success_response(users)
    except Exception as e:
        return error_response(f'Error fetching users: {str(e)}', 500)


@api_bp.route('/users', methods=['POST'])
def api_create_user():
    """POST /api/users - Create a new user"""
    try:
        data = request.get_json()
        if not data:
            return error_response('No JSON data provided')

        if not data.get('name') or not data.get('email'):
            return error_response('Name and email are required')

        user_data = {
            'name': data['name'].strip(),
            'email': data['email'].strip()
        }

        new_user = data_manager.add_user(user_data)
        return success_response(new_user, 'User created successfully'), 201

    except IntegrityError:
        return error_response('Email already exists', 409)
    except Exception as e:
        return error_response(f'Error creating user: {str(e)}', 500)


@api_bp.route('/users/<int:user_id>', methods=['GET'])
def api_get_user(user_id):
    """GET /api/users/{id} - Get specific user"""
    try:
        users = data_manager.get_all_users()
        user = next((u for u in users if u['id'] == user_id), None)

        if not user:
            return error_response('User not found', 404)

        return success_response(user)
    except Exception as e:
        return error_response(f'Error fetching user: {str(e)}', 500)


# ==================== MOVIE ENDPOINTS ====================

@api_bp.route('/users/<int:user_id>/movies', methods=['GET'])
def api_get_user_movies(user_id):
    """GET /api/users/{id}/movies - Get user's movies"""
    try:
        users = data_manager.get_all_users()
        user = next((u for u in users if u['id'] == user_id), None)
        if not user:
            return error_response('User not found', 404)

        movies = data_manager.get_user_movies(user_id)
        return success_response(movies)
    except Exception as e:
        return error_response(f'Error fetching movies: {str(e)}', 500)


@api_bp.route('/users/<int:user_id>/movies', methods=['POST'])
def api_create_movie(user_id):
    """POST /api/users/{id}/movies - Add movie to user"""
    try:
        users = data_manager.get_all_users()
        user = next((u for u in users if u['id'] == user_id), None)
        if not user:
            return error_response('User not found', 404)

        data = request.get_json()
        if not data:
            return error_response('No JSON data provided')

        if not data.get('title'):
            return error_response('Movie title is required')

        movie_data = {
            'title': data['title'].strip(),
            'director': data.get('director', '').strip() or None,
            'year': data.get('year'),
            'genre': data.get('genre', '').strip() or None,
            'rating': data.get('rating')
        }

        if movie_data['year']:
            try:
                movie_data['year'] = int(movie_data['year'])
            except ValueError:
                return error_response('Year must be a valid integer')

        if movie_data['rating']:
            try:
                movie_data['rating'] = float(movie_data['rating'])
                if not (1 <= movie_data['rating'] <= 10):
                    return error_response('Rating must be between 1 and 10')
            except ValueError:
                return error_response('Rating must be a valid number')

        enhanced_data = omdb_service.enhance_movie_data(movie_data)

        new_movie = data_manager.add_user_movie(user_id, enhanced_data)
        return success_response(new_movie, 'Movie added successfully'), 201

    except Exception as e:
        return error_response(f'Error adding movie: {str(e)}', 500)


@api_bp.route('/movies/<int:movie_id>', methods=['GET'])
def api_get_movie(movie_id):
    """GET /api/movies/{id} - Get specific movie with reviews"""
    try:
        all_users = data_manager.get_all_users()
        movie = None
        user_id = None

        for user in all_users:
            movies = data_manager.get_user_movies(user['id'])
            found_movie = next((m for m in movies if m['id'] == movie_id), None)
            if found_movie:
                movie = found_movie
                user_id = user['id']
                break

        if not movie:
            return error_response('Movie not found', 404)

        reviews = data_manager.get_movie_reviews(movie_id)

        response_data = {
            'movie': movie,
            'reviews': reviews,
            'user_id': user_id
        }

        return success_response(response_data)
    except Exception as e:
        return error_response(f'Error fetching movie: {str(e)}', 500)


@api_bp.route('/movies/<int:movie_id>', methods=['PUT'])
def api_update_movie(movie_id):
    """PUT /api/movies/{id} - Update movie"""
    try:
        data = request.get_json()
        if not data:
            return error_response('No JSON data provided')

        update_data = {}
        if 'title' in data:
            if not data['title'].strip():
                return error_response('Title cannot be empty')
            update_data['title'] = data['title'].strip()

        if 'director' in data:
            update_data['director'] = data['director'].strip() or None

        if 'year' in data:
            if data['year']:
                try:
                    update_data['year'] = int(data['year'])
                except ValueError:
                    return error_response('Year must be a valid integer')

        if 'genre' in data:
            update_data['genre'] = data['genre'].strip() or None

        if 'rating' in data:
            if data['rating']:
                try:
                    rating = float(data['rating'])
                    if not (1 <= rating <= 10):
                        return error_response('Rating must be between 1 and 10')
                    update_data['rating'] = rating
                except ValueError:
                    return error_response('Rating must be a valid number')

        result = data_manager.update_movie(movie_id, update_data)

        if not result:
            return error_response('Movie not found', 404)

        return success_response(result, 'Movie updated successfully')

    except Exception as e:
        return error_response(f'Error updating movie: {str(e)}', 500)


@api_bp.route('/movies/<int:movie_id>', methods=['DELETE'])
def api_delete_movie(movie_id):
    """DELETE /api/movies/{id} - Delete movie"""
    try:
        success = data_manager.delete_movie(movie_id)

        if not success:
            return error_response('Movie not found', 404)

        return success_response(message='Movie deleted successfully')

    except Exception as e:
        return error_response(f'Error deleting movie: {str(e)}', 500)


# ==================== REVIEW ENDPOINTS ====================

@api_bp.route('/movies/<int:movie_id>/reviews', methods=['GET'])
def api_get_movie_reviews(movie_id):
    """GET /api/movies/{id}/reviews - Get all reviews for a movie"""
    try:
        reviews = data_manager.get_movie_reviews(movie_id)
        return success_response(reviews)
    except Exception as e:
        return error_response(f'Error fetching reviews: {str(e)}', 500)


@api_bp.route('/movies/<int:movie_id>/reviews', methods=['POST'])
def api_create_review(movie_id):
    """POST /api/movies/{id}/reviews - Add review to movie"""
    try:
        data = request.get_json()
        if not data:
            return error_response('No JSON data provided')

        if not data.get('content'):
            return error_response('Review content is required')

        review_data = {
            'content': data['content'].strip(),
            'reviewer_rating': data.get('reviewer_rating')
        }

        if review_data['reviewer_rating']:
            try:
                rating = int(review_data['reviewer_rating'])
                if not (1 <= rating <= 10):
                    return error_response('Rating must be between 1 and 10')
                review_data['reviewer_rating'] = rating
            except ValueError:
                return error_response('Rating must be a valid integer')

        new_review = data_manager.add_review(movie_id, review_data)
        return success_response(new_review, 'Review added successfully'), 201

    except ValueError as e:
        if 'not found' in str(e):
            return error_response('Movie not found', 404)
        return error_response(str(e))
    except Exception as e:
        return error_response(f'Error adding review: {str(e)}', 500)


@api_bp.route('/reviews/<int:review_id>', methods=['PUT'])
def api_update_review(review_id):
    """PUT /api/reviews/{id} - Update review"""
    try:
        data = request.get_json()
        if not data:
            return error_response('No JSON data provided')

        update_data = {}
        if 'content' in data:
            if not data['content'].strip():
                return error_response('Content cannot be empty')
            update_data['content'] = data['content'].strip()

        if 'reviewer_rating' in data:
            if data['reviewer_rating']:
                try:
                    rating = int(data['reviewer_rating'])
                    if not (1 <= rating <= 10):
                        return error_response('Rating must be between 1 and 10')
                    update_data['reviewer_rating'] = rating
                except ValueError:
                    return error_response('Rating must be a valid integer')

        result = data_manager.update_review(review_id, update_data)

        if not result:
            return error_response('Review not found', 404)

        return success_response(result, 'Review updated successfully')

    except Exception as e:
        return error_response(f'Error updating review: {str(e)}', 500)


@api_bp.route('/reviews/<int:review_id>', methods=['DELETE'])
def api_delete_review(review_id):
    """DELETE /api/reviews/{id} - Delete review"""
    try:
        success = data_manager.delete_review(review_id)

        if not success:
            return error_response('Review not found', 404)

        return success_response(message='Review deleted successfully')

    except Exception as e:
        return error_response(f'Error deleting review: {str(e)}', 500)


@api_bp.route('/reviews/<int:review_id>/like', methods=['POST'])
def api_like_review(review_id):
    """POST /api/reviews/{id}/like - Like a review"""
    try:
        result = data_manager.like_review(review_id)

        if not result:
            return error_response('Review not found', 404)

        return success_response(result, 'Review liked successfully')

    except Exception as e:
        return error_response(f'Error liking review: {str(e)}', 500)


# ==================== API INFO ENDPOINT ====================

@api_bp.route('/', methods=['GET'])
def api_info():
    """GET /api/ - API information"""
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