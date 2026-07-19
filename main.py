from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain.agents import create_agent
import os
import requests


load_dotenv()

def get_weather(city: str):
    """Get weather for a given city"""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }

    "So we make this request. This comes from request Library."
    "So we make a request URL by sending this parameters."
    response = requests.get(base_url, params=params)
    data = response.json()
    return data

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

"""
agent = create_agent(
    model=llm,
    tools=[get_weather, get_location],
    system_prompt=system_prompt
)

# We execute this line of code when the user runs main.py
if __name__ == "__main__":
    user_query = input("Enter your query: ")

    # response1 = llm.invoke("How is the weather in Rome?")
    response1 = agent.invoke(
        {"messages": [{'role': 'user',
                    'content':user_query}]})
    print(response1['messages'][-1].content)
