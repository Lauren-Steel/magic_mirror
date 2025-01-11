import tkinter as tk
from datetime import datetime
import requests
from config import get_config
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
import pytz
from PIL import Image, ImageTk, ImageOps

# SCOPES defines the level of access to the Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

weather_icon_map = {
    # Thunderstorm group
    "thunderstorm with light rain": "thunderstorm.png",
    "thunderstorm with rain": "thunderstorm.png",
    "thunderstorm with heavy rain": "thunderstorm.png",
    "light thunderstorm": "thunderstorm.png",
    "thunderstorm": "thunderstorm.png",
    "heavy thunderstorm": "thunderstorm.png",
    "ragged thunderstorm": "thunderstorm.png",
    "thunderstorm with light drizzle": "thunderstorm.png",
    "thunderstorm with drizzle": "thunderstorm.png",
    "thunderstorm with heavy drizzle": "thunderstorm.png",

    # Drizzle group
    "light intensity drizzle": "rainy.png",
    "drizzle": "rainy.png",
    "heavy intensity drizzle": "rainy.png",
    "light intensity drizzle rain": "rainy.png",
    "drizzle rain": "rainy.png",
    "heavy intensity drizzle rain": "rainy.png",
    "shower rain and drizzle": "rainy.png",
    "heavy shower rain and drizzle": "rainy.png",
    "shower drizzle": "rainy.png",

    # Rain group
    "light rain": "rainy.png",
    "moderate rain": "rainy.png",
    "heavy intensity rain": "rainy.png",
    "very heavy rain": "rainy.png",
    "extreme rain": "rainy.png",
    "freezing rain": "rainy.png",
    "light intensity shower rain": "rainy.png",
    "shower rain": "rainy.png",
    "heavy intensity shower rain": "rainy.png",
    "ragged shower rain": "rainy.png",

    # Snow group
    "light snow": "snow.png",
    "snow": "snow.png",
    "heavy snow": "snow.png",
    "sleet": "snow.png",
    "light shower sleet": "snow.png",
    "shower sleet": "snow.png",
    "light rain and snow": "snow.png",
    "rain and snow": "snow.png",
    "light shower snow": "snow.png",
    "shower snow": "snow.png",
    "heavy shower snow": "snow.png",

    # Atmosphere group
    "mist": "fog.png",
    "smoke": "cloudy.png",
    "haze": "cloudy.png",
    "sand/dust whirls": "sandstorm.png",
    "fog": "fog.png",
    "sand": "sandstorm.png",
    "dust": "sandstorm.png",
    "volcanic ash": "sandstorm.png",
    "squalls": "snow.png",
    "tornado": "tornado.png",

    # Clear and Clouds group
    "clear sky": "default_sun.png",
    "few clouds": "partly_cloudy.png",
    "scattered clouds": "partly_clouds.png",
    "broken clouds": "cloudy.png",
    "overcast clouds": "cloudy.png"
}

def authenticate_google_calendar():
    """Authenticate with Google Calendar API."""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '/home/capstone/secure_credentials/googlecal_credentials.json', SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def fetch_calendar_events():
    """Fetch upcoming events from Google Calendar."""
    try:
        creds = authenticate_google_calendar()
        service = build('calendar', 'v3', credentials=creds)

        # Get the current time in Eastern Time
        eastern_tz = pytz.timezone("America/New_York")
        now_eastern = datetime.now(eastern_tz)

        # Convert to UTC for the Google Calendar API
        now_utc = now_eastern.astimezone(pytz.utc)
        now = now_utc.isoformat()  # ISO format for the API

        # Fetch events starting from now
        events_result = service.events().list(
            calendarId='primary', timeMin=now,
            maxResults=5, singleEvents=True,
            orderBy='startTime'
        ).execute()

        # Safely fetch items from the API result
        events = events_result.get('items', [])
        print(f"Fetched events: {events}")  # Debugging line
        return events
    except Exception as e:
        # Explicitly log the error and ensure empty list is returned
        print(f"Error fetching calendar events: {e}")
        return []


def fetch_weather(api_key, lat, lon, units):
    """Fetch weather data from OpenWeatherMap API."""
    try:
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {"lat": lat, "lon": lon, "units": units, "appid": api_key}
        print(f"Fetching weather with params: {params}")  # Debugging line
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
        print(f"Error fetching weather: {e}")
        return None

def update_time(time_label, time_format):
    """Update the time displayed on the label."""
    now = datetime.now()
    time_string = now.strftime("%H:%M" if time_format == 24 else "%I:%M %p")
    date_string = now.strftime("%A, %B %d, %Y")
    time_label.config(text=f"{time_string}\n{date_string}")
    time_label.after(1000, update_time, time_label, time_format)

def recolor_icon_to_white(icon_path):
    """Recolor the icon to white for better visibility on black background."""
    img = Image.open(icon_path).convert("RGBA")
    data = img.getdata()
    new_data = []
    for item in data:
        # Replace non-transparent pixels with white
        if item[3] > 0:  # Alpha > 0 (not transparent)
            new_data.append((255, 255, 255, item[3]))  # White with original transparency
        else:
            new_data.append(item)  # Keep transparency
    img.putdata(new_data)
    return img

def update_weather(weather_label, weather_icon_label, config):
    """Fetch and update weather data and icon on the label."""
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

        # Update the weather icon
        description = weather["description"].lower()
        icon_filename = weather_icon_map.get(description, "default_sun.png")  # Fallback to default icon
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "weather_icons", icon_filename)
            img = recolor_icon_to_white(icon_path)  # Recolor dynamically
            img = img.resize((50, 50))  # Resize icon
            icon = ImageTk.PhotoImage(img)
            weather_icon_label.config(image=icon)
            weather_icon_label.image = icon  # Keep reference to avoid garbage collection
        except Exception as e:
            print(f"Error loading weather icon: {e}")
    else:
        weather_label.config(text="Error fetching weather data.")
    weather_label.after(600000, update_weather, weather_label, weather_icon_label, config)  # Update every 10 minutes


def update_calendar(calendar_label):
    """Update the calendar events displayed on the label."""
    events = fetch_calendar_events()
    if events:
        calendar_text = "Upcoming Events:\n"
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            start_time = datetime.fromisoformat(start).strftime('%Y-%m-%d %H:%M')
            calendar_text += f"{start_time}: {event['summary']}\n"
    else:
        calendar_text = "No upcoming events found."
    calendar_label.config(text=calendar_text)
    calendar_label.after(600000, update_calendar, calendar_label)

def main():
    config = get_config()

    # Create main window
    root = tk.Tk()
    root.title("Smart Display")
    root.geometry("1920x1080")  # Adjust as per your display
    root.configure(bg="black")

    # Time Widget
    time_label = tk.Label(
        root, text="", font=("Times New Roman", 60, "bold"), fg="white", bg="black", borderwidth=2, relief="solid"
    )
    time_label.pack(anchor="w", pady=10, padx=20)
    update_time(time_label, config["time_format"])

    # Weather Widget
    weather_label = tk.Label(
        root, text="Loading weather...", font=("Times New Roman", 30), fg="white", bg="black", borderwidth=2, relief="solid"
    )
    weather_label.pack(anchor="w", pady=10, padx=20)

    # Weather Icon
    weather_icon_label = tk.Label(root, bg="black")
    weather_icon_label.pack(anchor="w", padx=20, pady=5)

    # Corrected call to update_weather
    update_weather(weather_label, weather_icon_label, config)

    # Calendar Widget
    calendar_label = tk.Label(
        root, text="Loading calendar...", font=("Times New Roman", 20, "italic"), fg="white", bg="black", justify="left", anchor="w", borderwidth=2, relief="solid"
    )
    calendar_label.pack(anchor="w", pady=10, padx=20)
    update_calendar(calendar_label)

    # Run the tkinter event loop
    root.mainloop()

if __name__ == "__main__":
    main()
