
import pygame
from tkinter import ttk 
from .inputs import InputBox

# --------------GLOABAL VARIABLE CONFIGURATION----------------
WHITE = (255, 255, 255)
GREY = (70, 70, 70)
DARK_GREEN = (100, 140, 0)
LIGHT_GREEN = (0, 255, 0)
YELLOW = (198,206,0)
RED = (178,34,34)
BLUE = (0,191,255)
BLACK = (30, 30, 30)
# BLACK = (0,0,0)

# ------Screen configuration and display-----
# The (0,0)px screenCoord is located in the left-top corner
screenWidth = 1500; screenHeight = 600
screenSize = [screenWidth, screenHeight]

# ------------------------------------------------------------------------------------
# ----- Funciones para mostrar las opciones de partida -----
def showOptions(screen):
    posGenerator = _calcDisplayOfOption(3)
    rect1 = _showText(screen, "Elige un modo:", WHITE, BLACK, screenWidth/2, next(posGenerator),40, True)
    rect2 = _showText(screen, "=> Modo Usuario", BLACK,WHITE, screenWidth/2, next(posGenerator),40, True)
    rect3 = _showText(screen, "=> Modo Administrador",BLACK, WHITE, screenWidth/2, next(posGenerator),40, True)
    
    return [rect1,rect2,rect3]

def show_user_actions(screen):
    posGenerator = _calcDisplayOfOption(3)
    rect1 = _showText(screen, "Selecciona una acción", WHITE, BLACK, screenWidth/2, next(posGenerator),40, True)
    rect2 = _showText(screen, "=> Añadir", BLACK,WHITE, screenWidth/2, next(posGenerator),40, True)
    rect3 = _showText(screen, "=> Comprobar si 'ID' ya existe",BLACK, WHITE, screenWidth/2, next(posGenerator),40, True)
    
    return [rect1,rect2,rect3]

def showInput(screen, order:int, width=140, height=32) -> InputBox:
    posGenerator = _calcDisplayOfOption(order)
    for _ in range(order-1):
        next(posGenerator) # Queremos el ultimo solo
    
    box = InputBox((screenWidth/2) - width, next(posGenerator), width, height)
    box.draw(screen)
    
    return box

def show_msg(screen, msg:str, color=WHITE, backgroundColor=BLACK, fontSize=25, order=1):
    posGenerator = _calcDisplayOfOption(order)
    for _ in range(order-1): next(posGenerator) # Nos interesa el ultimo
    rect = _showText(screen, msg, color, backgroundColor, screenWidth/2, next(posGenerator), fontSize, True)
    
    return rect

def _calcDisplayOfOption(numOptions):
    global screenHeight
    reduc = 200
    button_group_height = screenHeight - reduc
    centralPosOfRect = 0
    for i in range(numOptions):
        centralPosOfRect = button_group_height*((1/2)+i)/numOptions + reduc/2
        yield centralPosOfRect
    
def _showText(screen, text,color, backgroundColor, x,y, fontSize, RETURN=False):
    font = pygame.font.Font('freesansbold.ttf', fontSize)
    if backgroundColor == None:  
        text = font.render(text, True, color)
    else:
        text = font.render(text, True, color, backgroundColor)
    textRect = text.get_rect()
    textRect.center = (x, y)
    screen.blit(text,textRect)
    if RETURN:
        return textRect

# ----Funcion para configurar la pantalla una vez se reajusta el tamaño ----
def configureScreen(size):
    global screenWidth, screenHeight, screenSize, initX, initY, squareSide
    screenWidth = size[0]
    screenHeight = size[1]
    screenSize = size
    squareSide = int(screenHeight/10)
    initX = int((screenWidth - squareSide*8)/2)
    initY = squareSide
    pygame.display.set_mode(size, pygame.RESIZABLE)

from tkinter import *
import tkinter.messagebox as tkMessageBox
import tkinter.filedialog as tkFileDialog
import tkinter.font as tkFont
from pathlib import Path
from typing import Dict, List, Tuple, Union
from editor.csv_editor import CSVEditor

def showTextBoxMsg(msg:str, title:str=""):
    tkMessageBox.showinfo(title, msg)

# Custom Editor
def showCustomEditor(csv_group_label:str, csv_paths:Dict={}, rsa_key_pairs:Tuple=None, sensitive_fields=[], hide_fields=[]):
    
    win = Tk()

    wrapper1 = LabelFrame(win)
    #wrapper2 = LabelFrame(win)

    my_canvas = Canvas(wrapper1, relief='ridge', highlightthickness=0)
    my_canvas.pack(side=LEFT, fill="both", expand="yes")
    
    font_size = 13
    if rsa_key_pairs[0] is None:
        font_size = 14
        
    def calc_window_size(myframe:CSVEditor):
        cell_width = myframe.currentCell.winfo_reqwidth()
        cell_height = myframe.currentCell.winfo_reqheight()

        rows = len(myframe.currentCells)
        colums = len(myframe.currentCells[0])
        w_offset = 40
        h_offset = 45
        window_w = colums*cell_width+w_offset; window_h = rows*cell_height+h_offset
        max_w_size = 1000; max_h_size = 500
        if window_w > max_w_size: window_w = max_w_size
        if window_h > max_h_size: window_h = max_h_size
        
        return window_w, window_h
        
    # ------ APP CONFIGURATION -------
    myframe = CSVEditor(
        master=win,
        font_size=font_size, 
        private_key=rsa_key_pairs[0],
        public_key=rsa_key_pairs[1],
        sensitive_fields=sensitive_fields,
        hide_fields=hide_fields
    )
    menubar = Menu(myframe)

    filemenu = Menu(menubar, tearoff=0)
    #filemenu.add_command(label="New", command=app.newCells)     # add save dialog
    # add save dialog
    #filemenu.add_command(label="Open", command=app.loadCells)
    # filemenu.add_command(label="Add Row", command=app.add_row)
    filemenu.add_command(label="Save", command=myframe.saveCells)
    #filemenu.add_command(label="Save as", command=app.saveCells)
    menubar.add_cascade(label="File", menu=filemenu)
    
    def update_sheet_display(myframe:CSVEditor, filepath, only_headers, title):
        window_w, window_h = calc_window_size(myframe) 
        myframe.master.geometry(f"{window_w}x{window_h}")
        myframe.loadCells(filepath=filepath, only_headers=only_headers, title=title)
    
    sheetsmenu = Menu(menubar,tearoff=0)
    only_headers = True if rsa_key_pairs[0] is None else False
    for label, path in csv_paths.items(): 
        sheetsmenu.add_command(
            label=label, 
            command=lambda bound_path=path, bound_label=label, bframe=myframe: 
                update_sheet_display(bframe, bound_path, only_headers, bound_label)
        )
    menubar.add_cascade(label=csv_group_label, menu=sheetsmenu)
    
    myframe.master.config(menu=menubar)

    default_font = tkFont.nametofont("TkTextFont")
    default_font.configure(family="Helvetica")

    myframe.option_add("*Font", default_font)
    main_path = None
    if bool(csv_paths):
        label = list(csv_paths.keys())[0]
        main_path = csv_paths[label]
        myframe.loadCells(filepath=main_path, only_headers=only_headers, title=label)
    else:
        myframe.defaultCells()  
    # ------ END APP CONFIGURATION -------
    
    my_canvas.create_window((0,0), window=myframe)
    
    yscrollbar = ttk.Scrollbar(win, orient="vertical", command=my_canvas.yview)
    yscrollbar.pack(side=RIGHT, fill="y")

    xscrollbar = ttk.Scrollbar(win, orient="horizontal", command=my_canvas.xview)
    xscrollbar.pack(side=BOTTOM, fill="x")

    my_canvas.configure(xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set)
    my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox('all')))
    # TODO: Arreglar scroll del mouse
    # def _on_mousewheel(event):
    #     my_canvas.yview_scroll(-1*(event.delta/120), "units")
    # my_canvas.bind("<MouseWheel>", _on_mousewheel)

    wrapper1.pack(fill="both", expand="yes", padx=10, pady=10)

    window_w, window_h = calc_window_size(myframe) 
    
    win.geometry(f"{window_w}x{window_h}")
    win.resizable(False, False)
    win.mainloop()
    
    
    # # When closing (doesn't work)
    # root = Tk()
    # root.protocol("WM_DELETE_WINDOW", lambda: app.destroy())
    
    
    
