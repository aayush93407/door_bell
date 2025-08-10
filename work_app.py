from flask import Flask, render_template, request
import threading
import cv2
from utils import detect_harmful_objects_ifacenet, speak, recognize_speech, send_email

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ring', methods=['POST'])
def ring():
    threading.Thread(target=handle_visitor).start()
    return '', 204

def handle_visitor():
    print("📸 Opening camera...")
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("❌ Failed to capture frame")
        return

    print("🧠 Detecting objects with FaceNet...")
    detected_items = detect_harmful_objects_ifacenet(frame)
    print("✅ Detected:", detected_items)

    speak("Can you say your name, sir?")
    name = recognize_speech()
    print("🎤 Name heard:", name)

    speak(f"Your name is {name}, right?")
    confirmation = recognize_speech()
    print("🎤 Confirmation heard:", confirmation)

    if any(word in confirmation.lower() for word in ["yes", "yeah", "yup", "sure", "correct"]):
        print("✅ Visitor confirmed their name.")
        speak("Thank you for confirming your name.")
        print("✉️ Sending email...")
        send_email(name, detected_items)
    else:
        speak("Sorry, could you please confirm again?")
        confirmation = recognize_speech()
        if "yes" in confirmation.lower():
            send_email(name, detected_items)

if __name__ == '__main__':
    app.run(debug=True)
