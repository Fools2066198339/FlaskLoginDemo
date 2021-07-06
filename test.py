import os

import face_recognition

with open(os.path.dirname(os.path.abspath(__file__))+"/FaceBaseImg/mayun.jpg", "rb") as f:
    img = face_recognition.load_image_file(f)
    print(img)
