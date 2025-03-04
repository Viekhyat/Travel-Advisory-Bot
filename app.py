from flask import Flask, request, jsonify
from flask_cors import CORS
import spacy
from datetime import datetime
import logging
from typing import Dict
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load spaCy model for NLP
try:
    nlp = spacy.load("en_core_web_sm")
    logger.info("Successfully loaded spaCy model")
except Exception as e:
    logger.error(f"Error loading spaCy model: {str(e)}")
    raise

class TravelAdvisor:
    def __init__(self, cities_csv_path: str = 'cities.csv', states_csv_path: str = 'states.csv'):
        """
        Initialize TravelAdvisor with data from CSV files.
        
        CSV file structures:
        cities.csv: city,state,travel_restrictions,vaccination_requirements,culture,
                   transportation,weather_summer,weather_monsoon,weather_winter
        states.csv: state,capital,major_cities,tourist_attractions,culture,best_time_to_visit
        """
        self.cities_info: Dict[str, Dict] = {}
        self.states_info: Dict[str, Dict] = {}
        
        self._load_cities_data(cities_csv_path)
        self._load_states_data(states_csv_path)

    def _load_cities_data(self, csv_path: str) -> None:
        """Load cities data from CSV file."""
        try:
            # Specify encoding='ISO-8859-1' to handle special characters
            df = pd.read_csv(csv_path, encoding='ISO-8859-1')
            for _, row in df.iterrows():
                city_data = {
                    'state': row['state'],
                    'travel_restrictions': row['travel_restrictions'],
                    'vaccination_requirements': row['vaccination_requirements'],
                    'culture': row['culture'],
                    'transportation': row['transportation'],
                    'weather': {
                        'summer': row['weather_summer'],
                        'monsoon': row['weather_monsoon'],
                        'winter': row['weather_winter']
                    }
                }
                self.cities_info[row['city'].lower()] = city_data
            logger.info(f"Successfully loaded data for {len(self.cities_info)} cities")
        except Exception as e:
            logger.error(f"Error loading cities data: {str(e)}")
            raise

    def _load_states_data(self, csv_path: str) -> None:
        """Load states data from CSV file."""
        try:
            # Specify encoding='ISO-8859-1' to handle special characters
            df = pd.read_csv(csv_path, encoding='ISO-8859-1')
            for _, row in df.iterrows():
                state_data = {
                    'capital': row['capital'],
                    'major_cities': row['major_cities'].split('|'),  # Assuming cities are pipe-separated
                    'tourist_attractions': row['tourist_attractions'].split('|'),
                    'culture': row['culture'],
                    'best_time_to_visit': row['best_time_to_visit']
                }
                self.states_info[row['state'].lower()] = state_data
            logger.info(f"Successfully loaded data for {len(self.states_info)} states")
        except Exception as e:
            logger.error(f"Error loading states data: {str(e)}")
            raise

    def get_city_info(self, city: str, info_type: str) -> str:
        """Get specific information about a city."""
        city = city.lower()
        if city in self.cities_info:
            if info_type == 'weather':
                weather_info = self.cities_info[city]['weather']
                return f"""
                Weather in {city.title()}:
                Summer: {weather_info['summer']}
                Monsoon: {weather_info['monsoon']}
                Winter: {weather_info['winter']}
                """
            return self.cities_info[city].get(info_type, 
                   "Specific information not available for this aspect of the city.")
        return f"Information about {city.title()} is not available."

    def get_state_info(self, state: str) -> Dict:
        """Get information about a state."""
        state = state.lower()
        return self.states_info.get(state, {})

    def process_query(self, message: str) -> str:
        """Process user query and return relevant travel information."""
        doc = nlp(message.lower())
        
        city = None
        state = None
        info_type = None
        
        for ent in doc.ents:
            if ent.label_ == "GPE":  # Geopolitical entity
                if ent.text.lower() in self.cities_info:
                    city = ent.text.lower()
                elif ent.text.lower() in self.states_info:
                    state = ent.text.lower()
        
        # Identify type of information requested
        if "weather" in message:
            info_type = "weather"
        elif "travel restrictions" in message:
            info_type = "travel_restrictions"
        elif "vaccination" in message:
            info_type = "vaccination_requirements"
        elif "culture" in message:
            info_type = "culture"
        elif "transportation" in message:
            info_type = "transportation"
        elif "tourist attractions" in message:
            info_type = "tourist_attractions"
        
        # Generate response based on identified city or state and info type
        if city:
            if info_type:
                return self.get_city_info(city, info_type)
            else:
                return f"Here is some general information about {city.title()}: {self.cities_info[city]}"
        
        elif state:
            state_info = self.get_state_info(state)
            if state_info:
                # Provide general information if no specific info type is requested
                if not info_type:
                    return f"Here is some general information about {state.title()}: Capital: {state_info['capital']}, Major Cities: {', '.join(state_info['major_cities'])}, Tourist Attractions: {', '.join(state_info['tourist_attractions'])}, Culture: {state_info['culture']}, Best Time to Visit: {state_info['best_time_to_visit']}"
                return f"Here is some specific information about {state.title()}: {state_info.get(info_type, 'Information not available.')}"
        
        return "Sorry, I couldn't understand the location or information type in your query. Please ask about a city or state and specify the type of information you're interested in, such as weather, culture, or tourist attractions."


# Example CSV content for cities.csv
example_cities_csv = """city,state,travel_restrictions,vaccination_requirements,culture,transportation,weather_summer,weather_monsoon,weather_winter
delhi,Delhi,"Current Status: Open for tourism\nNo specific travel restrictions in place\nMasks recommended in crowded areas","COVID-19 vaccination recommended but not mandatory\nRoutine vaccinations advised","Delhi blends old and new with historical sites like Red Fort","Metro network\nBuses\nAuto-rickshaws","Very hot (April-June) 35-45°C","Humid (July-September) 25-35°C","Cool (December-February) 5-25°C"
mumbai,Maharashtra,"Current Status: Open for tourism\nNo specific restrictions","COVID-19 vaccination recommended\nStandard vaccinations advised","Financial capital with attractions like Gateway of India","Local trains\nMetro\nBEST buses","Hot and humid (March-May) 25-35°C","Heavy rainfall (June-September) 24-30°C","Pleasant (November-February) 15-30°C"
"""

# Example CSV content for states.csv
example_states_csv = """state,capital,major_cities,tourist_attractions,culture,best_time_to_visit
maharashtra,Mumbai,"Mumbai|Pune|Nagpur|Nashik","Ajanta Caves|Ellora Caves|Mahabaleshwar","Rich Marathi culture with Lavani dance and festivals","October to March"
rajasthan,Jaipur,"Jaipur|Udaipur|Jodhpur|Jaisalmer","Amber Fort|City Palace|Lake Palace|Thar Desert","Vibrant culture with Ghoomar dance and Desert Festival","October to March"
"""

# Create CSV files if they don't exist (for demonstration)
def create_example_csv_files():
    if not os.path.exists('cities.csv'):
        with open('cities.csv', 'w', encoding='ISO-8859-1') as f:
            f.write(example_cities_csv)
        logger.info("Created example cities.csv file")
    
    if not os.path.exists('states.csv'):
        with open('states.csv', 'w', encoding='ISO-8859-1') as f:
            f.write(example_states_csv)
        logger.info("Created example states.csv file")

# Initialize the travel advisor
create_example_csv_files()
travel_advisor = TravelAdvisor()

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        logger.info(f"Received query: {user_message}")
        response = travel_advisor.process_query(user_message)
        logger.info(f"Sending response for query")
        
        return jsonify({
            "reply": response,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == "__main__":
    app.run(port=8075 ,debug=True)
