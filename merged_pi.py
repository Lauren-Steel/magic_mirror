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

import ollama
import speech_recognition as sr
import pyttsx3
import threading

# --- Global Constants ---
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
modelname = "VirtualAssistant3.0"  # Name of your Ollama model

# Mapping for weather icons based on description
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

# --- Google Calendar Functions ---
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
        eastern_tz = pytz.timezone("America/New_York")
        now_eastern = datetime.now(eastern_tz)
        now_utc = now_eastern.astimezone(pytz.utc)
        now = now_utc.isoformat()
        events_result = service.events().list(
            calendarId='primary', timeMin=now,
            maxResults=5, singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        return events
    except Exception as e:
        print(f"Error fetching calendar events: {e}")
        return []

# --- Weather Functions ---
def fetch_weather(api_key, lat, lon, units):
    """Fetch weather data from OpenWeatherMap API."""
    try:
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {"lat": lat, "lon": lon, "units": units, "appid": api_key}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        weather = {
            "temperature": round(data["main"]["temp"]),
            "description": data["weather"][0]["description"].capitalize(),
            "location": data["name"],
        }
        return weather
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return None

def update_time_with_date(time_label, date_label, time_format):
    """Update the time and date displayed on the labels."""
    now = datetime.now()
    time_string = now.strftime("%H:%M" if time_format == 24 else "%I:%M %p")
    date_string = now.strftime("%A, %B %d")
    time_label.config(text=time_string)
    date_label.config(text=date_string)
    time_label.after(1000, update_time_with_date, time_label, date_label, time_format)

def recolor_icon_to_white(icon_path):
    """Recolor the icon to white for better visibility on black background."""
    img = Image.open(icon_path).convert("RGBA")
    data = img.getdata()
    new_data = []
    for item in data:
        if item[3] > 0:
            new_data.append((255, 255, 255, item[3]))
        else:
            new_data.append(item)
    img.putdata(new_data)
    return img

def update_weather(weather_label, weather_icon_label, description_label, config):
    """Fetch and update weather data and icon on the label."""
    weather = fetch_weather(
        config["weather"]["api_key"],
        config["weather"]["lat"],
        config["weather"]["lon"],
        config["weather"].get("units", "metric")
    )
    if weather:
        location = weather["location"]
        temperature = f"{weather['temperature']}°C"
        description = weather["description"].capitalize()
        weather_label.config(text=f"{location}\n{temperature}")
        description_label.config(text=description)
        description_key = weather["description"].lower()
        icon_filename = weather_icon_map.get(description_key, "default_sun.png")
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "weather_icons", icon_filename)
            img = recolor_icon_to_white(icon_path)
            img = img.resize((70, 70))
            icon = ImageTk.PhotoImage(img)
            weather_icon_label.config(image=icon)
            weather_icon_label.image = icon
        except Exception as e:
            print(f"Error loading weather icon: {e}")
    else:
        weather_label.config(text="Weather data unavailable")
        description_label.config(text="")
    weather_label.after(600000, update_weather, weather_label, weather_icon_label, description_label, config)

def update_calendar(calendar_label):
    """Fetch and update calendar events on the label."""
    events = fetch_calendar_events()
    if events:
        calendar_text = "Upcoming Events:\n"
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            start_time = datetime.fromisoformat(start).strftime('%Y-%m-%d %H:%M')
            calendar_text += f"{start_time}: {event.get('summary', 'No Title')}\n"
    else:
        calendar_text = "No upcoming events found."
    calendar_label.config(text=calendar_text)
    calendar_label.after(600000, update_calendar, calendar_label)

# --- Prompt Augmentation Functions ---
def get_api_context(config):
    """Fetch API data and format it for prompt augmentation, including current time."""
    current_time = datetime.now().strftime('%I:%M %p, %A, %B %d, %Y')
    time_info = f"Current Time: {current_time}."
    
    weather = fetch_weather(
        config["weather"]["api_key"],
        config["weather"]["lat"],
        config["weather"]["lon"],
        config["weather"].get("units", "metric")
    )
    if weather:
        weather_info = f"Weather: {weather['location']}, {weather['temperature']}°C, {weather['description']}."
    else:
        weather_info = "Weather data unavailable."
    
    events = fetch_calendar_events()
    if events:
        calendar_info = "Upcoming Events:\n"
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            start_time = datetime.fromisoformat(start).strftime('%Y-%m-%d %H:%M')
            calendar_info += f"{start_time}: {event.get('summary', 'No Title')}\n"
    else:
        calendar_info = "No upcoming events found."
        
    context = f"{time_info}\n{weather_info}\n{calendar_info}\n"
    return context

# --- LLM Conversation Functions ---
def update_text_widget(widget, text):
    """Thread-safe update of the text widget."""
    def inner():
        widget.insert(tk.END, text)
        widget.see(tk.END)
    widget.after(0, inner)

def llm_conversation_thread(llm_text_widget, config):
    client = ollama.Client()
    recognizer = sr.Recognizer()
    tts_engine = pyttsx3.init()
    
    while True:
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=5)
                update_text_widget(llm_text_widget, "\nListening for your prompt...")
                audio_data = recognizer.listen(source, timeout=None, phrase_time_limit=20)
            prompt = recognizer.recognize_google(audio_data).strip()
            update_text_widget(llm_text_widget, f"\nYou said: {prompt}")
            if prompt.lower() in ["stop", "exit"]:
                update_text_widget(llm_text_widget, "\nExiting Conversation.\n")
                break
            # Get API context and build the augmented prompt
            api_context = get_api_context(config)
            augmented_prompt = f"{api_context}\nUser Prompt: {prompt}"
            # (Augmented prompt is used for the LLM call but not shown in the text widget)
            response = client.generate(model=modelname, prompt=augmented_prompt)
            model_reply = response.response
            update_text_widget(llm_text_widget, f"\nAssistant Response: {model_reply}\n")
            tts_engine.say(model_reply)
            tts_engine.runAndWait()
        except sr.UnknownValueError:
            update_text_widget(llm_text_widget, "\nCould not understand audio. Please try again.\n")
        except sr.RequestError as e:
            update_text_widget(llm_text_widget, f"\nSpeech service error: {e}\n")
        except Exception as e:
            update_text_widget(llm_text_widget, f"\nError: {e}\n")


# --- Main GUI Setup ---
def main():
    config = get_config()

    root = tk.Tk()
    root.title("Smart Display with LLM")
    root.geometry("1920x1080")
    root.configure(bg="black")

    # Font definitions
    roboto_light = ("Roboto Light", 20)
    roboto_large = ("Roboto Light", 56)
    roboto_medium = ("Roboto Light", 32)

    # Top Right Section: Time, Date, Weather and Calendar
    time_label = tk.Label(root, text="", font=roboto_large, fg="white", bg="black", anchor="e", justify="right")
    time_label.place(relx=0.7, rely=0.02)
    
    date_label = tk.Label(root, text="", font=roboto_light, fg="white", bg="black", anchor="e", justify="right")
    date_label.place(relx=0.7, rely=0.1)
    update_time_with_date(time_label, date_label, config["time_format"])

    # Weather Section (placed below Date)
    weather_label = tk.Label(root, text="Loading weather...", font=roboto_medium, fg="white", bg="black", anchor="w", justify="left")
    weather_label.place(relx=0.7, rely=0.18)
    
    weather_icon_label = tk.Label(root, bg="black")
    weather_icon_label.place(relx=0.9, rely=0.18)  # Positioned to the right of weather_label
    
    description_label = tk.Label(root, text="", font=roboto_light, fg="white", bg="black", anchor="w", justify="left")
    description_label.place(relx=0.7, rely=0.27)
    update_weather(weather_label, weather_icon_label, description_label, config)

    # Calendar Section (placed below Weather)
    calendar_label = tk.Label(root, text="Loading calendar...", font=roboto_light, fg="white", bg="black", anchor="w", justify="left")
    calendar_label.place(relx=0.7, rely=0.35, relwidth=0.25, relheight=0.2)
    update_calendar(calendar_label)

    # LLM Conversation Widget (Bottom Left)
    llm_text_widget = tk.Text(root, font=("Roboto Light", 16), fg="white", bg="black", wrap="word")
    llm_text_widget.place(relx=0.02, rely=0.02, relwidth=0.46, relheight=0.96)



    # Start the LLM conversation thread (pass config as argument)
    threading.Thread(target=llm_conversation_thread, args=(llm_text_widget, config), daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    main()
