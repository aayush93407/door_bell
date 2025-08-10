import cv2
import pyttsx3
import speech_recognition as sr
import smtplib
from email.mime.text import MIMEText
import numpy as np

# Dummy iFacenet-based classifier using Haar cascades as a placeholder
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def detect_harmful_objects_ifacenet(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    # Dummy logic: assume if more than 1 face is present or face partially covered, it's suspicious
    harmful = []
    if len(faces) > 1:
        harmful.append("multiple faces")
    elif len(faces) == 1 and is_face_masked(gray, faces[0]):
        harmful.append("mask")

    return harmful

def is_face_masked(gray, face_rect):
    x, y, w, h = face_rect
    face_area = gray[y:y+h, x:x+w]
    mid_y = y + h // 2
    lower_half = gray[mid_y:y+h, x:x+w]
    darkness = np.mean(lower_half)
    return darkness > 100  # Tunable threshold

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source, duration=0.5)  # Allow time to adjust
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=3)
            print("Processing...")
            return r.recognize_google(audio)
        except sr.WaitTimeoutError:
            print("Timeout: No speech detected")
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
    return "unknown"


def send_email(name, items):
    sender = "aayushkumar9340@gmail.com"
    receiver = "aayushkumar93407@gmail.com"
    app_password = "xagi cuds ogin ogao"

    body = f"🔔 Someone is at the door.\n\nName: {name}\nSuspicious items: {', '.join(items) if items else 'None'}"
    msg = MIMEText(body)
    msg['Subject'] = f'Doorbell Alert: {name}'
    msg['From'] = sender
    msg['To'] = receiver

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, app_password)
            server.send_message(msg)
        print("Email sent!")
    except Exception as e:
        print("Failed to send email:", e)
