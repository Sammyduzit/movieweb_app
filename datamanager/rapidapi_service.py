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
        self.base_url = "https://chatgpt-ai-chat-bot.p.rapidapi.com/ask"  # Example endpoint

    def generate_movie_trivia(self, movie_data):
        """Generate 7 trivia questions for a specific movie"""
        query = f"""Generate exactly 7 trivia questions about the movie 
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
        for i, movie in enumerate(movies_data[:15]):  # Limit to 15 movies
            movie_list.append(f"{movie['title']} ({movie.get('year', 'Unknown')}) directed by {movie.get('director', 'Unknown')}")

        movies_text = ", ".join(movie_list)

        query = f"""
        Generate exactly 21 trivia questions about these movies:
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

        payload = {"query": query}
        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "chatgpt-ai-chat-bot.p.rapidapi.com",
            "Content-Type": "application/json"
        }

        try:
            print("🤖 Generating trivia questions...")
            response = requests.post(self.base_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            print(f"✅ API Response received: {len(str(data))} characters")

            ai_response = data.get('response', '')
            if not ai_response:
                print("🔴 No response text in API response")
                return None

            json_match = re.search(r'\{.*"questions".*\}', ai_response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                try:
                    parsed_json = json.loads(json_str)
                    questions = parsed_json.get('questions', [])
                    print(f"✅ Generated {len(questions)} trivia questions")
                    return parsed_json
                except json.JSONDecodeError as e:
                    print(f"🔴 JSON parsing error: {e}")
                    print(f"Raw JSON: {json_str[:200]}...")
                    return None
            else:
                print("🔴 No JSON structure found in response")
                print(f"Raw response: {ai_response[:200]}...")
                return None

        except requests.RequestException as e:
            print(f"🔴 RapidAPI request error: {e}")
            return None
        except Exception as e:
            print(f"🔴 Unexpected error: {e}")
            return None

    def test_connection(self):
        """Test if RapidAPI connection works"""
        test_query = "Say 'Hello, trivia game!' in JSON format: {\"message\": \"Hello, trivia game!\"}"
        result = self._make_api_call(test_query)
        return result is not None


# service = RapidAPIService()
# movie_data = {
#     "title": "The Matrix",
#     "year": 1999
# }
# test = service.generate_movie_trivia(movie_data)
#
# print(test)
# print(type(test))

# url = "https://chatgpt-ai-chat-bot.p.rapidapi.com/ask"
# payload = {"query": "What is google?"}
# headers = {
#     "x-rapidapi-key": os.getenv('RAPIDAPI_KEY'),
#     "x-rapidapi-host": "chatgpt-ai-chat-bot.p.rapidapi.com",
#     "Content-Type": "application/json"
# }
#
# response = requests.post(url, json=payload, headers=headers)
# print(f"Status: {response.status_code}")
# print(response.json())