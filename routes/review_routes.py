from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.user_service import UserService
from services.movie_service import MovieService
from services.review_service import ReviewService
from exceptions import (
    UserNotFoundError, MovieNotFoundError, ReviewNotFoundError,
    ValidationError, DatabaseError
)

review_bp = Blueprint('reviews', __name__, url_prefix='/users/<int:user_id>/movies/<int:movie_id>')

user_service = UserService()
movie_service = MovieService()
review_service = ReviewService()


@review_bp.route('/add_review', methods=['POST'])
def add_review(user_id, movie_id):
    """Add a review to a movie"""
    try:
        user_service.get_user_by_id(user_id)
        movie_service.get_movie_for_user(user_id, movie_id)

        review_data = {
            'content': request.form.get('content', '').strip(),
            'reviewer_rating': request.form.get('reviewer_rating')
        }

        review_service.create_review(movie_id, review_data)
        flash('Review added successfully!', 'success')

    except UserNotFoundError:
        flash('User not found', 'error')
        return redirect(url_for('users.list_users'))

    except MovieNotFoundError:
        flash('Movie not found', 'error')
        return redirect(url_for('movies.user_movies', user_id=user_id))

    except ValidationError as e:
        flash(f'Validation error: {e.message}', 'error')

    except DatabaseError as e:
        flash(f'Database error: {e.message}', 'error')

    except Exception as e:
        flash(f'Error adding review: {str(e)}', 'error')

    return redirect(url_for('movies.movie_detail', user_id=user_id, movie_id=movie_id))


@review_bp.route('/like_review/<int:review_id>')
def like_review(user_id, movie_id, review_id):
    """Like a review"""
    try:
        review_service.like_review(review_id)
        flash('Review liked!', 'success')

    except ReviewNotFoundError:
        flash('Review not found', 'error')

    except DatabaseError as e:
        flash(f'Database error: {e.message}', 'error')

    except Exception as e:
        flash(f'Error liking review: {str(e)}', 'error')

    return redirect(url_for('movies.movie_detail', user_id=user_id, movie_id=movie_id))


@review_bp.route('/edit_review/<int:review_id>', methods=['GET', 'POST'])
def edit_review(user_id, movie_id, review_id):
    """Edit a review"""
    try:
        user = user_service.get_user_by_id(user_id)
        movie = movie_service.get_movie_for_user(user_id, movie_id)

        reviews = review_service.get_movie_reviews(movie_id)
        review = next((r for r in reviews if r['id'] == review_id), None)

        if not review:
            raise ReviewNotFoundError(review_id)

        if request.method == 'POST':
            updated_data = {
                'content': request.form.get('content', '').strip(),
                'reviewer_rating': request.form.get('reviewer_rating')
            }

            try:
                review_service.update_review(review_id, updated_data)
                flash('Review updated successfully!', 'success')
                return redirect(url_for('movies.movie_detail', user_id=user_id, movie_id=movie_id))

            except ValidationError as e:
                flash(f'Validation error: {e.message}', 'error')
                return render_template('edit_review.html', user=user, movie=movie, review=review)

        return render_template('edit_review.html', user=user, movie=movie, review=review)

    except UserNotFoundError:
        flash('User not found', 'error')
        return redirect(url_for('users.list_users'))

    except MovieNotFoundError:
        flash('Movie not found', 'error')
        return redirect(url_for('movies.user_movies', user_id=user_id))

    except ReviewNotFoundError:
        flash('Review not found', 'error')
        return redirect(url_for('movies.movie_detail', user_id=user_id, movie_id=movie_id))

    except DatabaseError as e:
        flash(f'Database error: {e.message}', 'error')
        return redirect(url_for('movies.movie_detail', user_id=user_id, movie_id=movie_id))

    except Exception as e:
        flash(f'Error editing review: {str(e)}', 'error')
        return redirect(url_for('movies.movie_detail', user_id=user_id, movie_id=movie_id))


@review_bp.route('/delete_review/<int:review_id>')
def delete_review_route(user_id, movie_id, review_id):
    """Delete a review"""
    try:
        review_service.delete_review(review_id)
        flash('Review deleted successfully!', 'success')

    except ReviewNotFoundError:
        flash('Review not found or already deleted', 'warning')

    except DatabaseError as e:
        flash(f'Database error: {e.message}', 'error')

    except Exception as e:
        flash(f'Error deleting review: {str(e)}', 'error')

    return redirect(url_for('movies.movie_detail', user_id=user_id, movie_id=movie_id))