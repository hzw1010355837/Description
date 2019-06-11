import tkinter as tk
from tkinter import filedialog

FILE_PATH = None

def find_file_path():
    global FILE_PATH
    FILE_PATH = filedialog.askopenfilename()

root = tk.Tk()
root.title("nani")
root.geometry("400x400")
frame = tk.Frame(root)
frame.pack()

button = tk.Button(frame, text="点击输入mp4文件",command = find_file_path)
button.pack()

# TODO 之后继续完成开始按钮,以及主要逻辑



root.mainloop()
