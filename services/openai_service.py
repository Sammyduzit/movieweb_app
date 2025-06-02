"""
OpenAI Service - ChatGPT API fallback for trivia generation.
Provides fallback trivia generation when RapidAPI service is unavailable.
"""
import json
import os
import re
import requests
from dotenv import load_dotenv

from config import TriviaConfig, APIConfig

load_dotenv()


class OpenAIService:
    """Service to interact with OpenAI ChatGPT API for trivia generation"""

    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-3.5-turbo"

    def generate_movie_trivia(self, movie_data):
        """
        Generate trivia questions for a specific movie.

        :param movie_data: Dictionary containing movie information
        :return: Dictionary with trivia questions or None if failed
        """
        prompt = f"""Generate exactly {TriviaConfig.MOVIE_QUESTIONS} trivia 
        questions about the movie "{movie_data['title']} ({movie_data.get('year', 'Unknown')})". 

        Movie details:
        - Director: {movie_data.get('director', 'Unknown')}
        - Genre: {movie_data.get('genre', 'Unknown')}
        - Year: {movie_data.get('year', 'Unknown')}

        Create questions about plot details, character interactions, 
        memorable quotes, behind-the-scenes facts, 
        and movie trivia that only true fans would know.

        Mix difficulty levels: 2 medium, 4 very hard, and 1 with 
        'highest difficulty' possible.

        Return ONLY valid JSON in this exact format:
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

        No additional text, just the JSON."""

        return self._make_api_call(prompt)

    def generate_collection_trivia(self, movies_data):
        """
        Generate trivia questions across user's movie collection.

        :param movies_data: List of movie dictionaries
        :return: Dictionary with trivia questions or None if failed
        """
        movie_list = []
        for i, movie in enumerate(movies_data[:10]):
            movie_list.append(
                f"{movie['title']} ({movie.get('year', 'Unknown')}) "
                f"directed by {movie.get('director', 'Unknown')}")

        movies_text = "\n- ".join(movie_list)

        prompt = f"""Generate exactly {TriviaConfig.COLLECTION_QUESTIONS} 
        trivia questions about these movies:

        - {movies_text}

        Create comparative questions (which movie was released first?), 
        character questions across movies, director questions, and challenging 
        trivia that tests knowledge of the entire collection.

        Mix difficulty levels: 3 easy, 11 medium, 7 hard.

        Only use movies from the provided collection above.

        Return ONLY valid JSON in this exact format:
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

        No additional text, just the JSON."""

        return self._make_api_call(prompt)

    # ==================== API COMMUNICATION ====================

    def _make_api_call(self, prompt):
        """
        Make API call to OpenAI ChatGPT.

        :param prompt: Prompt string to send to API
        :return: Parsed JSON response or None if failed
        """
        if not self.api_key:
            print("⚠️ No OpenAI API key found")
            return None

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a movie trivia expert. "
                               "You only respond with valid JSON "
                               "containing trivia questions. "
                               "Never include any text outside "
                               "of the JSON structure."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.7
        }

        try:
            print("🤖 Generating trivia with OpenAI ChatGPT...")
            response = requests.post(self.base_url,
                                     json=payload,
                                     headers=headers,
                                     timeout=30)

            print(f"📡 OpenAI API Response Status: {response.status_code}")

            if response.status_code == 200:
                return self._process_successful_response(response)
            else:
                return self._handle_error_response(response)

        except requests.RequestException as e:
            print(f"🔴 OpenAI Request error: {e}")
            return None
        except Exception as e:
            print(f"🔴 OpenAI Unexpected error: {e}")
            return None

    def _process_successful_response(self, response):
        """
        Process successful API response.

        :param response: Response object from requests
        :return: Parsed JSON data or None if parsing failed
        """
        try:
            data = response.json()
            ai_response = data['choices'][0]['message']['content'].strip()

            # Try direct JSON parsing first
            try:
                parsed_json = json.loads(ai_response)
                if 'questions' in parsed_json and len(parsed_json['questions']) > 0:
                    print(f"✅ Generated {len(parsed_json['questions'])} OpenAI trivia questions")
                    return parsed_json
                else:
                    print("🔴 OpenAI response missing questions array")
                    return None

            except json.JSONDecodeError:
                # Try regex extraction as fallback
                return self._extract_json_from_response(ai_response)

        except (KeyError, IndexError) as e:
            print(f"🔴 OpenAI response format error: {e}")
            return None

    def _extract_json_from_response(self, ai_response):
        """
        Extract JSON from response using regex.

        :param ai_response: Raw AI response string
        :return: Parsed JSON data or None if extraction failed
        """
        json_match = re.search(r'\{.*"questions".*\}', ai_response, re.DOTALL)
        if json_match:
            try:
                parsed_json = json.loads(json_match.group())
                questions = parsed_json.get('questions', [])

                if questions and len(questions) > 0:
                    print(f"✅ Extracted {len(questions)} OpenAI trivia questions")
                    return parsed_json
            except json.JSONDecodeError as e:
                print(f"🔴 JSON extraction error: {e}")

        print(f"🔴 OpenAI JSON parsing failed. Raw response: {ai_response[:200]}...")
        return None

    def _handle_error_response(self, response):
        """
        Handle API error responses.

        :param response: Response object from requests
        :return: None (always fails)
        """
        if response.status_code == 429:
            print("🔴 OpenAI API rate limit exceeded")
        elif response.status_code == 401:
            print("🔴 OpenAI API authentication failed - check your API key")
        else:
            print(f"🔴 OpenAI API error: {response.status_code} - {response.text}")
        return None

    def test_connection(self):
        """Test if OpenAI API connection works"""
        test_prompt = ('Generate a simple JSON response: '
                       '{"message": "Hello from OpenAI!", "status": "working"}')

        if not self.api_key:
            print("❌ No OpenAI API key configured")
            return False

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": test_prompt}],
            "max_tokens": 100,
            "temperature": 0.3
        }

        try:
            response = requests.post(self.base_url,
                                     json=payload,
                                     headers=headers,
                                     timeout=10)

            if response.status_code == 200:
                print("✅ OpenAI API connection successful")
                return True
            else:
                print(f"❌ OpenAI API test failed: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ OpenAI API test error: {e}")
            return False