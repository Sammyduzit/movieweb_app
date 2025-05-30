from config import LeaderboardConfig
from .data_manager_interface import DataManagerInterface
from .data_models import User, Movie
from .database import db
from flask import current_app

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
            rating=movie_data.get('rating') or movie_data.get('imdb_rating'),
            genre=movie_data.get('genre'),
            poster=movie_data.get('poster'),
            user_id=user_id
        )

        try:
            db.session.add(new_movie)
            db.session.commit()
            return new_movie.to_dict()
        except Exception as e:
            print(f"Database error: {e}")
            db.session.rollback()
            raise


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
            rating=movie_data.get('rating') or movie_data.get('imdb_rating'),
            genre=movie_data.get('genre'),
            poster=movie_data.get('poster'),
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
        if 'poster' in updated_data:
            movie.poster = updated_data['poster']

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

        db.session.delete(movie)
        db.session.commit()

        return True

    def add_review(self, movie_id, review_data):
        """Add a review to a movie"""
        from .data_models import Review

        movie = Movie.query.get(movie_id)
        if not movie:
            raise ValueError(f"Movie with ID {movie_id} not found")

        new_review = Review(
            content=review_data.get('content'),
            reviewer_rating=review_data.get('reviewer_rating'),
            movie_id=movie_id
        )

        db.session.add(new_review)
        db.session.commit()
        return new_review.to_dict()

    def get_movie_reviews(self, movie_id):
        """Get all reviews for a specific movie"""
        from .data_models import Review
        reviews = Review.query.filter_by(movie_id=movie_id).all()
        return [review.to_dict() for review in reviews]

    def like_review(self, review_id):
        """Increment likes for a review"""
        from .data_models import Review
        review = Review.query.get(review_id)
        if review:
            review.likes += 1
            db.session.commit()
            return review.to_dict()
        return None

    def update_review(self, review_id, updated_data):
        """Update a review by ID"""
        from .data_models import Review

        review = Review.query.get(review_id)
        if not review:
            return None

        if 'content' in updated_data:
            review.content = updated_data['content']
        if 'reviewer_rating' in updated_data:
            review.reviewer_rating = updated_data['reviewer_rating']

        review.updated_at = db.func.current_timestamp()

        db.session.commit()
        return review.to_dict()

    def delete_review(self, review_id):
        """Delete a review by ID"""
        from .data_models import Review

        review = Review.query.get(review_id)
        if not review:
            return False

        db.session.delete(review)
        db.session.commit()
        return True

    def save_trivia_score(self, score_data):
        """Save a trivia score to the database"""
        from .data_models import TriviaScore

        new_score = TriviaScore(
            user_id=score_data['user_id'],
            trivia_type=score_data['trivia_type'],
            movie_id=score_data.get('movie_id'),
            score=score_data['score'],
            total_questions=score_data['total_questions'],
            percentage=score_data['percentage'],
            completion_time=score_data.get('completion_time')
        )

        db.session.add(new_score)
        db.session.commit()
        return new_score.to_dict()

    def get_global_leaderboard(self, limit=10):
        """Get global trivia leaderboard (best scores across all trivia)"""
        from .data_models import TriviaScore, User

        # Get best scores with user info
        scores = db.session.query(TriviaScore, User).join(User).order_by(
            TriviaScore.percentage.desc(),
            TriviaScore.score.desc(),
            TriviaScore.created_at.asc()
        ).limit(limit).all()

        leaderboard = []
        for score, user in scores:
            entry = score.to_dict()
            entry['user_name'] = user.name
            leaderboard.append(entry)

        return leaderboard

    def get_movie_leaderboard(self, movie_id, limit=10):
        """Get leaderboard for specific movie"""
        from .data_models import TriviaScore, User

        scores = db.session.query(TriviaScore, User).join(User).filter(
            TriviaScore.movie_id == movie_id,
            TriviaScore.trivia_type == 'movie'
        ).order_by(
            TriviaScore.percentage.desc(),
            TriviaScore.score.desc(),
            TriviaScore.created_at.asc()
        ).limit(limit).all()

        leaderboard = []
        for score, user in scores:
            entry = score.to_dict()
            entry['user_name'] = user.name
            leaderboard.append(entry)

        return leaderboard

    def get_collection_leaderboard(self, limit=10):
        """Get leaderboard for collection trivia"""
        from .data_models import TriviaScore, User

        scores = db.session.query(TriviaScore, User).join(User).filter(
            TriviaScore.trivia_type == 'collection'
        ).order_by(
            TriviaScore.percentage.desc(),
            TriviaScore.score.desc(),
            TriviaScore.created_at.asc()
        ).limit(limit).all()

        leaderboard = []
        for score, user in scores:
            entry = score.to_dict()
            entry['user_name'] = user.name
            leaderboard.append(entry)

        return leaderboard

    def get_user_trivia_stats(self, user_id):
        """Get trivia statistics for a specific user"""
        from .data_models import TriviaScore

        stats = db.session.query(TriviaScore).filter(
            TriviaScore.user_id == user_id
        ).all()

        if not stats:
            return {
                'total_attempts': 0,
                'best_score': 0,
                'average_score': 0,
                'movie_attempts': 0,
                'collection_attempts': 0
            }

        total_attempts = len(stats)
        movie_attempts = len([s for s in stats if s.trivia_type == 'movie'])
        collection_attempts = len([s for s in stats if s.trivia_type == 'collection'])
        best_score = max(s.percentage for s in stats)
        average_score = round(sum(s.percentage for s in stats) / total_attempts)

        return {
            'total_attempts': total_attempts,
            'best_score': best_score,
            'average_score': average_score,
            'movie_attempts': movie_attempts,
            'collection_attempts': collection_attempts,
            'recent_scores': [s.to_dict() for s in sorted(stats, key=lambda x: x.created_at, reverse=True)[:LeaderboardConfig.USER_STATS_RECENT_LIMIT]]
        }