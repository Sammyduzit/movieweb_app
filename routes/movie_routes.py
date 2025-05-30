from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.movie_service import MovieService
from services.review_service import ReviewService
from services.user_service import UserService
from exceptions import (
    UserNotFoundError, MovieNotFoundError, ValidationError,
    DatabaseError, ExternalAPIError, DuplicateMovieError
)
from utils.decorators import require_user, require_user_and_movie

movie_bp = Blueprint('movies', __name__, url_prefix='/users/<int:user_id>')

movie_service = MovieService()
review_service = ReviewService()
user_service = UserService()


@movie_bp.route('/')
@require_user
def user_movies(user_id, user):
    """Display a user's favorite movies."""
    try:
        movies = movie_service.get_user_movies(user_id)
        return render_template('user_movies.html', user=user, movies=movies)

    except DatabaseError as e:
        flash(f'Database error: {e.message}', 'error')
        return redirect(url_for('users.list_users'))

    except Exception as e:
        flash(f'Unexpected error loading movies: {str(e)}', 'error')
        return redirect(url_for('users.list_users'))

@movie_bp.route('/movies/<int:movie_id>')
@require_user_and_movie
def movie_detail(user_id, movie_id, user, movie):
    """Display movie details with reviews."""
    try:
        reviews = review_service.get_movie_reviews(movie_id)
        return render_template('movie_detail.html', user=user, movie=movie, reviews=reviews)

    except DatabaseError as e:
        flash(f'Database error: {e.message}', 'error')
        return redirect(url_for('movies.user_movies', user_id=user_id))

    except Exception as e:
        flash(f'Error loading movie details: {str(e)}', 'error')
        return redirect(url_for('movies.user_movies', user_id=user_id))


@movie_bp.route('/add_movie', methods=['GET', 'POST'])
@require_user
def add_movie(user_id, user):
    """Add a new movie to a user's favorites."""
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

        except DuplicateMovieError as e:
            flash(e.message, 'warning')
            return render_template('add_movie.html', user=user)

        except ExternalAPIError as e:
            flash(f'Movie added, but API enhancement failed: {e.message}', 'warning')
            return redirect(url_for('movies.user_movies', user_id=user_id))

        except DatabaseError as e:
            flash(f'Database error: {e.message}', 'error')
            return render_template('add_movie.html', user=user)

        except Exception as e:
            flash(f'Unexpected error: {str(e)}', 'error')
            return render_template('add_movie.html', user=user)

    return render_template('add_movie.html', user=user)


@movie_bp.route('/update_movie/<int:movie_id>', methods=['GET', 'POST'])
@require_user_and_movie
def update_movie(user_id, movie_id, user, movie):
    """Update a movie's details."""
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

        except DuplicateMovieError as e:
            flash(e.message, 'warning')
            return render_template('update_movie.html', user=user, movie=movie)

        except DatabaseError as e:
            flash(f'Database error: {e.message}', 'error')
            return render_template('update_movie.html', user=user, movie=movie)

        except Exception as e:
            flash(f'Unexpected error: {str(e)}', 'error')
            return render_template('update_movie.html', user=user, movie=movie)

    return render_template('update_movie.html', user=user, movie=movie)


@movie_bp.route('/delete_movie/<int:movie_id>')
@require_user
def delete_movie(user_id, movie_id, user):
    """Delete a movie from a user's favorites."""
    try:
        # Get movie title before deletion for flash message
        try:
            movie = movie_service.get_movie_for_user(user_id, movie_id)
            movie_title = movie['title']
        except MovieNotFoundError:
            movie_title = 'Unknown Movie'

        movie_service.delete_movie(movie_id)
        flash(f'Movie "{movie_title}" deleted successfully!', 'success')

    except MovieNotFoundError:
        flash('Movie not found or already deleted', 'warning')

    except DatabaseError as e:
        flash(f'Database error: {e.message}', 'error')

    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'error')

    return redirect(url_for('movies.user_movies', user_id=user_id))