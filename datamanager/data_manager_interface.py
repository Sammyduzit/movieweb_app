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

    @abstractmethod
    def add_review(self, movie_id, review_data):
        """Add a review to a movie"""
        pass

    @abstractmethod
    def get_movie_reviews(self, movie_id):
        """Get all reviews for a specific movie"""
        pass

    @abstractmethod
    def update_review(self, review_id, updated_data):
        """Update a review by ID"""
        pass

    @abstractmethod
    def delete_review(self, review_id):
        """Delete a review by ID"""
        pass

    @abstractmethod
    def like_review(self, review_id):
        """Increment likes for a review"""
        pass

    @abstractmethod
    def save_trivia_score(self, score_data):
        """Save a trivia score to the database"""
        pass

    @abstractmethod
    def get_global_leaderboard(self, limit=10):
        """Get global trivia leaderboard (all users, all attempts)"""
        pass

    @abstractmethod
    def get_movie_leaderboard(self, movie_id, limit=10):
        """Get leaderboard for specific movie"""
        pass

    @abstractmethod
    def get_collection_leaderboard(self, limit=10):
        """Get leaderboard for collection trivia"""
        pass

    @abstractmethod
    def get_user_trivia_stats(self, user_id):
        """Get trivia statistics for a specific user"""
        pass