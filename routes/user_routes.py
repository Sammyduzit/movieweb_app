"""
User Routes - Web routes for user management functionality.
Handles user listing and creation operations.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash

from services.user_service import UserService
from exceptions import ValidationError, DatabaseError
from utils.decorators import require_user

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


@user_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@require_user
def edit_user(user_id, user):
    """
    Edit an existing user.

    :param user_id: ID of the user to edit
    :param user: User object (injected by decorator)
    :return: Rendered template for GET, redirect for successful POST
    """

    if request.method == 'POST':
        try:
            user_data = {
                'name': request.form.get('name', '').strip(),
                'email': request.form.get('email', '').strip()
            }

            updated_user = user_service.update_user(user_id, user_data)
            flash(f'User {updated_user["name"]} updated successfully!',
                  'success')
            return redirect(url_for('movies.user_movies', user_id=user_id))

        except ValidationError as e:
            if e.field == 'email' and 'already exists' in e.message:
                flash('Email already exists. Please use a different email.',
                      'error')
            else:
                flash(f'Validation error: {e.message}', 'error')
            return render_template('edit_user.html',
                           user=user,
                           back_url=f'/users/{user_id}/')

        except DatabaseError as e:
            flash(f'Database error: {e.message}', 'error')
            return render_template('edit_user.html',
                                   user=user,
                                   back_url=f'/users/{user_id}/')

        except Exception as e:
            flash(f'Unexpected error updating user: {str(e)}', 'error')
            return render_template('edit_user.html',
                                   user=user,
                                   back_url=f'/users/{user_id}/')

        #
        # except ValidationError as e:
        #     if e.field == 'email' and 'already exists' in e.message:
        #         flash('Email already exists. Please use a different email.',
        #               'error')
        #     else:
        #         flash(f'Validation error: {e.message}', 'error')
        #     return render_template('edit_user.html', user=user,
        #                            back_url=url_for('movies.user_movies', user_id=user_id))
        #
        # except DatabaseError as e:
        #     flash(f'Database error: {e.message}', 'error')
        #     return render_template('edit_user.html', user=user,
        #                            back_url=url_for('movies.user_movies', user_id=user_id))
        #
        # except Exception as e:
        #     flash(f'Unexpected error updating user: {str(e)}', 'error')
        #     return render_template('edit_user.html', user=user,
        #                            back_url=url_for('movies.user_movies', user_id=user_id))

    back_url = f'/users/{user_id}/'       # <-- HINZUFÜGEN
    print(f"DEBUG: back_url = {back_url}") # <-- HINZUFÜGEN

    return render_template('edit_user.html', user=user)


@user_bp.route('/<int:user_id>/delete')
@require_user
def delete_user(user_id, user):
    """
    Delete a user and all associated data.

    :param user_id: ID of the user to delete
    :param user: User object (injected by decorator)
    :return: Redirect to user list with status message
    """
    try:
        user_name = user['name']
        user_service.delete_user(user_id)
        flash(f'User "{user_name}" and all '
              f'associated data deleted successfully!', 'success')

    except DatabaseError as e:
        flash(f'Database error: {e.message}', 'error')

    except Exception as e:
        flash(f'Unexpected error deleting user: {str(e)}', 'error')

    return redirect(url_for('users.list_users'))