import asyncio

import imutils
import numpy as np
import pickle
import cv2
import sqlite3 as lite
import datetime
from transliterate import translit

from face_recognition import face_distance, face_locations, face_encodings, compare_faces

def start_recognition(process=False):
    con = lite.connect('face_recognition.db')
    encoding = "encodings\\encoding1.pickle"
    data = pickle.loads(open(encoding, "rb").read())
    # cap = cv2.VideoCapture(0)
    cap = cv2.VideoCapture('http://admin:admin123@192.168.43.102/video.cgi?&subtype=1')
    # cap = cv2.VideoCapture('test/test.jpg') #0
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    ret, img = cap.read()
    # frame = img.copy()

    if cap.isOpened :
        ret, frame = cap.read()
    else:
        ret = False
    while(ret):
        ret, frame = cap.read()

        # rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb = imutils.resize(frame, width=640)
        r = frame.shape[1] / float(rgb.shape[1])

        boxes = face_locations(rgb, model= "hog")
        encodings = face_encodings(rgb, boxes)
        names = []
        for encoding in encodings:
            matches = compare_faces(np.array(encoding),np.array(data["encodings"]), tolerance=0.55)
            print(100*(1 - min(face_distance(np.array(encoding),np.array(data["encodings"])))))
            name = "Unknown"
            if True in matches:
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}

                for i in matchedIdxs:
                    name = data["names"][i]
                    counts[name] = counts.get(name, 0) + 1
                    name = max(counts, key=counts.get)
            names.append(name)
        for name in names:
            if name != "Unknown":
                try:
                    with con:
                        now = datetime.datetime.now()
                        date = str(now.date().strftime("%Y-%m-%d"))
                        time = str(now.time().strftime("%H:%M:%S"))
                        weekday = now.weekday()
                        cur = con.cursor()
                        cur.execute("INSERT INTO datetime(student_id, date, time, weekday) VALUES(?,?,?,?)", (name, date, time, weekday,))
                        cur.execute("SELECT firstname FROM students WHERE id=?", (name,))
                        for row in cur.fetchall():
                            name = row[0]
                        con.commit()
                except Exception as e:
                    print(e)
                    name = "Unknown"
            print(name)
        for ((top, right, bottom, left), name) in zip(boxes, names):
            top = int(top * r)
            right = int(right * r)
            bottom = int(bottom * r)
            left = int(left * r)
            cv2.rectangle(frame, (left, top), (right, bottom),(0, 255, 0), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            father_name = ''
            if name != "Unknown":
                try:
                    with con:
                        cur = con.cursor()
                        cur.execute("SELECT firstname, fathername FROM students WHERE id=?", (name,))
                        for row in cur.fetchall():
                            name = row[0]
                            father_name = row[1]
                            print(name)
                except:
                    name = "Unknown"
            full_name = '%s %s' % (name, father_name)
            cv2.putText(frame, translit(full_name.replace('и', 'ы').replace('і', 'и'), 'ru', reversed=True), (left, y), cv2.FONT_HERSHEY_SIMPLEX,0.75, (0, 255, 0), 2)
        cv2.imshow("Frame", frame)
        if (cv2.waitKey(1) == 27 and not process) or (process and process.end_recognition):
            break

    cv2.destroyAllWindows()

    cap.release()
if __name__ == "__main__":
    start_recognition()

