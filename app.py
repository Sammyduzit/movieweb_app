from flask import Flask, jsonify
from datamanager.database import init_database
from datamanager.sqlite_data_manager import SQLiteDataManager
import os

# base_dir = os.path.abspath(os.path.dirname(__file__))
# data_dir = os.path.join(base_dir, 'instance')
#
# db_path = os.path.join(data_dir, "moviewebapp.sqlite")


def create_app():
    """
    Application factory function to create and configure the Flask app.

    :return: Configured Flask application instance
    """
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moviewebapp.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'secret-key'

    init_database(app)

    data_manager = SQLiteDataManager()

    @app.route('/users')
    def list_users():
        """
        Get all users from the database.

        :return: JSON response with list of all users
        """
        try:
            users = data_manager.get_all_users()
            return jsonify({
                'success': True,
                'users': users,
                'count': len(users)
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    return app


def main():
    """Main function to run the application"""
    app = create_app()

    with app.app_context():
        try:
            print("Testing data manager...")

            data_manager = SQLiteDataManager()

            user_data = {
                'name': 'John Doe',
                'email': 'john.doe@example.com'
            }
            new_user = data_manager.add_user(user_data)
            print(f"Added user: {new_user}")

            users = data_manager.get_all_users()
            print(f"All users: {users}")

        except Exception as e:
            print(f"Error during testing: {e}")

    print("Starting Flask server...")
    print("Access users at: http://127.0.0.1:5002/users")
    app.run(host="0.0.0.0", port=5002, debug=True)


if __name__ == "__main__":
    main()