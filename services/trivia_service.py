"""
Trivia Service - Business logic for trivia operations.
Handles trivia generation, scoring, and leaderboard operations.
"""
from config import TriviaConfig, LeaderboardConfig
from datamanager import SQLiteDataManager
from services.openai_service import OpenAIService
from services.rapidapi_service import RapidAPIService
from exceptions import (
    TriviaError, InsufficientMoviesError, UserNotFoundError,
    MovieNotFoundError, ExternalAPIError
)
from utils.template_helpers import format_percentage, get_performance_badge


class TriviaService:
    """Service class for handling trivia-related business logic"""

    def __init__(self):
        """Initialize trivia service with data manager and API services."""
        self.data_manager = SQLiteDataManager()
        self.rapidapi_service = RapidAPIService()
        self.openai_service = OpenAIService()

    # ==================== VALIDATION METHODS ====================

    def validate_user(self, user_id):
        """
        Validate that user exists, raise UserNotFoundError if not.

        :param user_id: ID of the user to validate
        :return: User dictionary if found
        """
        """Validate that user exists, raise UserNotFoundError if not"""
        users = self.data_manager.get_all_users()
        user = next((u for u in users if u['id'] == user_id), None)
        if not user:
            raise UserNotFoundError(user_id)
        return user

    def validate_movie(self, user_id, movie_id):
        """
        Validate that movie exists for user, raise MovieNotFoundError if not.

        :param user_id: ID of the user
        :param movie_id: ID of the movie to validate
        :return: Movie dictionary if found
        """
        movies = self.data_manager.get_user_movies(user_id)
        movie = next((m for m in movies if m['id'] == movie_id), None)
        if not movie:
            raise MovieNotFoundError(movie_id)
        return movie

    def validate_collection_trivia_requirements(self, user_id):
        """
        Validate user has enough movies for collection trivia.

        :param user_id: ID of the user
        :return: List of user's movies if requirements met
        """
        movies = self.data_manager.get_user_movies(user_id)
        required_count = TriviaConfig.MIN_MOVIES_FOR_COLLECTION

        if len(movies) < required_count:
            raise InsufficientMoviesError(user_id, len(movies), required_count)
        return movies

    # ==================== TRIVIA GENERATION ====================

    def generate_movie_trivia(self, user_id, movie_id):
        """
        Generate trivia questions for a specific movie with API fallback.

        :param user_id: ID of the user
        :param movie_id: ID of the movie
        :return: Dictionary containing trivia data and metadata
        """
        user = self.validate_user(user_id)
        movie = self.validate_movie(user_id, movie_id)

        trivia_data, api_used = self._generate_trivia_with_fallback(
            'movie', movie
        )

        if not trivia_data or not trivia_data.get('questions'):
            raise TriviaError(
                "Both RapidAPI and OpenAI failed to generate movie trivia questions",
                "movie"
            )

        questions = trivia_data['questions'][:TriviaConfig.MOVIE_QUESTIONS]

        return {
            'type': 'movie',
            'user_id': user_id,
            'movie_id': movie_id,
            'questions': questions,
            'user': user,
            'movie': movie,
            'api_used': api_used
        }


    def generate_collection_trivia(self, user_id):
        """
        Generate trivia questions for user's movie collection with API fallback.

        :param user_id: ID of the user
        :return: Dictionary containing trivia data and metadata
        """
        user = self.validate_user(user_id)
        movies = self.validate_collection_trivia_requirements(user_id)

        trivia_data, api_used = self._generate_trivia_with_fallback(
            'collection', movies
        )

        if not trivia_data or not trivia_data.get('questions'):
            raise TriviaError(
                "Both RapidAPI and OpenAI failed to generate "
                "collection trivia questions",
                "collection"
            )

        questions = trivia_data['questions'][:TriviaConfig.COLLECTION_QUESTIONS]

        return {
            'type': 'collection',
            'user_id': user_id,
            'questions': questions,
            'user': user,
            'movies': movies,
            'api_used': api_used
        }

    def _generate_trivia_with_fallback(self, trivia_type, data):
        """
        Generate trivia with automatic fallback from RapidAPI to OpenAI.

        :param trivia_type: Type of trivia ('movie' or 'collection')
        :param data: Movie data or movies list depending on type
        :return: Tuple of (trivia_data, api_used)
        """
        # Try RapidAPI first
        trivia_data, api_used = self._try_rapidapi_generation(trivia_type, data)

        if trivia_data and trivia_data.get('questions'):
            return trivia_data, api_used

        # Fallback to OpenAI
        print("⚠️ RapidAPI failed, trying fallback...")
        trivia_data, api_used = self._try_openai_generation(trivia_type, data)

        return trivia_data, api_used

    def _try_rapidapi_generation(self, trivia_type, data):
        """
        Try generating trivia with RapidAPI.

        :param trivia_type: Type of trivia ('movie' or 'collection')
        :param data: Movie data or movies list
        :return: Tuple of (trivia_data, api_used)
        """
        try:
            print("🎯 Attempting trivia generation with RapidAPI...")

            if trivia_type == 'movie':
                trivia_data = self.rapidapi_service.generate_movie_trivia(data)
            else:
                trivia_data = self.rapidapi_service.generate_collection_trivia(data)

            if trivia_data and trivia_data.get('questions'):
                print("✅ RapidAPI trivia generation successful")
                return trivia_data, "rapidapi"
            else:
                print("⚠️ RapidAPI returned no valid questions")
                return None, "none"

        except Exception as e:
            print(f"⚠️ RapidAPI error: {e}")
            return None, "none"

    def _try_openai_generation(self, trivia_type, data):
        """
        Try generating trivia with OpenAI.

        :param trivia_type: Type of trivia ('movie' or 'collection')
        :param data: Movie data or movies list
        :return: Tuple of (trivia_data, api_used)
        """
        try:
            print("🔄 Falling back to OpenAI ChatGPT...")

            if trivia_type == 'movie':
                trivia_data = self.openai_service.generate_movie_trivia(data)
            else:
                trivia_data = self.openai_service.generate_collection_trivia(data)

            if trivia_data and trivia_data.get('questions'):
                print("✅ OpenAI trivia generation successful")
                return trivia_data, "openai"
            else:
                print("❌ OpenAI also failed")
                return None, "none"

        except Exception as e:
            print(f"❌ OpenAI fallback error: {e}")
            return None, "none"

    # ==================== GAME PROCESSING ====================

    def process_trivia_answer(self, trivia_session, user_answer):
        """
        Process a trivia answer and update session state.

        :param trivia_session: Current trivia session dictionary
        :param user_answer: User's answer (integer index)
        :return: Updated trivia session dictionary
        """
        current_q = trivia_session['current_question']
        questions = trivia_session['questions']

        if current_q >= len(questions):
            return trivia_session

        question = questions[current_q]
        correct_answer = question.get('correct', 0)
        is_correct = user_answer == correct_answer
        self._log_answer_debug(question, user_answer, correct_answer,
                             is_correct, trivia_session.get('score', 0))

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

    def _log_answer_debug(self, question, user_answer, correct_answer,
                         is_correct, current_score):
        """
        Log debug information about answer processing.

        :param question: Question dictionary
        :param user_answer: User's answer
        :param correct_answer: Correct answer
        :param is_correct: Whether answer was correct
        :param current_score: Current score before this answer
        :return: None
        """
        print(f"🔍 DEBUG: Answer checking:")
        print(f"  Question: {question.get('question', 'N/A')[:50]}...")
        print(f"  User answer: {user_answer}")
        print(f"  Correct answer: {correct_answer}")
        print(f"  Is correct: {is_correct}")
        print(f"  Current score: {current_score}")

    # ==================== SCORING AND RESULTS ====================

    def calculate_trivia_results(self, trivia_session):
        """
        Calculate final trivia results and performance metrics.

        :param trivia_session: Completed trivia session dictionary
        :return: Dictionary containing results and performance data
        """
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
        """
        Save trivia score to database.

        :param trivia_session: Trivia session dictionary with results
        :return: Saved score dictionary or None if failed
        """
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

    # ==================== LEADERBOARDS AND STATISTICS ====================

    def get_leaderboard(self, leaderboard_type, **kwargs):
        """
        Get leaderboard data based on type.

        :param leaderboard_type: Type of leaderboard ('global', 'collection', 'movie')
        :param kwargs: Additional parameters (movie_id, limit)
        :return: List of leaderboard entries
        """
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
        """
        Get comprehensive trivia statistics for a user.

        :param user_id: ID of the user
        :return: Dictionary containing user and stats data
        """
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

    # ==================== UTILITY METHODS ====================

    def test_apis(self):
        """
        Test both API connections for diagnostics.

        :return: Dictionary containing test results for both APIs
        """
        print("🧪 Testing API connections...")

        rapidapi_status = self.rapidapi_service.test_connection()
        openai_status = self.openai_service.test_connection()

        return {
            'rapidapi': rapidapi_status,
            'openai': openai_status,
            'fallback_available': openai_status
        }