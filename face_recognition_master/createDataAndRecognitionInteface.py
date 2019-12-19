import threading
import tkinter as tk
import tkinter.ttk as ttk
import asyncio
from face_recognition_master.graphic_window import centerWindow, find_students, on_closing
from face_recognition_master.datasetCreation import create_dataset
from face_recognition_master.recognition import start_recognition
from face_recognition_master.trainingTheData import create_pickle


class Process():
    status = ''
    data = ''
    pickle_status = ''
    recognition_data = ''
    end_recognition = True

    def __init__(self):
        self.root = tk.Tk()
        self.root.iconbitmap('lntu.ico')
        self.root.title("LNTU Recognition")
        centerWindow(self.root, 550, 60)
        self.root.resizable(False, False)

        frame1 = tk.Frame(self.root)
        frame1.place(x=20, y=10)

        create_dataset_btn = ttk.Button(frame1, text=u'Зберегти зображення для розпізнавання',
                                        command=self.__create_dataset)
        create_dataset_btn.grid(row=0, column=0)
        self.create_dataset_label = ttk.Label(frame1, text=u'%s %s' % (self.status, self.data))
        self.create_dataset_label.grid(row=1, column=0, sticky='ew')

        training_btn = ttk.Button(frame1, text=u'Створити словник',
                                  command=self.__create_pickle)
        training_btn.grid(row=0, column=1)
        self.training_btn_label = ttk.Label(frame1, text=u'%s' % (self.pickle_status))
        self.training_btn_label.grid(row=1, column=1, sticky='ew')

        self.recognition_btn = ttk.Button(frame1, text=u'Запустити розпізнавання',
                                     command=lambda: self.recognition())
        self.recognition_btn.grid(row=0, column=2)
        self.recognition_btn_label = ttk.Label(frame1, text=u'%s' % (self.recognition_data))
        self.recognition_btn_label.grid(row=1, column=2, sticky='ew')

        self.root.bind('<Return>', find_students)
        self.root.protocol("WM_DELETE_WINDOW", lambda window=self.root: on_closing(window))
        self.root.mainloop()
    def __create_dataset(self):
        t = threading.Thread(target=create_dataset, args=(self,))
        t.start()

    def __create_pickle(self):
        t = threading.Thread(target=create_pickle, args=(self,))
        t.start()

    def start(self):
        self.status = 'Створюються'
        self.__set_label()

    def start_pickle(self):
        self.pickle_status = 'Створюються'
        self.__set_label()

    def update_data(self, data):
        self.data = data
        self.__set_label()

    def update_recognition_data(self, data):
        self.recognition_data = data
        self.__set_label()
        self.root.update_idletasks()

    def end(self):
        self.status = 'Завершено'
        self.data = ''
        self.__set_label()

    def end_pickle(self):
        self.pickle_status = 'Завершено'
        self.__set_label()

    def __set_label(self):
        self.create_dataset_label['text'] = '%s %s' % (self.status, self.data)
        self.training_btn_label['text'] = self.pickle_status
        self.recognition_btn_label['text'] = self.recognition_data
        self.root.update_idletasks()

    def recognition(self):
        if self.end_recognition:
            self.start_recognition()
        else:
            self.stop_recognition()

    def start_recognition(self):
        self.end_recognition = False
        self.recognition_btn['text'] = 'Зупинити розпізнавання'
        t = threading.Thread(target=start_recognition, args=(self,))
        t.start()
        self.root.update_idletasks()


    def stop_recognition(self):
        self.end_recognition = True
        self.recognition_btn['text'] = 'Запустити розпізнавання'
        self.root.update_idletasks()

if __name__ == '__main__':
    Process()
    # process = Process()