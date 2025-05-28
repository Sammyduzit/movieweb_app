from abc import ABC, abstractmethod

class DataManagerInterface(ABC):
    """Abstract base class defining the interface for any data manager"""

    @abstractmethod
    def get_all_users(self):
        """Return a list of all users"""
        pass

    @abstractmethod
    def get_user_movies(self, user_id):
        """Return a list of movies for a specific user"""
        pass

    @abstractmethod
    def add_user(self, user_data):
        """Add a new user to the database"""
        pass

    @abstractmethod
    def add_user_movie(self, user_id, movie_data):
        """Add a new movie to a user's movie list"""
        pass

    @abstractmethod
    def add_movie(self, movie_data):
        """Add a new movie to the database"""
        pass

    @abstractmethod
    def update_movie(self, movie_id, updated_data):
        """Update a movie by ID with new data"""
        pass

    @abstractmethod
    def delete_movie(self, movie_id):
        """Delete a movie by ID"""
        pass