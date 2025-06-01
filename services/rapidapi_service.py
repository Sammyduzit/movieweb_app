"""
RapidAPI Service - Primary ChatGPT API service for trivia generation.
Integrates with RapidAPI ChatGPT endpoint with usage tracking and rate limiting.
"""
import json
import os
import re

import requests
from dotenv import load_dotenv

from config import TriviaConfig, APIConfig

load_dotenv()

class RapidAPIService:
    """Service to interact with RapidAPI ChatGPT for trivia generation"""

    def __init__(self):
        """Initialize RapidAPI service with API key and usage tracker."""
        self.api_key = os.getenv('RAPIDAPI_KEY')
        self.base_url = "https://chatgpt-ai-chat-bot.p.rapidapi.com/ask"

        from .api_usage_tracker import APIUsageTracker
        self.usage_tracker = APIUsageTracker(limit=95)


    # ==================== TRIVIA GENERATION METHODS ====================

    def generate_movie_trivia(self, movie_data):
        """
        Generate trivia questions for a specific movie.

        :param movie_data: Dictionary containing movie information
        :return: Dictionary with trivia questions or None if failed
        """
        query = self._build_movie_trivia_query(movie_data)
        return self._make_api_call(query)

    def generate_collection_trivia(self, movies_data):
        """
        Generate trivia questions across user's movie collection.

        :param movies_data: List of movie dictionaries
        :return: Dictionary with trivia questions or None if failed
        """
        query = self._build_collection_trivia_query(movies_data)
        return self._make_api_call(query)

    # ==================== QUERY BUILDING METHODS ====================

    def _build_movie_trivia_query(self, movie_data):
        """
        Build trivia query for a specific movie.

        :param movie_data: Dictionary containing movie information
        :return: Formatted query string for API
        """
        movie_info = (
            f'"{movie_data["title"]} ({movie_data.get("year", "Unknown")})"'
        )

        details = []
        if movie_data.get('director'):
            details.append(f"Director: {movie_data['director']}")
        if movie_data.get('genre'):
            details.append(f"Genre: {movie_data['genre']}")

        movie_details = ", ".join(details) if details else "Unknown details"

        return f"""Generate exactly {TriviaConfig.MOVIE_QUESTIONS} trivia questions about the movie 
        {movie_info}. 
        Movie details: {movie_details}

        IMPORTANT: Return ONLY valid JSON. No extra text before or after.

        {{
            "questions": [
                {{
                    "question": "What year was this movie released?",
                    "options": ["1999", "2000", "2001", "1998"],
                    "correct": 0,
                    "difficulty": "easy"
                }}
            ]
        }}

        Make questions for ultimate nerds about plot, things that happen in the movie and easter eggs.
        Mix difficulty levels: 2 medium, 4 very hard and 1 with 'highest difficulty' possible.
        Return valid JSON ONLY.
        """

    def _build_collection_trivia_query(self, movies_data):
        """
        Build trivia query for movie collection.

        :param movies_data: List of movie dictionaries
        :return: Formatted query string for API
        """
        # Limit movies to 10 for better prompts
        movie_list = []
        for movie in movies_data[:10]:
            movie_info = (
                f"{movie['title']} ({movie.get('year', 'Unknown')}) "
                f"directed by {movie.get('director', 'Unknown')}"
            )
            movie_list.append(movie_info)

        movies_text = ", ".join(movie_list)

        return f"""
        Generate exactly {TriviaConfig.COLLECTION_QUESTIONS} trivia questions about these movies:
        {movies_text}

        Format your response as valid JSON with this exact structure:
        {{
            "questions": [
                {{
                    "question": "Which movie in the collection was released first?",
                    "options": ["Movie A", "Movie B", "Movie C", "Movie D"],
                    "correct": 1,
                    "difficulty": "medium"
                }}
            ]
        }}

        Question types: comparative (which movie...), specific facts.
        Mix difficulty: 3 easy, 11 medium, 7 hard.
        Only use movies from the provided collection.
        """

    # ==================== API COMMUNICATION ====================

    def _make_api_call(self, query):
        """
        Make API call to RapidAPI ChatGPT with usage tracking.

        :param query: Query string to send to API
        :return: Parsed JSON response or None if failed
        """
        if not self.api_key:
            print("⚠️ No RapidAPI key found")
            return None

        if not self.usage_tracker.can_make_call():
            print("🚫 Monthly API limit reached - blocking API call")
            return None

        payload = {"query": query}
        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "chatgpt-ai-chat-bot.p.rapidapi.com",
            "Content-Type": "application/json"
        }

        try:
            print("🤖 Generating trivia questions...")
            response = requests.post(self.base_url,
                                     json=payload,
                                     headers=headers,
                                     timeout=APIConfig.RAPIDAPI_TIMEOUT)

            self.usage_tracker.record_call()
            print(f"📡 API Response Status: {response.status_code}")

            if response.status_code == 200:
                return self._process_api_response(response)
            else:
                print(f"🔴 API request failed with status: {response.status_code}")
                return None

        except requests.RequestException as e:
            self.usage_tracker.record_call()
            print(f"🔴 Request error: {e}")
            return None
        except Exception as e:
            print(f"🔴 Unexpected error: {e}")
            return None

    def _process_api_response(self, response):
        """
        Process and parse API response.

        :param response: Response object from requests
        :return: Parsed JSON data or None if parsing failed
        """
        try:
            response_text = response.text.strip()

            if "I'm sorry, right now I'm not able to answer that question" in response_text:
                print("🔴 ChatGPT service temporarily unavailable")
                return None

            # Try to parse as JSON first
            try:
                data = response.json()
                ai_response = data.get('response', data.get('message', ''))
            except json.JSONDecodeError:
                ai_response = response_text

            # Extract JSON from response using regex
            json_match = re.search(r'\{.*"questions".*\}', ai_response, re.DOTALL)
            if json_match:
                try:
                    parsed_json = json.loads(json_match.group())
                    questions = parsed_json.get('questions', [])

                    if questions and len(questions) > 0:
                        print(f"✅ Generated {len(questions)} AI trivia questions")
                        return parsed_json
                except json.JSONDecodeError as e:
                    print(f"🔴 JSON parsing error: {e}")

            print("🔴 No valid trivia questions found in response")
            return None

        except Exception as e:
            print(f"🔴 Error processing response: {e}")
            return None

    # ==================== UTILITY METHODS ====================

    def test_connection(self):
        """
        Test if RapidAPI connection works.

        :return: True if connection successful, False otherwise
        """
        test_query = "Say 'Hello, trivia game!' in JSON format: {\"message\": \"Hello, trivia game!\"}"
        result = self._make_api_call(test_query)
        return result is not None
