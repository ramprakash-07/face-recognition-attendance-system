import cv2
import os

# Configuration
max_count = 500
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

s_name = input("Enter your name: ")
s_id = input("Enter your id: ")
# Class (label) input — avoid using the reserved word `class` as a variable name
class_name = input("Enter class/label: ")

# Simple sanitizer for folder names: keep alphanumerics, dash and underscore
def _sanitize(name: str) -> str:
    return "".join(c for c in name if c.isalnum() or c in ("-", "_")).strip()

class_name = _sanitize(class_name) or "default"
s_name = _sanitize(s_name) or "user"
s_id = _sanitize(s_id) or "id"
# Save captured faces in: <BASE_DIR>/<class_name>/<sname_sid>/
BASE_DIR = os.path.dirname(__file__)
SAVE_DIR = os.path.join(BASE_DIR, f"{s_name}_{s_id}")
os.makedirs(SAVE_DIR, exist_ok=True)

# Count existing images to continue from the right number
def count_existing_images(directory):
    exts = (".jpg", ".jpeg", ".png")
    return len([f for f in os.listdir(directory) if f.lower().endswith(exts)])

image_count = count_existing_images(SAVE_DIR)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open video capture device.")
    raise SystemExit(1)

print(f"Starting capture — saving up to {max_count} images to: {SAVE_DIR}")
print(f"Current count: {image_count}/{max_count}")

try:
    while image_count < max_count:
        ret, frame = cap.read()
        if not ret:
            print("Warning: empty frame read, stopping.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)

        # Draw rectangles for all detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Show frame once per loop (not inside the face loop)
        cv2.imshow("Face Detection", frame)

        # If at least one face detected, save the first detected face region
        if len(faces) > 0:
            x, y, w, h = faces[0]
            face_img = frame[y : y + h, x : x + w]
            # Convert the cropped face to grayscale before saving
            face_gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
            image_count += 1
            # Save as: <sname>_<sid>_<count>.jpg (grayscale)
            face_filename = f"{s_name}_{s_id}_{image_count}.jpg"
            path = os.path.join(SAVE_DIR, face_filename)
            cv2.imwrite(path, face_gray)
            print(f"Saved (grayscale): {face_filename} ({image_count}/{max_count})")

        # Exit if user presses 'q'
        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("User requested exit.")
            break
finally:
    cap.release()
    cv2.destroyAllWindows()
    print("Capture finished. Resources released.")
