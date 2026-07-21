from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain.agents import create_agent
import os
import requests
from langgraph.checkpoint.postgres import PostgresSaver

load_dotenv()

DB_URI = os.getenv("SUPABASE_DB_URI")

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
    response = requests.get(base_url, params=params)
    data = response.json()
    temperature_celsius = data['main']['temp']
    temperature_fahrenheit = temperature_celsius * 9/5 + 32
    return data, {'temperature_fahrenheit': temperature_fahrenheit}

def get_location():
    """Get user's current location. Use this when the user asks about weather."""
    response = requests.get(
        "https://ipapi.co/json/",
        headers={"User-Agent": "weather-agent/0.1"},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    return f"{data.get('city')}, {data.get('country_name')}"

# Initialize the current Gemini Flash model
llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    temperature=0.7,
)


system_prompt = """
You are a helpful weather assistant. 
YOUR WORKFLOW:
1. If the user asks about weather WITHOUT specifying a location, you MUST:
   - First call get_location() to find their location
   - Then call get_weather(city) with that location
   
2. If the user provides a city, call get_weather(city) directly.

3. Use your knowledge to determine which temperature unit is standard for the given location.

4. Present the weather information including temperature, condition, wind speed, and any other relevant details.

"""
def get_message_text(message):
    """Return only user-facing text from a LangChain message."""
    if isinstance(message.content, str):
        return message.content

    return "\n".join(
        block["text"]
        for block in message.content
        if isinstance(block, dict)
        and block.get("type") == "text"
        and block.get("text")
    )


# We execute this line of code when the user runs main.py
if __name__ == "__main__":
    if not DB_URI:
        raise RuntimeError("SUPABASE_DB_URI is missing from your .env file.")

    try:
        with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
            # Creates the checkpoint tables when running against a new database.
            checkpointer.setup()

            agent = create_agent(
                model=llm,
                tools=[get_weather, get_location],
                system_prompt=system_prompt,
                checkpointer=checkpointer,
            )

    except KeyboardInterrupt:
        print("\n\nAgent: Goodbye!")
