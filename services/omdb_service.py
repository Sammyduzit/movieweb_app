"""
OMDb Service - External API service for movie data enhancement.
Integrates with OMDb API to fetch comprehensive movie information.
"""
import os

import requests

from config import APIConfig




class OMDbService:
    """Service to interact with OMDb API for movie data"""


    def __init__(self, api_key=None):
        """
        Initialize OMDb service with API key.

        :param api_key: OMDb API key
        """
        self.api_key = api_key or os.getenv('OMDB_API_KEY')
        self.base_url = APIConfig.OMDB_BASE_URL


    def search_movie(self, title, year=None):
        """
        Search for a movie by title and optionally year.

        :param title: Movie title to search for
        :param year: Optional year to narrow search
        :return: Dictionary with movie data or None if not found
        """
        if not self.api_key:
            print("Warning: No OMDb API key provided. Skipping API call.")
            return None

        try:
            params = {
                'apikey': self.api_key,
                't': title,
                'type': 'movie',
                'plot': 'short'
            }

            if year:
                params['y'] = year

            response = requests.get(self.base_url,
                                    params=params,
                                    timeout=APIConfig.OMDB_TIMEOUT)
            response.raise_for_status()

            data = response.json()

            if data.get('Response') == 'True':
                return self._extract_movie_data(data, title, year)
            else:
                print(f"Movie not found in OMDb: {data.get('Error', 'Unknown error')}")
                return None

        except requests.RequestException as e:
            print(f"Error calling OMDb API: {e}")
            return None
        except Exception as e:
            print(f"Error processing OMDb response: {e}")
            return None

    def _extract_movie_data(self, data, fallback_title, fallback_year):
        """
        Extract and clean movie data from OMDb API response.

        :param data: Raw API response data
        :param fallback_title: Fallback title if API data is missing
        :param fallback_year: Fallback year if API data is missing
        :return: Dictionary with cleaned movie data
        """
        year_str = data.get('Year', str(fallback_year or 0))
        year = int(year_str) if year_str.isdigit() else fallback_year

        imdb_rating_str = data.get('imdbRating', 'N/A')
        imdb_rating = None
        if imdb_rating_str != 'N/A':
            try:
                imdb_rating = float(imdb_rating_str)
            except (ValueError, TypeError):
                imdb_rating = None

        return {
            'title': data.get('Title', fallback_title),
            'director': data.get('Director', ''),
            'year': year,
            'genre': data.get('Genre', ''),
            'imdb_rating': imdb_rating,
            'plot': data.get('Plot', ''),
            'poster': data.get('Poster', '')
        }

    def enhance_movie_data(self, movie_data):
        """
        Enhance movie data with information from OMDb API.

        :param movie_data: Dictionary with at least 'title' key
        :return: Enhanced movie data dictionary
        """
        title = movie_data.get('title')
        year = movie_data.get('year')

        if not title:
            return movie_data

        omdb_data = self.search_movie(title, year)

        if omdb_data:
            enhanced_data = movie_data.copy()

            enhancement_fields = {
                'director': 'director',
                'year': 'year',
                'genre': 'genre'
            }

            for original_field, omdb_field in enhancement_fields.items():
                if not enhanced_data.get(original_field):
                    enhanced_data[original_field] = omdb_data.get(omdb_field, '')

            enhanced_data['imdb_rating'] = omdb_data.get('imdb_rating')
            enhanced_data['plot'] = omdb_data.get('plot', '')
            enhanced_data['poster'] = omdb_data.get('poster', '')

            return enhanced_data

        return movie_data