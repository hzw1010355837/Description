import tkinter as tk
from tkinter import filedialog, messagebox

from main import VideoToTxt

FILE_PATH = None

def find_file_path():
    global FILE_PATH
    FILE_PATH = filedialog.askopenfilename()
    if FILE_PATH.split('.')[-1] not in ["mp4", "MP4", "avi", "AVI"]:
        FILE_PATH = None
        return messagebox.showinfo("提示", "目前只支持mp4和avi格式哦!")

def run():
    global FILE_PATH
    if not FILE_PATH:
        return messagebox.showinfo("警告", "请先输入文件!")
    mp3_flag = VideoToTxt(FILE_PATH, flag).main()
    if mp3_flag:
        messagebox.showinfo("提示", "Done!")
    else:
        messagebox.showerror("错误", "未安装ffmpeg(视频没有声音)!如未将缓存文件删除,可在缓存%s文件中看到初期效果" % (FILE_PATH.split(".")+"avi"))
    root.destroy()

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
