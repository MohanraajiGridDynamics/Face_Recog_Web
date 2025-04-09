🧩 1. Backend Changes (views.py)
You’ll need:

reference_encoding saved globally (not ideal in prod, but fine for this demo)

A streaming view that sends live webcam frames as an MJPEG stream

````
# views.py
import cv2
import face_recognition
import numpy as np
from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

reference_encoding = None  # 🧠 Store globally

def upload_and_run(request):
    global reference_encoding

    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(image.name, image)
        file_path = os.path.join(settings.MEDIA_ROOT, filename)

        reference_image = cv2.imread(file_path)
        rgb = cv2.cvtColor(reference_image, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb)

        if encodings:
            reference_encoding = encodings[0]

    return render(request, 'face_app/index.html')


def gen_frames():
    global reference_encoding

    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            match = False
            if reference_encoding is not None:
                match = face_recognition.compare_faces([reference_encoding], face_encoding)[0]

            label = "MATCH" if match else "NO MATCH"
            color = (0, 255, 0) if match else (0, 0, 255)

            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()


def video_feed(request):
    return StreamingHttpResponse(gen_frames(), content_type='multipart/x-mixed-replace; boundary=frame')
````

🧩 2. Frontend (index.html)


````
<!DOCTYPE html>
<html>
<head>
    <title>Face Match Live</title>
</head>
<body>
    <h1>Upload Reference Image</h1>
    <form method="post" enctype="multipart/form-data">
        {% csrf_token %}
        <input type="file" name="image" required>
        <button type="submit">Upload</button>
    </form>

    <h2>Live Webcam Feed</h2>
    <img src="{% url 'video_feed' %}" width="640" height="480">
</body>
</html>
````


🧩 3. URLs (urls.py)

````
from django.urls import path
from face_app import views

urlpatterns = [
    path('', views.upload_and_run, name='home'),
    path('video_feed/', views.video_feed, name='video_feed'),
]
````

✅ Final Result
The webcam will start streaming live

It’ll draw boxes with MATCH or NO MATCH in real-time

When you upload a new image → the match logic will refresh with the new face