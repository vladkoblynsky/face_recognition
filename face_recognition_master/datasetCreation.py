import numpy as np
import os
import cv2
import sqlite3 as lite

IMAGES_PATH = 'images/'

def create_dataset(process=False):
    if process:
        process.start()
    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")


    path = "dataset\\"# path were u want store the data set

    con = lite.connect('face_recognition.db')
    with con:
        cur = con.cursor()
        cur.execute("SELECT id, firstname, lastname, image FROM students")
        for row in cur.fetchall():
            print(row[0], row[1], row[2], row[3])
            if process:
                data = '%s %s' % (row[1], row[2])
                process.update_data(data)
            # cap = cv2.VideoCapture(0)
            # id = input('enter user name')
            cap = cv2.VideoCapture('%s%s' %(IMAGES_PATH, row[3]))
            id = row[0]

            try:
                # Create target Directory
                os.mkdir(path+str(id))
                print("Directory " , path+str(id),  " Created ")
            except FileExistsError:
                print("Directory " , path+str(id) ,  " already exists")
            sampleN=0

            # while 1:
            ret, img = cap.read()
            frame = img.copy()

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                sampleN = sampleN + 1

                cv2.imwrite(path + str(id) + "\\" + str(sampleN) + ".jpg", gray[y:y + h, x:x + w])

                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

                cv2.waitKey(100)
            # cv2.imshow('img', img)

            # if sampleN > 5:
            #     break
            cv2.waitKey(1)

            cap.release()
            cv2.destroyAllWindows()
        if process:
            process.end()

if __name__ == '__main__':
    create_dataset()


