import google.generativeai as genai
from config import Config
import json
import requests
import re

class AIService:
    def __init__(self):
        if Config.GEMINI_API_KEY:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            # FIXED: Correct model name for 2025
            self.model = genai.GenerativeModel('models/gemini-2.5-flash')
        self.maps_api_key = Config.GOOGLE_MAPS_API_KEY
    
    def generate_itinerary(self, destination, budget, members, days, from_loc, accommodation, interests):
        try:
            prompt = f"""
            Plan a {days}-day trip to {destination} from {from_loc}.
            Budget: ₹{budget} total for {members} people.
            Interests: {interests}. Stay: {accommodation}.

            Return JSON ONLY:
            {{
                "itinerary": [
                    {{
                        "day": 1,
                        "title": "Day Title",
                        "activities": [
                            {{ "time": "10am", "activity": "Name", "cost": 500, "description": "desc", "tips": "tip" }}
                        ]
                    }}
                ],
                "recommendations": {{ "safety_tips": [], "must_try_foods": [] }},
                "estimated_costs": {{ "transportation": 0, "accommodation": 0, "food": 0, "activities": 0, "miscellaneous": 0 }}
            }}
            """
            
            response = self.model.generate_content(prompt)
            # Robust JSON cleaning
            text = response.text
            match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
            if match: text = match.group(1)
            
            return {'success': True, 'itinerary': json.loads(text)}
        except Exception as e:
            print(f"AI Error: {e}")
            return self._fallback(destination, days, budget)

    def _fallback(self, dest, days, budget):
        return {
            'success': True, 
            'itinerary': {
                'itinerary': [{'day': i, 'title': f'Visit {dest}', 'activities': [{'activity': 'Sightseeing', 'cost': 0}]} for i in range(1, days+1)],
                'estimated_costs': {'total': budget},
                'recommendations': {}
            }
        }