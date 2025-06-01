"""
Homepage Routes - Landing page for MovieWeb Gaming Platform.
Provides entry points to the MovieWeb application with welcome and homepage routes.
"""
from flask import Blueprint, render_template

homepage_bp = Blueprint('homepage', __name__)


@homepage_bp.route('/')
def homepage():
    """
    Main landing page - Gateway to the Gaming Arena.

    :return: Rendered homepage template
    """
    return render_template('homepage.html')


@homepage_bp.route('/welcome')
def welcome():
    """
    Alternative welcome route that redirects to the main homepage.

    :return: Rendered homepage template
    """
    return render_template('homepage.html')