from config import DatabaseConfig, AppConfig
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask import Flask, redirect, url_for, render_template, request
from datamanager import init_database, User, Movie, SQLiteDataManager
from routes import user_bp, movie_bp, review_bp, api_bp, trivia_bp
from utils.template_helpers import register_template_helpers
import os


def create_app():
    """Application factory function to create and configure the Flask app."""
    app = Flask(__name__)

    base_dir = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(base_dir, DatabaseConfig.INSTANCE_FOLDER)
    os.makedirs(data_dir, exist_ok=True)
    db_path = os.path.join(data_dir, DatabaseConfig.DB_FILENAME)

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = DatabaseConfig.TRACK_MODIFICATIONS
    app.config['SECRET_KEY'] = AppConfig.SECRET_KEY

    init_database(app)

    register_template_helpers(app)

    app.register_blueprint(user_bp)
    app.register_blueprint(movie_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(trivia_bp)

    @app.route('/')
    def index():
        """Redirect to users page"""
        return redirect(url_for('users.list_users'))

    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors"""
        return render_template('error.html',
                               error_code=400,
                               error_message="Bad request - invalid input provided",
                               back_url=request.referrer or url_for('users.list_users'),
                               home_url=url_for('users.list_users')), 400

    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden errors"""
        return render_template('error.html',
                               error_code=403,
                               error_message="Access forbidden - you don't have permission",
                               back_url=request.referrer or url_for('users.list_users'),
                               home_url=url_for('users.list_users')), 403

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return render_template('error.html',
                               error_code=404,
                               error_message="Page not found",
                               back_url=request.referrer or url_for('users.list_users'),
                               home_url=url_for('users.list_users')), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 Method Not Allowed errors"""
        return render_template('error.html',
                               error_code=405,
                               error_message="Method not allowed for this endpoint",
                               back_url=request.referrer or url_for('users.list_users'),
                               home_url=url_for('users.list_users')), 405

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        return render_template('error.html',
                               error_code=500,
                               error_message="Internal server error - something went wrong",
                               back_url=request.referrer or url_for('users.list_users'),
                               home_url=url_for('users.list_users')), 500

    @app.errorhandler(503)
    def service_unavailable(error):
        """Handle 503 Service Unavailable errors"""
        return render_template('error.html',
                               error_code=503,
                               error_message="Service temporarily unavailable - please try again later",
                               back_url=request.referrer or url_for('users.list_users'),
                               home_url=url_for('users.list_users')), 503

    return app


def main():
    """Main function to run the application"""
    app = create_app()

    with app.app_context():
        try:
            print("Testing data manager...")

            data_manager = SQLiteDataManager()

            users = data_manager.get_all_users()
            if not users:
                user_data = {
                    'name': 'John Doe',
                    'email': 'john.doe@example.com'
                }
                new_user = data_manager.add_user(user_data)
                print(f"Added sample user: {new_user}")

            print(f"Total users: {len(data_manager.get_all_users())}")

        except SQLAlchemyError as e:
            print(f"Database error during testing: {e}")
        except Exception as e:
            print(f"Error during testing: {e}")

    print("Starting Flask server...")
    print("Access users at: http://127.0.0.1:5002/users")
    print("- http://127.0.0.1:5002/users (List all users)")
    print("- http://127.0.0.1:5002/add_user (Add new user)")
    print("- OMDb API integration enabled (set OMDB_API_KEY environment variable)")
    app.run(host=AppConfig.HOST, port=AppConfig.PORT, debug=AppConfig.DEBUG)


if __name__ == "__main__":
    main()