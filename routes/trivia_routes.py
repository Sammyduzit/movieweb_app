from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datamanager import SQLiteDataManager, RapidAPIService
import random

trivia_bp = Blueprint('trivia', __name__)

data_manager = SQLiteDataManager()
rapidapi_service = RapidAPIService()


# ==================== MOVIE TRIVIA ====================

@trivia_bp.route('/users/<int:user_id>/movies/<int:movie_id>/trivia')
def movie_trivia(user_id, movie_id):
    """Start trivia for a specific movie (7 questions)"""
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

        trivia_data = rapidapi_service.generate_movie_trivia(movie)

        if not trivia_data or not trivia_data.get('questions'):
            return render_template('trivia_error.html', user=user, movie=movie,
                                   error_type='movie',
                                   back_url=url_for('movies.movie_detail', user_id=user_id, movie_id=movie_id))

        questions = trivia_data['questions'][:7]  # Ensure exactly 7 questions

        session['trivia_session'] = {
            'type': 'movie',
            'user_id': user_id,
            'movie_id': movie_id,
            'questions': questions,
            'current_question': 0,
            'score': 0,
            'answers': []
        }

        return redirect(url_for('trivia.trivia_question'))

    except Exception as e:
        flash(f'Error starting trivia: {str(e)}', 'error')
        return redirect(url_for('movies.movie_detail', user_id=user_id, movie_id=movie_id))


# ==================== COLLECTION TRIVIA ====================

@trivia_bp.route('/users/<int:user_id>/trivia')
def collection_trivia(user_id):
    """Start trivia for user's entire collection (21 questions)"""
    try:
        users = data_manager.get_all_users()
        user = next((u for u in users if u['id'] == user_id), None)

        if not user:
            flash('User not found', 'error')
            return redirect(url_for('users.list_users'))

        movies = data_manager.get_user_movies(user_id)

        if len(movies) < 3:
            flash('You need at least 3 movies for collection trivia!', 'error')
            return redirect(url_for('movies.user_movies', user_id=user_id))

        trivia_data = rapidapi_service.generate_collection_trivia(movies)

        if not trivia_data or not trivia_data.get('questions'):
            return render_template('trivia_error.html', user=user,
                                   error_type='collection', back_url=url_for('movies.user_movies', user_id=user_id))

        questions = trivia_data['questions'][:21]  # Ensure exactly 21 questions

        session['trivia_session'] = {
            'type': 'collection',
            'user_id': user_id,
            'questions': questions,
            'current_question': 0,
            'score': 0,
            'answers': []
        }

        return redirect(url_for('trivia.trivia_question'))

    except Exception as e:
        flash(f'Error starting trivia: {str(e)}', 'error')
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

    # Check if trivia is complete
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
        current_q = trivia_session['current_question']
        questions = trivia_session['questions']

        if current_q >= len(questions):
            return redirect(url_for('trivia.trivia_results'))

        question = questions[current_q]
        correct_answer = question.get('correct', 0)
        is_correct = user_answer == correct_answer

        trivia_session['answers'].append({
            'question': question['question'],
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'options': question.get('options', [])
        })

        if is_correct:
            trivia_session['score'] += 1

        trivia_session['current_question'] += 1
        session['trivia_session'] = trivia_session

        return redirect(url_for('trivia.trivia_question'))

    except ValueError:
        flash('Invalid answer format', 'error')
        return redirect(url_for('trivia.trivia_question'))


@trivia_bp.route('/trivia/results')
def trivia_results():
    """Show trivia results"""
    trivia_session = session.get('trivia_session')

    if not trivia_session:
        flash('No trivia session found', 'error')
        return redirect(url_for('users.list_users'))

    total_questions = len(trivia_session['questions'])
    score = trivia_session['score']
    percentage = round((score / total_questions) * 100) if total_questions > 0 else 0

    try:
        score_data = {
            'user_id': trivia_session['user_id'],
            'trivia_type': trivia_session['type'],
            'movie_id': trivia_session.get('movie_id'),
            'score': score,
            'total_questions': total_questions,
            'percentage': percentage,
            'completion_time': None
        }

        data_manager.save_trivia_score(score_data)
        print(f"✅ Saved trivia score: {score}/{total_questions} ({percentage}%)")

    except Exception as e:
        print(f"🔴 Error saving trivia score: {e}")

    if percentage >= 90:
        performance = "🏆 Movie Master!"
    elif percentage >= 75:
        performance = "🌟 Cinema Expert!"
    elif percentage >= 60:
        performance = "🎬 Movie Buff!"
    elif percentage >= 40:
        performance = "🍿 Getting There!"
    else:
        performance = "📚 Study More!"

    results = {
        'score': score,
        'total': total_questions,
        'percentage': percentage,
        'performance': performance,
        'answers': trivia_session['answers'],
        'type': trivia_session['type']
    }

    session.pop('trivia_session', None)

    if trivia_session['type'] == 'movie':
        back_url = url_for('movies.movie_detail',
                           user_id=trivia_session['user_id'],
                           movie_id=trivia_session['movie_id'])
    else:
        back_url = url_for('movies.user_movies', user_id=trivia_session['user_id'])

    return render_template('trivia_results.html', results=results, back_url=back_url)


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
        leaderboard = data_manager.get_global_leaderboard(limit=20)
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
        leaderboard = data_manager.get_collection_leaderboard(limit=20)
        return render_template('leaderboard.html',
                               leaderboard=leaderboard,
                               leaderboard_type='collection',
                               title='🎯 Collection Trivia Leaderboard')
    except Exception as e:
        flash(f'Error loading collection leaderboard: {str(e)}', 'error')
        return redirect(url_for('users.list_users'))


@trivia_bp.route('/users/<int:user_id>/movies/<int:movie_id>/leaderboard')
def movie_leaderboard(user_id, movie_id):
    """Movie-specific leaderboard"""
    try:
        movies = data_manager.get_user_movies(user_id)
        movie = next((m for m in movies if m['id'] == movie_id), None)

        if not movie:
            flash('Movie not found', 'error')
            return redirect(url_for('users.list_users'))

        leaderboard = data_manager.get_movie_leaderboard(movie_id, limit=15)
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
def user_trivia_stats(user_id):
    """User's personal trivia statistics"""
    try:
        users = data_manager.get_all_users()
        user = next((u for u in users if u['id'] == user_id), None)

        if not user:
            flash('User not found', 'error')
            return redirect(url_for('users.list_users'))

        stats = data_manager.get_user_trivia_stats(user_id)
        return render_template('user_trivia_stats.html',
                               user=user,
                               stats=stats)
    except Exception as e:
        flash(f'Error loading trivia stats: {str(e)}', 'error')
        return redirect(url_for('movies.user_movies', user_id=user_id))