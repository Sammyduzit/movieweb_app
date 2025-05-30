"""
Validation decorators for MovieWeb application.
Provides reusable decorators for common route validations.
"""

from functools import wraps
from flask import flash, redirect, url_for
from services.user_service import UserService
from services.movie_service import MovieService
from exceptions import UserNotFoundError, MovieNotFoundError, DatabaseError

_user_service = UserService()
_movie_service = MovieService()


def require_user(f):
    """
    Decorator that validates user exists and injects user object.

    Usage:
        @require_user
        def my_route(user_id, user):  # user object automatically injected
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = kwargs.get('user_id')
        if user_id is None:
            for arg in args:
                if isinstance(arg, int):
                    user_id = arg
                    break

        if user_id is None:
            flash('Invalid user ID', 'error')
            return redirect(url_for('users.list_users'))

        try:
            user = _user_service.get_user_by_id(user_id)
            kwargs['user'] = user
            return f(*args, **kwargs)

        except UserNotFoundError:
            flash('User not found', 'error')
            return redirect(url_for('users.list_users'))

        except DatabaseError as e:
            flash(f'Database error: {e.message}', 'error')
            return redirect(url_for('users.list_users'))

        except Exception as e:
            flash(f'Unexpected error: {str(e)}', 'error')
            return redirect(url_for('users.list_users'))

    return decorated_function


def require_user_and_movie(f):
    """
    Decorator that validates user and movie exist and injects both objects.

    Usage:
        @require_user_and_movie
        def my_route(user_id, movie_id, user, movie):  # both objects injected
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = kwargs.get('user_id')
        movie_id = kwargs.get('movie_id')

        if user_id is None or movie_id is None:
            flash('Invalid user or movie ID', 'error')
            return redirect(url_for('users.list_users'))

        try:
            user = _user_service.get_user_by_id(user_id)

            movie = _movie_service.get_movie_for_user(user_id, movie_id)

            kwargs['user'] = user
            kwargs['movie'] = movie
            return f(*args, **kwargs)

        except UserNotFoundError:
            flash('User not found', 'error')
            return redirect(url_for('users.list_users'))

        except MovieNotFoundError:
            flash('Movie not found', 'error')
            return redirect(url_for('movies.user_movies', user_id=user_id))

        except DatabaseError as e:
            flash(f'Database error: {e.message}', 'error')
            return redirect(url_for('users.list_users'))

        except Exception as e:
            flash(f'Unexpected error: {str(e)}', 'error')
            return redirect(url_for('users.list_users'))

    return decorated_function


def require_movie_exists(f):
    """
    Decorator that validates movie exists across all users (for global movie operations).

    Usage:
        @require_movie_exists
        def my_route(movie_id, movie, owner_user_id):  # movie and owner_user_id injected
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        movie_id = kwargs.get('movie_id')

        if movie_id is None:
            flash('Invalid movie ID', 'error')
            return redirect(url_for('users.list_users'))

        try:
            movie, owner_user_id = _movie_service.get_movie_by_id(movie_id)

            kwargs['movie'] = movie
            kwargs['owner_user_id'] = owner_user_id
            return f(*args, **kwargs)

        except MovieNotFoundError:
            flash('Movie not found', 'error')
            return redirect(url_for('users.list_users'))

        except DatabaseError as e:
            flash(f'Database error: {e.message}', 'error')
            return redirect(url_for('users.list_users'))

        except Exception as e:
            flash(f'Unexpected error: {str(e)}', 'error')
            return redirect(url_for('users.list_users'))

    return decorated_function


def handle_validation_errors(f):
    """
    Decorator that provides consistent error handling for validation errors.
    Can be combined with other decorators.

    Usage:
        @handle_validation_errors
        @require_user
        def my_route(user_id, user):
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            if hasattr(e, 'status_code'):
                raise

            flash(f'Unexpected error: {str(e)}', 'error')
            return redirect(url_for('users.list_users'))

    return decorated_function