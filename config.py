# config.py

config = {
    "address": "localhost",  # Address to bind the application
    "port": 8080,  # Port number
    "language": "en",
    "units": "metric",  # Units for weather ("metric" for Celsius, "imperial" for Fahrenheit)
    "weather": {
        "api_key": "045d9994e00389311caee651ccbe6f88",  # Replace with your OpenWeatherMap API key
        "lat": 44.230480,  # Latitude for your location
        "lon": -76.481247,  # Longitude for your location
        "units": "metric" # Celsius 
    },
    "time_format": 24,  # 24-hour or 12-hour time format
}

def get_config():
    return config

