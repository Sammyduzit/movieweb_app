"""
Configuration constants for MovieWeb application.
Centralizes magic numbers and configuration values.
"""


class TriviaConfig:
    """Configuration for trivia functionality"""

    # Question counts
    MOVIE_QUESTIONS = 7
    COLLECTION_QUESTIONS = 21

    # Business rules
    MIN_MOVIES_FOR_COLLECTION = 3

    # Performance thresholds (percentages)
    MASTER_THRESHOLD = 90
    EXPERT_THRESHOLD = 75
    BUFF_THRESHOLD = 60
    LEARNING_THRESHOLD = 40


class LeaderboardConfig:
    """Configuration for leaderboard functionality"""

    # Default limits
    GLOBAL_LIMIT = 20
    COLLECTION_LIMIT = 20
    MOVIE_LIMIT = 15
    USER_STATS_RECENT_LIMIT = 5


class ValidationConfig:
    """Configuration for validation rules"""

    # String length limits
    MOVIE_TITLE_MAX = 200
    DIRECTOR_NAME_MAX = 100
    GENRE_MAX = 100
    USER_NAME_MAX = 100
    USER_EMAIL_MAX = 120
    REVIEW_CONTENT_MAX = 2000

    # Rating limits
    RATING_MIN = 1
    RATING_MAX = 10

    # Year limits
    YEAR_MIN = 1800
    YEAR_MAX = 2050


class DatabaseConfig:
    """Configuration for database settings"""

    # Database file settings
    DB_FILENAME = "moviewebapp.sqlite"
    INSTANCE_FOLDER = "instance"

    # Connection settings
    TRACK_MODIFICATIONS = False


class APIConfig:
    """Configuration for external API services"""

    # Timeouts (seconds)
    OMDB_TIMEOUT = 5
    RAPIDAPI_TIMEOUT = 30

    # API endpoints
    OMDB_BASE_URL = "http://www.omdbapi.com/"
    RAPIDAPI_BASE_URL = "https://chatgpt-ai-chat-bot.p.rapidapi.com/ask"


class AppConfig:
    """Main application configuration"""

    # Flask settings
    SECRET_KEY = 'secret-key'
    DEBUG = True
    HOST = "0.0.0.0"
    PORT = 5002

    # Environment variables
    OMDB_API_KEY_ENV = 'OMDB_API_KEY'
    RAPIDAPI_KEY_ENV = 'RAPIDAPI_KEY'
    OPENAI_API_KEY_ENV = 'OPENAI_API_KEY'
