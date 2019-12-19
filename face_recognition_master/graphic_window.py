import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import tkinter.ttk as ttk
import sqlite3 as lite
import datetime
import xlsxwriter
import os

DEFAULT_DB_PATH = '/Users/Admin/PycharmProjects/FaceRecognition/face_recognition_master/face_recognition_master'
WEEKDAYS = ['Понеділок', 'Вівторок', 'Середа', 'Четвер', "П'ятниця", 'Субота', 'Неділя']
MONTHS = ['', 'Січня', 'Лютого', 'Березня', 'Квітня', 'Травня', 'Червня', 'Липня', 'Серпня', 'Вересня', 'Жовтня', 'Листопада', 'Грудня']
DEFAULT_SUBJECT_TIMEDELTA = datetime.timedelta(0, 4800)
student_detail_windows = {}
NOT_FOUND = 'Not found'
PATH_FOR_REPORTS = './reports'

class DB:
    def __init__(self, name=None):
        self.name = name
        self.images_path = os.path.dirname(name) + '/images' if name else None
        self.con = None

    def change_name(self, name):
        old_name = self.name
        self.name = name
        self.images_path = os.path.dirname(name) + '/images' if name else None
        self.connect()
        if not self.con:
            self.images_path = os.path.dirname(old_name) + '/images' if old_name else None
            self.name = old_name

    def connect(self):
        try:
            self.con = connect_to_db(self.name)
        except:
            messagebox.showerror('Помилка', 'Вибраний файл не є БД!')
            self.con = None

selected_db = DB()

def on_closing(window):
    if messagebox.askokcancel("Вихід", "Ви справді хочете вийти?"):
        window.destroy()

def create_window(width=500, height=400, resizeable=True):
    window = tk.Toplevel(root)
    window.iconbitmap('lntu.ico')
    centerWindow(window, width, height)
    if not resizeable:
        window.resizable(False, False)
    return window


def on_closing_student_window(window, id):
    student_detail_windows.pop(id, None)
    window.destroy()

def change_listbox_size(event):
    if students_listbox:
        students_listbox['width'] = round(root.winfo_width()/7)
        students_listbox['height'] = round(root.winfo_height() / 25)

def centerWindow(window, width=None, height=None):
    windowWidth = width or root.winfo_reqwidth()
    windowHeight = height or root.winfo_reqheight()

    # Gets both half the screen width/height and window width/height
    positionRight = int(window.winfo_screenwidth() / 2 - windowWidth / 2)
    positionDown = int(window.winfo_screenheight() / 2 - windowHeight / 2)

    # Positions the window in the center of the page.
    window.geometry("{}x{}+{}+{}".format(windowWidth, windowHeight, positionRight, positionDown))

def openFileDialog():
    file = filedialog.askopenfilename(initialdir=DEFAULT_DB_PATH, title="Select file",
                               filetypes=(("db files", "*.db"), ("all files", "*.*")))
    return file

def select_db():
    name = openFileDialog()
    if name:
        selected_db.change_name(name)
        select_db_label['text'] = 'Підключено'
        select_db_btn['text'] = u'Змінити'
        init_data_frame2()

def connect_to_db(db_name):
    con = lite.connect(db_name)
    with con:
        cur = con.cursor()
        cur.execute("SELECT firstname FROM students")
        cur.fetchone()[0]
    return con

def init_data_frame2():
    # Grid widgets in tab2
    group_label.grid(row=0, column=0, sticky='we')
    group_ent.grid(row=1, column=0, sticky='ew')
    # find_by_group_btn.grid(row=1, column=1, sticky='w')

    last_name_label.grid(row=0, column=1, sticky='we')
    last_name_ent.grid(row=1, column=1, sticky='we')
    first_name_label.grid(row=0, column=2, sticky='we')
    first_name_ent.grid(row=1, column=2, sticky='we')
    father_name_label.grid(row=0, column=3, sticky='we')
    father_name_ent.grid(row=1, column=3, sticky='we')
    # find_by_name_btn.grid(row=1, column=4, sticky='we')
    find_btn.grid(row=1, column=4, sticky='we')

    scrollbar_listbox.pack(expand=True, fill='y', side='right')
    students_listbox.pack(expand=True, fill='both', side='left')

def write_students_to_list(students_listbox, students):
    if not students:
        messagebox.showinfo('Не знайдено', 'Студенти за даним запитом не знайдені!')
    for row in students:
        id = row[0]
        student_data = get_student_data_by_id(id)
        student_id = student_data['student_id']
        firstname = student_data['firstname']
        lastname = student_data['lastname']
        fathername = student_data['fathername']
        group_id = student_data['group_id']
        group_data = get_group_data_by_id(group_id)
        group_name = group_data['group_name']
        record = "%s %s %s %s" % (group_name, lastname, firstname, fathername)
        students_listbox.students_id.update({record: student_id})
        students_listbox.insert(tk.END, record)

def find_students(event=None):
    """ Find students by group or lastname or firstname or fathername and write them to list """

    last_name = last_name_ent.get()
    first_name = first_name_ent.get()
    father_name = father_name_ent.get()
    last_name = last_name and last_name.capitalize()
    first_name = first_name and first_name.capitalize()
    father_name = father_name and father_name.capitalize()
    last_name_ent.delete(0, tk.END)
    first_name_ent.delete(0, tk.END)
    father_name_ent.delete(0, tk.END)
    if selected_db.con:
        con = selected_db.con
        with con:
            cur = con.cursor()
            cur.execute("PRAGMA case_sensitive_like = off")
            execute_str = "SELECT id FROM students WHERE "
            groups = find_by_group()
            if not(groups == NOT_FOUND) and any([first_name, last_name, father_name, groups]):
                for i, row in enumerate(groups):
                    id = row[0]
                    if i == 0:
                        execute_str += "group_id=%s " %(id)
                    else:
                        execute_str += "OR group_id=%s " % (id)
                if groups and (last_name or first_name or father_name):
                    execute_str += "AND "
                if last_name:
                    if first_name:
                        if father_name:
                            cur.execute(execute_str + "lastname LIKE ? AND firstname LIKE ? AND fathername LIKE ?",("%"+ last_name+"%", "%"+first_name+"%", "%"+father_name+"%",))
                        else:
                            cur.execute(execute_str + "lastname LIKE ? AND firstname LIKE ?",("%"+ last_name+"%","%"+ first_name+"%" ,))
                    elif father_name:
                        cur.execute(execute_str + "lastname LIKE ? AND fathername LIKE ?",("%"+ last_name+"%","%"+ father_name+"%", ))
                    else:
                        cur.execute(execute_str + "lastname LIKE ?",("%"+ last_name+"%",))
                elif first_name:
                    if father_name:
                        cur.execute(execute_str + "firstname LIKE ? AND fathername LIKE ?",("%"+ first_name+"%", "%"+ father_name+"%",))
                    else:
                        cur.execute(execute_str + "firstname LIKE ?", ("%"+ first_name+"%",))
                elif father_name:
                    cur.execute(execute_str + "fathername LIKE ?", ("%"+ father_name+"%",))
                else:
                    cur.execute(execute_str)
                data = cur.fetchall()
            else:
                data = []
            students_listbox.delete(0, tk.END)
            write_students_to_list(students_listbox, data)
            cur.close()

def find_by_group():
    """ Find students by group and write them to list in tab3 """
    group = group_ent.get()
    group_ent.delete(0, tk.END)
    if selected_db.con:
        con = selected_db.con
        with con:
            cur = con.cursor()
            if group:
                cur.execute("SELECT id, name, course FROM groups WHERE name LIKE ?", ("%"+group+"%",))
                groups = cur.fetchall()
                return groups if groups else NOT_FOUND
            else:
                return []

def get_student_data_by_id(id):
    """ Return dict {group_id, lastname, firstname, fathername} """
    if selected_db.con:
        con = selected_db.con
        with con:
            cur = con.cursor()
            cur.execute("SELECT group_id, lastname, firstname, fathername, id, image FROM students WHERE id=?", (id,))
            student_row = cur.fetchone()
            data = {'group_id': student_row[0], 'lastname': student_row[1],
                    'firstname': student_row[2], 'fathername': student_row[3],
                    'student_id': student_row[4], 'image': student_row[5]}
            return data
    return []
def get_group_data_by_id(id):
    """ Return dict {group_id, lastname, firstname, fathername} """
    if selected_db.con:
        con = selected_db.con
        with con:
            cur = con.cursor()
            cur.execute("SELECT id, name, course FROM groups WHERE id=?", (id,))
            group_row = cur.fetchone()
            data = {'group_id': group_row[0],
                    'group_name': group_row[1],
                    'course': group_row[2]}
            return data
    return []

def onFrameConfigure(canvas, event):
    '''Reset the scroll region to encompass the inner frame'''
    canvas.configure(scrollregion=canvas.bbox("all"))



def show_details(event):
    """ Show new window with student subjects """
    record_index = students_listbox.curselection()
    if record_index:
        record = students_listbox.get(record_index[0])
        student_id = students_listbox.students_id.get(record)
        if not student_detail_windows.get(student_id):
            new_window = create_window(900, 300, False)
            student_detail_windows.update({student_id: new_window})
            new_window.protocol("WM_DELETE_WINDOW", lambda window=new_window, id=student_id: on_closing_student_window(new_window, student_id))
            student_data = get_student_data_by_id(student_id)
            ##### WIDGETS #####
            new_window.title("%s %s" %(student_data['lastname'], student_data['firstname']))
            ##### CANVAS SCROLL #####
            def _on_mousewheel(event):
                canvas.yview_scroll(-1 * round((event.delta / 120)), "units")

            ##### DATA #####
            student_subjects = get_student_subjects(student_id)
            tab_parent = ttk.Notebook(new_window, width=700)
            path = "%s/%s" %(selected_db.images_path, student_data['image'])
            load = Image.open(path)
            load.thumbnail((190,190), Image.ANTIALIAS)
            render = ImageTk.PhotoImage(load)
            img = ttk.Label(new_window, image=render)
            img.image = render
            img.place(x=0, y=0)
            report_btn = ttk.Button(new_window, text='Звіт (xlsx)', command=lambda id=student_id:report(id))
            report_btn.place(x=20, y=200)
            for i, day in enumerate(WEEKDAYS):
                if student_subjects[i]:
                    tab1 = ttk.Frame(tab_parent)
                    tab_parent.add(tab1, text=day)
                    canvas = tk.Canvas(tab1, width=800, bd=0, relief='ridge', highlightthickness=0)
                    canvas_frame = tk.Frame(canvas, padx=10)
                    myscrollbarY = tk.Scrollbar(tab1, orient="vertical", command=canvas.yview)
                    canvas.configure(yscrollcommand=myscrollbarY.set)
                    myscrollbarY.pack(side="right", fill="y")
                    canvas.pack(side="right", fill='both')
                    canvas.create_window(0, 0, anchor='nw', window=canvas_frame)
                    # canvas.bind_all("<MouseWheel>", _on_mousewheel)
                    count = 0
                    col = 0
                    row = 0
                    for j, sub in enumerate(student_subjects[i]):
                        sub_name = sub[0]
                        sub_time = sub[1]
                        time_object = datetime.datetime.strptime(sub_time, '%H:%M:%S') + DEFAULT_SUBJECT_TIMEDELTA
                        student_datetime = get_student_datetime(student_id, i, sub_time, time_object.strftime('%H:%M:%S'))
                        # was = "Був присутній" if student_datetime else 'Був відсутній'
                        dates_set = {row[0] for row in student_datetime}
                        # dates_set = list(dates_set) + list(dates_set) + list(dates_set) + list(dates_set) + list(dates_set)
                        label_day_frame = ttk.Labelframe(canvas_frame, text=sub_name)
                        label_day_frame.grid(row=row, column=col)
                        col += 1
                        if col == 3:
                            row += 1
                            col = 0
                        scrollbar_listbox = tk.Scrollbar(label_day_frame, orient="vertical")
                        dates_listbox = tk.Listbox(label_day_frame, height=6,
                                                          yscrollcommand=scrollbar_listbox.set)
                        scrollbar_listbox.config(command=dates_listbox.yview)
                        dates_listbox.pack(side='left', fill='both', expand=1)
                        scrollbar_listbox.pack(side='right')
                        for date in dates_set:
                            datetime_object = datetime.datetime.strptime(date, '%Y-%m-%d')
                            day = datetime_object.strftime('%d')
                            month = datetime_object.strftime('%m')
                            year = datetime_object.strftime('%Y')
                            record = "%s %s, %sр" % (day, MONTHS[int(month)].lower(), year)
                            dates_listbox.insert(tk.END, record)

                    canvas_frame.update_idletasks()
                    canvas.config(scrollregion=canvas.bbox("all"))
            tab_parent.place(x=200, y=0)

def get_student_subjects(student_id):
    if selected_db.con:
        con = selected_db.con
        with con:
            cur = con.cursor()
            student_data = get_student_data_by_id(student_id)
            group_id = student_data['group_id']
            cur.execute("SELECT subject_id FROM groups_subjects WHERE group_id=?", (group_id,))
            subjects = [ [] for i, day in enumerate(WEEKDAYS)]
            for row in cur.fetchall():
                sub_id = row[0]
                cur.execute("SELECT weekday, name, time FROM subjects WHERE id=?", (sub_id,))
                sub_row = cur.fetchone()
                subjects[sub_row[0]].append([sub_row[1], sub_row[2]])
            return subjects

def get_student_datetime(id, weekday, start_time, end_time):
    """ Return [Y-m-d, H:M:S] """
    if selected_db.con:
        con = selected_db.con
        with con:
            cur = con.cursor()
            cur.execute("SELECT date, time, weekday FROM datetime WHERE student_id=? AND weekday=? AND time <= ? AND time >= ? ORDER BY date", (id, weekday, end_time, start_time, ))
            return cur.fetchall()

def report(student_id):
    student_subjects = get_student_subjects(student_id)
    student_data = get_student_data_by_id(student_id)
    if not os.path.exists(PATH_FOR_REPORTS):
        os.makedirs(PATH_FOR_REPORTS)

    full_name = "%s/%s %s %s.xlsx" %(PATH_FOR_REPORTS, student_data['lastname'], student_data['firstname'], student_data['fathername'])
    workbook = xlsxwriter.Workbook(full_name)
    for i, day in enumerate(WEEKDAYS):
        if student_subjects[i]:
            worksheet = workbook.add_worksheet(day)
            worksheet.set_column(0, len(student_subjects[i])-1,width=20)
            col = 'A'
            for j, sub in enumerate(student_subjects[i]):
                row = 1
                sub_name = sub[0]
                sub_time = sub[1]
                time_object = datetime.datetime.strptime(sub_time, '%H:%M:%S') + DEFAULT_SUBJECT_TIMEDELTA
                student_datetime = get_student_datetime(student_id, i, sub_time, time_object.strftime('%H:%M:%S'))
                dates_set = {row[0] for row in student_datetime}
                worksheet.write("%s%i" %(col, row), sub_name)
                row += 1
                for date in dates_set:
                    datetime_object = datetime.datetime.strptime(date, '%Y-%m-%d')
                    day = datetime_object.strftime('%d')
                    month = datetime_object.strftime('%m')
                    year = datetime_object.strftime('%Y')
                    record = "%s %s, %sр" % (day, MONTHS[int(month)].lower(), year)
                    worksheet.write("%s%i" %(col, row),  record)
                    row += 1
                col = chr(ord(col) + 1)

    workbook.close()

if __name__ == '__main__':

    root = tk.Tk()
    root.iconbitmap('lntu.ico')
    root.title("LNTU students")
    tk.Grid.rowconfigure(root, 0, weight=1)
    tk.Grid.columnconfigure(root, 0, weight=1)
    centerWindow(root, 640, 500)
    root.resizable(False, False)
    # root.resizable(True, True)


    tab_parent = ttk.Notebook(root)
    tab1 = ttk.Frame(tab_parent)
    # tab2 = ttk.Frame(tab_parent)
    tab_parent.add(tab1, text="Знайти студентів")
    # tab_parent.add(tab2, text="Сформувати звіт")
    tab_parent.pack(expand=1, fill='both')

    frame1 = tk.Frame(tab1)
    frame1.place(x=20, y=10)
    frame2 = tk.Frame(tab1)
    frame2.place(x=20, y=50)
    frame3 = tk.Frame(tab1)
    frame3.place(x=20, y=100)

    ##### WIDGETS FRAME 1 #####
    select_db_label = ttk.Label(frame1, text=u'Виберіть БД')
    select_db_label.grid(row=0, column=0, columnspan=3)
    select_db_btn = ttk.Button(frame1, text=u'Вибрати', command=select_db)
    select_db_btn.grid(row=0, column=3)

    ##### WIDGETS FRAME 2 #####
    last_name_label = ttk.Label(frame2, text=u"Прізвище")
    last_name_ent = ttk.Entry(frame2)
    first_name_label = ttk.Label(frame2, text=u"Ім'я")
    first_name_ent = ttk.Entry(frame2)
    father_name_label = ttk.Label(frame2, text=u"По батькові")
    father_name_ent = ttk.Entry(frame2)
    group_label = ttk.Label(frame2, text=u"Група")
    group_ent = ttk.Entry(frame2)
    find_btn = ttk.Button(frame2, text=u'Знайти', command=find_students)

    scrollbar_listbox = tk.Scrollbar(frame3, orient="vertical")
    students_listbox = tk.Listbox(frame3, width=95,  height=20,
                                  yscrollcommand=scrollbar_listbox.set)
    students_listbox.students_id = {}
    students_listbox.bind("<<ListboxSelect>>", show_details)
    scrollbar_listbox.config(command=students_listbox.yview)

    root.bind('<Return>', find_students)
    root.protocol("WM_DELETE_WINDOW", lambda window=root: on_closing(window))
    root.mainloop()