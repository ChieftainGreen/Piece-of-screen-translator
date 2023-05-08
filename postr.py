"""Piece-of-screen Translation (POSTR)
Education project. GUI utility that makes
1)screen capture (select zone on screen, or use previously-selected zone)
2)OCR
3)Translation
4)display translated text, with history of previous texts
defaults are set for my display
Not expected for non-windows because ctypes is used for DPI correction
 """

# TODO:
# status bar for errors (like 5000 symbols) - DONE
# format source text - delete unnecessary line breaks, leave only paragraphs - DONE
# translator menu choice
# correct work with empty pastebin.txt file - DONE
# one approach - global vars or pass/take from func
# backend func file
# fill requirements.txt
# clean PEP8

import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import pyscreenshot as ImageGrab
import pytesseract
from deep_translator import (GoogleTranslator,
#                             MicrosoftTranslator,  #maybe later menu choice and selection
                             PonsTranslator,
                             LingueeTranslator,
#                             MyMemoryTranslator,
                             YandexTranslator,
#                             PapagoTranslator,
#                             DeeplTranslator,
#                             QcriTranslator,
#                             single_detection,
#                             batch_detection
                                 )

import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(2)  # DPI awareness for correct screen size
# mywindowgeometry = '3440x1440+0+0' #in case ctypes don't work (Linux etc)

# pytesseract.pytesseract.tesseract_cmd = r'E:\_PYTHON\tesseract_ocr'
topx, topy, botx, boty = 0, 0, 0, 0
rect_id = None
troot = None
oldgeo = None
tcanvas = None
LANG_SOURCE = 'en'  # Deep-Translator library code
LANG_DEST = 'ru'
DELIMITER = '\n\n===============BEAUTIFUL DELIMITER===============\n\n'
err5000 = ' NO GO, too long'  # error from Google API if translating > 5k character
mywindowgeometry = None
# mywindowgeometry = '700x1440+2500+0' # based on my desktop. Comment if not necessary
current_text = 0
text_array = ['Press "Scan Zone" to start']
position = 0


def get_mouse_posn(event):
    """calculates coords for first corner for the screenshot box"""
    global topy, topx
    topx, topy = event.x_root, event.y_root
    print(topx, topy)


def update_sel_rect(event):
    """probably unnecessary?"""
    global rect_id, tcanvas
    global topy, topx, botx, boty
    botx, boty = event.x_root, event.y_root
    tcanvas.coords(rect_id, topx, topy, botx, boty)  # Update selection rect. Зачем это?


def stop_updating(event):
    """calculates coords of second corner for the screenshot box and call the screenshot function"""
    global topy, topx, botx, boty, twindow
    global oldgeo, tcanvas
    botx, boty = event.x_root, event.y_root
    print(topx, topy, botx, boty)
    troot.destroy()
    screen_zone()

# def send_to_clipboard(clip_type, data):


def add_text_to_file(translated):
    file = open("pastebin.txt", "a")  # storage file
    file.write(translated)
    file.write(DELIMITER)
    file.close()


def read_text_from_file():
    """returns list of strings, taken from the file where strings are separated by DELIMITER"""
    global text_array
    file = open("pastebin.txt", "r")
    text_full_string = file.read()
    #print(text_full_string)
    file.close()
    text_array = text_full_string.split(DELIMITER)
    text_array.pop()  # remove last element, because it's an empty string.
#   better solution will require some intelligence in placing beautiful delimiter
    return text_array


def refresh_pad():
    global text_array
    #text_array = read_text_from_file()
    print(text_array[position], position)
    textEditor.configure(state=tk.NORMAL)
    textEditor.delete('1.0', tk.END)
    textEditor.insert(tk.INSERT, (str(position) + "\n"))
    textEditor.insert(tk.INSERT, text_array[position])
    textEditor.grid(row=2, column=0, columnspan=5, ipadx=10, ipady=10, sticky=tk.NSEW)
    mygui.grid_rowconfigure(2, weight=50)
    mygui.grid_columnconfigure(5,weight=20)
    textEditor.configure(state=tk.DISABLED)


def print_prev():
    global position, text_array
    print(position)
    position = position - 1
    if position < 0:
        position = len(text_array) - 1
    #position = position-1
    refresh_pad()


def print_next():
    global position, text_array
    print(position)
    position = position + 1
    if position >= len(text_array):
        position = 0
    refresh_pad()


def select_zone():
    """performs necessary action to select zone for screenshot (red selection over new Toplevel)"""
    global troot, oldgeo, tcanvas, rect_id, dimensions, topx, topy, botx, boty
    troot = tk.Toplevel(mygui)
    troot.attributes('-fullscreen', True)
    troot.wm_attributes('-alpha', 0.3)
    troot.geometry(str(mygui.winfo_screenwidth()) + 'x' + str(mygui.winfo_screenheight()) + '+0+0')
    tcanvas = tk.Canvas(troot, bg="lightgreen")
    tcanvas.pack(fill=tk.BOTH, expand=True)
    troot.bind('<Button-1>', get_mouse_posn)
    troot.bind('<B1-Motion>', update_sel_rect)
    troot.bind('<ButtonRelease-1>', stop_updating)
    rect_id = tcanvas.create_rectangle(0, 0, 0, 0, fill='red')


def screen_zone():
    """takes screenshot, returns picture (ImageGrab) or an error"""
    global status_line, text_array, position
    dimensions = (topx, topy, botx, boty)
    tdimensions = tuple(map(int, dimensions))
    try:
        if (dimensions):
            print(tuple(map(int, dimensions)))
            image = ImageGrab.grab(bbox=tdimensions)
            # print(type(image),len(image)) # imange has no length! such string will cause except
            eng_string=pytesseract.image_to_string(image, lang='eng')
            eng_string=eng_string.replace('\n\n', 'DOUBLECARR555')
            eng_string=eng_string.replace('\n', '')
            eng_string=eng_string.replace('DOUBLECARR555', '\n\n')
            if len(eng_string)>=5000:
                print(len(eng_string), err5000)
                status_line.configure(text = err5000)
                status_line.grid(row=0, columnspan=5, sticky=tk.NSEW)
                # translated = None
                # TODO - split large chunks to <5k symbols pieces for translation
            else:
                status_line.configure(text = '')
                status_line.grid(row=0, columnspan=5, sticky=tk.NSEW)
                translated = GoogleTranslator(source=LANG_SOURCE, target=LANG_DEST).translate(text=eng_string)
                #translated = PonsTranslator(source=LANG_SOURCE, target=LANG_DEST).translate(text=eng_string)
                print(repr(translated))
                text_array.append(translated)
                position=position+1
                #add_text_to_file(translated)
                refresh_pad()
        else:
            print("no dimensions")

    except Exception as e:
        print(e)
        return e


mygui = tk.Tk()
mygui.configure(background='lightgreen', )
if 'mywindowgeometry' != None:
    mygui.geometry(mywindowgeometry)
else:
    pass

style = ttk.Style(mygui)
style.theme_use('clam')
style.configure("TButton", background ="orange", foreground ="black")

mygui.title("Piece of screen translater")
mygui.resizable(True,True)

status_line = ttk.Label(mygui)
status_line.grid(row=0, columnspan=5, sticky=tk.NSEW)

crop_button = ttk.Button(mygui, text="Select\narea", command=select_zone, style="TButton")
                        #padx=10, width=7, height=4)
re_button = ttk.Button(mygui, text="Re-capture", command=screen_zone, style="TButton")
                        #padx=10, width=7, height=4)
save_button = ttk.Button(mygui, text="add to pastebin.txt",
                         command=add_text_to_file, style="TButton")
prev_button = ttk.Button(mygui, text="Previous", command=print_prev, style="TButton")#,
                        #padx=10, width=7, height=4)
next_button = ttk.Button(mygui, text="Next", command=print_next, style="TButton")#,
                        #padx=10, width=7, height=4)
crop_button.grid(row=1, column=0, ipadx=10, ipady=10, sticky=tk.NSEW)
re_button.grid(row=1, column=1, ipadx=10, ipady=20, sticky=tk.NSEW)
save_button.grid(row=1, column=2, ipadx=10, ipady=20, sticky=tk.NSEW)
prev_button.grid(row=1, column=3, ipadx=10, ipady=20, sticky=tk.NSEW)
next_button.grid(row=1, column=4, ipadx=10, ipady=20, sticky=tk.NSEW)

textEditor = scrolledtext.ScrolledText(mygui, font=("Nirmala UI", 11), wrap=tk.WORD,
                     fg="LightSteelBlue1", bg="grey17")

refresh_pad()

mygui.mainloop()
