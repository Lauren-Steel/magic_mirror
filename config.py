# config.py

config = {
    "address": "localhost",  # Address to bind the application
    "port": 8080,  # Port number
    "language": "en",
    "units": "metric",  # Units for weather ("metric" for Celsius, "imperial" for Fahrenheit)
    "weather": {
        "api_key": "2cf8cf9ed9af67c236990163ece2b97a",
        "lat": 51.5074,
        "lon": -0.1278,
        "units": "metric"
    },
    "time_format": 24,  # 24-hour or 12-hour time format
}

def get_config():
    return config

