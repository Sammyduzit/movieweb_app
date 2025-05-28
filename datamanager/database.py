from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_database(app):
    """
    Initialize the database with the Flask app and create all tables.
    :param app: Flask application instance
    """
    db.init_app(app)

    with app.app_context():
        db.create_all()
        print("Database tables created successfully.")