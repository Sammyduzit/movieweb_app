"""
Application Helper Functions.
Provides utility functions for Flask application setup and error handling.
"""
from flask import render_template, request, url_for
from config import AppConfig


def register_error_handlers(app):
    """
    Register error handlers for common HTTP errors.

    :param app: Flask application instance
    """
    error_configs = {
        400: "Bad request - invalid input provided",
        403: "Access forbidden - you don't have permission",
        404: "Page not found",
        405: "Method not allowed for this endpoint",
        500: "Internal server error - something went wrong",
        503: "Service temporarily unavailable - please try again later"
    }

    for error_code, message in error_configs.items():
        _register_single_error_handler(app, error_code, message)


def _register_single_error_handler(app, error_code, error_message):
    """
    Register a single error handler for the given error code.

    :param app: Flask application instance
    :param error_code: HTTP error code
    :param error_message: Error message to display
    """
    @app.errorhandler(error_code)
    def error_handler(error):
        template_context = get_error_template_context(error_code, error_message)
        return render_template('error.html',
                               **template_context), error_code

    # Set function name to avoid conflicts
    error_handler.__name__ = f'error_handler_{error_code}'


def get_error_template_context(error_code, error_message):
    """
    Generate template context for error pages.

    :param error_code: HTTP error code
    :param error_message: Error message to display
    :return: Dictionary with template context
    """
    return {
        'error_code': error_code,
        'error_message': error_message,
        'back_url': request.referrer or url_for('users.list_users'),
        'home_url': url_for('users.list_users')
    }


def print_startup_info():
    """
    Print startup information and available endpoints.

    :return: None
    """
    print("🚀 Starting MovieWeb application...")
    print(f"📡 Server running on: http://{AppConfig.HOST}:{AppConfig.PORT}")
    print(f"🎬 Main interface: http://{AppConfig.HOST}:{AppConfig.PORT}/users")
    print("🔧 API endpoints available at /api/")
    print("🎯 Trivia gaming features enabled")
    print("📽️  OMDb API integration (set OMDB_API_KEY environment variable)")
    print("🤖 AI Trivia generation (set RAPIDAPI_KEY and OPENAI_API_KEY)")