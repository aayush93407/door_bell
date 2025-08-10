# app.py
from flask import Flask, render_template, request
import os
import cv2
from utils import (
    detect_harmful_objects_ifacenet,
    speak,
    recognize_speech,
    send_email,
    record_video,
    camera
)

app = Flask(__name__)
os.makedirs("logs", exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ring', methods=['POST'])
def ring():
    print(" Doorbell was pressed.")
    print(" Asking for visitor's name...")
    speak("Hello! Please say your name.")
    print(" Listening for name...")
    name = recognize_speech()
    print(f" Name heard: {name}")
    speak("Hello " + name + ", please wait while we confirm your identity.")
    
    print(" Starting video recording for 5 seconds...")
    video_path = record_video(duration=5, record_from_global_camera=True)

    print(" Checking for harmful items in frame...")
    ret, frame = camera.read()
    if not ret:
        print(" Failed to capture frame for detection.")
        items = []
    else:
        items = detect_harmful_objects_ifacenet(frame)

    print(" Sending email with video and threat status...")
    send_email(name, items, video_path)

    print(" Process complete. Video email sent.")
    return ('', 204)

if __name__ == '__main__':
    app.run(debug=True)
