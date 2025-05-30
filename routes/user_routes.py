from flask import Blueprint, render_template, request, redirect, url_for, flash
from datamanager import SQLiteDataManager
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

user_bp = Blueprint('users', __name__, url_prefix='/users')

data_manager = SQLiteDataManager()


@user_bp.route('/')
def list_users():
    """Display all users in an HTML template."""
    try:
        users = data_manager.get_all_users()
        return render_template('users.html', users=users)
    except SQLAlchemyError as e:
        flash(f'Database error loading users: {str(e)}', 'error')
        return render_template('users.html', users=[])
    except Exception as e:
        flash(f'Unexpected error loading users: {str(e)}', 'error')
        return render_template('users.html', users=[])


@user_bp.route('/add', methods=['GET', 'POST'])
def add_user():
    """Add a new user to the database."""
    if request.method == 'POST':
        try:
            user_data = {
                'name': request.form.get('name', '').strip(),
                'email': request.form.get('email', '').strip()
            }

            if not user_data['name'] or not user_data['email']:
                flash('Name and email are required', 'error')
                return render_template('add_user.html')

            new_user = data_manager.add_user(user_data)
            flash(f'User {new_user["name"]} added successfully!', 'success')
            return redirect(url_for('users.list_users'))

        except IntegrityError as e:
            flash('Email already exists. Please use a different email.', 'error')
            return render_template('add_user.html')
        except SQLAlchemyError as e:
            flash(f'Database error adding user: {str(e)}', 'error')
            return render_template('add_user.html')
        except Exception as e:
            flash(f'Unexpected error adding user: {str(e)}', 'error')
            return render_template('add_user.html')

    return render_template('add_user.html')