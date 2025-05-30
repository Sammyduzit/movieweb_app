from flask import Blueprint, render_template, request, redirect, url_for, flash
from datamanager import SQLiteDataManager
from sqlalchemy.exc import SQLAlchemyError

# Create blueprint
review_bp = Blueprint('reviews', __name__, url_prefix='/users/<int:user_id>/movies/<int:movie_id>')

# Initialize data manager
data_manager = SQLiteDataManager()


@review_bp.route('/add_review', methods=['POST'])
def add_review(user_id, movie_id):
    """Add a review to a movie"""
    try:
        review_data = {
            'content': request.form.get('content', '').strip(),
            'reviewer_rating': request.form.get('reviewer_rating')
        }

        if not review_data['content']:
            flash('Review content is required', 'error')
            return redirect(url_for('movies.movie_detail', user_id=user_id, movie_id=movie_id))

        if review_data['reviewer_rating']:
            try:
                review_data['reviewer_rating'] = int(review_data['reviewer_rating'])
                if not (1 <= review_data['reviewer_rating'] <= 10):
                    flash('Rating must be between 1 and 10', 'error')
                    return redirect(url_for('movies.movie_detail', user_id=user_id, movie_id=movie_id))
            except ValueError:
                flash('Invalid rating format', 'error')
                return redirect(url_for('movies.movie_detail', user_id=user_id, movie_id=movie_id))

        new_review = data_manager.add_review(movie_id, review_data)
        flash('Review added successfully!', 'success')
        return redirect(url_for('movies.movie_detail', user_id=user_id, movie_id=movie_id))

    except Exception as e:
        flash(f'Error adding review: {str(e)}', 'error')
        return redirect(url_for('movies.movie_detail', user_id=user_id, movie_id=movie_id))


@review_bp.route('/like_review/<int:review_id>')
def like_review(user_id, movie_id, review_id):
    """Like a review"""
    try:
        data_manager.like_review(review_id)
        flash('Review liked!', 'success')
    except Exception as e:
        flash(f'Error liking review: {str(e)}', 'error')

    return redirect(url_for('movies.movie_detail', user_id=user_id, movie_id=movie_id))


@review_bp.route('/edit_review/<int:review_id>', methods=['GET', 'POST'])
def edit_review(user_id, movie_id, review_id):
    """Edit a review"""
    try:
        users = data_manager.get_all_users()
        user = next((u for u in users if u['id'] == user_id), None)
        movies = data_manager.get_user_movies(user_id)
        movie = next((m for m in movies if m['id'] == movie_id), None)

        if not user or not movie:
            flash('User or movie not found', 'error')
            return redirect(url_for('users.list_users'))

        reviews = data_manager.get_movie_reviews(movie_id)
        review = next((r for r in reviews if r['id'] == review_id), None)

        if not review:
            flash('Review not found', 'error')
            return redirect(url_for('movies.movie_detail', user_id=user_id, movie_id=movie_id))

        if request.method == 'POST':
            updated_data = {
                'content': request.form.get('content', '').strip(),
                'reviewer_rating': request.form.get('reviewer_rating')
            }

            if not updated_data['content']:
                flash('Review content is required', 'error')
                return render_template('edit_review.html', user=user, movie=movie, review=review)

            if updated_data['reviewer_rating']:
                try:
                    updated_data['reviewer_rating'] = int(updated_data['reviewer_rating'])
                    if not (1 <= updated_data['reviewer_rating'] <= 10):
                        flash('Rating must be between 1 and 10', 'error')
                        return render_template('edit_review.html', user=user, movie=movie, review=review)
                except ValueError:
                    flash('Invalid rating format', 'error')
                    return render_template('edit_review.html', user=user, movie=movie, review=review)

            result = data_manager.update_review(review_id, updated_data)
            if result:
                flash('Review updated successfully!', 'success')
            else:
                flash('Error updating review', 'error')

            return redirect(url_for('movies.movie_detail', user_id=user_id, movie_id=movie_id))

        return render_template('edit_review.html', user=user, movie=movie, review=review)

    except Exception as e:
        flash(f'Error editing review: {str(e)}', 'error')
        return redirect(url_for('movies.movie_detail', user_id=user_id, movie_id=movie_id))


@review_bp.route('/delete_review/<int:review_id>')
def delete_review_route(user_id, movie_id, review_id):
    """Delete a review"""
    try:
        success = data_manager.delete_review(review_id)

        if success:
            flash('Review deleted successfully!', 'success')
        else:
            flash('Review not found or could not be deleted', 'error')

        return redirect(url_for('movies.movie_detail', user_id=user_id, movie_id=movie_id))

    except Exception as e:
        flash(f'Error deleting review: {str(e)}', 'error')
        return redirect(url_for('movies.movie_detail', user_id=user_id, movie_id=movie_id))