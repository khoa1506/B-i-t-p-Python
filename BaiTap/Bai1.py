import tkinter as tk
from tkinter import ttk
from tkinter import Menu
win = tk.Tk()
win.title("Tinh toan")

menu_bar = Menu(win)
win.config(menu=menu_bar)

file_menu = Menu(menu_bar)
file_menu = Menu(menu_bar, tearoff=0)

file_menu.add_command(label="New")
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_separator()
file_menu.add_command(label="Exit")

tabControl = ttk.Notebook(win)
tab1 = ttk.Frame(tabControl)
tabControl.add(tab1, text="Tab 1")
tabControl.pack(expand=1, fill="both")
tab2 = ttk.Frame(tabControl)
tabControl.add(tab2, text="Tab 2")

frame1 = ttk.Labelframe(tab1, text="Nhap")
frame1.grid(column=0, row=0)
ttk.Label(frame1, text="a: ").grid(column=0, row=0, sticky=tk.W)
ttk.Label(frame1, text="b: ").grid(column=0, row=1, sticky=tk.W)
num1 = tk.IntVar()
txt1 = ttk.Entry(frame1, width=12, textvariable=num1)
txt1.grid(column=1, row=0, sticky=tk.W)
num2 = tk.IntVar()
txt2 = ttk.Entry(frame1, width=12, textvariable=num2)
txt2.grid(column=1, row=1)
frame2 = ttk.Labelframe(tab1, text="Tinh")
frame2.grid(column=1, row=0 )

# def phep_cong():
#     cong = int(num1.get()) + int(num2.get())
#     ket_qua.set(cong)

def phep_tru():
    tru = int(num1.get()) - int(num2.get())
    ket_qua.set(tru)

def phep_cong():
    try:
        cong = int(num1.get()) + int(num2.get())
        ket_qua.set(cong) 
    except:
        pass
        
cong = ttk.Button(frame2, text="+", command=phep_cong)
cong.grid(column=0, row=0)
tru = ttk.Button(frame2, text="-", command=phep_tru)
tru.grid(column=1, row=0)

frame3 = ttk.Labelframe(tab2, text="Ket qua")
frame3.grid(column=0, row=1)
ket_qua = tk.StringVar()
kq_label = ttk.Label(frame3, textvariable=ket_qua)
kq_label.grid(column=0, row=0)
win.mainloop()