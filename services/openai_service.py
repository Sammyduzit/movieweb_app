"""
OpenAI Service - ChatGPT API fallback for trivia generation.
"""
import os

import requests

from config import TriviaConfig, APIConfig

import json

from dotenv import load_dotenv

load_dotenv()


class OpenAIService:
    """Service to interact with OpenAI ChatGPT API for trivia generation"""

    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-3.5-turbo"  # or "gpt-4" if you have access

    def generate_movie_trivia(self, movie_data):
        """Generate 7 trivia questions for a specific movie"""
        prompt = f"""Generate exactly {TriviaConfig.MOVIE_QUESTIONS} trivia questions about the movie 
        "{movie_data['title']} ({movie_data.get('year', 'Unknown')})". 

        Movie details:
        - Director: {movie_data.get('director', 'Unknown')}
        - Genre: {movie_data.get('genre', 'Unknown')}
        - Year: {movie_data.get('year', 'Unknown')}

        Create questions about plot details, character interactions, memorable quotes, behind-the-scenes facts, 
        and movie trivia that only true fans would know.

        Mix difficulty levels: 2 medium, 4 very hard, and 1 with 'highest difficulty' possible.

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
        """Generate 21 trivia questions across user's movie collection"""
        movie_list = []
        # Limit movies to 10 for better prompts
        for i, movie in enumerate(movies_data[:10]):
            movie_list.append(
                f"{movie['title']} ({movie.get('year', 'Unknown')}) directed by {movie.get('director', 'Unknown')}")

        movies_text = "\n- ".join(movie_list)

        prompt = f"""Generate exactly {TriviaConfig.COLLECTION_QUESTIONS} trivia questions about these movies:

        - {movies_text}

        Create comparative questions (which movie was released first?), character questions across movies, 
        director questions, and challenging trivia that tests knowledge of the entire collection.

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

    def _make_api_call(self, prompt):
        """Make API call to OpenAI ChatGPT"""
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
                    "content": "You are a movie trivia expert. You only respond with valid JSON containing trivia questions. Never include any text outside of the JSON structure."
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
            response = requests.post(self.base_url, json=payload, headers=headers, timeout=30)

            print(f"📡 OpenAI API Response Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                ai_response = data['choices'][0]['message']['content'].strip()

                try:
                    parsed_json = json.loads(ai_response)

                    if 'questions' in parsed_json and len(parsed_json['questions']) > 0:
                        print(f"✅ Generated {len(parsed_json['questions'])} OpenAI trivia questions")
                        return parsed_json
                    else:
                        print("🔴 OpenAI response missing questions array")
                        return None

                except json.JSONDecodeError:
                    import re
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

            elif response.status_code == 429:
                print("🔴 OpenAI API rate limit exceeded")
                return None
            elif response.status_code == 401:
                print("🔴 OpenAI API authentication failed - check your API key")
                return None
            else:
                print(f"🔴 OpenAI API error: {response.status_code} - {response.text}")
                return None

        except requests.RequestException as e:
            print(f"🔴 OpenAI Request error: {e}")
            return None
        except Exception as e:
            print(f"🔴 OpenAI Unexpected error: {e}")
            return None

    def test_connection(self):
        """Test if OpenAI API connection works"""
        test_prompt = 'Generate a simple JSON response: {"message": "Hello from OpenAI!", "status": "working"}'

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
            response = requests.post(self.base_url, json=payload, headers=headers, timeout=10)

            if response.status_code == 200:
                print("✅ OpenAI API connection successful")
                return True
            else:
                print(f"❌ OpenAI API test failed: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ OpenAI API test error: {e}")
            return False