import sqlite3 as lite
import sys

con = lite.connect('face_recognition.db')
with con:
    cur = con.cursor()
    cur.execute("CREATE TABLE students( "
                "id INTEGER PRIMARY KEY,"
                "group_id INT,"
                "lastname VARCHAR,"
                "firstname VARCHAR,"
                "fathername VARCHAR,"
                "image VARCHAR,"
                "FOREIGN KEY (group_id) REFERENCES groups(id)"
                ")")
    cur.execute("CREATE TABLE groups( "
                "id INTEGER PRIMARY KEY,"
                "name VARCHAR,"
                "course INT"
                ")")
    cur.execute("CREATE TABLE subjects( "
                "id INTEGER PRIMARY KEY,"
                "name VARCHAR,"
                "day_of_week INT,"
                "time TIME"
                ")")
    cur.execute("CREATE TABLE datetime( "
                "id INTEGER PRIMARY KEY,"
                "student_id INT,"
                "weekday INT,"
                "date DATE,"
                "time TIME,"
                "FOREIGN KEY (student_id) REFERENCES students(id)"
                ")")
    cur.execute("CREATE TABLE groups_subjects( "
                "id INTEGER PRIMARY KEY,"
                "group_id INT,"
                "subject_id INT,"
                "FOREIGN KEY (group_id) REFERENCES groups(id),"
                "FOREIGN KEY (subject_id) REFERENCES subjects(id)"
                ")")

    con.commit()