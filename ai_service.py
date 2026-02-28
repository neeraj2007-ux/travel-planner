"""
AI Service for Trip Itinerary Generation using Gemini API
"""
import google.generativeai as genai
from config import Config
import json

class AIService:
    """Handle AI-powered itinerary generation using Google Gemini"""
    
    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def generate_itinerary(self, destination, budget, members, days, from_location, accommodation, interests):
        """
        Generate AI-powered travel itinerary
        
        Args:
            destination (str): Travel destination
            budget (float): Total budget
            members (int): Number of travelers
            days (int): Trip duration
            from_location (str): Starting location
            accommodation (str): Accommodation preference
            interests (str): Travel interests
            
        Returns:
            dict: Generated itinerary with day-wise plans
        """
        try:
            per_person_budget = budget / members
            
            prompt = f"""You are an expert travel planner specializing in budget-friendly student trips.

Create a detailed {days}-day itinerary for a trip to {destination}.

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
            
            # Extract JSON from response
            response_text = response.text
            
            # Clean up the response (remove markdown code blocks if present)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            # Parse JSON
            itinerary_data = json.loads(response_text.strip())
            
            return {
                'success': True,
                'itinerary': itinerary_data
            }
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            # Fallback to basic itinerary
            return self._generate_basic_itinerary(destination, days, budget, members)
        
        except Exception as e:
            print(f"Error generating itinerary: {str(e)}")
            return self._generate_basic_itinerary(destination, days, budget, members)
    
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
    
    def get_destination_info(self, destination):
        """
        Get detailed information about a destination
        
        Args:
            destination (str): Destination name
            
        Returns:
            dict: Destination information
        """
        try:
            prompt = f"""Provide a brief overview of {destination} as a travel destination.
            
Include:
1. Best time to visit
2. Top 5 attractions
3. Average costs
4. Local cuisine highlights
5. Transportation options
6. Safety information

Keep it concise and student-friendly."""

            response = self.model.generate_content(prompt)
            
            return {
                'success': True,
                'info': response.text
            }
            
        except Exception as e:
            print(f"Error getting destination info: {str(e)}")
            return {
                'success': False,
                'info': 'Unable to fetch destination information'
            }
    
    def optimize_route(self, places):
        """
        Optimize visiting order of multiple places
        
        Args:
            places (list): List of places to visit
            
        Returns:
            dict: Optimized route
        """
        try:
            prompt = f"""Given these places to visit: {', '.join(places)}
            
Suggest the most efficient order to visit them to minimize travel time and costs.
Provide brief reasoning for the order."""

            response = self.model.generate_content(prompt)
            
            return {
                'success': True,
                'optimized_route': response.text
            }
            
        except Exception as e:
            print(f"Error optimizing route: {str(e)}")
            return {
                'success': False,
                'optimized_route': places
            }