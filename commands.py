import speech_recognition as sr
import re
import requests
from gtts import gTTS
import os
import playsound

    """
    آی پی esp32 را در متغیر زیر وارد کنید
    """
# ESP32 details
ESP32_URL = "http://your-ESP32-IP/control"  


def speak(text):
    """
    پاسخ را با استفاده از gTTS به زبان انگلیسی تولید کرده و از بلندگوی سیستم پخش می‌کند.
    """
    try:
        tts = gTTS(text=text, lang='en')  # پاسخ‌ها به انگلیسی
        file_name = "response.mp3"
        tts.save(file_name)
        playsound.playsound(file_name)  # پخش صوت از بلندگوی سیستم
        os.remove(file_name)  # حذف فایل موقت پس از پخش
    except Exception as e:
        print(f"Error in TTS: {e}")

def list_microphones():
    """
    نمایش تمام میکروفون‌های موجود.
    """
    print("Available microphones:")
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"{index}: {name}")

def getUserInput(mic_index=None):
    """
    دریافت دستورات صوتی به زبان فارسی.
    """
    recognizer = sr.Recognizer()
    
    if mic_index is None:
        print("Using default microphone...")
        mic = sr.Microphone()
    else:
        print(f"Using microphone with index {mic_index}: {sr.Microphone.list_microphone_names()[mic_index]}")
        mic = sr.Microphone(device_index=mic_index)
    
    with mic as source:
        print("Listening for your command in Farsi...")
        try:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio, language="fa-IR")
            print(f"You said (in Farsi): {command}")
            return command
        except sr.UnknownValueError:
            error_message = "متاسفم، نتوانستم گفتار شما را درک کنم."
            print(error_message)
            speak("Sorry, I could not understand what you said.")
            return "Error: Could not understand audio"
        except sr.RequestError as e:
            error_message = f"خطا در اتصال به سرویس تشخیص گفتار: {e}"
            print(error_message)
            speak("Error connecting to the speech recognition service.")
            return "Error: Unable to connect to recognition service"
        except Exception as e:
            error_message = f"خطای غیرمنتظره رخ داد: {e}"
            print(error_message)
            speak("An unexpected error occurred.")
            return "Error: Unexpected issue"

def parse_command(command):
    """
    پردازش دستور فارسی برای استخراج عمل (روشن/خاموش) و تعداد چراغ‌ها.
    """
    command = command.strip().replace("یک", "1").replace("دو", "2").replace("سه", "3") \
                             .replace("چهار", "4").replace("پنج", "5")

    turn_on_match = re.search(r"(\d+)\s*چراغ\s*روشن", command)
    turn_off_match = re.search(r"(\d+)\s*چراغ\s*خاموش", command)
    
    if turn_on_match:
        count = int(turn_on_match.group(1))
        return "turn_on", count
    elif turn_off_match:
        count = int(turn_off_match.group(1))
        return "turn_off", count
    elif "تمام" in command:
        speak("Exiting the program.")
        return "exit", 0
    else:
        error_message = "دستور نامعتبر است. لطفا دوباره امتحان کنید."
        print(error_message)
        speak("Invalid command. Please try again.")
        return None, None

def send_to_esp32(action, count):
    """
    ارسال عمل و تعداد چراغ‌ها به ESP32 برای کنترل LED‌ها.
    """
    try:
        payload = {
            "action": action,
            "count": count
        }
        response = requests.post(ESP32_URL, json=payload)
        
        if response.status_code == 200:
            if action == "turn_on":
                message = f"{count} lights turned on."
                print(message)
                speak(f"Turning on {count} lights.")
            elif action == "turn_off":
                message = f"{count} lights turned off."
                print(message)
                speak(f"Turning off {count} lights.")
        else:
            error_message = f"ESP32 returned an error. Status code: {response.status_code}."
            print(error_message)
            speak(error_message)
    except Exception as e:
        error_message = "An error occurred while communicating with ESP32."
        print(f"{error_message} {e}")
        speak(error_message)

def main():
    # نمایش میکروفون‌های موجود
    list_microphones()
    
    try:
        mic_index = int(input("Enter the index of the microphone you want to use: "))
    except ValueError:
        print("Invalid input. Using default microphone.")
        mic_index = None
    
    while True:
        command = getUserInput(mic_index)
        if not command.startswith("Error"):
            action, count = parse_command(command)
            
            if action == "exit":
                print("Exiting the program.")
                break
            elif action and count:
                send_to_esp32(action, count)
        else:
            print("لطفا دوباره امتحان کنید.")

if __name__ == "__main__":
    main()
