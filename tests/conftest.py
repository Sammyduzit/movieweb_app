import pytest
import os
import tempfile
import sys

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import threading
import time

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(current_dir)
sys.path.insert(0, project_dir)

# Import with new structure
from app import create_app
from datamanager import db, User, Movie, Review, TriviaScore
from services.user_service import UserService
from services.movie_service import MovieService
from services.review_service import ReviewService
from services.trivia_service import TriviaService


@pytest.fixture
def app():
    """Create and configure a test Flask application"""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix='.db')

    # Create test app with temporary database
    test_app = create_app()
    test_app.config['TESTING'] = True
    test_app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    test_app.config['WTF_CSRF_ENABLED'] = False
    test_app.config['SECRET_KEY'] = 'test-secret-key'

    with test_app.app_context():
        db.create_all()
        # Clear any existing data to avoid conflicts
        db.session.query(TriviaScore).delete()
        db.session.query(Review).delete()
        db.session.query(Movie).delete()
        db.session.query(User).delete()
        db.session.commit()

    yield test_app

    # Cleanup
    with test_app.app_context():
        db.session.remove()
        db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Test client for the Flask app"""
    return app.test_client()


@pytest.fixture
def user_service(app):
    """User service instance for testing"""
    with app.app_context():
        return UserService()


@pytest.fixture
def movie_service(app):
    """Movie service instance for testing"""
    with app.app_context():
        return MovieService()


@pytest.fixture
def review_service(app):
    """Review service instance for testing"""
    with app.app_context():
        return ReviewService()


@pytest.fixture
def trivia_service(app):
    """Trivia service instance for testing"""
    with app.app_context():
        return TriviaService()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing - unique for each test"""
    import time
    timestamp = str(int(time.time() * 1000))
    return {
        'name': f'Test User {timestamp}',
        'email': f'test{timestamp}@example.com'
    }


@pytest.fixture
def sample_movie_data():
    """Sample movie data for testing - unique for each test"""
    import time
    timestamp = str(int(time.time() * 1000))
    return {
        'title': f'Test Movie {timestamp}',
        'director': f'Test Director {timestamp}',
        'year': '2023',
        'genre': 'Test Genre',
        'rating': '8.5'
    }


@pytest.fixture
def sample_review_data():
    """Sample review data for testing"""
    return {
        'content': 'This is a great test movie!',
        'reviewer_rating': '9'
    }


@pytest.fixture
def created_user(app, user_service, sample_user_data):
    """Create a user for testing"""
    with app.app_context():
        return user_service.create_user(sample_user_data)


@pytest.fixture
def created_movie(app, movie_service, created_user, sample_movie_data):
    """Create a movie for testing"""
    with app.app_context():
        return movie_service.create_movie_for_user(created_user['id'], sample_movie_data)


@pytest.fixture
def created_review(app, review_service, created_movie, sample_review_data):
    """Create a review for testing"""
    with app.app_context():
        return review_service.create_review(created_movie['id'], sample_review_data)


@pytest.fixture(scope="session")
def live_server():
    """Start a live server for Selenium tests"""
    import tempfile
    db_fd, db_path = tempfile.mkstemp(suffix='.db')

    test_app = create_app()
    test_app.config['TESTING'] = True
    test_app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    test_app.config['WTF_CSRF_ENABLED'] = False
    test_app.config['SECRET_KEY'] = 'selenium-test-key'

    def run_server():
        with test_app.app_context():
            db.create_all()
            print("Selenium live server database created")

        print("Starting Selenium live server on http://127.0.0.1:5003")
        test_app.run(host='127.0.0.1', port=5003, debug=False, threaded=True)

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(4)

    yield 'http://127.0.0.1:5003'

    # Cleanup
    try:
        os.close(db_fd)
        os.unlink(db_path)
    except:
        pass


@pytest.fixture
def selenium_driver():
    """Create a Selenium WebDriver instance"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-web-security')
    options.add_argument('--allow-running-insecure-content')

    try:
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)
        yield driver
    except Exception as e:
        print(f"Chrome driver error: {e}")
        pytest.skip("Chrome driver not available")
    finally:
        try:
            driver.quit()
        except:
            pass


class SeleniumHelper:
    """Helper class for common Selenium operations"""

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 10)

    def get(self, path=''):
        """Navigate to a path"""
        url = f"{self.base_url}{path}"
        self.driver.get(url)
        return self

    def find_element(self, by, value):
        """Find an element with wait"""
        return self.wait.until(EC.presence_of_element_located((by, value)))

    def find_elements(self, by, value):
        """Find multiple elements"""
        return self.driver.find_elements(by, value)

    def click(self, by, value):
        """Click an element with wait"""
        element = self.wait.until(EC.element_to_be_clickable((by, value)))
        element.click()
        return self

    def type_text(self, by, value, text):
        """Type text into an input field"""
        element = self.find_element(by, value)
        element.clear()
        element.send_keys(text)
        return self

    def submit_form(self, form_selector=None):
        """Submit a form"""
        if form_selector:
            form = self.find_element(By.CSS_SELECTOR, form_selector)
            form.submit()
        else:
            self.click(By.CSS_SELECTOR, 'button[type="submit"], input[type="submit"]')
        return self

    def wait_for_text(self, text, timeout=10):
        """Wait for specific text to appear on page"""
        WebDriverWait(self.driver, timeout).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), text)
        )
        return self

    def get_flash_messages(self):
        """Get all flash messages from the page"""
        try:
            messages = self.find_elements(By.CSS_SELECTOR, '.message, .alert, .flash')
            return [msg.text for msg in messages]
        except:
            return []


@pytest.fixture
def selenium_helper(selenium_driver, live_server):
    """Create a Selenium helper instance"""
    return SeleniumHelper(selenium_driver, live_server)