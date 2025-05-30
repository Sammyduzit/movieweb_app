import pytest
from exceptions import (
    UserNotFoundError, MovieNotFoundError, ReviewNotFoundError,
    ValidationError, DuplicateMovieError, InsufficientMoviesError
)


class TestUserService:
    """Test user service functionality"""

    def test_create_user_valid(self, app, user_service, sample_user_data):
        """Test creating a user with valid data"""
        with app.app_context():
            user = user_service.create_user(sample_user_data)

            assert user['name'] == sample_user_data['name']
            assert user['email'] == sample_user_data['email']
            assert 'id' in user

    def test_create_user_missing_name(self, app, user_service):
        """Test creating user without name"""
        with app.app_context():
            with pytest.raises(ValidationError) as exc_info:
                user_service.create_user({'name': '', 'email': 'test@example.com'})

            assert 'Name is required' in str(exc_info.value)

    def test_create_user_missing_email(self, app, user_service):
        """Test creating user without email"""
        with app.app_context():
            with pytest.raises(ValidationError) as exc_info:
                user_service.create_user({'name': 'Test User', 'email': ''})

            assert 'Email is required' in str(exc_info.value)

    def test_create_user_duplicate_email(self, app, user_service, sample_user_data):
        """Test creating user with duplicate email"""
        with app.app_context():
            # Create first user
            user_service.create_user(sample_user_data)

            # Try to create second user with same email
            duplicate_data = sample_user_data.copy()
            duplicate_data['name'] = 'Different Name'

            with pytest.raises(ValidationError) as exc_info:
                user_service.create_user(duplicate_data)

            assert 'Email already exists' in str(exc_info.value)

    def test_get_user_by_id_exists(self, app, user_service, created_user):
        """Test getting existing user by ID"""
        with app.app_context():
            user = user_service.get_user_by_id(created_user['id'])
            assert user['id'] == created_user['id']
            assert user['name'] == created_user['name']

    def test_get_user_by_id_not_exists(self, app, user_service):
        """Test getting non-existent user by ID"""
        with app.app_context():
            with pytest.raises(UserNotFoundError):
                user_service.get_user_by_id(999)

    def test_get_all_users(self, app, user_service, created_user):
        """Test getting all users"""
        with app.app_context():
            users = user_service.get_all_users()
            assert len(users) >= 1
            user_ids = [u['id'] for u in users]
            assert created_user['id'] in user_ids


class TestMovieService:
    """Test movie service functionality"""

    def test_create_movie_valid(self, app, movie_service, created_user, sample_movie_data):
        """Test creating a movie with valid data"""
        with app.app_context():
            movie = movie_service.create_movie_for_user(created_user['id'], sample_movie_data)

            assert movie['title'] == sample_movie_data['title']
            assert movie['director'] == sample_movie_data['director']
            assert movie['year'] == int(sample_movie_data['year'])
            assert movie['user_id'] == created_user['id']

    def test_create_movie_missing_title(self, app, movie_service, created_user):
        """Test creating movie without title"""
        with app.app_context():
            with pytest.raises(ValidationError) as exc_info:
                movie_service.create_movie_for_user(created_user['id'], {'title': ''})

            assert 'Movie title is required' in str(exc_info.value)

    def test_create_movie_invalid_year(self, app, movie_service, created_user):
        """Test creating movie with invalid year"""
        with app.app_context():
            with pytest.raises(ValidationError) as exc_info:
                movie_service.create_movie_for_user(created_user['id'], {
                    'title': 'Test Movie',
                    'year': '1700'  # Too old
                })

            assert 'Year must be between' in str(exc_info.value)

    def test_create_movie_invalid_rating(self, app, movie_service, created_user):
        """Test creating movie with invalid rating"""
        with app.app_context():
            with pytest.raises(ValidationError) as exc_info:
                movie_service.create_movie_for_user(created_user['id'], {
                    'title': 'Test Movie',
                    'rating': '15'  # Too high
                })

            assert 'Rating must be between' in str(exc_info.value)

    def test_create_duplicate_movie(self, app, movie_service, created_user, created_movie):
        """Test creating duplicate movie for same user"""
        with app.app_context():
            # Try to create the same movie again
            duplicate_data = {
                'title': created_movie['title'],
                'year': str(created_movie['year'])
            }

            with pytest.raises(DuplicateMovieError) as exc_info:
                movie_service.create_movie_for_user(created_user['id'], duplicate_data)

            assert 'already have' in str(exc_info.value)

    def test_get_user_movies(self, app, movie_service, created_user, created_movie):
        """Test getting movies for a user"""
        with app.app_context():
            movies = movie_service.get_user_movies(created_user['id'])
            assert len(movies) >= 1
            movie_ids = [m['id'] for m in movies]
            assert created_movie['id'] in movie_ids

    def test_get_movie_for_user_exists(self, app, movie_service, created_user, created_movie):
        """Test getting existing movie for user"""
        with app.app_context():
            movie = movie_service.get_movie_for_user(created_user['id'], created_movie['id'])
            assert movie['id'] == created_movie['id']

    def test_get_movie_for_user_not_exists(self, app, movie_service, created_user):
        """Test getting non-existent movie for user"""
        with app.app_context():
            with pytest.raises(MovieNotFoundError):
                movie_service.get_movie_for_user(created_user['id'], 999)

    def test_update_movie(self, app, movie_service, created_movie):
        """Test updating movie"""
        with app.app_context():
            updated_data = {
                'title': 'Updated Movie Title',
                'director': 'Updated Director',
                'year': '2024'
            }

            updated_movie = movie_service.update_movie(created_movie['id'], updated_data)
            assert updated_movie['title'] == 'Updated Movie Title'
            assert updated_movie['director'] == 'Updated Director'
            assert updated_movie['year'] == 2024

    def test_update_movie_duplicate(self, app, movie_service, created_user):
        """Test updating movie to create duplicate"""
        with app.app_context():
            # Create two movies
            movie1 = movie_service.create_movie_for_user(created_user['id'], {
                'title': 'Movie One',
                'year': '2023'
            })
            movie2 = movie_service.create_movie_for_user(created_user['id'], {
                'title': 'Movie Two',
                'year': '2024'
            })

            # Try to update movie2 to have same title/year as movie1
            with pytest.raises(DuplicateMovieError):
                movie_service.update_movie(movie2['id'], {
                    'title': 'Movie One',
                    'year': '2023'
                })

    def test_delete_movie(self, app, movie_service, created_movie):
        """Test deleting movie"""
        with app.app_context():
            success = movie_service.delete_movie(created_movie['id'])
            assert success is True

            # Verify movie is deleted
            with pytest.raises(MovieNotFoundError):
                movie_service.get_movie_by_id(created_movie['id'])


class TestReviewService:
    """Test review service functionality"""

    def test_create_review_valid(self, app, review_service, created_movie, sample_review_data):
        """Test creating review with valid data"""
        with app.app_context():
            review = review_service.create_review(created_movie['id'], sample_review_data)

            assert review['content'] == sample_review_data['content']
            assert review['reviewer_rating'] == int(sample_review_data['reviewer_rating'])
            assert review['movie_id'] == created_movie['id']

    def test_create_review_missing_content(self, app, review_service, created_movie):
        """Test creating review without content"""
        with app.app_context():
            with pytest.raises(ValidationError) as exc_info:
                review_service.create_review(created_movie['id'], {'content': ''})

            assert 'Review content is required' in str(exc_info.value)

    def test_create_review_invalid_rating(self, app, review_service, created_movie):
        """Test creating review with invalid rating"""
        with app.app_context():
            with pytest.raises(ValidationError) as exc_info:
                review_service.create_review(created_movie['id'], {
                    'content': 'Test review',
                    'reviewer_rating': '15'  # Too high
                })

            assert 'Rating must be between' in str(exc_info.value)

    def test_get_movie_reviews(self, app, review_service, created_movie, created_review):
        """Test getting reviews for a movie"""
        with app.app_context():
            reviews = review_service.get_movie_reviews(created_movie['id'])
            assert len(reviews) >= 1
            review_ids = [r['id'] for r in reviews]
            assert created_review['id'] in review_ids

    def test_update_review(self, app, review_service, created_review):
        """Test updating review"""
        with app.app_context():
            updated_data = {
                'content': 'Updated review content',
                'reviewer_rating': '8'
            }

            updated_review = review_service.update_review(created_review['id'], updated_data)
            assert updated_review['content'] == 'Updated review content'
            assert updated_review['reviewer_rating'] == 8

    def test_like_review(self, app, review_service, created_review):
        """Test liking a review"""
        with app.app_context():
            initial_likes = created_review['likes']
            liked_review = review_service.like_review(created_review['id'])
            assert liked_review['likes'] == initial_likes + 1

    def test_delete_review(self, app, review_service, created_review):
        """Test deleting review"""
        with app.app_context():
            success = review_service.delete_review(created_review['id'])
            assert success is True


class TestTriviaService:
    """Test trivia service functionality"""

    def test_validate_user_exists(self, app, trivia_service, created_user):
        """Test validating existing user"""
        with app.app_context():
            user = trivia_service.validate_user(created_user['id'])
            assert user['id'] == created_user['id']

    def test_validate_user_not_exists(self, app, trivia_service):
        """Test validating non-existent user"""
        with app.app_context():
            with pytest.raises(UserNotFoundError):
                trivia_service.validate_user(999)

    def test_validate_movie_exists(self, app, trivia_service, created_user, created_movie):
        """Test validating existing movie"""
        with app.app_context():
            movie = trivia_service.validate_movie(created_user['id'], created_movie['id'])
            assert movie['id'] == created_movie['id']

    def test_validate_movie_not_exists(self, app, trivia_service, created_user):
        """Test validating non-existent movie"""
        with app.app_context():
            with pytest.raises(MovieNotFoundError):
                trivia_service.validate_movie(created_user['id'], 999)

    def test_insufficient_movies_for_collection(self, app, trivia_service, created_user, created_movie):
        """Test collection trivia with insufficient movies"""
        with app.app_context():
            # User has only 1 movie (from created_movie fixture), need 3
            with pytest.raises(InsufficientMoviesError) as exc_info:
                trivia_service.validate_collection_trivia_requirements(created_user['id'])

            assert exc_info.value.required_count == 3
            assert exc_info.value.movie_count == 1

    def test_sufficient_movies_for_collection(self, app, trivia_service, movie_service, created_user):
        """Test collection trivia with sufficient movies"""
        with app.app_context():
            # Add more movies to reach minimum
            for i in range(3):
                movie_service.create_movie_for_user(created_user['id'], {
                    'title': f'Collection Movie {i}',
                    'year': str(2020 + i)
                })

            movies = trivia_service.validate_collection_trivia_requirements(created_user['id'])
            assert len(movies) >= 3

    def test_calculate_trivia_results(self, app, trivia_service):
        """Test calculating trivia results"""
        with app.app_context():
            mock_session = {
                'questions': [{'question': 'Q1'}, {'question': 'Q2'}],
                'score': 1,
                'answers': [
                    {'question': 'Q1', 'is_correct': True},
                    {'question': 'Q2', 'is_correct': False}
                ],
                'type': 'movie'
            }

            results = trivia_service.calculate_trivia_results(mock_session)
            assert results['score'] == 1
            assert results['total'] == 2
            assert results['percentage'] == 50
            assert 'performance' in results