from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.movie_service import MovieService
from services.review_service import ReviewService
from services.user_service import UserService
from exceptions import (
    UserNotFoundError, MovieNotFoundError, ValidationError,
    DatabaseError, ExternalAPIError
)

movie_bp = Blueprint('movies', __name__, url_prefix='/users/<int:user_id>')

movie_service = MovieService()
review_service = ReviewService()
user_service = UserService()


@movie_bp.route('/')
def user_movies(user_id):
    """Display a user's favorite movies."""
    try:
        user = user_service.get_user_by_id(user_id)
        movies = movie_service.get_user_movies(user_id)

        return render_template('user_movies.html', user=user, movies=movies)

    except UserNotFoundError:
        flash('User not found', 'error')
        return redirect(url_for('users.list_users'))

    except DatabaseError as e:
        flash(f'Database error: {e.message}', 'error')
        return redirect(url_for('users.list_users'))

    except Exception as e:
        flash(f'Unexpected error loading movies: {str(e)}', 'error')
        return redirect(url_for('users.list_users'))


@movie_bp.route('/movies/<int:movie_id>')
def movie_detail(user_id, movie_id):
    """Display movie details with reviews."""
    try:
        user = user_service.get_user_by_id(user_id)
        movie = movie_service.get_movie_for_user(user_id, movie_id)
        reviews = review_service.get_movie_reviews(movie_id)

        return render_template('movie_detail.html', user=user, movie=movie, reviews=reviews)

    except UserNotFoundError:
        flash('User not found', 'error')
        return redirect(url_for('users.list_users'))

    except MovieNotFoundError:
        flash('Movie not found', 'error')
        return redirect(url_for('movies.user_movies', user_id=user_id))

    except DatabaseError as e:
        flash(f'Database error: {e.message}', 'error')
        return redirect(url_for('movies.user_movies', user_id=user_id))

    except Exception as e:
        flash(f'Error loading movie details: {str(e)}', 'error')
        return redirect(url_for('movies.user_movies', user_id=user_id))


@movie_bp.route('/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    """Add a new movie to a user's favorites."""
    try:
        user = user_service.get_user_by_id(user_id)

        if request.method == 'POST':
            movie_data = {
                'title': request.form.get('title', '').strip(),
                'director': request.form.get('director', '').strip(),
                'year': request.form.get('year', '').strip(),
                'genre': request.form.get('genre', '').strip(),
                'rating': request.form.get('rating', '').strip()
            }

            try:
                new_movie = movie_service.create_movie_for_user(user_id, movie_data)
                flash(f'Movie "{new_movie["title"]}" added successfully!', 'success')
                return redirect(url_for('movies.user_movies', user_id=user_id))

            except ValidationError as e:
                flash(f'Validation error: {e.message}', 'error')
                return render_template('add_movie.html', user=user)

            except ExternalAPIError as e:
                flash(f'Movie added, but API enhancement failed: {e.message}', 'warning')
                return redirect(url_for('movies.user_movies', user_id=user_id))

        return render_template('add_movie.html', user=user)

    except UserNotFoundError:
        flash('User not found', 'error')
        return redirect(url_for('users.list_users'))

    except DatabaseError as e:
        flash(f'Database error: {e.message}', 'error')
        return redirect(url_for('movies.user_movies', user_id=user_id))

    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'error')
        return redirect(url_for('movies.user_movies', user_id=user_id))


@movie_bp.route('/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """Update a movie's details."""
    try:
        user = user_service.get_user_by_id(user_id)
        movie = movie_service.get_movie_for_user(user_id, movie_id)

        if request.method == 'POST':
            updated_data = {
                'title': request.form.get('title', '').strip(),
                'director': request.form.get('director', '').strip(),
                'year': request.form.get('year', '').strip(),
                'genre': request.form.get('genre', '').strip(),
                'rating': request.form.get('rating', '').strip()
            }

            try:
                result = movie_service.update_movie(movie_id, updated_data)
                flash(f'Movie "{result["title"]}" updated successfully!', 'success')
                return redirect(url_for('movies.user_movies', user_id=user_id))

            except ValidationError as e:
                flash(f'Validation error: {e.message}', 'error')
                return render_template('update_movie.html', user=user, movie=movie)

        return render_template('update_movie.html', user=user, movie=movie)

    except UserNotFoundError:
        flash('User not found', 'error')
        return redirect(url_for('users.list_users'))

    except MovieNotFoundError:
        flash('Movie not found', 'error')
        return redirect(url_for('movies.user_movies', user_id=user_id))

    except DatabaseError as e:
        flash(f'Database error: {e.message}', 'error')
        return redirect(url_for('movies.user_movies', user_id=user_id))

    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'error')
        return redirect(url_for('movies.user_movies', user_id=user_id))


@movie_bp.route('/delete_movie/<int:movie_id>')
def delete_movie(user_id, movie_id):
    """Delete a movie from a user's favorites."""
    try:
        user_service.get_user_by_id(user_id)

        try:
            movie = movie_service.get_movie_for_user(user_id, movie_id)
            movie_title = movie['title']
        except MovieNotFoundError:
            movie_title = 'Unknown Movie'

        movie_service.delete_movie(movie_id)
        flash(f'Movie "{movie_title}" deleted successfully!', 'success')

    except UserNotFoundError:
        flash('User not found', 'error')
        return redirect(url_for('users.list_users'))

    except MovieNotFoundError:
        flash('Movie not found or already deleted', 'warning')

    except DatabaseError as e:
        flash(f'Database error: {e.message}', 'error')

    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'error')

    return redirect(url_for('movies.user_movies', user_id=user_id))