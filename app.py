from config import DatabaseConfig, AppConfig
from flask import Flask, redirect, url_for
from datamanager import init_database
from routes import user_bp, movie_bp, review_bp, api_bp, trivia_bp, homepage_bp
from utils.template_helpers import register_template_helpers
from utils.app_helpers import register_error_handlers, print_startup_info
import os


def create_app():
    """
    Application factory function to create and configure the Flask app.

    :return: Configured Flask application instance
    """
    app = Flask(__name__)

    _configure_database(app)
    _configure_app_settings(app)

    init_database(app)
    register_template_helpers(app)

    _register_blueprints(app)
    register_error_handlers(app)
    _register_routes(app)

    return app


def _configure_database(app):
    """
    Configure database settings for the Flask app.

    :param app: Flask application instance
    """
    base_dir = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(base_dir, DatabaseConfig.INSTANCE_FOLDER)
    os.makedirs(data_dir, exist_ok=True)
    db_path = os.path.join(data_dir, DatabaseConfig.DB_FILENAME)

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = (
        DatabaseConfig.TRACK_MODIFICATIONS
    )


def _configure_app_settings(app):
    """
    Configure general Flask application settings.

    :param app: Flask application instance
    """
    app.config['SECRET_KEY'] = AppConfig.SECRET_KEY


def _register_blueprints(app):
    """
    Register all application blueprints.

    :param app: Flask application instance
    """
    app.register_blueprint(user_bp)
    app.register_blueprint(movie_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(trivia_bp)
    app.register_blueprint(homepage_bp)


def _register_routes(app):
    """
    Register application routes.

    :param app: Flask application instance
    """
    @app.route('/')
    def index():
        """Redirect to homepage"""
        return redirect(url_for('homepage.homepage'))


def main():
    """
    Main function to run the application in production mode.

    :return: None
    """
    app = create_app()

    print_startup_info()

    app.run(
        host=AppConfig.HOST,
        port=AppConfig.PORT,
        debug=AppConfig.DEBUG
    )


if __name__ == "__main__":
    main()