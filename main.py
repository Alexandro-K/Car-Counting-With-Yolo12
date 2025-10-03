import os
import math
import pandas as pd
import numpy as np

import subprocess
import cv2
import cvzone
from sort import *
from ultralytics import YOLO

from datetime import datetime

# Taking the video source url (from Tol Kelapa Gading-Pulo Gebang)(23+150)
url = "https://camera.jtd.co.id/camera/share/tios/2/27/index.m3u8"
ffmpeg_cmd = [
    "ffmpeg",
    "-fflags", "nobuffer", # Reducing buffering
    "-flags", "low_delay",  # Reduce delay
    "-i", url, # Input stream from url
    "-vf", "scale=640:360", # Resizing using video filter
    "-f", "rawvideo", # Output in raw video
    "-pix_fmt", "bgr24", # Pixel format in bgr
    "-" # Output to stdout, (stream not file)
]

# Run ffmpeg with above command
proc = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE) # stdout makes output in raw bytes
                                                            # can be read from python with proc.stdout

w, h = 640, 360 # Frame after resizing

model = YOLO("../Yolo-Weights/yolo12m.pt") # Initialiaze the model
classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
              "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
              "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
              "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
              "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
              "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
              "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
              "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
              "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
              "teddy bear", "hair drier", "toothbrush"
              ]
mask = cv2.imread("mask.png") # Taking the mask
tracker = Sort(max_age=90, min_hits=4, iou_threshold=0.3) # Initialize the tracker (mark for 90 frames,

# Setting up line limits
limitsLeft = [155, 250, 320, 250]
limitsRight = [340, 300, 570, 300]

# Total vehicles count
totalCountLeft = []
totalCountRight = []

result_df = [] # df to store the result

# Setting up time for 3 minutes timeframe
last_minute = datetime.now().minute
minutes_passed = 0

# Checking if minutes timeframe has passed
while True and minutes_passed != 3:
    raw_frame = proc.stdout.read(w * h * 3) # Take the raw data and calculate total bytes in 1 frame
    if not raw_frame:
        break

    frame = np.frombuffer(raw_frame, dtype=np.uint8).reshape((h, w, 3)) # Taking the raw data and turning it into numpy array
                                                                        # And reshaping it into normal picture array
    frame = frame.copy() # We need to copy because the default one is read only
    frameRegion = cv2.bitwise_and(frame, mask) # Placing the mask on top of the original frame
    imgGraphics = cv2.imread("graphics.png", cv2.IMREAD_UNCHANGED) # This is used for vehicles number placeholder
    cvzone.overlayPNG(frame, imgGraphics, (420, 2)) # Placing the graphics
    results = model(frameRegion, imgsz=960, conf=0.3, stream=True) # Passing the frame into the model
    detections = np.empty((0, 5)) # Making the empty np arr for detections
    for r in results:
        boxes = r.boxes
        for box in boxes:
            # Creating the bounding box
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            boxW, boxH = x2 - x1, y2 - y1
            bbox = x1, y1, int(boxW), int(boxH)

            # Confidence and Class Name
            conf = math.ceil((box.conf[0] * 100)) / 100
            cls = int(box.cls[0])
            currentClass = classNames[cls]

            # Checking the results
            if currentClass == "car" or currentClass == "truck" or currentClass == "bus" \
                    or currentClass == "motorbike" and conf > 0.3:
                currentArray = np.array([x1, y1, x2, y2, conf])
                detections = np.vstack((detections, currentArray))

    # Updating tracker and placing the line for detections
    resultsTracker = tracker.update(detections)
    cv2.line(frame, (limitsLeft[0], limitsLeft[1]), (limitsLeft[2], limitsLeft[3]), (0, 0, 255), 5)
    cv2.line(frame, (limitsRight[0], limitsRight[1]), (limitsRight[2], limitsRight[3]), (0, 0, 255), 5)

    # Loop for every result we got
    for result in resultsTracker:
        # Taking every points from the result
        x1, y1, x2, y2, Id = result
        x1, y1, x2, y2, Id = int(x1), int(y1), int(x2), int(y2), int(Id)
        resultW, resultH = x2 - x1, y2 - y1

        # Putting the rectangle and the text(id)
        cvzone.cornerRect(frame, (x1, y1, resultW, resultH), l=10, t=2, rt=2, colorR=(0, 255, 0))
        cvzone.putTextRect(frame, f'{Id}', (max(0, x1), max(20, y1)), scale=1, thickness=1, offset=2)

        # This is for the centered circle
        cx, cy = x1 + resultW // 2, y1 + resultH // 2
        cv2.circle(frame, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

        # Determine the limits for every line we have
        if limitsLeft[0] < cx < limitsLeft[2] and limitsLeft[1] - 10 < cy < limitsLeft[1] + 10:
            if totalCountLeft.count(Id) == 0:
                totalCountLeft.append(Id)
                cv2.line(frame, (limitsLeft[0], limitsLeft[1]), (limitsLeft[2], limitsLeft[3]), (0, 255, 0), 5)

        if limitsRight[0] < cx < limitsRight[2] and limitsRight[1] - 10 < cy < limitsRight[1] + 10:
            if totalCountRight.count(Id) == 0:
                totalCountRight.append(Id)
                cv2.line(frame, (limitsRight[0], limitsRight[1]), (limitsRight[2], limitsRight[3]), (0, 255, 0), 5)

    # Taking current time and checking if the minutes has passed
    # If yes, append the data to the dataframe
    now = datetime.now()
    if now.minute != last_minute:
        result_df.append({
            "Waktu": now.strftime("%d-%m-%Y %H:%M"),
            "Total Bagian Kiri": len(totalCountLeft),
            "Total Bagian Kanan": len(totalCountRight),
            "Rata-rata Keseluruhan": None
        })
        totalCountLeft = []
        totalCountRight = []
        minutes_passed += 1
        last_minute = now.minute

    # This is for number on the top right
    cv2.putText(frame, str(len(totalCountLeft)), (490, 35), cv2.FONT_HERSHEY_PLAIN, 2, (139, 95, 75), 3)
    cv2.putText(frame, str(len(totalCountRight)), (590, 35), cv2.FONT_HERSHEY_PLAIN, 2, (139, 95, 75), 3)

    # Showing the video and the masked region
    cv2.imshow("Stream", frame) # Show the frame
    cv2.imshow("StreamRegion", frameRegion) # The masked region
    if cv2.waitKey(1) & 0xFF == ord('q'): # delay 1ms and q for quit
        break

proc.kill() # Turn off ffmpeg process
cv2.destroyAllWindows() # Close all OpenCV window

# Convert to dataframe
result_df = pd.DataFrame(result_df)

# Average
avg_left = result_df["Total Bagian Kiri"].mean()
avg_right = result_df["Total Bagian Kanan"].mean()
avg_total = (result_df["Total Bagian Kiri"] + result_df["Total Bagian Kanan"]).mean()

# Total
total_left = result_df["Total Bagian Kiri"].sum()
total_right = result_df["Total Bagian Kanan"].sum()
total = total_left + total_right

# Average + Total
summary = pd.DataFrame([
    {"Waktu": "AVERAGE",
     "Total Bagian Kiri": round(avg_left, 2),
     "Total Bagian Kanan": round(avg_right, 2),
     "Rata-rata Keseluruhan": round(avg_total, 2)},
    {"Waktu": "TOTAL",
     "Total Bagian Kiri": round(total_left, 2),
     "Total Bagian Kanan": round(total_right, 2),
     "Rata-rata Keseluruhan": round(total, 2)}
])

# Combine Avg and Total
result_df = pd.concat([result_df, summary], ignore_index=True)

# Setting up the save path
save_path = "result"
os.makedirs(save_path, exist_ok=True)
filename = datetime.now().strftime("result/hasil_%d-%m-%Y_%H-%M-%S.csv")

result_df = pd.DataFrame(result_df)
result_df.to_csv(filename, index=False)

print(f"Hasil berhasil disimpan ke {filename}")