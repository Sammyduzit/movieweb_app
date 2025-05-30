import requests
import os


class OMDbService:
    """Service to interact with OMDb API for movie data"""


    def __init__(self, api_key=None):
        """
        Initialize OMDb service with API key.

        :param api_key: OMDb API key
        """
        self.api_key = api_key or os.getenv('OMDB_API_KEY')
        self.base_url = "http://www.omdbapi.com/"


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

            response = requests.get(self.base_url, params=params, timeout=5)
            response.raise_for_status()

            data = response.json()

            if data.get('Response') == 'True':
                return {
                    'title': data.get('Title', title),
                    'director': data.get('Director', ''),
                    'year': int(data.get('Year', year or 0)) if data.get('Year', '').isdigit() else year,
                    'genre': data.get('Genre', ''),
                    'imdb_rating': float(data.get('imdbRating', 0)) if data.get('imdbRating', 'N/A') != 'N/A' else None,
                    'plot': data.get('Plot', ''),
                    'poster': data.get('Poster', '')
                }
            else:
                print(f"Movie not found in OMDb: {data.get('Error', 'Unknown error')}")
                return None

        except requests.RequestException as e:
            print(f"Error calling OMDb API: {e}")
            return None
        except Exception as e:
            print(f"Error processing OMDb response: {e}")
            return None


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

        ##TEST
        print("got title in OMDB SERVICE")
        ##TEST

        omdb_data = self.search_movie(title, year)

        if omdb_data:
            enhanced_data = movie_data.copy()
            ##TEST
            print("omdbdata:", omdb_data)
            print("enhanced:",enhanced_data)
            ##TEST

            if not enhanced_data.get('director'):
                enhanced_data['director'] = omdb_data.get('director', '')

            if not enhanced_data.get('year'):
                enhanced_data['year'] = omdb_data.get('year')

            if not enhanced_data.get('genre'):
                enhanced_data['genre'] = omdb_data.get('genre', '')

            enhanced_data['imdb_rating'] = omdb_data.get('imdb_rating')
            enhanced_data['plot'] = omdb_data.get('plot', '')
            enhanced_data['poster'] = omdb_data.get('poster', '')

            ##TEST
            print("final encanced data: \n", enhanced_data)
            ##TEST
            return enhanced_data

        return movie_data