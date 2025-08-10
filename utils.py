# utils.py
import cv2
import os
import datetime
import pyttsx3
import speech_recognition as sr
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from ultralytics import YOLO
import mediapipe as mp

# Load YOLOv8n model
yolo_model = YOLO('yolov8n.pt')

# Open camera once and keep it open
camera = cv2.VideoCapture(0)

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

def is_face_covered(frame):
    with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
        results = face_detection.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if results.detections:
            return False  # Face detected, likely not covered
        else:
            return True  # No face detected, assume covered

def detect_harmful_objects_ifacenet(frame):
    print("🔍 Running YOLOv8n detection...")
    results = yolo_model(frame)[0]

    # Get label names from model output
    all_labels = [yolo_model.names[int(cls)] for cls in results.boxes.cls.tolist()]
    print("🧾 All labels detected:", all_labels)

    # Define threat labels to keep
    threat_labels = ['knife', 'gun', 'scissors', 'cap', 'sunglasses']

    # Filter for only threat-related items
    detected = [label for label in all_labels if label in threat_labels]

    # Add "face_covered" if face not detected
    if is_face_covered(frame):
        detected.append("face_covered")

    print("⚠️ Threat labels detected:", detected)
    return detected


def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print(" Adjusting for ambient noise...")
        r.adjust_for_ambient_noise(source)
        print(" Listening...")
        audio = r.listen(source)
        try:
            return r.recognize_google(audio)
        except:
            return "unknown"

def record_video(duration=5, output_dir="logs/", record_from_global_camera=False):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    video_path = os.path.join(output_dir, f"visitor_{timestamp}.avi")
    out = cv2.VideoWriter(video_path, fourcc, 20.0, (640, 480))

    print(" Recording video...")
    start_time = datetime.datetime.now()
    cam = camera if record_from_global_camera else cv2.VideoCapture(0)
    while (datetime.datetime.now() - start_time).seconds < duration:
        ret, frame = cam.read()
        if ret:
            out.write(frame)
    if not record_from_global_camera:
        cam.release()
    out.release()
    print(" Video saved:", video_path)
    return video_path

def send_email(name, items, video_path):
    sender = "aayushkumar9340@gmail.com"
    receiver = "aayushkumar93407@gmail.com"
    app_password = "use ur app password"

    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    msg = MIMEMultipart()
    msg['Subject'] = f"Doorbell Alert: {name}"
    msg['From'] = sender
    msg['To'] = receiver

    body = f"""
    Dear Homeowner,

    Someone has arrived at your door at {current_time}.

     Visitor Name: {name}
     Detected Items: {', '.join(items) if items else 'None'}

     A short video clip of the visitor is attached for your review.

    Regards,
    Smart Doorbell System
    """
    msg.attach(MIMEText(body, 'plain'))

    with open(video_path, 'rb') as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(video_path)}')
        msg.attach(part)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, app_password)
            server.send_message(msg)
        print(" Email sent successfully to owner.")

    except Exception as e:
        print(" Failed to send email:", e)
