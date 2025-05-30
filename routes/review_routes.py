from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.user_service import UserService
from services.movie_service import MovieService
from services.review_service import ReviewService
from exceptions import (
    UserNotFoundError, MovieNotFoundError, ReviewNotFoundError,
    ValidationError, DatabaseError
)
from utils.decorators import require_user_and_movie

review_bp = Blueprint('reviews', __name__, url_prefix='/users/<int:user_id>/movies/<int:movie_id>')

user_service = UserService()
movie_service = MovieService()
review_service = ReviewService()


@review_bp.route('/add_review', methods=['POST'])
@require_user_and_movie
def add_review(user_id, movie_id, user, movie):
    """Add a review to a movie"""
    review_data = {
        'content': request.form.get('content', '').strip(),
        'reviewer_rating': request.form.get('reviewer_rating')
    }

    try:
        review_service.create_review(movie_id, review_data)
        flash('Review added successfully!', 'success')

    except ValidationError as e:
        flash(f'Validation error: {e.message}', 'error')

    except DatabaseError as e:
        flash(f'Database error: {e.message}', 'error')

    except Exception as e:
        flash(f'Error adding review: {str(e)}', 'error')

    return redirect(url_for('movies.movie_detail', user_id=user_id, movie_id=movie_id))


@review_bp.route('/like_review/<int:review_id>')
@require_user_and_movie
def like_review(user_id, movie_id, review_id, user, movie):  # both injected!
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
@require_user_and_movie
def edit_review(user_id, movie_id, review_id, user, movie):
    """Edit a review"""
    try:
        # Get existing reviews to find the one being edited
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
@require_user_and_movie
def delete_review_route(user_id, movie_id, review_id, user, movie):  # both injected!
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