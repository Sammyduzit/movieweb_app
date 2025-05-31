from config import TriviaConfig, APIConfig
import requests
import json
import os
import re
from dotenv import load_dotenv

load_dotenv()

class RapidAPIService:
    """Service to interact with RapidAPI ChatGPT for trivia generation"""

    def __init__(self):
        self.api_key = os.getenv('RAPIDAPI_KEY')
        self.base_url = "https://chatgpt-ai-chat-bot.p.rapidapi.com/ask"

        from .api_usage_tracker import APIUsageTracker
        self.usage_tracker = APIUsageTracker(limit=95)


    def generate_movie_trivia(self, movie_data):
        """Generate 7 trivia questions for a specific movie"""
        query = f"""Generate exactly {TriviaConfig.MOVIE_QUESTIONS} trivia questions about the movie 
        "{movie_data['title']} ({movie_data.get('year', 'Unknown')})". 
        Movie details: Director: {movie_data.get('director', 'Unknown')}, 
        Genre: {movie_data.get('genre', 'Unknown')}
        
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

        return self._make_api_call(query)


    def generate_collection_trivia(self, movies_data):
        """Generate 21 trivia questions across user's movie collection"""
        movie_list = []
        #Limit movies to 10
        for i, movie in enumerate(movies_data[:10]):
            movie_list.append(f"{movie['title']} ({movie.get('year', 'Unknown')}) directed by {movie.get('director', 'Unknown')}")

        movies_text = ", ".join(movie_list)

        query = f"""
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

        return self._make_api_call(query)


    def _make_api_call(self, query):
        """Make API call to RapidAPI ChatGPT"""
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
            response = requests.post(self.base_url, json=payload, headers=headers, timeout=APIConfig.RAPIDAPI_TIMEOUT)

            self.usage_tracker.record_call()

            print(f"📡 API Response Status: {response.status_code}")

            if response.status_code == 200:
                response_text = response.text.strip()

                if "I'm sorry, right now I'm not able to answer that question" in response_text:
                    print("🔴 ChatGPT service temporarily unavailable")
                    return None

                try:
                    data = response.json()
                    ai_response = data.get('response', data.get('message', ''))
                except json.JSONDecodeError:
                    ai_response = response_text

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

        except requests.RequestException as e:
            self.usage_tracker.record_call()
            print(f"🔴 Request error: {e}")
        except Exception as e:
            print(f"🔴 Unexpected error: {e}")

        return None


    def test_connection(self):
        """Test if RapidAPI connection works"""
        test_query = "Say 'Hello, trivia game!' in JSON format: {\"message\": \"Hello, trivia game!\"}"
        result = self._make_api_call(test_query)
        return result is not None
