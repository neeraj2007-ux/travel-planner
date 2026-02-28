import google.generativeai as genai
from config import Config
import json
import requests
import re

class AIService:
    def __init__(self):
        # Configure Gemini API
        if Config.GEMINI_API_KEY:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            # FIXED: Changed model to 1.5-flash (2.5 does not exist publicly yet)
            self.model = genai.GenerativeModel('models/gemini-1.5-flash')
        self.maps_api_key = Config.GOOGLE_MAPS_API_KEY
    
    def generate_itinerary(self, destination, budget, members, days, from_location, accommodation, interests):
        try:
            per_person_budget = budget / members
            distance_km = self._get_distance(from_location, destination)
            
            prompt = f"""
            Act as an expert travel planner. Create a {days}-day itinerary for {destination} from {from_location}.
            Budget: ₹{budget} total ({members} people).
            Interests: {interests}.
            Accommodation: {accommodation}.

            Return ONLY valid JSON format with this structure:
            {{
                "itinerary": [
                    {{
                        "day": 1,
                        "title": "Day Title",
                        "activities": [
                            {{
                                "time": "10:00 AM",
                                "activity": "Activity Name",
                                "cost": 0,
                                "description": "Details",
                                "tips": "Tip"
                            }}
                        ]
                    }}
                ],
                "recommendations": {{ "safety_tips": [], "must_try_foods": [] }},
                "estimated_costs": {{ "transportation": 0, "accommodation": 0, "food": 0, "activities": 0, "miscellaneous": 0 }}
            }}
            """

            response = self.model.generate_content(prompt)
            return {'success': True, 'itinerary': self._clean_json(response.text)}
        
        except Exception as e:
            print(f"AI Error: {str(e)}")
            return self._generate_basic_itinerary(destination, days, budget, members)

    def _clean_json(self, text):
        """Robust JSON extraction from AI response"""
        try:
            # Remove Markdown code blocks
            match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
            if match:
                text = match.group(1)
            return json.loads(text)
        except:
            return None

    def _get_distance(self, origin, destination):
        if not self.maps_api_key: return 0
        try:
            url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin}&destinations={destination}&key={self.maps_api_key}"
            response = requests.get(url)
            data = response.json()
            if 'rows' in data and data['rows'][0]['elements'][0]['status'] == 'OK':
                return round(data['rows'][0]['elements'][0]['distance']['value'] / 1000, 2)
        except:
            pass
        return 0
    
    def _generate_basic_itinerary(self, destination, days, budget, members):
        # Fallback if AI fails
        return {
            'success': True,
            'itinerary': {
                'itinerary': [{'day': i, 'title': f'Explore {destination}', 'activities': [{'activity': 'Sightseeing', 'cost': 500}]} for i in range(1, days+1)],
                'estimated_costs': {'total': budget},
                'recommendations': {'safety_tips': ['Stay safe']}
            }
        }