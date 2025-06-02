"""
User Service - Business logic for user operations.
"""
import re

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from config import ValidationConfig
from datamanager import SQLiteDataManager
from exceptions import UserNotFoundError, ValidationError, DatabaseError


class UserService:
    """Service class for handling user-related business logic"""

    def __init__(self):
        """Initialize user service with data manager."""
        self.data_manager = SQLiteDataManager()

    def validate_email(self, email):
        """
        Validate email format using regex pattern.

        :param email: Email address to validate
        :return: Cleaned and normalized email address
        """
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError('email', 'Invalid email format')
        return email.strip().lower()

    def validate_user_data(self, user_data):
        """
        Validate user input data according to business rules.

        :param user_data: Dictionary containing user data to validate
        :return: Dictionary with validated and cleaned user data
        """
        name = self._validate_name(user_data.get('name', ''))
        email = self._validate_email_field(user_data.get('email', ''))

        return {
            'name': name,
            'email': email
        }

    def _validate_name(self, name):
        """
        Validate user name.

        :param name: User name to validate
        :return: Cleaned name string
        """
        name = name.strip()
        if not name:
            raise ValidationError('name', 'Name is required')

        if len(name) > ValidationConfig.USER_NAME_MAX:
            raise ValidationError('name', 'Name must be less than 100 characters')

        return name

    def _validate_email_field(self, email):
        """
        Validate email field with format checking.

        :param email: Email address to validate
        :return: Validated and normalized email address
        """
        email = email.strip()
        if not email:
            raise ValidationError('email', 'Email is required')

        return self.validate_email(email)

    # ==================== USER OPERATIONS ====================

    def get_all_users(self):
        """
        Get all users with error handling.

        :return: List of user dictionaries
        """
        try:
            return self.data_manager.get_all_users()
        except SQLAlchemyError as e:
            raise DatabaseError('fetching users', e)

    def get_user_by_id(self, user_id):
        """
        Get user by ID, raise UserNotFoundError if not found.

        :param user_id: ID of the user to retrieve
        :return: User dictionary
        """
        users = self.get_all_users()
        user = next((u for u in users if u['id'] == user_id), None)
        if not user:
            raise UserNotFoundError(user_id)
        return user

    def create_user(self, user_data):
        """
        Create new user with validation.

        :param user_data: Dictionary containing user data
        :return: Dictionary representation of created user
        """
        validated_data = self.validate_user_data(user_data)

        try:
            return self.data_manager.add_user(validated_data)
        except IntegrityError:
            raise ValidationError('email', 'Email already exists')
        except SQLAlchemyError as e:
            raise DatabaseError('creating user', e)