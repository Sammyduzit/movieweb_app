"""
Mock Trivia Service - For testing without API calls
Generates fake trivia questions to test scoring system
"""
from config import TriviaConfig
from datamanager import SQLiteDataManager
from exceptions import (
    TriviaError, InsufficientMoviesError, UserNotFoundError,
    MovieNotFoundError
)
from utils.template_helpers import format_percentage, get_performance_badge


class MockTriviaService:
    """Mock service for testing trivia without API calls"""

    def __init__(self):
        self.data_manager = SQLiteDataManager()

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
        """Generate MOCK trivia questions for a specific movie"""
        user = self.validate_user(user_id)
        movie = self.validate_movie(user_id, movie_id)

        print("🧪 MOCK: Generating movie trivia questions...")

        mock_questions = [
            {
                "question": f"What year was '{movie['title']}' released?",
                "options": ["2019", "2020", "2021", "2022"],
                "correct": 1,
                "difficulty": "easy"
            },
            {
                "question": f"Who directed '{movie['title']}'?",
                "options": [f"{movie.get('director', 'Unknown')}", "Steven Spielberg", "Christopher Nolan",
                            "Martin Scorsese"],
                "correct": 0,
                "difficulty": "medium"
            },
            {
                "question": f"What genre is '{movie['title']}'?",
                "options": ["Action", "Comedy", f"{movie.get('genre', 'Drama')}", "Horror"],
                "correct": 2,
                "difficulty": "easy"
            },
            {
                "question": f"In '{movie['title']}', what is the main character's motivation?",
                "options": ["Love", "Revenge", "Money", "Survival"],
                "correct": 0,  # Answer: Love
                "difficulty": "hard"
            },
            {
                "question": f"What is a memorable quote from '{movie['title']}'?",
                "options": ["I'll be back", "May the force be with you", "Here's looking at you, kid",
                            "Show me the money"],
                "correct": 2,
                "difficulty": "very hard"
            },
            {
                "question": f"What filming technique was notably used in '{movie['title']}'?",
                "options": ["Long takes", "Split screen", "Found footage", "Time loops"],
                "correct": 0,
                "difficulty": "very hard"
            },
            {
                "question": f"What easter egg appears in '{movie['title']}'?",
                "options": ["Stan Lee cameo", "Director cameo", "Previous movie reference", "Hidden number"],
                "correct": 1,
                "difficulty": "highest difficulty"
            }
        ]

        print(f"✅ MOCK: Generated {len(mock_questions)} trivia questions")

        return {
            'type': 'movie',
            'user_id': user_id,
            'movie_id': movie_id,
            'questions': mock_questions,
            'user': user,
            'movie': movie,
            'api_used': 'mock'
        }

    def generate_collection_trivia(self, user_id):
        """Generate MOCK trivia questions for user's movie collection"""
        user = self.validate_user(user_id)
        movies = self.validate_collection_trivia_requirements(user_id)

        print("🧪 MOCK: Generating collection trivia questions...")

        mock_questions = []

        for i, movie in enumerate(movies[:3]):
            mock_questions.append({
                "question": f"Which movie in your collection was directed by {movie.get('director', 'Unknown')}?",
                "options": [movie['title'], "The Matrix", "Inception", "Pulp Fiction"],
                "correct": 0,
                "difficulty": "medium"
            })

        if len(movies) >= 2:
            movie1, movie2 = movies[0], movies[1]
            mock_questions.extend([
                {
                    "question": f"Between '{movie1['title']}' and '{movie2['title']}', which was released first?",
                    "options": [movie1['title'], movie2['title'], "They were released the same year", "Unknown"],
                    "correct": 0 if (movie1.get('year', 2000) or 2000) <= (movie2.get('year', 2000) or 2000) else 1,
                    "difficulty": "medium"
                },
                {
                    "question": "How many movies do you have in your collection?",
                    "options": [str(len(movies)), str(len(movies) + 1), str(len(movies) - 1), str(len(movies) + 2)],
                    "correct": 0,
                    "difficulty": "easy"
                }
            ])

        generic_questions = [
            {
                "question": "Which genre appears most in your collection?",
                "options": ["Action", "Drama", "Comedy", "Sci-Fi"],
                "correct": 1,
                "difficulty": "medium"
            },
            {
                "question": "What decade do most of your movies come from?",
                "options": ["1990s", "2000s", "2010s", "2020s"],
                "correct": 2,
                "difficulty": "easy"
            },
            {
                "question": "Which director appears most frequently in your collection?",
                "options": ["Christopher Nolan", "Steven Spielberg", "Quentin Tarantino", "Martin Scorsese"],
                "correct": 0,
                "difficulty": "hard"
            }
        ]

        while len(mock_questions) < TriviaConfig.COLLECTION_QUESTIONS:
            for q in generic_questions:
                if len(mock_questions) < TriviaConfig.COLLECTION_QUESTIONS:
                    mock_questions.append(q)

        print(f"✅ MOCK: Generated {len(mock_questions)} collection questions")

        return {
            'type': 'collection',
            'user_id': user_id,
            'questions': mock_questions[:TriviaConfig.COLLECTION_QUESTIONS],
            'user': user,
            'movies': movies,
            'api_used': 'mock'
        }

    def process_trivia_answer(self, trivia_session, user_answer):
        """Process a trivia answer and update session - SAME AS REAL SERVICE"""
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
        """Calculate final trivia results and performance metrics - SAME AS REAL SERVICE"""
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
            'type': trivia_session['type'],
            'api_used': trivia_session.get('api_used', 'mock')
        }

    def save_trivia_score(self, trivia_session):
        """Save trivia score to database - SAME AS REAL SERVICE"""
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
        """Get leaderboard data based on type - SAME AS REAL SERVICE"""
        try:
            if leaderboard_type == 'global':
                limit = kwargs.get('limit', 20)
                return self.data_manager.get_global_leaderboard(limit)
            elif leaderboard_type == 'collection':
                limit = kwargs.get('limit', 20)
                return self.data_manager.get_collection_leaderboard(limit)
            elif leaderboard_type == 'movie':
                movie_id = kwargs.get('movie_id')
                limit = kwargs.get('limit', 15)
                if not movie_id:
                    raise ValueError("movie_id required for movie leaderboard")
                return self.data_manager.get_movie_leaderboard(movie_id, limit)
            else:
                raise ValueError(f"Unknown leaderboard type: {leaderboard_type}")
        except Exception as e:
            print(f"Error fetching {leaderboard_type} leaderboard: {e}")
            return []

    def get_user_stats(self, user_id):
        """Get comprehensive trivia statistics for a user - SAME AS REAL SERVICE"""
        user = self.validate_user(user_id)
        try:
            stats = self.data_manager.get_user_trivia_stats(user_id)
            return {'user': user, 'stats': stats}
        except Exception as e:
            print(f"Error fetching user stats for {user_id}: {e}")
            return {
                'user': user,
                'stats': {
                    'total_attempts': 0, 'best_score': 0, 'average_score': 0,
                    'movie_attempts': 0, 'collection_attempts': 0, 'recent_scores': []
                }
            }