from config import TriviaConfig
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.mock_trivia_service import MockTriviaService
from exceptions import (
    TriviaError, UserNotFoundError, MovieNotFoundError,
    InsufficientMoviesError, ExternalAPIError
)
from utils.decorators import require_user, require_user_and_movie

trivia_bp = Blueprint('trivia', __name__)
trivia_service = MockTriviaService()

def get_api_status():
    """Get current API status for templates"""
    try:
        from services.rapidapi_service import RapidAPIService
        rapidapi_service = RapidAPIService()
        stats = rapidapi_service.usage_tracker.get_usage_stats()
        return {
            'api_available': stats['remaining'] > 0,
            'calls_made': stats['calls_made'],
            'limit': stats['limit'],
            'remaining': stats['remaining']
        }
    except:
        return {'api_available': True, 'calls_made': 0, 'limit': 95, 'remaining': 95}
# ==================== MOVIE TRIVIA ====================

@trivia_bp.route('/users/<int:user_id>/movies/<int:movie_id>/trivia')
@require_user_and_movie
def movie_trivia(user_id, movie_id, user, movie):
    """Start trivia for a specific movie (7 questions)"""
    api_status = get_api_status()

    # CHECK API LIMIT
    if not api_status['api_available']:
        flash(
            f'Monthly API limit reached ({api_status["calls_made"]}/{api_status["limit"]}). Trivia resets next month.',
            'error')
        return redirect(url_for('movies.movie_detail', user_id=user_id, movie_id=movie_id))

    if api_status['remaining'] <= 5:
        flash(f'Warning: Only {api_status["remaining"]} API calls remaining this month!', 'warning')

    try:
        trivia_data = trivia_service.generate_movie_trivia(user_id, movie_id)

        session['trivia_session'] = {
            'type': trivia_data['type'],
            'user_id': trivia_data['user_id'],
            'movie_id': trivia_data['movie_id'],
            'questions': trivia_data['questions'],
            'current_question': 0,
            'score': 0,
            'answers': [],
            'api_used': trivia_data.get('api_used', 'unknown')
        }

        return redirect(url_for('trivia.trivia_question'))

    except TriviaError as e:
        return render_template('trivia_error.html',
                               user=user,
                               movie=movie,
                               error_type=e.trivia_type,
                               back_url=url_for('movies.movie_detail', user_id=user_id, movie_id=movie_id))

    except ExternalAPIError as e:
        flash(f'API Error: {e.message}', 'error')
        return redirect(url_for('movies.movie_detail', user_id=user_id, movie_id=movie_id))

    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'error')
        return redirect(url_for('movies.movie_detail', user_id=user_id, movie_id=movie_id))

# ==================== COLLECTION TRIVIA ====================

@trivia_bp.route('/users/<int:user_id>/trivia')
@require_user
def collection_trivia(user_id, user):
    """Start trivia for user's entire collection (21 questions)"""
    api_status = get_api_status()

    # CHECK API LIMIT
    if not api_status['api_available']:
        flash(
            f'Monthly API limit reached ({api_status["calls_made"]}/{api_status["limit"]}). Trivia resets next month.',
            'error')
        return redirect(url_for('movies.user_movies', user_id=user_id))

    if api_status['remaining'] <= 5:
        flash(f'Warning: Only {api_status["remaining"]} API calls remaining this month!', 'warning')

    try:
        trivia_data = trivia_service.generate_collection_trivia(user_id)

        session['trivia_session'] = {
            'type': trivia_data['type'],
            'user_id': trivia_data['user_id'],
            'questions': trivia_data['questions'],
            'current_question': 0,
            'score': 0,
            'answers': [],
            'api_used': trivia_data.get('api_used', 'unknown')
        }

        return redirect(url_for('trivia.trivia_question'))

    except InsufficientMoviesError as e:
        flash(f'You need at least {e.required_count} movies for collection trivia! You have {e.movie_count}.', 'error')
        return redirect(url_for('movies.user_movies', user_id=user_id))

    except TriviaError as e:
        return render_template('trivia_error.html',
                               user=user,
                               error_type=e.trivia_type,
                               back_url=url_for('movies.user_movies', user_id=user_id))

    except ExternalAPIError as e:
        flash(f'API Error: {e.message}', 'error')
        return redirect(url_for('movies.user_movies', user_id=user_id))

    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'error')
        return redirect(url_for('movies.user_movies', user_id=user_id))


# ==================== TRIVIA GAME LOGIC ====================

@trivia_bp.route('/trivia/question')
def trivia_question():
    """Display current trivia question"""
    trivia_session = session.get('trivia_session')

    if not trivia_session:
        flash('No active trivia session', 'error')
        return redirect(url_for('users.list_users'))

    current_q = trivia_session['current_question']
    questions = trivia_session['questions']

    if current_q >= len(questions):
        return redirect(url_for('trivia.trivia_results'))

    question_data = questions[current_q]
    progress = {
        'current': current_q + 1,
        'total': len(questions),
        'percentage': round(((current_q + 1) / len(questions)) * 100)
    }

    return render_template('trivia_question.html',
                           question=question_data,
                           progress=progress,
                           trivia_type=trivia_session['type'])


@trivia_bp.route('/trivia/answer', methods=['POST'])
def trivia_answer():
    """Process trivia answer and move to next question"""
    trivia_session = session.get('trivia_session')

    if not trivia_session:
        flash('No active trivia session', 'error')
        return redirect(url_for('users.list_users'))

    try:
        user_answer = int(request.form.get('answer', -1))

        updated_session = trivia_service.process_trivia_answer(trivia_session, user_answer)

        session['trivia_session'] = updated_session

        return redirect(url_for('trivia.trivia_question'))

    except ValueError:
        flash('Invalid answer format', 'error')
        return redirect(url_for('trivia.trivia_question'))
    except Exception as e:
        flash(f'Error processing answer: {str(e)}', 'error')
        return redirect(url_for('trivia.trivia_question'))


@trivia_bp.route('/trivia/results')
def trivia_results():
    """Show trivia results"""
    trivia_session = session.get('trivia_session')

    if not trivia_session:
        flash('No trivia session found', 'error')
        return redirect(url_for('users.list_users'))

    try:
        results = trivia_service.calculate_trivia_results(trivia_session)
        trivia_service.save_trivia_score(trivia_session)

        session.pop('trivia_session', None)

        if trivia_session['type'] == 'movie':
            back_url = url_for('movies.movie_detail',
                               user_id=trivia_session['user_id'],
                               movie_id=trivia_session['movie_id'])
        else:
            back_url = url_for('movies.user_movies', user_id=trivia_session['user_id'])

        return render_template('trivia_results.html', results=results, back_url=back_url)

    except Exception as e:
        flash(f'Error calculating results: {str(e)}', 'error')
        return redirect(url_for('users.list_users'))


@trivia_bp.route('/trivia/quit')
def trivia_quit():
    """Quit current trivia session"""
    trivia_session = session.get('trivia_session')

    if trivia_session:
        user_id = trivia_session['user_id']

        if trivia_session['type'] == 'movie':
            movie_id = trivia_session['movie_id']
            back_url = url_for('movies.movie_detail', user_id=user_id, movie_id=movie_id)
        else:
            back_url = url_for('movies.user_movies', user_id=user_id)

        session.pop('trivia_session', None)
        flash('Trivia session ended', 'info')
        return redirect(back_url)

    return redirect(url_for('users.list_users'))


# ==================== LEADERBOARD ROUTES ====================

@trivia_bp.route('/leaderboard')
def global_leaderboard():
    """Global trivia leaderboard"""
    try:
        leaderboard = trivia_service.get_leaderboard('global', limit=20)
        return render_template('leaderboard.html',
                               leaderboard=leaderboard,
                               leaderboard_type='global',
                               title='🏆 Global Trivia Leaderboard')
    except Exception as e:
        flash(f'Error loading leaderboard: {str(e)}', 'error')
        return redirect(url_for('users.list_users'))


@trivia_bp.route('/leaderboard/collection')
def collection_leaderboard():
    """Collection trivia leaderboard"""
    try:
        leaderboard = trivia_service.get_leaderboard('collection', limit=20)
        return render_template('leaderboard.html',
                               leaderboard=leaderboard,
                               leaderboard_type='collection',
                               title='🎯 Collection Trivia Leaderboard')
    except Exception as e:
        flash(f'Error loading collection leaderboard: {str(e)}', 'error')
        return redirect(url_for('users.list_users'))


@trivia_bp.route('/users/<int:user_id>/movies/<int:movie_id>/leaderboard')
@require_user_and_movie
def movie_leaderboard(user_id, movie_id, user, movie):
    """Movie-specific leaderboard"""
    try:
        leaderboard = trivia_service.get_leaderboard('movie', movie_id=movie_id, limit=15)

        return render_template('leaderboard.html',
                               leaderboard=leaderboard,
                               leaderboard_type='movie',
                               title=f'🎬 "{movie["title"]}" Trivia Leaderboard',
                               movie=movie,
                               back_url=url_for('movies.movie_detail', user_id=user_id, movie_id=movie_id))

    except Exception as e:
        flash(f'Error loading movie leaderboard: {str(e)}', 'error')
        return redirect(url_for('movies.movie_detail', user_id=user_id, movie_id=movie_id))


@trivia_bp.route('/users/<int:user_id>/trivia-stats')
@require_user
def user_trivia_stats(user_id, user):
    """User's personal trivia statistics"""
    try:
        user_stats = trivia_service.get_user_stats(user_id)

        return render_template('user_trivia_stats.html',
                               user=user_stats['user'],
                               stats=user_stats['stats'])

    except Exception as e:
        flash(f'Error loading trivia stats: {str(e)}', 'error')
        return redirect(url_for('movies.user_movies', user_id=user_id))