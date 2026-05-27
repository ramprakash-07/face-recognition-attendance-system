import cv2
import json
import datetime
import os

# Try to import database helper (optional). If not available or not configured,
# the script will fallback to writing `attendance.txt`.
db_available = False
try:
    import database
    db_available = database.is_configured()
    if db_available:
        print("MongoDB configured — attendance will be stored in DB.")
    else:
        print("MongoDB not configured (MONGO_URI empty or connection failed). Falling back to file.")
except Exception:
    database = None
    db_available = False

# Load trained LBPH model
try:
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("face_recognizer.xml")
except Exception as e:
    print("Error loading recognizer:", e)
    raise

# Load name mapping
with open("names.json", "r") as f:
    names = json.load(f)

# keep track of who was already recorded during this run
recorded = set()

# Face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Start webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open video capture device.")
    raise SystemExit(1)

print("Recognition started... Press Q to stop.")

# Ensure attendance file exists as fallback
attendance_file = "attendance.txt"
if not os.path.exists(attendance_file):
    open(attendance_file, "a").close()

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        now = datetime.datetime.now()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # detect faces
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            roi = gray[y:y+h, x:x+w]

            # resize ROI to the same size used for training (if needed)
            try:
                roi_resized = cv2.resize(roi, (200, 200))
            except Exception:
                roi_resized = roi

            # Predict ID + confidence
            try:
                label, confidence = recognizer.predict(roi_resized)
            except Exception:
                # prediction failed
                label, confidence = -1, 999

            # Lower confidence = better match (LBPH rule)
            if confidence > 60 and label is not None and label >= 0:
                person = names.get(str(label), "Unknown") 
                # person is saved as "Class/StudentID" in training script
                if "/" in person:
                    class_name, student = person.split("/", 1)
                else:
                    class_name = None
                    student = person
                name = student
                text = f"{name} ({round(confidence,2)})"
            else:
                name = "Unknown"
                class_name = None
                text = "Unknown"

            # Draw on screen
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)
            cv2.putText(frame, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

            # Record attendance whenever a known face is detected, once per run.
            if name != "Unknown":
                key = label
                if key not in recorded:
                    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
                    recorded.add(key)
                    if db_available:
                        ok = database.insert_attendance(name=student, label=label, timestamp=timestamp, class_name=class_name)
                        if ok:
                            print(f"Recorded to DB: {student} at {timestamp}")
                        else:
                            # fallback to file
                            with open(attendance_file, "a") as f:
                                f.write(f"{student} - {timestamp}\n")
                            print(f"DB write failed, recorded to file: {student} at {timestamp}")
                    else:
                        with open(attendance_file, "a") as f:
                            f.write(f"{student} - {timestamp}\n")
                        print(f"Recorded to file: {student} at {timestamp}")

        cv2.imshow("Face Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
finally:
    cap.release()
    cv2.destroyAllWindows()
    print("Stopped.")