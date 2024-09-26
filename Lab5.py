import streamlit as st
import openai
import requests

# Set API Keys from Streamlit secrets
openai.api_key = st.secrets["openai"]  # Accessing OpenAI API key from Streamlit secrets
weather_api_key = st.secrets["weather"]  # Accessing OpenWeatherMap API key from Streamlit secrets

def get_weather(location="Syracuse, NY"):
    """Fetch weather data from OpenWeatherMap."""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={weather_api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "location": data["name"],
            "temperature": round(data["main"]["temp"], 2),
            "feels_like": round(data["main"]["feels_like"], 2),
            "temp_min": round(data["main"]["temp_min"], 2),
            "temp_max": round(data["main"]["temp_max"], 2),
            "humidity": round(data["main"]["humidity"], 2),
            "weather": data["weather"][0]["description"]
        }
    else:
        return {"error": "Could not retrieve weather data."}

def llm_tool(location):
    """Function to call OpenAI's API for clothing suggestions based on the weather."""
    if not location:
        location = "Syracuse, NY"  # Default location
    
    weather_data = get_weather(location)
    
    if 'error' in weather_data:
        return f"Error: {weather_data['error']}"
    
    # Prepare the weather details for the prompt
    weather_info = (f"The current weather in {weather_data['location']}:\n"
                    f"Temperature: {weather_data['temperature']}°C\n"
                    f"Feels Like: {weather_data['feels_like']}°C\n"
                    f"Min Temp: {weather_data['temp_min']}°C\n"
                    f"Max Temp: {weather_data['temp_max']}°C\n"
                    f"Humidity: {weather_data['humidity']}%\n"
                    f"Conditions: {weather_data['weather']}")
    
    # Prepare the prompt for OpenAI
    prompt = (f"Here is the weather information:\n"
              f"{weather_info}\n\n"
              f"Based on this weather, what are some appropriate clothing suggestions for today?")

    # Call OpenAI to get the response
    response = openai.Completion.create(
        engine="text-davinci-003",  # Specify the model you want to use
        prompt=prompt,
        max_tokens=100  # Adjust this if needed
    )
    
    clothing_suggestion = response.choices[0].text.strip()
    
    return f"{weather_info}\n\nClothing Suggestions: {clothing_suggestion}"

# Streamlit UI
st.title("Weather-Based Clothing Suggestion Bot")
user_input = st.text_input("Enter a city (leave blank for default - Syracuse, NY):")

if st.button("Get Clothing Suggestion"):
    suggestion = llm_tool(user_input)
    st.write(suggestion)
