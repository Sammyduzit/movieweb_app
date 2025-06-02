"""
Trivia Routes - Web routes for trivia game functionality.
Handles trivia generation, game flow, scoring, and leaderboards.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from config import TriviaConfig
from services.mock_trivia_service import MockTriviaService
from services.rapidapi_service import RapidAPIService
from services.trivia_service import TriviaService
from utils.decorators import require_user, require_user_and_movie

from exceptions import (
    TriviaError, UserNotFoundError, MovieNotFoundError,
    InsufficientMoviesError, ExternalAPIError
)

rapidapi_service = RapidAPIService()
trivia_bp = Blueprint('trivia', __name__)
trivia_service = TriviaService()


def get_api_status():
    """
    Get current API status for templates.

    :return: Dictionary containing API status information
    """
    try:
        stats = rapidapi_service.usage_tracker.get_usage_stats()
        return {
            'api_available': stats['remaining'] > 0,
            'calls_made': stats['calls_made'],
            'limit': stats['limit'],
            'remaining': stats['remaining']
        }
    except Exception:
        return {
            'api_available': True,
            'calls_made': 0,
            'limit': 95,
            'remaining': 95
        }


def handle_api_limit_check(api_status, redirect_url, limit_warning=5):
    """
    Check API limits and handle warnings/errors.

    :param api_status: API status dictionary from get_api_status()
    :param redirect_url: URL to redirect to if limit reached
    :param limit_warning: Warning threshold for remaining calls
    :return: Redirect response if limit reached, None otherwise
    """
    if not api_status['api_available']:
        flash(
            f'Monthly API limit reached '
            f'({api_status["calls_made"]}/{api_status["limit"]}). '
            f'Trivia resets next month.',
            'error'
        )
        return redirect(redirect_url)

    if api_status['remaining'] <= limit_warning:
        flash(
            f'Warning: Only {api_status["remaining"]} API calls '
            f'remaining this month!',
            'warning'
        )

    return None


# ==================== MOVIE TRIVIA ====================

@trivia_bp.route('/users/<int:user_id>/movies/<int:movie_id>/trivia')
@require_user_and_movie
def movie_trivia(user_id, movie_id, user, movie):
    """
    Start trivia for a specific movie (7 questions).

    :param user_id: ID of the user
    :param movie_id: ID of the movie
    :param user: User object (injected by decorator)
    :param movie: Movie object (injected by decorator)
    :return: Redirect to trivia question or error page
    """
    api_status = get_api_status()
    redirect_url = url_for('movies.movie_detail',
                          user_id=user_id,
                          movie_id=movie_id)

    # CHECK API LIMIT
    limit_check = handle_api_limit_check(api_status, redirect_url)
    if limit_check:
        return limit_check

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
                               back_url=redirect_url)

    except ExternalAPIError as e:
        flash(f'API Error: {e.message}', 'error')
        return redirect(redirect_url)

    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'error')
        return redirect(redirect_url)


# ==================== COLLECTION TRIVIA ====================

@trivia_bp.route('/users/<int:user_id>/trivia')
@require_user
def collection_trivia(user_id, user):
    """
    Start trivia for user's entire collection (21 questions).

    :param user_id: ID of the user
    :param user: User object (injected by decorator)
    :return: Redirect to trivia question or error page
    """
    api_status = get_api_status()
    redirect_url = url_for('movies.user_movies', user_id=user_id)

    # CHECK API LIMIT
    limit_check = handle_api_limit_check(api_status, redirect_url)
    if limit_check:
        return limit_check

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
        flash(f'You need at least {e.required_count} movies for collection trivia! '
              f'You have {e.movie_count}.',
              'error')
        return redirect(redirect_url)

    except TriviaError as e:
        return render_template('trivia_error.html',
                               user=user,
                               error_type=e.trivia_type,
                               back_url=redirect_url)

    except ExternalAPIError as e:
        flash(f'API Error: {e.message}', 'error')
        return redirect(redirect_url)

    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'error')
        return redirect(redirect_url)


# ==================== TRIVIA GAME LOGIC ====================

@trivia_bp.route('/trivia/question')
def trivia_question():
    """
    Display current trivia question.

    :return: Rendered trivia question template or redirect if no session
    """
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
    """
    Process trivia answer and move to next question.

    :return: Redirect to next question or error page
    """
    trivia_session = session.get('trivia_session')

    if not trivia_session:
        flash('No active trivia session', 'error')
        return redirect(url_for('users.list_users'))

    try:
        user_answer = int(request.form.get('answer', -1))
        updated_session = trivia_service.process_trivia_answer(
                            trivia_session, user_answer)

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
    """
    Show trivia results and save score.

    :return: Rendered results template or redirect if no session
    """
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
            back_url = url_for('movies.user_movies',
                               user_id=trivia_session['user_id'])

        return render_template('trivia_results.html',
                               results=results,
                               back_url=back_url)

    except Exception as e:
        flash(f'Error calculating results: {str(e)}', 'error')
        return redirect(url_for('users.list_users'))


@trivia_bp.route('/trivia/quit')
def trivia_quit():
    """
    Quit current trivia session.

    :return: Redirect to appropriate page based on trivia type
    """
    trivia_session = session.get('trivia_session')

    if trivia_session:
        user_id = trivia_session['user_id']

        if trivia_session['type'] == 'movie':
            movie_id = trivia_session['movie_id']
            back_url = url_for('movies.movie_detail',
                               user_id=user_id,
                               movie_id=movie_id)
        else:
            back_url = url_for('movies.user_movies', user_id=user_id)

        session.pop('trivia_session', None)
        flash('Trivia session ended', 'info')
        return redirect(back_url)

    return redirect(url_for('users.list_users'))


# ==================== LEADERBOARD ROUTES ====================

@trivia_bp.route('/leaderboard')
def global_leaderboard():
    """
    Display global trivia leaderboard.

    :return: Rendered leaderboard template
    """
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
    """
    Display collection trivia leaderboard.

    :return: Rendered leaderboard template
    """
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
    """
    Display movie-specific leaderboard.

    :param user_id: ID of the user
    :param movie_id: ID of the movie
    :param user: User object (injected by decorator)
    :param movie: Movie object (injected by decorator)
    :return: Rendered leaderboard template
    """
    try:
        leaderboard = trivia_service.get_leaderboard('movie',
                                                     movie_id=movie_id,
                                                     limit=15)

        return render_template('leaderboard.html',
                               leaderboard=leaderboard,
                               leaderboard_type='movie',
                               title=f'🎬 "{movie["title"]}" Trivia Leaderboard',
                               movie=movie,
                               back_url=url_for('movies.movie_detail',
                                                user_id=user_id,
                                                movie_id=movie_id))

    except Exception as e:
        flash(f'Error loading movie leaderboard: {str(e)}', 'error')
        return redirect(url_for('movies.movie_detail',
                                user_id=user_id,
                                movie_id=movie_id))


@trivia_bp.route('/users/<int:user_id>/trivia-stats')
@require_user
def user_trivia_stats(user_id, user):
    """
    Display user's personal trivia statistics.

    :param user_id: ID of the user
    :param user: User object (injected by decorator)
    :return: Rendered user statistics template
    """
    try:
        user_stats = trivia_service.get_user_stats(user_id)

        return render_template('user_trivia_stats.html',
                               user=user_stats['user'],
                               stats=user_stats['stats'])

    except Exception as e:
        flash(f'Error loading trivia stats: {str(e)}', 'error')
        return redirect(url_for('movies.user_movies', user_id=user_id))