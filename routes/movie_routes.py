from flask import Blueprint, render_template, request, redirect, url_for, flash
from datamanager import SQLiteDataManager, OMDbService
from sqlalchemy.exc import SQLAlchemyError

movie_bp = Blueprint('movies', __name__, url_prefix='/users/<int:user_id>')

data_manager = SQLiteDataManager()
omdb_service = OMDbService()


@movie_bp.route('/')
def user_movies(user_id):
    """Display a user's favorite movies."""
    try:
        users = data_manager.get_all_users()
        user = next((u for u in users if u['id'] == user_id), None)

        if not user:
            flash('User not found', 'error')
            return redirect(url_for('users.list_users'))

        movies = data_manager.get_user_movies(user_id)
        return render_template('user_movies.html', user=user, movies=movies)
    except SQLAlchemyError as e:
        flash(f'Database error loading movies: {str(e)}', 'error')
        return redirect(url_for('users.list_users'))
    except Exception as e:
        flash(f'Unexpected error loading movies: {str(e)}', 'error')
        return redirect(url_for('users.list_users'))


@movie_bp.route('/movies/<int:movie_id>')
def movie_detail(user_id, movie_id):
    """Display movie details with reviews."""
    try:
        users = data_manager.get_all_users()
        user = next((u for u in users if u['id'] == user_id), None)

        if not user:
            flash('User not found', 'error')
            return redirect(url_for('users.list_users'))

        movies = data_manager.get_user_movies(user_id)
        movie = next((m for m in movies if m['id'] == movie_id), None)

        if not movie:
            flash('Movie not found', 'error')
            return redirect(url_for('movies.user_movies', user_id=user_id))

        reviews = data_manager.get_movie_reviews(movie_id)
        return render_template('movie_detail.html', user=user, movie=movie, reviews=reviews)

    except Exception as e:
        flash(f'Error loading movie details: {str(e)}', 'error')
        return redirect(url_for('movies.user_movies', user_id=user_id))


@movie_bp.route('/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    """Add a new movie to a user's favorites."""
    try:
        users = data_manager.get_all_users()
        user = next((u for u in users if u['id'] == user_id), None)

        if not user:
            flash('User not found', 'error')
            return redirect(url_for('users.list_users'))

        if request.method == 'POST':
            movie_data = {
                'title': request.form.get('title', '').strip(),
                'director': request.form.get('director', '').strip() or None,
                'year': request.form.get('year', '').strip() or None,
                'genre': request.form.get('genre', '').strip() or None,
                'rating': request.form.get('rating', '').strip() or None
            }

            if not movie_data['title']:
                flash('Movie title is required', 'error')
                return render_template('add_movie.html', user=user)

            try:
                if movie_data['year']:
                    movie_data['year'] = int(movie_data['year'])
                if movie_data['rating']:
                    movie_data['rating'] = float(movie_data['rating'])
                    if not (1 <= movie_data['rating'] <= 10):
                        flash('Rating must be between 1 and 10', 'error')
                        return render_template('add_movie.html', user=user)
            except ValueError as e:
                flash('Invalid year or rating format', 'error')
                return render_template('add_movie.html', user=user)

            enhanced_data = omdb_service.enhance_movie_data(movie_data)
            new_movie = data_manager.add_user_movie(user_id, enhanced_data)
            flash(f'Movie "{new_movie["title"]}" added successfully!', 'success')
            return redirect(url_for('movies.user_movies', user_id=user_id))

        return render_template('add_movie.html', user=user)

    except SQLAlchemyError as e:
        flash(f'Database error adding movie: {str(e)}', 'error')
        return redirect(url_for('movies.user_movies', user_id=user_id))
    except ValueError as e:
        flash(f'User not found or invalid data: {str(e)}', 'error')
        return redirect(url_for('users.list_users'))
    except Exception as e:
        flash(f'Unexpected error adding movie: {str(e)}', 'error')
        return redirect(url_for('movies.user_movies', user_id=user_id))


@movie_bp.route('/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """Update a movie's details."""
    try:
        users = data_manager.get_all_users()
        user = next((u for u in users if u['id'] == user_id), None)

        if not user:
            flash('User not found', 'error')
            return redirect(url_for('users.list_users'))

        movies = data_manager.get_user_movies(user_id)
        movie = next((m for m in movies if m['id'] == movie_id), None)

        if not movie:
            flash('Movie not found', 'error')
            return redirect(url_for('movies.user_movies', user_id=user_id))

        if request.method == 'POST':
            updated_data = {
                'title': request.form.get('title', '').strip(),
                'director': request.form.get('director', '').strip() or None,
                'year': request.form.get('year', '').strip() or None,
                'genre': request.form.get('genre', '').strip() or None,
                'rating': request.form.get('rating', '').strip() or None
            }

            if not updated_data['title']:
                flash('Movie title is required', 'error')
                return render_template('update_movie.html', user=user, movie=movie)

            try:
                if updated_data['year']:
                    updated_data['year'] = int(updated_data['year'])
                if updated_data['rating']:
                    updated_data['rating'] = float(updated_data['rating'])
                    if not (1 <= updated_data['rating'] <= 10):
                        flash('Rating must be between 1 and 10', 'error')
                        return render_template('update_movie.html', user=user, movie=movie)
            except ValueError as e:
                flash('Invalid year or rating format', 'error')
                return render_template('update_movie.html', user=user, movie=movie)

            result = data_manager.update_movie(movie_id, updated_data)

            if result:
                flash(f'Movie "{updated_data["title"]}" updated successfully!', 'success')
            else:
                flash('Error updating movie', 'error')

            return redirect(url_for('movies.user_movies', user_id=user_id))

        return render_template('update_movie.html', user=user, movie=movie)

    except SQLAlchemyError as e:
        flash(f'Database error updating movie: {str(e)}', 'error')
        return redirect(url_for('movies.user_movies', user_id=user_id))
    except Exception as e:
        flash(f'Unexpected error updating movie: {str(e)}', 'error')
        return redirect(url_for('movies.user_movies', user_id=user_id))


@movie_bp.route('/delete_movie/<int:movie_id>')
def delete_movie(user_id, movie_id):
    """Delete a movie from a user's favorites."""
    try:
        users = data_manager.get_all_users()
        user = next((u for u in users if u['id'] == user_id), None)

        if not user:
            flash('User not found', 'error')
            return redirect(url_for('users.list_users'))

        movies = data_manager.get_user_movies(user_id)
        movie = next((m for m in movies if m['id'] == movie_id), None)
        movie_title = movie['title'] if movie else 'Unknown Movie'

        success = data_manager.delete_movie(movie_id)

        if success:
            flash(f'Movie "{movie_title}" deleted successfully!', 'success')
        else:
            flash('Movie not found or could not be deleted', 'error')

        return redirect(url_for('movies.user_movies', user_id=user_id))

    except SQLAlchemyError as e:
        flash(f'Database error deleting movie: {str(e)}', 'error')
        return redirect(url_for('movies.user_movies', user_id=user_id))
    except Exception as e:
        flash(f'Unexpected error deleting movie: {str(e)}', 'error')
        return redirect(url_for('movies.user_movies', user_id=user_id))