# config.py

config = {
    "address": "localhost",  # Address to bind the application
    "port": 8080,  # Port number
    "language": "en",
    "units": "metric",  # Units for weather ("metric" for Celsius, "imperial" for Fahrenheit)
    "weather": {
        "api_key": "YOUR_OPENWEATHERMAP_API_KEY",  # Replace with your OpenWeatherMap API key
        "lat": 40.776676,  # Latitude for your location
        "lon": -73.971321,  # Longitude for your location
    },
    "time_format": 24,  # 24-hour or 12-hour time format
}

def get_config():
    return config

