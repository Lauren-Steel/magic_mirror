import tkinter as tk
from datetime import datetime
import requests
from config import get_config
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle

# SCOPES defines the level of access to the Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def authenticate_google_calendar():
    """Authenticate with Google Calendar API."""
    creds = None
    # Token storage to avoid re-authenticating every time
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If no valid credentials, authenticate via OAuth
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save credentials for future use
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def fetch_calendar_events():
    """Fetch upcoming events from Google Calendar."""
    try:
        creds = authenticate_google_calendar()
        service = build('calendar', 'v3', credentials=creds)
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = service.events().list(
            calendarId='primary', timeMin=now,
            maxResults=5, singleEvents=True,
            orderBy='startTime').execute()
        events = events_result.get('items', [])
        return events
    except Exception as e:
        print(f"Error fetching calendar events: {e}")
        return []

def fetch_weather(api_key, lat, lon, units):
    """Fetch weather data from OpenWeatherMap API."""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {"lat": lat, "lon": lon, "units": units, "appid": api_key}
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
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
    time_string = now.strftime("%H:%M:%S" if time_format == 24 else "%I:%M:%S %p")
    time_label.config(text=f"Time: {time_string}")
    time_label.after(1000, update_time, time_label, time_format)

def update_weather(weather_label, config):
    """Fetch and update weather data on the label."""
    weather = fetch_weather(
        config["weather"]["api_key"], config["weather"]["lat"], config["weather"]["lon"], config["units"]
    )
    if weather:
        weather_text = (
            f"Weather in {weather['location']}:\n"
            f"{weather['temperature']}°C, {weather['description']}"
        )
        weather_label.config(text=weather_text)
    else:
        weather_label.config(text="Error fetching weather data.")
    weather_label.after(600000, update_weather, weather_label, config)  # Update every 10 minutes

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
    calendar_label.after(600000, update_calendar, calendar_label)  # Update every 10 minutes

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

    # Calendar Widget
    calendar_label = tk.Label(root, text="Loading calendar...", font=("Helvetica", 18), fg="white", bg="black", justify="left", anchor="w")
    calendar_label.pack(pady=20, padx=20, anchor="w")
    update_calendar(calendar_label)

    # Run the tkinter event loop
    root.mainloop()

if __name__ == "__main__":
    main()