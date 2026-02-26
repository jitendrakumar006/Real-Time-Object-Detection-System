import cv2
import numpy as np
import time
import os

def speak(text):
    os.system(
        f'powershell -Command "Add-Type -AssemblyName System.Speech; '
        f'(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{text}\');"'
    )

CLASSES = [
    "background","aeroplane","bicycle","bird","boat","bottle",
    "bus","car","cat","chair","cow","diningtable","dog","horse",
    "motorbike","person","pottedplant","sheep","sofa","train","tvmonitor"
]

net = cv2.dnn.readNetFromCaffe(
    "deploy.prototxt",
    "mobilenet_iter_73000.caffemodel"
)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Camera nahi mila")
    exit()

last_time = 0

print("AI Navigation start...")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w = frame.shape[:2]

    left = False
    center = False
    right = False
    person_front = False

    blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()

    for i in range(detections.shape[2]):
        conf = detections[0, 0, i, 2]

        if conf > 0.6:
            idx = int(detections[0, 0, i, 1])
            label = CLASSES[idx]

            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            x1, y1, x2, y2 = box.astype("int")

            cx = (x1 + x2) // 2
            area = (x2 - x1) * (y2 - y1)

            if cx < w // 3:
                left = True
            elif cx > 2 * w // 3:
                right = True
            else:
                center = True
                if label == "person" and area > 90000:
                    person_front = True

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    message = "seedha jao rasta clear hai"

    if person_front:
        message = "ruk jao samne aadmi hai"
    elif center:
        message = "ruk jao samne obstacle hai"
    elif left and not right:
        message = "right jao"
    elif right and not left:
        message = "left jao"
    elif left and right:
        message = "dhire chalo"

    if time.time() - last_time > 2:
        print(message)
        speak(message)
        last_time = time.time()

    cv2.putText(frame, message, (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    cv2.imshow("Blind Navigation", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
