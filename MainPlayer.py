from tkinter import *
import sys
from tkinter.ttk import Style
import eyed3
import os
import pygame
import subprocess
from functools import partial
import re
from tkinter import ttk
import random

root = Tk()
root.title("MPlayer")
root['bg'] = "black"
songs = []
temp = []
current = 0
pid = None

pygame.mixer.init()

root.resizable(False, False)

class ScrollableFrame(Frame):
    def __init__(self, container, *args, **kwargs):

        super().__init__(container, *args, **kwargs)
        self.canvas = Canvas(self, width=500, height = 600, highlightthickness=0)
        self.scrollbar = Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True, pady=20)
        self.scrollbar.pack(side="right", fill="y")
        self.scrollable_frame.bind('<Enter>', self.mouse_on_widget)
        self.scrollable_frame.bind('<Leave>', self.mouse_off_widget)


    def mouse_on_widget(self, event):
        self.canvas.bind_all("<MouseWheel>", self.scroll)

    def mouse_off_widget(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def scroll(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

def rundir():
    global pid
    if pid is None or pid.poll() is not None:
        pid = subprocess.Popen([sys.executable,"ManageDir.py"])

def gather():
    songs = []
    f = open('configs.txt', 'r')
    lines = f.readlines()
    f.close()
    for line in lines:
        with os.scandir(line[:-1]) as dirs:
            for entry in dirs:
                if re.search(".(aac|mp3|m4a)$", entry.path) != None:
                    songs.append(entry.path)
    return songs

def metdata(songpath):
        song = eyed3.load(songpath)
        info = []
        try:
            info.append(song.tag.title)
        except:
            info.append(os.path.basename(songpath))
        else:
            if info[0] is None:
                info[0] = os.path.basename(songpath)
        try:
            info.append(song.tag.artist)
        except:
            info.append("Unknown Artist")
        else:
            if info[1] is None:
                info[1] = "Unknown Artist"
        try:
            info.append(song.tag.album)
        except:
            info.append("Unknown Album")
        else:
            if info[2] is None:
                info[2] = "Unknown Album"
        try:
            info.append(song.tag.genre.name)
        except:
            info.append("Unknown Genre")
        else:
            if info[3] is None:
                info[3] = "Unknown Genre"
        for i in range(4):
            if info[i] is None:
                info[i] = " "*50
            if len(info[i]) > 50:
                info[i] = info[i][:46] + "..."
            else:
                info[i] = info[i] + " "*(50-len(info[i]))
        return info

started = False
repeat = False
firstrun = True
shuffle = False

def nowplaying():
    global current
    if check['text'] == 'Continue':
        pass
    else:
        global started, firstrun
        if pygame.mixer.music.get_busy():
            started = True
        else:
            started = False
        if started == False and firstrun == False:
            if repeat:
                play(current, 0)
            else:
                if current == len(songs)-1 and shuffle == False and repeat == False:
                    title['text'] = f"\n\n\n"
                    scale['label'] = "- 00 : 00                00 : 00"
                    seektime.set(0)
                    scale['to_'] = 0
                    songbuttons[current]['bg'] = "#EA8CA7"
                    songbuttons[current]['fg'] = "black"
                    firstrun = True
                neb.invoke()
    root.after(1000, nowplaying)

def play(ind, user):
    
    if user == 1:
        global songs, temp
        songs = temp

    global current, lastcount, firstrun, songbuttons
    try:
        inf = eyed3.load(songs[ind])
        songbuttons[current]['bg'] = "#EA8CA7"
        songbuttons[current]['fg'] = "black"
    except:
        return
    current = ind
    if firstrun:
        firstrun = False
    pygame.mixer.music.load(songs[current])
    titleinfo(songs[current])
    scale.set(0)
    scale['to_'] = inf.info.time_secs
    pygame.mixer.music.play()
    songbuttons[current]['bg'] = 'black'
    songbuttons[current]['fg'] = "#EA8CA7"
    
def seek(_=None):
    pygame.mixer.music.play()
    if scale.get() != 0:
        pygame.mixer.music.set_pos(scale.get())
    if check['text'] == "Continue":
            check.invoke()

def titleinfo(songpath):
        info = metdata(songpath)
        title["text"] = f"{info[0]}\n{info[1]}\n{info[2]}\n{info[3]}"

def previous():
    if firstrun:
        return
    global current
    
    if current == 0 and shuffle == False:
        pass
    else:
        songbuttons[current]['bg'] = '#EA8CA7'
        songbuttons[current]['fg'] = "black"
        if shuffle:
            current = random.randint(0, len(songs)-1)
        else:
            current = current - 1

        play(current, 0)
        if check['text'] == "Continue":
            check.invoke()

def next():
    if firstrun:
        return
    global current, songs
    
    if current == len(songs)-1 and shuffle == False:
        pass
    else:
        songbuttons[current]['bg'] = '#EA8CA7'
        songbuttons[current]['fg'] = "black"
        if shuffle:
            current = random.randint(0, len(songs)-1)
        else:
            current = current + 1

        play(current, 0)
        if check['text'] == "Continue":
            check.invoke()

songbuttons = []

def listview():
    global songs, temp, songbuttons
    temp = gather()
    if songs == []:
        songs = temp

    refresh()
    songbuttons = []
    ind = 0
    temp1 = temp
    for songpath in temp1:
        try:
            info = metdata(songpath)
        except:
            temp.pop(ind)
            continue
        frame = Frame(songslist.scrollable_frame, bg="black")
        meta = Button(
            frame,
            text=f"\n\n\n",
            padx=10,
            pady=10,
            font=("Verdana", 10),
            justify=LEFT,
            bg="#EA8CA7",
            fg="black",
            width=70,
            borderwidth=0,
            command = partial(play, ind, 1),
            anchor=W,
            activebackground="black",
            activeforeground="#EA8CA7"
        )
        meta.pack(pady=2)
        songbuttons.append(meta)
        
        meta["text"] = f"{info[0]}\n{info[1]}\n{info[2]}\n{info[3]}"
        frame.pack()
        ind = ind + 1
    if pygame.mixer.music.get_busy():
            songbuttons[current]['bg'] = "black"
            songbuttons[current]['fg'] = "#EA8CA7"

def refresh():
    for x in songslist.scrollable_frame.winfo_children():
        x.destroy()
    

def pause():
    if firstrun:
        return
    if check['text'] != "Pause":
        pygame.mixer.music.unpause()
        check['text'] = "Pause"
        check['fg'] = "black"
        check['bg'] = "#EA8CA7"
    else:
        pygame.mixer.music.pause()
        check['text'] = "Continue"
        check['fg'] = "#EA8CA7"
        check['bg'] = "black"

def vol(_=None):
    volm = float(volslider.get()/100)
    pygame.mixer.music.set_volume(volm)

# Song List
songslist = ScrollableFrame(root, bg="black")
songslist.grid(rowspan=6, column = 1)

# Title Label
tt = LabelFrame(
    root,
    text="Now Playing",
    font = ("Verdana", 15),
    fg = "#EA8CA7",
    bg="black",
    borderwidth=0
)
tt.grid(row = 0, column = 0, padx = 20)
title = Label(
    tt,
    justify=LEFT,
    font=("Verdana", 15),
    text=f"\n\n\n",
    width=50,
    anchor=W,
    padx = 40,
    bg="black",
    fg = "#EA8CA7"
)
title.grid(row = 0, column=0)

# Controls Grid
controls = Frame(root, width = 50, bg = "black")
controls.grid(row = 1, column=0)

# Pause/Unpause Button
check = Button(
    controls,
    activebackground="black",
    activeforeground="#EA8CA7",
    font=("Verdana", 10),
    text = "Pause",
    command=pause,
    fg="black",
    bg = "#EA8CA7",
    relief=FLAT,
    borderwidth=0,
    width=10,
    height=5
)
check.grid(row = 0,column=1, padx=5)

# Previous 
Button(
    controls,
    activebackground="black",
    activeforeground="#EA8CA7",
    font=("Verdana", 10),
    text = 'Previous',
    command = previous,
    fg="black",
    bg = "#EA8CA7",
    relief=FLAT,
    borderwidth=0,
    width=10,
    height=5
).grid(row = 0,column=0)

# Next
neb = Button(
    controls,
    activebackground="black",
    activeforeground="#EA8CA7",
    font=("Verdana", 10),
    text = 'Next',
    command = next,
    fg="black",
    bg = "#EA8CA7",
    relief=FLAT,
    borderwidth=0,
    width=10,
    height=5
)
neb.grid(row = 0,column=2)

def rep():
    global repeat
    if repeat:
        repeat = False
        repb['text'] = 'Repeat'
        repb['bg'] = "#EA8CA7"
        repb['fg'] = "black"
    else:
        repeat = True
        repb['text'] = 'Repeating'
        repb['bg'] = "black"
        repb['fg'] = "#EA8CA7"

def shf():
    global shuffle
    if shuffle:
        shuffle = False
        shfl['text'] = 'Shuffle : Off'
        shfl['bg'] = "#EA8CA7"
        shfl['fg'] = "black"
        
    else:
        shuffle = True
        shfl['text'] = 'Shuffle : On'
        shfl['bg'] = "black"
        shfl['fg'] = "#EA8CA7"

# Repeat
repb = Button(
    controls,
    activebackground="black",
    activeforeground="#EA8CA7",
    font=("Verdana", 10),
    text = 'Repeat',
    command = rep ,
    fg="black",
    bg = "#EA8CA7",
    relief=FLAT,
    borderwidth=0,
    width=10,
    height=5
)
repb.grid(row = 0,column=3, padx=5)

# Shuffle
shfl = Button(
    controls,
    activebackground="black",
    activeforeground="#EA8CA7",
    font=("Verdana", 10),
    text = 'Shuffle : Off',
    command = shf ,
    fg="black",
    bg = "#EA8CA7",
    relief=FLAT,
    borderwidth=0,
    width=10,
    height=5
)
shfl.grid(row = 0,column=4)

aux = Frame(root, bg = "black")
aux.grid(row = 2, column=0)

volslider = Scale(
    aux,
    showvalue=0,
    sliderrelief=FLAT,
    sliderlength = 20,
    font=("Verdana", 10), 
    label="Volume",
    from_=0, 
    to_=100,
    orient=HORIZONTAL, 
    command=vol,
    resolution=1, 
    relief=FLAT, 
    length=200, 
    troughcolor="#EA8CA7", 
    fg = "#EA8CA7", 
    bg = "black",
    highlightbackground="black", 
    borderwidth=0
)
volslider.grid(column=0, row = 0, padx = 5)

# Manage Folders
Button(
    aux, 
    font=("Verdana", 10), 
    activebackground="black", 
    activeforeground="#EA8CA7",
    text = 'Folders', 
    command = rundir, 
    fg="black", 
    bg = "#EA8CA7", 
    relief=FLAT,
    borderwidth=0,
    width=10, 
    height=5
).grid(row=1, column=0, pady = 20)

# Refresh
Button(
    aux, 
    font=("Verdana", 10), 
    activebackground="black", 
    activeforeground="#EA8CA7",
    text = 'Refresh', 
    command = listview, 
    fg="black", 
    bg = "#EA8CA7", 
    relief=FLAT, 
    borderwidth=0,
    width=10, 
    height=5
).grid(row=1, column=1, pady = 20)

seektime = IntVar()
scale=Scale(
    aux,
    showvalue=0,
    sliderrelief=FLAT,
    label="- 00 : 00                00 : 00",
    command = seek,
    variable=seektime,
    sliderlength = 20,
    from_=0, 
    to_=0, 
    resolution=1,
    orient=HORIZONTAL, 
    length=200,  
    troughcolor="#EA8CA7", 
    fg = "#EA8CA7",
    bg = "black", 
    highlightbackground="black", 
    borderwidth=0,
    font=("Verdana", 10)
)
scale.grid(column=1, row = 0)

def cha():
    if pygame.mixer.music.get_busy():
        timenow = scale.get()
        elapsed = int(eyed3.load(songs[current]).info.time_secs) - timenow
        seektime.set(timenow+1)
        tt = f"{'{:0>2}'.format(elapsed//60)} : {'{:0>2}'.format(elapsed%60)}"
        scale['label'] = f"- {tt}               {'{:0>2}'.format(timenow//60)} : {'{:0>2}'.format(timenow%60)}"
        root.after(1000, cha)
    else:
        root.after(1, cha)
    
root.after(1,cha)

if firstrun:
    volslider.set(50)

listview()
root.after(1,nowplaying)
root.mainloop()
