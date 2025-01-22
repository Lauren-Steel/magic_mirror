import speech_recognition as sr

recognizer = sr.Recognizer()
print("Testing microphone access...")
try:
    with sr.Microphone() as source:
        print("Say something...")
        audio = recognizer.listen(source, timeout=5)
        print("Microphone is working.")
except Exception as e:
    print(f"Error: {e}")
