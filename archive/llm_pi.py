import ollama
import speech_recognition as sr
import pyttsx3

# Name of your Ollama model
modelname = "llama3.2"


def main():
    # Initialize the Ollama client
    client = ollama.Client()

    # Initialize the speech recognizer
    recognizer = sr.Recognizer()

    # Initialize the TTS engine
    tts_engine = pyttsx3.init()
    # (Optional) Configure voices, rate, volume as desired, e.g.:
    # tts_engine.setProperty('rate', 150)
    # tts_engine.setProperty('volume', 1.0)

    # Continuously wait for a prompt
    while True:
        try:
            with sr.Microphone(device_index=2) as source:
                # Optionally reduce background noise:
                recognizer.adjust_for_ambient_noise(source, duration=5)

                print("\nPlease speak your prompt (say 'stop' or 'exit' to quit).")
                print("Speak now")

                # Increase time to listen:
                # - `timeout=None` means there's no fixed time limit to start hearing speech
                # - `phrase_time_limit=20` means you can speak for up to 20 seconds per utterance
                audio_data = recognizer.listen(
                    source,
                    timeout=None,
                    phrase_time_limit=20  # Adjust as desired (None for no limit)
                )

            # Convert speech to text
            prompt = recognizer.recognize_google(audio_data).strip()
            print(f"You said: {prompt}")

            # Check for exit keywords
            if prompt.lower() in ["stop", "exit"]:
                print("Exiting the loop. Goodbye!")
                break

            # Send the recognized text to Ollama
            # If your model is cutting off responses, try adjusting max_tokens or other parameters.
            response = client.generate(
                model=modelname,
                prompt=prompt,
                # max_tokens=1024,  # Uncomment/adjust if you want longer responses from the model
            )
            model_reply = response.response
            print("\nResponse from Ollama:")
            print(model_reply)

            # Use text-to-speech to read out Ollama's response
            tts_engine.say(model_reply)
            tts_engine.runAndWait()

        except sr.UnknownValueError:
            print("Sorry, I did not understand the audio. Please try again.")
        except sr.RequestError as e:
            print(f"Could not request results from the speech service; {e}")
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received. Exiting.")
            break


if __name__ == "__main__":
    main()


#AUDIO VISUALIZATION

