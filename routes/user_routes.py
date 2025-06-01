"""
User Routes - Web routes for user management functionality.
Handles user listing and creation operations.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash

from services.user_service import UserService
from exceptions import ValidationError, DatabaseError

user_bp = Blueprint('users', __name__, url_prefix='/users')

user_service = UserService()


@user_bp.route('/')
def list_users():
    """
    Display all users in an HTML template.

    :return: Rendered template with list of all users
    """
    try:
        users = user_service.get_all_users()
        return render_template('users.html', users=users)

    except DatabaseError as e:
        flash(f'Database error: {e.message}', 'error')
        return render_template('users.html', users=[])

    except Exception as e:
        flash(f'Unexpected error loading users: {str(e)}', 'error')
        return render_template('users.html', users=[])


@user_bp.route('/add', methods=['GET', 'POST'])
def add_user():
    """
    Add a new user to the database.

    :return: Rendered template for GET, redirect for successful POST
    """
    if request.method == 'POST':
        try:
            user_data = {
                'name': request.form.get('name', '').strip(),
                'email': request.form.get('email', '').strip()
            }

            new_user = user_service.create_user(user_data)
            flash(f'User {new_user["name"]} added successfully!', 'success')
            return redirect(url_for('users.list_users'))

        except ValidationError as e:
            if e.field == 'email' and 'already exists' in e.message:
                flash('Email already exists. Please use a different email.',
                      'error')
            else:
                flash(f'Validation error: {e.message}', 'error')
            return render_template('add_user.html')

        except DatabaseError as e:
            flash(f'Database error: {e.message}', 'error')
            return render_template('add_user.html')

        except Exception as e:
            flash(f'Unexpected error adding user: {str(e)}', 'error')
            return render_template('add_user.html')

    return render_template('add_user.html')