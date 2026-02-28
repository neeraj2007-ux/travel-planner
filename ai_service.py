"""
AI Service for Trip Itinerary Generation using Gemini API
"""
import google.generativeai as genai
from config import Config
import json
import requests

class AIService:
    """Handle AI-powered itinerary generation using Google Gemini"""
    
    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')
        self.maps_api_key = Config.GOOGLE_MAPS_API_KEY
    
    def generate_itinerary(self, destination, budget, members, days, from_location, accommodation, interests):
        """Generate AI-powered travel itinerary"""
        try:
            per_person_budget = budget / members
            
            # Calculate distance using Google Maps
            distance_km = self._get_distance(from_location, destination)
            
            prompt = f"""You are an expert travel planner specializing in budget-friendly student trips.

Create a detailed {days}-day itinerary for a trip to {destination} starting from {from_location} ({distance_km} km away).

TRIP DETAILS:
- Destination: {destination}
- Starting from: {from_location}
- Total Budget: ₹{budget:,} ({members} travelers = ₹{per_person_budget:,} per person)
- Duration: {days} days
- Accommodation: {accommodation}
- Interests: {interests}

BUDGET ALLOCATION:
- Transportation: 30%
- Accommodation: 35%
- Food: 20%
- Activities: 10%
- Miscellaneous: 5%

Please provide:
1. Day-wise detailed itinerary
2. Specific places to visit with descriptions
3. Estimated costs for each activity
4. Budget-friendly food recommendations
5. Travel tips and money-saving advice
6. Best time to visit each attraction

Format the response as a JSON object with this structure:
{{
    "itinerary": [
        {{
            "day": 1,
            "title": "Day 1 - Arrival and Local Exploration",
            "activities": [
                {{
                    "time": "9:00 AM",
                    "activity": "Breakfast at local cafe",
                    "location": "Specific place name",
                    "cost": 200,
                    "description": "Brief description",
                    "tips": "Money-saving tips"
                }}
            ],
            "total_day_cost": 1500
        }}
    ],
    "recommendations": {{
        "best_restaurants": ["Restaurant 1", "Restaurant 2"],
        "free_attractions": ["Place 1", "Place 2"],
        "local_transport_tips": "How to get around cheaply",
        "must_try_foods": ["Food 1", "Food 2"],
        "safety_tips": ["Tip 1", "Tip 2"]
    }},
    "estimated_costs": {{
        "transportation": 9000,
        "accommodation": 10500,
        "food": 6000,
        "activities": 3000,
        "miscellaneous": 1500
    }}
}}

Make it practical, budget-friendly, and exciting for students!"""

            # Generate content using Gemini
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Extract JSON from response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            itinerary_data = json.loads(response_text.strip())
            return {'success': True, 'itinerary': itinerary_data}
        
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            return self._generate_basic_itinerary(destination, days, budget, members)
        
        except Exception as e:
            print(f"Error generating itinerary: {str(e)}")
            return self._generate_basic_itinerary(destination, days, budget, members)
    
    def _get_distance(self, origin, destination):
        """Get distance between origin and destination using Google Maps"""
        try:
            url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin}&destinations={destination}&key={self.maps_api_key}"
            response = requests.get(url)
            data = response.json()
            
            # Validate response safely
            if 'rows' in data and len(data['rows']) > 0:
                elements = data['rows'][0].get('elements', [])
                if len(elements) > 0 and elements[0].get('status') == 'OK':
                    distance_meters = elements[0]['distance']['value']
                    return round(distance_meters / 1000, 2)
            
            return 0
        except Exception as e:
            print(f"Error fetching distance from Google Maps: {str(e)}")
            return 0
    
    def _generate_basic_itinerary(self, destination, days, budget, members):
        """Fallback basic itinerary if AI generation fails"""
        per_person_budget = budget / members
        itinerary = []
        for day in range(1, days + 1):
            itinerary.append({
                'day': day,
                'title': f'Day {day} - Exploring {destination}',
                'activities': [
                    {
                        'time': '9:00 AM',
                        'activity': 'Breakfast at local cafe',
                        'location': destination,
                        'cost': 200,
                        'description': 'Start your day with local breakfast',
                        'tips': 'Look for student discounts'
                    },
                    {
                        'time': '11:00 AM',
                        'activity': 'Visit main attractions',
                        'location': destination,
                        'cost': 500,
                        'description': 'Explore popular tourist spots',
                        'tips': 'Book tickets online for discounts'
                    },
                    {
                        'time': '2:00 PM',
                        'activity': 'Lunch at budget restaurant',
                        'location': destination,
                        'cost': 300,
                        'description': 'Try local cuisine',
                        'tips': 'Ask locals for recommendations'
                    },
                    {
                        'time': '4:00 PM',
                        'activity': 'Cultural exploration',
                        'location': destination,
                        'cost': 300,
                        'description': 'Immerse in local culture',
                        'tips': 'Many museums offer free entry days'
                    },
                    {
                        'time': '7:00 PM',
                        'activity': 'Dinner and evening stroll',
                        'location': destination,
                        'cost': 400,
                        'description': 'End the day with local food',
                        'tips': 'Street food is cheaper and authentic'
                    }
                ],
                'total_day_cost': 1700
            })
        
        return {
            'success': True,
            'itinerary': {
                'itinerary': itinerary,
                'recommendations': {
                    'best_restaurants': ['Local cafes', 'Street food stalls'],
                    'free_attractions': ['Public parks', 'Historic areas'],
                    'local_transport_tips': 'Use public transport or walk when possible',
                    'must_try_foods': ['Local specialties'],
                    'safety_tips': ['Stay in groups', 'Keep valuables safe']
                },
                'estimated_costs': {
                    'transportation': budget * 0.30,
                    'accommodation': budget * 0.35,
                    'food': budget * 0.20,
                    'activities': budget * 0.10,
                    'miscellaneous': budget * 0.05
                }
            }
        }