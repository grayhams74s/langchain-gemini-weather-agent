# LangChain Gemini Weather Agent

A command-line AI weather assistant built with Python, LangChain, and Google
Gemini. The agent uses tool calling to retrieve live weather data and can
automatically estimate the user's location when no city is provided.

## Features

- Natural-language weather questions
- Google Gemini integration through LangChain
- Real-time weather data from OpenWeather
- IP-based location lookup through ipapi
- Agent tool calling that selects the appropriate workflow
- Environment-variable protection for API keys

## How It Works

When the user enters a question, the Gemini-powered LangChain agent decides
which tool to call:

1. If a city is included, the agent calls `get_weather()` directly.
2. If no city is included, it calls `get_location()` first and then passes the
   detected location to `get_weather()`.

## Tech Stack

- Python
- LangChain
- Google Gemini
- OpenWeather API
- ipapi

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/langchain-gemini-weather-agent.git
cd langchain-gemini-weather-agent
```

### 2. Create a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install the dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure the API keys

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY="your_google_gemini_api_key"
OPENWEATHER_API_KEY="your_openweather_api_key"
```

You can create a Gemini key in
[Google AI Studio](https://aistudio.google.com/app/apikey) and an OpenWeather
key from the [OpenWeather API](https://openweathermap.org/api).

Never commit the `.env` file. It is excluded by the included `.gitignore`.

### 5. Run the agent

```bash
python main.py
```

Example:

```text
Enter your query: What is the weather in Manila?
```

You can also omit the city:

```text
Enter your query: What is the weather where I am?
```

## Project Structure

```text
.
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Privacy Note

The automatic-location feature sends the user's public IP address to ipapi to
estimate their city and country. It does not access precise GPS coordinates.

## Future Improvements

- Add friendly error handling for invalid cities and API failures
- Include humidity, wind speed, and forecast data
- Add automated tests
- Build a web interface

