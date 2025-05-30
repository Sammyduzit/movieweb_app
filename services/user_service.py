"""
User Service - Business logic for user operations.
"""
from config import ValidationConfig
from datamanager import SQLiteDataManager
from exceptions import UserNotFoundError, ValidationError, DatabaseError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import re


class UserService:
    """Service class for handling user-related business logic"""

    def __init__(self):
        self.data_manager = SQLiteDataManager()

    def validate_email(self, email):
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError('email', 'Invalid email format')
        return email.strip().lower()

    def validate_user_data(self, user_data):
        """Validate user input data"""
        name = user_data.get('name', '').strip()
        email = user_data.get('email', '').strip()

        if not name:
            raise ValidationError('name', 'Name is required')

        if not email:
            raise ValidationError('email', 'Email is required')

        if len(name) > ValidationConfig.USER_NAME_MAX:
            raise ValidationError('name', 'Name must be less than 100 characters')

        email = self.validate_email(email)

        return {
            'name': name,
            'email': email
        }

    def get_all_users(self):
        """Get all users with error handling"""
        try:
            return self.data_manager.get_all_users()
        except SQLAlchemyError as e:
            raise DatabaseError('fetching users', e)

    def get_user_by_id(self, user_id):
        """Get user by ID, raise UserNotFoundError if not found"""
        users = self.get_all_users()
        user = next((u for u in users if u['id'] == user_id), None)
        if not user:
            raise UserNotFoundError(user_id)
        return user

    def create_user(self, user_data):
        """Create new user with validation"""
        validated_data = self.validate_user_data(user_data)

        try:
            return self.data_manager.add_user(validated_data)
        except IntegrityError:
            raise ValidationError('email', 'Email already exists')
        except SQLAlchemyError as e:
            raise DatabaseError('creating user', e)