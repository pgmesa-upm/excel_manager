# pylint: disable=C0103,C0111,W0614,W0401,C0200,C0325
from tkinter import *
from tkinter import ttk
import tkinter.messagebox as tkMessageBox
import tkinter.filedialog as tkFileDialog
import tkinter.font as tkFont
import csv
from pathlib import Path

import excel
import config
from crypt_utilities.asymmetric import rsa_encrypt, rsa_decrypt
from .protected_data import get_encrypted, hash_and_save_encrypted, hash_sheet_ids_and_save

# codigo base: https://github.com/ssebs/csveditor

##
#   TODO: Add + / - buttons to create/remove rows & coloumns
#   TODO: Add resizing of cells
##

class CSVEditor(Frame):

    cellList = []
    currentCells = []
    currentCell = None

    def __init__(self, master=None, font_size=10, private_key=None, public_key=None, sensitive_fields:list=None, hide_fields:list=[]):
        Frame.__init__(self, master)
        self.private_key = private_key
        self.public_key = public_key
        self.sensitive_fields = sensitive_fields
        self.current_path_file = None
        self.current_title = None
        self.font_size = font_size
        self.hide_fields = hide_fields
        self.hidded_indexes = {}
        #self.grid()
        #self.createDefaultWidgets()
        

    def focus_tab(self, event):
        event.widget.tk_focusNext().focus()
        return "break"

    def focus_sh_tab(self, event):
        event.widget.tk_focusPrev().focus()
        return "break"

    def focus_right(self, event):
        #event.widget.tk_focusNext().focus()
        widget = event.widget.focus_get()

        for i in range(len(self.currentCells)):
            for j in range(len(self.currentCells[0])):
                if widget == self.currentCells[i][j]:
                    if(j >= len(self.currentCells[0]) - 1 ):
                        j = -1    
                    self.currentCells[i][j+1].focus()
        return "break"

    def focus_left(self, event):
        #event.widget.tk_focusNext().focus()
        widget = event.widget.focus_get()

        for i in range(len(self.currentCells)):
            for j in range(len(self.currentCells[0])):
                if widget == self.currentCells[i][j]:
                    if(j == 0):
                        j = len(self.currentCells[0])    
                    self.currentCells[i][j-1].focus()
        return "break"

    def focus_up(self, event):
        #event.widget.tk_focusNext().focus()
        widget = event.widget.focus_get()

        for i in range(len(self.currentCells)):
            for j in range(len(self.currentCells[0])):
                if widget == self.currentCells[i][j]:
                    if(i < 0):
                        i = len(self.currentCells)
                    self.currentCells[i-1][j].focus()
        return "break"

    def focus_down(self, event):
        #event.widget.tk_focusNext().focus()
        widget = event.widget.focus_get()

        for i in range(len(self.currentCells)):
            for j in range(len(self.currentCells[0])):
                if widget == self.currentCells[i][j]:
                    if( i >= len(self.currentCells) - 1):
                        i = -1
                    self.currentCells[i+1][j].focus()
        return "break"

    def selectall(self, event):
        event.widget.tag_add("sel", "1.0", "end")
        event.widget.mark_set(INSERT, "1.0")
        event.widget.see(INSERT)
        return "break"

    def saveFile(self, event):
        self.saveCells()

    # TODO: Create bind for arrow keys and enter

    def add_row(self):
        # TODO: Acabar esta funcion (incompleta)
        # -> sacar w y h de las cldas que se estan mostrando
        # -> configurar celdas nuevas con los eventos de teclado, fuente etc... (config_cels())
        # -> añadirlas correctamente a currentCells
        # first_cell = self.currentCells[0][0] 
        # w, h = first_cell.winfo_width, first_cell.winfo_height
        # new_row = [Text(self, width=w, height=h).insert(END, "")]*len(self.currentCells[0])
        # self.currentCells.insert(len(self.currentCells), new_row)
        ...
        
    def config_cell(self, cell):
        ...
    
    def createDefaultWidgets(self):
        w, h = 7, 1
        self.sizeX = 4
        self.sizeY = 6
        self.defaultCells = []
        for i in range(self.sizeY):
            self.defaultCells.append([])
            for j in range(self.sizeX):
                self.defaultCells[i].append([])

        for i in range(self.sizeY):
            for j in range(self.sizeX):
                tmp = Entry(self,)
                tmp.bind("<Tab>", self.focus_tab)
                tmp.bind("<Shift-Tab>", self.focus_sh_tab)
                tmp.bind("<Return>", self.focus_down)
                tmp.bind("<Shift-Return>", self.focus_up)
                tmp.bind("<Right>", self.focus_right)
                tmp.bind("<Left>", self.focus_left)
                tmp.bind("<Up>", self.focus_up)
                tmp.bind("<Down>", self.focus_down)
                tmp.bind("<Control-a>", self.selectall)
                tmp.bind("<Control-s>", self.saveFile)
                #TODO: Add resize check on column when changing focus
                tmp.insert(END, "")
                tmp.grid(padx=0, pady=0, column=j, row=i)
                
                tmp.config(font=("Helvetica", self.font_size))

                self.defaultCells[i][j] = tmp
                self.cellList.append(tmp)

        self.defaultCells[0][0].focus_force()
        self.currentCells = self.defaultCells
        self.currentCell = self.currentCells[0][0]

        # TODO: Add buttons to create new rows/columns

    def newCells(self):
        self.removeCells()
        self.createDefaultWidgets()

    def removeCells(self):
        while(len(self.cellList) > 0):
            for cell in self.cellList:
                # print str(i) + str(j)
                cell.destroy()
                self.cellList.remove(cell)
        self.currentCells = []
        self.currentCell = None

    def loadCells(self, filepath=None, only_headers=False, title=None):
        if filepath is None:
            filepath = tkFileDialog.askopenfilename(initialdir=".", title="Select file",
                                                filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
        self.current_path_file = filepath
        if title is not None:
            self.master.title(title)
            self.current_title = title
        ary = []
        col = -1
        rows = []

        # get array size & get contents of rows
        with open(filepath, "r") as csvfile:
            rd_generator = csv.reader(csvfile, delimiter=",", quotechar='"')
            rd = []
            for row in rd_generator: rd.append(row)
            num_rows = len(rd)
            self.master.title(self.current_title + " -> Size = " + str(num_rows-1))
            if self.private_key is None:
                headers = rd[0]
                hide_headers = []
                for header in self.hide_fields:
                    if header in headers: 
                        h_index = headers.index(header)
                        self.hidded_indexes[h_index] = header
                        hide_headers.append(header)
                for h in hide_headers:
                    headers.remove(h)
                col = len(headers)
                rows.append(headers)
                for _ in range(6):
                    ary.append([])
                    rows.append([""]*col)
            else:
                for row in rd:
                    ary.append([])
                    decrypted = False; posible_row = []
                    for val in row:
                        if self.private_key is not None:
                            ciphertext = get_encrypted(val.encode()); 
                            if ciphertext is not None:
                                val = rsa_decrypt(ciphertext, self.private_key).decode()
                                decrypted = True
                        posible_row.append(val)
                    if decrypted: row = posible_row
                    col = len(row)
                    rows.append(row)
        
        # create the array
        for i in range(len(ary)):
            for j in range(col):
                ary[i].append([])

        # fill the array
        for i in range(len(ary)):
            for j in range(col):
                # print rows[i][j]
                ary[i][j] = rows[i][j]

        self.removeCells()

        # get the max width of the cells
        mx = 0
        for i in range(len(ary)):
            for j in range(len(ary[0])):
                if(len(ary[i][j]) >= mx):
                    mx = len(ary[i][j])
        w = mx
        if w < 20: w = 20

        loadCells = []
        for i in range(len(ary)):
            loadCells.append([])
            for j in range(len(ary[0])):
                loadCells[i].append([])
                

        headers = []
        # create the new cells
        for i in range(len(ary)):
            for j in range(len(ary[0])):
                tmp = Text(self, width=w, height=1)
                tmp.bind("<Tab>", self.focus_tab)
                tmp.bind("<Shift-Tab>", self.focus_sh_tab)
                tmp.bind("<Return>", self.focus_down)
                tmp.bind("<Shift-Return>", self.focus_up)
                tmp.bind("<Control-Right>", self.focus_right)
                tmp.bind("<Control-Left>", self.focus_left)
                tmp.bind("<Up>", self.focus_up)
                tmp.bind("<Down>", self.focus_down)
                tmp.bind("<Control-a>", self.selectall)
                tmp.bind("<Control-s>", self.saveFile)
                # Vemos si solo ponemos las cabeceras
                val = ary[i][j]
                
                tmp.insert(END, val)
                    
                if(i == 0):
                    tmp.config(font=("Helvetica", self.font_size, tkFont.BOLD))
                    tmp.config(relief=FLAT, bg=self.master.cget('bg'))
                else:
                    tmp.config(font=("Helvetica", self.font_size))

                loadCells[i][j] = tmp
                tmp.focus_force()
                self.cellList.append(tmp)

                tmp.grid(padx=0, pady=0, column=j, row=i)
            
        self.currentCells = loadCells
        self.currentCell = self.currentCells[0][0]


    def saveCells(self):
        filepath = self.current_path_file
        if filepath is None:
            filepath = tkFileDialog.asksaveasfilename(initialdir=".", title="Save File", filetypes=(
                ("csv files", "*.csv"), ("all files", "*.*")), defaultextension=".csv")
            self.current_path_file = filepath

        mode = 'a'
        if self.private_key is not None:
            mode = 'w'
        
        self.master.title("Encriptando y Guardando (puede tardar)...")
        headers = []; vals = []
        ids_to_hash = {}
        for i in range(len(self.currentCells)):
            inserted_indexes = []
            z = 0
            for j in range(len(self.currentCells[0])): 
                # Añadimos los campos omitidos
                if j in self.hidded_indexes and j not in inserted_indexes:
                    z = j;
                    while z in self.hidded_indexes: 
                        if i == 0:
                            headers.append(self.hidded_indexes[z])
                        else:
                            vals.append("")
                        inserted_indexes.append(z); z+=1
                # Vemos si hay que encriptar
                val = self.currentCells[i][j].get(1.0, END).strip()
                if i != 0 and config.is_id_field(headers[z]) and val != "":
                    sheet_name = Path(self.current_path_file).name.removesuffix(".csv")
                    if sheet_name not in ids_to_hash:
                        ids_to_hash[sheet_name] = [val]
                    else:
                        ids_to_hash[sheet_name].append(val)
                if i == 0:
                    headers.append(val)
                elif headers[z] in self.sensitive_fields and self.public_key is not None and val != "":
                    ciphertext = rsa_encrypt(val.encode(), self.public_key)
                    salted_hash = hash_and_save_encrypted(ciphertext)
                    val = salted_hash.decode()
                z+=1
                if i == 0 and mode == 'a': continue
                vals.append(val);
        if len(ids_to_hash) > 0:
            for sheet_name, array in ids_to_hash.items():
                for elem in array:
                    found = excel.check_id_value(elem, sheet_n=sheet_name)
                    if len(found) == 1:
                        id_field = config.get("id_field")
                        tkMessageBox.showinfo("", f"ERROR: {id_field} '{elem}' already exist in '{sheet_name}' line {found[sheet_name]}")
                        return
                hash_sheet_ids_and_save(sheet_name, array, override=False)
                    
                
        num_rows = len(self.currentCells); num_colums = len(headers)
        if mode == 'a': num_rows -= 1
        
        with open(filepath, mode) as csvfile:
            for rw in range(num_rows):
                row = ""; empty = True
                for i in range(num_colums):
                    x = rw * num_colums
                    val = vals[x + i]
                    if val != "": empty = False
                    if(i != num_colums - 1):
                        row += val + ","
                    else:
                        row += val
                if empty: continue
                csvfile.write(row + "\n")
        self.master.title(self.current_title)
        o_h = True if self.private_key is None else False
        self.loadCells(filepath=self.current_path_file, only_headers=o_h)
        tkMessageBox.showinfo("", "Saved!")

# End Application Class #


    
