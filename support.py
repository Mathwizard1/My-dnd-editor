import tkinter as tk
from tkinter import Label, ttk
from tkinter import font
import os

'''class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

root = tk.Tk()

fonts=list(font.families())
fonts.sort()
frame = ScrollableFrame(root)

for item in fonts:
    ttk.Label(frame.scrollable_frame,text=item,font=(item,"15")).pack()

frame.pack()
root.mainloop()'''

'''s = "1d1+3"
s1 = "12"
p = s.split("d")
print(p, s1.split("d"))
print(p[0].isnumeric())'''
 
'''a = {"aa": "hello", 1: 3, 4: "bye", (1,2): 2}
b = str(a)
print(b)
print(eval(b)["aa"])'''



'''cur_dir_name = os.getcwd()
print(cur_dir_name)
print(os.path.basename(cur_dir_name))'''

class GUI:
    def __init__(self, master, x, y):
        self.master = master
        self.canvas = tk.Canvas(master, width=x, height=y)
        self.canvas.pack()
        self.canvas.create_polygon(10, 10, 10, 20, 200, 300, 250, 150, 10, 10,
        outline="green", fill="blue")
        self.canvas.create_polygon(100, 10, 10, 40, 50, 300, 250, 400, 100, 10,
        outline="green", fill="red", stipple="gray50")


x, y = 500, 500
root = tk.Tk()
gui = GUI(root, x, y)
root.mainloop()