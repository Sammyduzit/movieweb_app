"""
Trivia Service - Business logic for trivia operations.
Handles trivia generation, scoring, and leaderboard operations.
"""
from config import TriviaConfig, LeaderboardConfig
from datamanager import SQLiteDataManager
from services.rapidapi_service import RapidAPIService
from exceptions import (
    TriviaError, InsufficientMoviesError, UserNotFoundError,
    MovieNotFoundError, ExternalAPIError
)
from utils.template_helpers import format_percentage, get_performance_badge


class TriviaService:
    """Service class for handling trivia-related business logic"""

    def __init__(self):
        self.data_manager = SQLiteDataManager()
        self.rapidapi_service = RapidAPIService()

    def validate_user(self, user_id):
        """Validate that user exists, raise UserNotFoundError if not"""
        users = self.data_manager.get_all_users()
        user = next((u for u in users if u['id'] == user_id), None)
        if not user:
            raise UserNotFoundError(user_id)
        return user

    def validate_movie(self, user_id, movie_id):
        """Validate that movie exists for user, raise MovieNotFoundError if not"""
        movies = self.data_manager.get_user_movies(user_id)
        movie = next((m for m in movies if m['id'] == movie_id), None)
        if not movie:
            raise MovieNotFoundError(movie_id)
        return movie

    def validate_collection_trivia_requirements(self, user_id):
        """Validate user has enough movies for collection trivia"""
        movies = self.data_manager.get_user_movies(user_id)
        if len(movies) < TriviaConfig.MIN_MOVIES_FOR_COLLECTION:
            raise InsufficientMoviesError(user_id, len(movies), TriviaConfig.MIN_MOVIES_FOR_COLLECTION)
        return movies

    def generate_movie_trivia(self, user_id, movie_id):
        """Generate trivia questions for a specific movie"""
        user = self.validate_user(user_id)
        movie = self.validate_movie(user_id, movie_id)

        try:
            trivia_data = self.rapidapi_service.generate_movie_trivia(movie)

            if not trivia_data or not trivia_data.get('questions'):
                raise TriviaError("Failed to generate movie trivia questions", "movie")

            questions = trivia_data['questions'][:TriviaConfig.MOVIE_QUESTIONS]

            return {
                'type': 'movie',
                'user_id': user_id,
                'movie_id': movie_id,
                'questions': questions,
                'user': user,
                'movie': movie
            }

        except Exception as e:
            if isinstance(e, TriviaError):
                raise
            raise ExternalAPIError("RapidAPI", str(e))

    def generate_collection_trivia(self, user_id):
        """Generate trivia questions for user's movie collection"""
        user = self.validate_user(user_id)
        movies = self.validate_collection_trivia_requirements(user_id)

        try:
            trivia_data = self.rapidapi_service.generate_collection_trivia(movies)

            if not trivia_data or not trivia_data.get('questions'):
                raise TriviaError("Failed to generate collection trivia questions", "collection")

            questions = trivia_data['questions'][:TriviaConfig.COLLECTION_QUESTIONS]

            return {
                'type': 'collection',
                'user_id': user_id,
                'questions': questions,
                'user': user,
                'movies': movies
            }

        except Exception as e:
            if isinstance(e, (TriviaError, InsufficientMoviesError)):
                raise
            raise ExternalAPIError("RapidAPI", str(e))

    def process_trivia_answer(self, trivia_session, user_answer):
        """Process a trivia answer and update session"""
        current_q = trivia_session['current_question']
        questions = trivia_session['questions']

        if current_q >= len(questions):
            return trivia_session

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

        return trivia_session

    def calculate_trivia_results(self, trivia_session):
        """Calculate final trivia results and performance metrics"""
        total_questions = len(trivia_session['questions'])
        score = trivia_session['score']
        percentage = format_percentage(score, total_questions)
        performance = get_performance_badge(percentage)

        return {
            'score': score,
            'total': total_questions,
            'percentage': percentage,
            'performance': f"{performance['emoji']} {performance['text']}",
            'answers': trivia_session['answers'],
            'type': trivia_session['type']
        }

    def save_trivia_score(self, trivia_session):
        """Save trivia score to database"""
        total_questions = len(trivia_session['questions'])
        score = trivia_session['score']
        percentage = format_percentage(score, total_questions)

        score_data = {
            'user_id': trivia_session['user_id'],
            'trivia_type': trivia_session['type'],
            'movie_id': trivia_session.get('movie_id'),
            'score': score,
            'total_questions': total_questions,
            'percentage': percentage,
            'completion_time': trivia_session.get('completion_time')
        }

        try:
            return self.data_manager.save_trivia_score(score_data)
        except Exception as e:
            print(f"Warning: Failed to save trivia score: {e}")
            return None

    def get_leaderboard(self, leaderboard_type, **kwargs):
        """Get leaderboard data based on type"""
        try:
            if leaderboard_type == 'global':
                limit = kwargs.get('limit', LeaderboardConfig.GLOBAL_LIMIT)
                return self.data_manager.get_global_leaderboard(limit)

            elif leaderboard_type == 'collection':
                limit = kwargs.get('limit', LeaderboardConfig.COLLECTION_LIMIT)
                return self.data_manager.get_collection_leaderboard(limit)

            elif leaderboard_type == 'movie':
                movie_id = kwargs.get('movie_id')
                limit = kwargs.get('limit', LeaderboardConfig.MOVIE_LIMIT)
                if not movie_id:
                    raise ValueError("movie_id required for movie leaderboard")
                return self.data_manager.get_movie_leaderboard(movie_id, limit)

            else:
                raise ValueError(f"Unknown leaderboard type: {leaderboard_type}")

        except Exception as e:
            print(f"Error fetching {leaderboard_type} leaderboard: {e}")
            return []

    def get_user_stats(self, user_id):
        """Get comprehensive trivia statistics for a user"""
        # Validate user exists
        user = self.validate_user(user_id)

        try:
            stats = self.data_manager.get_user_trivia_stats(user_id)
            return {
                'user': user,
                'stats': stats
            }
        except Exception as e:
            print(f"Error fetching user stats for {user_id}: {e}")
            return {
                'user': user,
                'stats': {
                    'total_attempts': 0,
                    'best_score': 0,
                    'average_score': 0,
                    'movie_attempts': 0,
                    'collection_attempts': 0,
                    'recent_scores': []
                }
            }