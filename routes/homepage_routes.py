"""
Homepage Routes - Landing page for MovieWeb Gaming Platform
"""
from flask import Blueprint, render_template

homepage_bp = Blueprint('homepage', __name__)


@homepage_bp.route('/')
def homepage():
    """Main landing page - Gateway to the Gaming Arena"""
    return render_template('homepage.html')


@homepage_bp.route('/welcome')
def welcome():
    """Alternative welcome route"""
    return render_template('homepage.html')