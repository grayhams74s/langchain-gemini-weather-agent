from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain.agents import create_agent
import os
import requests
from langgraph.checkpoint.sqlite import SqliteSaver
import ast
import atexit
from flask import session

load_dotenv()

def get_weather(city: str):
    """Get weather for a given city.
    Return the temperature_fahrenheit value in Fahrenheit label for locations such as US, Liberia, Burma"""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q":city,
        "appid":api_key,
        'units': 'metric'
    }
    response = requests.get(base_url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()
    temperature_celsius = data['main']['temp']
    temperature_fahrenheit = temperature_celsius * 9/5 + 32
    return data, {'temperature_fahrenheit': temperature_fahrenheit}

def get_location():
    """Get user's current location. Use this when the user asks about weather."""

    user_location = session.get("user_location")
    if not user_location:
        return (
            "The user's browser location is unavailable. Ask the user to allow "
            "location access or provide a city. Do not call get_weather yet."
        )

    lat = float(user_location["lat"])
    lon = float(user_location["lon"])
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return "The user's browser returned invalid coordinates. Ask for a city."

    response = requests.get(
        "https://nominatim.openstreetmap.org/reverse",
        params={"lat": lat, "lon": lon, "format": "jsonv2"},
        headers={"User-Agent": "WeatherAssistant/1.0"},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    address = data.get("address", {})
    city = next(
        (
            address.get(key)
            for key in ("city", "municipality", "town", "city_district", "county", "state")
            if address.get(key)
        ),
        "Unknown location",
    )
    country = address.get("country", "")
    return f"{city}, {country}".strip(", ")

# Initialize the current Gemini Flash model
llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0.7,
    timeout=30,
    max_retries=1,
)


system_prompt = """
You are a helpful weather assistant. 
YOUR WORKFLOW:
1. If the user asks about weather WITHOUT specifying a location, you MUST:
   - First call get_location() to find their location
   - Then call get_weather(city) with that location
   - If get_location says browser location is unavailable, ask the user to allow
     location access or provide a city. Do not call get_weather.
   
2. If the user provides a city, call get_weather(city) directly.

3. Use your knowledge to determine which temperature unit is standard for the given location.

4. Present the weather information including temperature, condition, wind speed, and any other relevant details.

"""
def get_message_text(message):
    """Return only user-facing text from a LangChain message."""
    content = getattr(message, "content", message)

    if isinstance(content, str):
        # Some providers serialize structured content blocks as a string.
        if content.lstrip().startswith("["):
            try:
                content = ast.literal_eval(content)
            except (ValueError, SyntaxError):
                return content.replace("*", "")
        else:
            return content.replace("*", "")

    if isinstance(content, list):
        text_blocks = [
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("text")
        ]
        if text_blocks:
            return "\n".join(text_blocks).replace("*", "")

    return str(content).replace("*", "")


connection = SqliteSaver.from_conn_string("checkpoints.db")
checkpointer = connection.__enter__()
atexit.register(connection.__exit__, None, None, None)

agent = create_agent(
    model=llm,
    tools=[get_weather, get_location],
    system_prompt=system_prompt,
    checkpointer=checkpointer,
)
