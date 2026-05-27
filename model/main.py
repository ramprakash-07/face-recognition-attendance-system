import cv2
import os
import numpy as np
import json

# -------------------------------------
# Step 1: Load dataset (folders = names)
# -------------------------------------
def load_dataset(dataset_path):
    faces = []
    labels = []
    name_mapping = {}
    current_label_id = 0

    # Walk the dataset tree and treat any folder that contains image files
    # as a person entry. This supports the layout: <dataset>/<class>/<student_folder>/images
    for root, dirs, files in os.walk(dataset_path):
        # collect image files in this directory
        img_files = [f for f in files if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        if not img_files:
            continue

        # Use relative path from dataset_path as the person's name (e.g. "class/student")
        person_name = os.path.relpath(root, dataset_path).replace(os.sep, "/")
        name_mapping[current_label_id] = person_name

        # Load and normalize each image (convert to grayscale and resize)
        for img_name in img_files:
            img_path = os.path.join(root, img_name)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue

            # resize to a consistent size (LBPH works with variable sizes but
            # keeping consistent size avoids unexpected behavior with other recognizers)
            try:
                img_resized = cv2.resize(img, (200, 200))
            except Exception:
                img_resized = img

            faces.append(img_resized)
            labels.append(current_label_id)

        current_label_id += 1

    return faces, labels, name_mapping


# -------------------------------------
# Step 2: Train LBPH Recognizer
# -------------------------------------
def train_recognizer(faces, labels):
    # LBPHFaceRecognizer requires the contrib module. Give a helpful message if it's missing.
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
    except AttributeError:
        print("Error: cv2.face.LBPHFaceRecognizer_create not found.\nPlease install opencv-contrib-python:")
        print("    python -m pip install opencv-contrib-python")
        raise

    recognizer.train(faces, np.array(labels))
    recognizer.save("face_recognizer.xml")
    print("Model saved as face_recognizer.xml")


# -------------------------------------
# Step 3: Main
# -------------------------------------
dataset_path = "D:\\face reco\\dataset"
faces, labels, name_mapping = load_dataset(dataset_path)

print("Faces loaded :", len(faces))
print("Labels loaded:", len(labels))
print("Persons:", name_mapping)

# basic checks
if len(faces) == 0:
    print("Error: No face images found in dataset. Make sure dataset folder contains class/student subfolders with images.")
    raise SystemExit(1)

# save mapping (important)
with open("names.json", "w") as f:
    json.dump(name_mapping, f)

train_recognizer(faces, labels)

print("Training complete!")
print("Name mapping saved as names.json")
