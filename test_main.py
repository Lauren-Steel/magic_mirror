import tkinter as tk
from datetime import datetime
import requests
from config import get_config

def fetch_weather(api_key, lat, lon, units):
    try:
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {"lat": lat, "lon": lon, "units": units, "appid": api_key}
        print(f"Fetching weather with params: {params}")
        response = requests.get(url, params=params)
        print(f"Raw Response: {response.text}")  # Debugging line
        response.raise_for_status()
        data = response.json()
        print(f"Parsed Data: {data}")  # Debugging line
        weather = {
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"].capitalize(),
            "location": data["name"],
        }
        return weather
    except Exception as e:
        print(f"Error in fetch_weather: {e}")
        return None

def update_time(time_label, time_format):
    """Update the time displayed on the label."""
    now = datetime.now()
    time_string = now.strftime("%H:%M:%S" if time_format == 24 else "%I:%M:%S %p")
    time_label.config(text=f"Time: {time_string}")
    time_label.after(1000, update_time, time_label, time_format)

def update_weather(weather_label, config):
    weather = fetch_weather(
        config["weather"]["api_key"],
        config["weather"]["lat"],
        config["weather"]["lon"],
        config["weather"].get("units", "metric")
    )
    if weather:
        weather_text = (
            f"Weather in {weather['location']}:\n"
            f"{weather['temperature']}°C, {weather['description']}"
        )
        weather_label.config(text=weather_text)
    else:
        weather_label.config(text="Error fetching weather data.")
    weather_label.after(600000, update_weather, weather_label, config)

def main():
    config = get_config()

    # Create main window
    root = tk.Tk()
    root.title("Smart Display")

    # Configure full screen
    root.geometry("800x480")  # Adjust as per your display
    root.configure(bg="black")

    # Time Widget
    time_label = tk.Label(root, text="", font=("Helvetica", 48), fg="white", bg="black")
    time_label.pack(pady=20)
    update_time(time_label, config["time_format"])

    # Weather Widget
    weather_label = tk.Label(root, text="Loading weather...", font=("Helvetica", 24), fg="white", bg="black")
    weather_label.pack(pady=20)
    update_weather(weather_label, config)

    # Run the tkinter event loop
    root.mainloop()

if __name__ == "__main__":
    main()
