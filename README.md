# Face Recognition Attendance System

A simple OpenCV-based face recognition attendance app.

It works in three stages:

1. Capture face images into the dataset folder.
2. Train an LBPH face-recognition model.
3. Run live recognition from the webcam and record attendance.

## Project Structure

- `main.py` - runs live face recognition and marks attendance.
- `database.py` - optional MongoDB attendance storage.
- `dataset/main.py` - captures face images from the webcam.
- `model/main.py` - trains the recognition model from dataset images.
- `face_recognizer.xml` - trained model file.
- `names.json` - label-to-name mapping used by the recognizer.
- `attendance.txt` - fallback attendance log file.

## Requirements

- Python 3.10+ recommended
- Webcam
- The packages in `requirements.txt`

## Installation

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## How to Use

### 1. Capture Face Images

Run the capture script:

```bash
python dataset/main.py
```

Enter the name, id, and class/label when prompted. The script saves grayscale face images into a folder inside `dataset/`.

### 2. Train the Model

After collecting images, train the recognizer:

```bash
python model/main.py
```

This generates:

- `face_recognizer.xml`
- `names.json`

### 3. Start Attendance Recognition

Run the main app:

```bash
python main.py
```

The app will open your webcam, detect faces, and mark attendance once per person per session. Press `Q` to exit.

## Attendance Storage

The app tries to store attendance in MongoDB first. If MongoDB is not available, it falls back to writing entries into `attendance.txt`.

## Notes

- `dataset/VAsaa_45/` is ignored by Git on purpose.
- Large model files may trigger a GitHub size warning, but the project will still work.
- If recognition quality is poor, collect more clear face images before retraining.

## Troubleshooting

- If the webcam does not open, close other apps that may be using the camera.
- If `cv2.face.LBPHFaceRecognizer_create()` is missing, make sure `opencv-contrib-python` is installed.
- If no faces are detected, improve lighting and keep the face centered.