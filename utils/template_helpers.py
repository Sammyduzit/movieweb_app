"""
Template helper functions and filters for MovieWeb application.
Provides reusable functions for common template operations and data formatting.
"""
from datetime import datetime
from config import TriviaConfig


def format_percentage(score, total):
    """
    Calculate percentage from score and total questions.

    :param score: Number of correct answers
    :param total: Total number of questions
    :return: Percentage as integer (0-100)
    """
    if total == 0:
        return 0
    return round((score / total) * 100)


def get_performance_badge(percentage):
    """
    Get performance badge text and emoji based on percentage.

    :param percentage: Score percentage (0-100)
    :return: Dictionary with badge text, emoji, and CSS class
    """
    if percentage >= TriviaConfig.MASTER_THRESHOLD:
        return {"text": "Movie Master", "emoji": "🏆", "class": "master"}
    elif percentage >= TriviaConfig.EXPERT_THRESHOLD:
        return {"text": "Cinema Expert", "emoji": "🌟", "class": "expert"}
    elif percentage >= TriviaConfig.BUFF_THRESHOLD:
        return {"text": "Movie Buff", "emoji": "🎬", "class": "buff"}
    elif percentage >= TriviaConfig.LEARNING_THRESHOLD:
        return {"text": "Getting There", "emoji": "🍿", "class": "learning"}
    else:
        return {"text": "Study More", "emoji": "📚", "class": "learning"}


def get_rank_display(rank):
    """
    Get rank display with emoji for top 3 positions.

    :param rank: Numerical rank position
    :return: Dictionary with emoji and CSS class for rank
    """
    if rank == 1:
        return {"emoji": "🥇", "class": "rank-1"}
    elif rank == 2:
        return {"emoji": "🥈", "class": "rank-2"}
    elif rank == 3:
        return {"emoji": "🥉", "class": "rank-3"}
    else:
        return {"emoji": str(rank), "class": f"rank-{rank}"}


def format_trivia_type(trivia_type):
    """
    Format trivia type with emoji and styling.

    :param trivia_type: Type of trivia ('movie' or 'collection')
    :return: Dictionary with emoji, text, and CSS class
    """
    type_mapping = {
        'movie': {'emoji': '🎬', 'text': 'Movie Trivia', 'class': 'movie'},
        'collection': {'emoji': '🎯', 'text': 'Collection Trivia', 'class': 'collection'}
    }
    return type_mapping.get(trivia_type, {'emoji': '❓', 'text': 'Unknown', 'class': 'unknown'})


def format_date(date_obj, format_type='short'):
    """
    Format datetime object for display.

    :param date_obj: Datetime object or ISO string to format
    :param format_type: Format style ('short', 'long', 'datetime')
    :return: Formatted date string
    """
    if not date_obj:
        return ""

    # Handle string input (ISO format)
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
        except:
            return date_obj[:10]  # Fallback to string slice

    # Format based on requested type
    format_patterns = {
        'short': '%Y-%m-%d',
        'long': '%B %d, %Y',
        'datetime': '%Y-%m-%d %H:%M'
    }

    pattern = format_patterns.get(format_type, '%Y-%m-%d')
    return date_obj.strftime(pattern)


def truncate_text(text, max_length=50, suffix="..."):
    """
    Truncate text to specified length with suffix.

    :param text: Text to truncate
    :param max_length: Maximum length before truncation
    :param suffix: Suffix to append when truncating
    :return: Truncated text with suffix if needed
    """
    if not text or len(text) <= max_length:
        return text
    return text[:max_length].rstrip() + suffix


def get_difficulty_style(difficulty):
    """
    Get CSS class and color for difficulty level.

    :param difficulty: Difficulty level string
    :return: Dictionary with CSS class and color
    """
    difficulty_styles = {
        'easy': {'class': 'difficulty-easy', 'color': '#2ecc71'},
        'medium': {'class': 'difficulty-medium', 'color': '#f39c12'},
        'hard': {'class': 'difficulty-hard', 'color': '#e74c3c'},
        'very hard': {'class': 'difficulty-hard', 'color': '#e74c3c'},
        'highest difficulty': {'class': 'difficulty-hard', 'color': '#8e44ad'}
    }
    return difficulty_styles.get(difficulty.lower(), difficulty_styles['medium'])


def format_rating(rating):
    """
    Format movie rating for display.

    :param rating: Rating value (number or string)
    :return: Formatted rating string
    """
    if rating is None:
        return "No rating"
    try:
        return f"{float(rating):.1f}/10"
    except (ValueError, TypeError):
        return str(rating)


def get_poster_url(poster_url):
    """
    Get poster URL or return None for placeholder handling.

    :param poster_url: Raw poster URL from API
    :return: Valid poster URL or None if invalid/missing
    """
    if poster_url and poster_url != 'N/A' and poster_url.strip():
        return poster_url
    return None


def pluralize(count, singular, plural=None):
    """
    Simple pluralization helper.

    :param count: Number to check for pluralization
    :param singular: Singular form of the word
    :param plural: Plural form (defaults to singular + 's')
    :return: Appropriate word form based on count
    """
    if plural is None:
        plural = singular + 's'
    return singular if count == 1 else plural


def register_template_helpers(app):
    """
    Register all template helpers with Flask app.

    :param app: Flask application instance
    :return: None
    """
    app.jinja_env.globals.update(
        format_percentage=format_percentage,
        get_performance_badge=get_performance_badge,
        get_rank_display=get_rank_display,
        format_trivia_type=format_trivia_type,
        format_date=format_date,
        truncate_text=truncate_text,
        get_difficulty_style=get_difficulty_style,
        format_rating=format_rating,
        get_poster_url=get_poster_url,
        pluralize=pluralize
    )

    app.jinja_env.filters['truncate_text'] = truncate_text
    app.jinja_env.filters['format_date'] = format_date
    app.jinja_env.filters['format_rating'] = format_rating
    app.jinja_env.filters['pluralize'] = pluralize