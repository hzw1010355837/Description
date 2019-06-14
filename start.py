import tkinter as tk
from tkinter import filedialog, messagebox

from main import VideoToTxt

FILE_PATH = None

def find_file_path():
    global FILE_PATH
    FILE_PATH = filedialog.askopenfilename()
    if not FILE_PATH.endswith(".mp4"):
        FILE_PATH = None
        return messagebox.showinfo("提示", "目前只支持mp4格式哦!")

def run():
    global FILE_PATH
    if not FILE_PATH:
        return messagebox.showinfo("警告", "请先输入mp4文件!")
    VideoToTxt(FILE_PATH, flag).main()


root = tk.Tk()
root.title("nani")
root.geometry("400x400")
frame = tk.Frame(root)
frame.pack()

button = tk.Button(frame, text="点击输入mp4文件",command = find_file_path)
button.pack()

flag = tk.IntVar()
check = tk.Checkbutton(frame, text="删除缓存文件", variable=flag, onvalue=1, offvalue=0)
check.pack()

start = tk.Button(frame, text="start",command = run)
start.pack()

root.mainloop()
