from .data_manager_interface import DataManagerInterface
from .data_models import User, Movie
from .database import db

class SQLiteDataManager(DataManagerInterface):
    """SQLite implementation of the DataManagerInterface using SQLAlchemy ORM"""

    def __init__(self):
        pass

    def get_all_users(self):
        """
        Return a list of all users.

        :return: List of user dictionaries
        """
        users = User.query.all()
        return [user.to_dict() for user in users]

    def get_user_movies(self, user_id):
        """
        Return a list of all movies for a specific user.

        :param user_id: The ID of the user
        :return: List of movie dictionaries for the user
        """
        user = User.query.get(user_id)
        if user:
            return [movie.to_dict() for movie in user.movies]
        return []

    def add_user(self, user_data):
        """
        Add a new user to the database.

        :param user_data: Dictionary containing user data (name, email)
        :return: Dictionary representation of the created user
        """
        new_user = User(
            name=user_data.get('name'),
            email=user_data.get('email')
        )

        db.session.add(new_user)
        db.session.commit()

        return new_user.to_dict()

    def add_user_movie(self, user_id, movie_data):
        """
        Add a new movie to a user's movie list.

        :param user_id: The ID of the user
        :param movie_data: Dictionary containing movie data
        :return: Dictionary representation of the created movie
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")

        new_movie = Movie(
            title=movie_data.get('title'),
            director=movie_data.get('director'),
            year=movie_data.get('year'),
            rating=movie_data.get('rating'),
            genre=movie_data.get('genre'),
            user_id=user_id
        )

        db.session.add(new_movie)
        db.session.commit()

        return new_movie.to_dict()

    def add_movie(self, movie_data):
        """
        Add a new movie to the database.

        :param movie_data: Dictionary containing movie data including user_id
        :return: Dictionary representation of the created movie
        """
        user_id = movie_data.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            if not user:
                raise ValueError(f"User with ID {user_id} not found")

        new_movie = Movie(
            title=movie_data.get('title'),
            director=movie_data.get('director'),
            year=movie_data.get('year'),
            rating=movie_data.get('rating'),
            genre=movie_data.get('genre'),
            user_id=user_id
        )

        db.session.add(new_movie)
        db.session.commit()

        return new_movie.to_dict()

    def update_movie(self, movie_id, updated_data):
        """
        Update a movie by ID with new data.

        :param movie_id: The ID of the movie to update
        :param updated_data: Dictionary containing updated movie data
        :return: Dictionary representation of the updated movie or None if not found
        """
        movie = Movie.query.get(movie_id)
        if not movie:
            return None

        if 'title' in updated_data:
            movie.title = updated_data['title']
        if 'director' in updated_data:
            movie.director = updated_data['director']
        if 'year' in updated_data:
            movie.year = updated_data['year']
        if 'rating' in updated_data:
            movie.rating = updated_data['rating']
        if 'genre' in updated_data:
            movie.genre = updated_data['genre']

        db.session.commit()

        return movie.to_dict()

    def delete_movie(self, movie_id):
        """
        Delete a movie by ID.

        :param movie_id: The ID of the movie to delete
        :return: True if deleted successfully, False if movie not found
        """
        movie = Movie.query.get(movie_id)
        if not movie:
            return False
