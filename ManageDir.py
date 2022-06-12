from tkinter import *
from tkinter import filedialog
from pathlib import Path
class ScrollableFrame(Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = Canvas(self, width=500)
        scrollbar = Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = Frame(canvas)

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

root = Tk()


root.title('Manage Directories')
root.resizable(False, False)

def refresh():
    for x in alldir.scrollable_frame.winfo_children():
        x.destroy()
def makeframe(a):
    dirop = Frame(alldir.scrollable_frame)
    Label(dirop, text = a, padx = 20, pady=10, width = 50).pack(side=LEFT)
    Button(dirop, text = 'Delete', command = lambda: deldir(a), pady=10, fg="black", bg="#EA8CA7", relief=FLAT, borderwidth=0).pack(side=RIGHT)
    dirop.pack()
def view():
    try:
        validate()
        f = open('configs.txt', 'r')
        dires = f.readlines()
        for i in dires:
            makeframe(i)
        if dires != []:
            dirs.destroy()
        else:
            refresh()
        #if dires != []:
        #    dirs['text'] = str(dires)
        f.close()
    except(FileNotFoundError):
        refresh()
        f = open('configs.txt', 'w')
        f.close()
def addir():
    try:
        f = open('configs.txt', 'r')
        dires = f.readlines()
        f.close()
        f = open('configs.txt', 'a')
        dire = filedialog.askdirectory()
        if dire+'\n' not in dires and dire != "":
             f.writelines([dire,'\n'])
        f.close()
        refresh()
        view()
        if f:
            f.close()
    except(FileNotFoundError):
        f = open('configs.txt', 'w')
        f.close()
def deldir(a):
    try:
        f = open('configs.txt', 'r')
        lines = f.readlines()
        f.close()
        f = open('configs.txt', 'w')
        for line in lines:
            if line!=a:
                f.writelines(line)
        f.close()
        refresh()
        view()
    except(FileNotFoundError):
        f = open('configs.txt', 'w')
        f.close()
def validate():
    try:
        f = open('configs.txt', 'r')
        lines = f.readlines()
        f.close()
        f = open('configs.txt', 'w')
        for i in lines:
            if Path(i[:-1]).exists():
                f.writelines(i)
        f.close()
    except(FileNotFoundError):
        f = open('configs.txt', 'w')
        f.close()

alldir = ScrollableFrame(root)
alldir.pack()
dirs = Label(root, text = 'NO FOLDERS SELECTED')
dirs.pack(pady = (0,200))
Button(root, text="Add Folder", command = addir, height=2, fg="black", bg="#EA8CA7", relief=FLAT, borderwidth=0).pack(pady=10)

view()
root.mainloop()
