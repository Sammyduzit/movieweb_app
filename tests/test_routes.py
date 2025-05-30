import pytest
import json


class TestUserRoutes:
    """Test user route functionality"""

    def test_home_redirect(self, client):
        """Test that home page redirects to users"""
        response = client.get('/')
        assert response.status_code == 302
        assert '/users' in response.location

    def test_users_page_empty(self, client):
        """Test users page with no users"""
        response = client.get('/users/')
        assert response.status_code == 200
        assert b'No users found' in response.data or b'Users' in response.data

    def test_users_page_with_data(self, client, created_user):
        """Test users page with existing users"""
        response = client.get('/users/')
        assert response.status_code == 200
        assert created_user['name'].encode() in response.data
        assert created_user['email'].encode() in response.data

    def test_add_user_get(self, client):
        """Test GET request to add user page"""
        response = client.get('/users/add')
        assert response.status_code == 200
        assert b'Add New User' in response.data
        assert b'name' in response.data.lower()
        assert b'email' in response.data.lower()

    def test_add_user_post_valid(self, client, sample_user_data):
        """Test POST request to add user with valid data"""
        response = client.post('/users/add', data=sample_user_data, follow_redirects=True)
        assert response.status_code == 200
        assert sample_user_data['name'].encode() in response.data

    def test_add_user_post_invalid(self, client):
        """Test POST request to add user with invalid data"""
        response = client.post('/users/add', data={'name': ''}, follow_redirects=True)
        assert response.status_code == 200
        assert b'required' in response.data.lower()

    def test_add_user_duplicate_email(self, client, created_user):
        """Test adding user with duplicate email"""
        duplicate_data = {
            'name': 'Different Name',
            'email': created_user['email']
        }
        response = client.post('/users/add', data=duplicate_data, follow_redirects=True)
        assert response.status_code == 200
        assert b'already exists' in response.data.lower()


class TestMovieRoutes:
    """Test movie route functionality"""

    def test_user_movies_page(self, client, created_user, created_movie):
        """Test individual user's movies page"""
        response = client.get(f'/users/{created_user["id"]}/')
        assert response.status_code == 200
        assert created_movie['title'].encode() in response.data
        assert created_movie['director'].encode() in response.data

    def test_user_movies_page_invalid_user(self, client):
        """Test user movies page with invalid user ID"""
        response = client.get('/users/999', follow_redirects=True)
        assert response.status_code == 200
        assert b'not found' in response.data.lower()

    def test_movie_detail_page(self, client, created_user, created_movie):
        """Test movie detail page"""
        response = client.get(f'/users/{created_user["id"]}/movies/{created_movie["id"]}')
        assert response.status_code == 200
        assert created_movie['title'].encode() in response.data

    def test_movie_detail_invalid_movie(self, client, created_user):
        """Test movie detail with invalid movie ID"""
        response = client.get(f'/users/{created_user["id"]}/movies/999', follow_redirects=True)
        assert response.status_code == 200
        assert b'not found' in response.data.lower()

    def test_add_movie_get(self, client, created_user):
        """Test GET request to add movie page"""
        response = client.get(f'/users/{created_user["id"]}/add_movie')
        assert response.status_code == 200
        assert b'Add Movie' in response.data
        assert b'title' in response.data.lower()

    def test_add_movie_post_valid(self, client, created_user, sample_movie_data):
        """Test POST request to add movie with valid data"""
        response = client.post(f'/users/{created_user["id"]}/add_movie',
                               data=sample_movie_data, follow_redirects=True)
        assert response.status_code == 200
        assert sample_movie_data['title'].encode() in response.data

    def test_add_movie_post_invalid(self, client, created_user):
        """Test POST request to add movie with invalid data"""
        response = client.post(f'/users/{created_user["id"]}/add_movie',
                               data={'title': ''}, follow_redirects=True)
        assert response.status_code == 200
        assert b'required' in response.data.lower()

    def test_add_duplicate_movie(self, client, created_user, created_movie):
        """Test adding duplicate movie"""
        duplicate_data = {
            'title': created_movie['title'],
            'year': str(created_movie['year'])
        }
        response = client.post(f'/users/{created_user["id"]}/add_movie',
                               data=duplicate_data, follow_redirects=True)
        assert response.status_code == 200
        assert b'already have' in response.data.lower()

    def test_update_movie_get(self, client, created_user, created_movie):
        """Test GET request to update movie page"""
        response = client.get(f'/users/{created_user["id"]}/update_movie/{created_movie["id"]}')
        assert response.status_code == 200
        assert b'Edit Movie' in response.data
        assert created_movie['title'].encode() in response.data

    def test_update_movie_post_valid(self, client, created_user, created_movie):
        """Test POST request to update movie with valid data"""
        updated_data = {
            'title': 'Updated Movie Title',
            'director': created_movie['director'],
            'year': str(created_movie['year']),
            'genre': created_movie['genre'] or '',
            'rating': str(created_movie['rating']) if created_movie['rating'] else ''
        }

        response = client.post(f'/users/{created_user["id"]}/update_movie/{created_movie["id"]}',
                               data=updated_data, follow_redirects=True)
        assert response.status_code == 200
        assert b'Updated Movie Title' in response.data

    def test_delete_movie(self, client, created_user, created_movie):
        """Test movie deletion"""
        response = client.get(f'/users/{created_user["id"]}/delete_movie/{created_movie["id"]}',
                              follow_redirects=True)
        assert response.status_code == 200
        assert b'deleted successfully' in response.data

    def test_trivia_question_no_session(self, client):
        """Test trivia question without active session"""
        response = client.get('/trivia/question', follow_redirects=True)
        assert response.status_code == 200
        # Flash message wird als HTML-Attribut gesendet:
        assert (b'No active trivia session' in response.data or
                b'no active trivia session' in response.data.lower())

    def test_trivia_results_no_session(self, client):
        """Test trivia results without session"""
        response = client.get('/trivia/results', follow_redirects=True)
        assert response.status_code == 200
        assert (b'No trivia session' in response.data or
                b'no trivia session' in response.data.lower())


class TestReviewRoutes:
    """Test review route functionality"""

    def test_add_review_valid(self, client, created_user, created_movie, sample_review_data):
        """Test adding review with valid data"""
        response = client.post(f'/users/{created_user["id"]}/movies/{created_movie["id"]}/add_review',
                               data=sample_review_data, follow_redirects=True)
        assert response.status_code == 200
        assert sample_review_data['content'].encode() in response.data

    def test_add_review_invalid(self, client, created_user, created_movie):
        """Test adding review with invalid data"""
        response = client.post(f'/users/{created_user["id"]}/movies/{created_movie["id"]}/add_review',
                               data={'content': ''}, follow_redirects=True)
        assert response.status_code == 200
        assert b'required' in response.data.lower()

    def test_like_review(self, client, created_user, created_movie, created_review):
        """Test liking a review"""
        response = client.get(
            f'/users/{created_user["id"]}/movies/{created_movie["id"]}/like_review/{created_review["id"]}',
            follow_redirects=True)
        assert response.status_code == 200
        assert b'liked' in response.data.lower()

    def test_edit_review_get(self, client, created_user, created_movie, created_review):
        """Test GET request to edit review page"""
        response = client.get(
            f'/users/{created_user["id"]}/movies/{created_movie["id"]}/edit_review/{created_review["id"]}')
        assert response.status_code == 200
        assert b'Edit Review' in response.data
        assert created_review['content'].encode() in response.data

    def test_edit_review_post(self, client, created_user, created_movie, created_review):
        """Test POST request to edit review"""
        updated_data = {
            'content': 'Updated review content',
            'reviewer_rating': '8'
        }
        response = client.post(
            f'/users/{created_user["id"]}/movies/{created_movie["id"]}/edit_review/{created_review["id"]}',
            data=updated_data, follow_redirects=True)
        assert response.status_code == 200
        assert b'updated successfully' in response.data.lower()

    def test_delete_review(self, client, created_user, created_movie, created_review):
        """Test deleting a review"""
        response = client.get(
            f'/users/{created_user["id"]}/movies/{created_movie["id"]}/delete_review/{created_review["id"]}',
            follow_redirects=True)
        assert response.status_code == 200
        assert b'deleted successfully' in response.data.lower()


class TestAPIRoutes:
    """Test API route functionality"""

    def test_api_get_users(self, client, created_user):
        """Test GET /api/users"""
        response = client.get('/api/users')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']) >= 1

    def test_api_create_user_valid(self, client, sample_user_data):
        """Test POST /api/users with valid data"""
        response = client.post('/api/users',
                               json=sample_user_data,
                               content_type='application/json')
        assert response.status_code == 201

        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['name'] == sample_user_data['name']

    def test_api_create_user_invalid(self, client):
        """Test POST /api/users with invalid data"""
        response = client.post('/api/users',
                               json={'name': ''},
                               content_type='application/json')
        assert response.status_code == 400

        data = json.loads(response.data)
        assert data['success'] is False

    def test_api_get_user(self, client, created_user):
        """Test GET /api/users/{id}"""
        response = client.get(f'/api/users/{created_user["id"]}')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['id'] == created_user['id']

    def test_api_get_user_not_found(self, client):
        """Test GET /api/users/{id} with invalid ID"""
        response = client.get('/api/users/999')
        assert response.status_code == 404

        data = json.loads(response.data)
        assert data['success'] is False

    def test_api_get_user_movies(self, client, created_user, created_movie):
        """Test GET /api/users/{id}/movies"""
        response = client.get(f'/api/users/{created_user["id"]}/movies')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']) >= 1

    def test_api_create_movie_valid(self, client, created_user, sample_movie_data):
        """Test POST /api/users/{id}/movies with valid data"""
        response = client.post(f'/api/users/{created_user["id"]}/movies',
                               json=sample_movie_data,
                               content_type='application/json')
        assert response.status_code == 201

        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['title'] == sample_movie_data['title']

    def test_api_create_duplicate_movie(self, client, created_user, created_movie):
        """Test POST /api/users/{id}/movies with duplicate data"""
        duplicate_data = {
            'title': created_movie['title'],
            'year': created_movie['year']
        }
        response = client.post(f'/api/users/{created_user["id"]}/movies',
                               json=duplicate_data,
                               content_type='application/json')
        assert response.status_code == 409  # Conflict

        data = json.loads(response.data)
        assert data['success'] is False
        assert 'already have' in data['error']

    def test_api_get_movie(self, client, created_movie):
        """Test GET /api/movies/{id}"""
        response = client.get(f'/api/movies/{created_movie["id"]}')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['movie']['id'] == created_movie['id']

    def test_api_update_movie(self, client, created_movie):
        """Test PUT /api/movies/{id}"""
        updated_data = {
            'title': 'API Updated Movie',
            'director': 'API Director'
        }
        response = client.put(f'/api/movies/{created_movie["id"]}',
                              json=updated_data,
                              content_type='application/json')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['title'] == 'API Updated Movie'

    def test_api_delete_movie(self, client, created_movie):
        """Test DELETE /api/movies/{id}"""
        response = client.delete(f'/api/movies/{created_movie["id"]}')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['success'] is True

    def test_api_create_review(self, client, created_movie, sample_review_data):
        """Test POST /api/movies/{id}/reviews"""
        response = client.post(f'/api/movies/{created_movie["id"]}/reviews',
                               json=sample_review_data,
                               content_type='application/json')
        assert response.status_code == 201

        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['content'] == sample_review_data['content']

    def test_api_get_movie_reviews(self, client, created_movie, created_review):
        """Test GET /api/movies/{id}/reviews"""
        response = client.get(f'/api/movies/{created_movie["id"]}/reviews')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']) >= 1

    def test_api_info(self, client):
        """Test GET /api/ - API information"""
        response = client.get('/api/')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['success'] is True
        assert 'users' in data['data']
        assert 'movies' in data['data']
        assert 'reviews' in data['data']


class TestErrorHandling:
    """Test error handling functionality"""

    def test_404_error(self, client):
        """Test 404 error handling"""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
        assert b'404' in response.data
        assert b'Page Not Found' in response.data

    def test_validation_errors(self, client, created_user):
        """Test validation error handling"""
        # Test invalid rating
        invalid_movie = {
            'title': 'Test Movie',
            'rating': '15'  # Invalid: > 10
        }
        response = client.post(f'/users/{created_user["id"]}/add_movie',
                               data=invalid_movie, follow_redirects=True)
        assert response.status_code == 200
        assert b'between 1 and 10' in response.data.lower()

    def test_user_not_found_handling(self, client):
        """Test user not found error handling"""
        response = client.get('/users/999', follow_redirects=True)
        assert response.status_code == 200
        assert b'not found' in response.data.lower()

    def test_movie_not_found_handling(self, client, created_user):
        """Test movie not found error handling"""
        response = client.get(f'/users/{created_user["id"]}/movies/999', follow_redirects=True)
        assert response.status_code == 200
        assert b'not found' in response.data.lower()


class TestTriviaRoutes:
    """Test trivia route functionality (basic tests without external API)"""

    def test_trivia_question_no_session(self, client):
        """Test trivia question without active session"""
        response = client.get('/trivia/question')
        assert response.status_code == 302
        assert '/users' in response.location

        # Check the flash message in session
        with client.session_transaction() as sess:
            flashes = sess.get('_flashes', [])
            flash_messages = [msg[1] for msg in flashes]  # msg[0] is category, msg[1] is message
            assert any('No active trivia session' in msg for msg in flash_messages)


    def test_trivia_results_no_session(self, client):
        """Test trivia results without session"""
        response = client.get('/trivia/results')
        assert response.status_code == 302
        assert '/users' in response.location

        with client.session_transaction() as sess:
            flashes = sess.get('_flashes', [])
            flash_messages = [msg[1] for msg in flashes]
            assert any('No trivia session' in msg for msg in flash_messages)

    def test_global_leaderboard(self, client):
        """Test global leaderboard page"""
        response = client.get('/leaderboard')
        assert response.status_code == 200
        assert b'Global Trivia Leaderboard' in response.data

    def test_collection_leaderboard(self, client):
        """Test collection leaderboard page"""
        response = client.get('/leaderboard/collection')
        assert response.status_code == 200
        assert b'Collection Trivia Leaderboard' in response.data

    def test_user_trivia_stats(self, client, created_user):
        """Test user trivia stats page"""
        response = client.get(f'/users/{created_user["id"]}/trivia-stats')
        assert response.status_code == 200
        assert b'Trivia Statistics' in response.data