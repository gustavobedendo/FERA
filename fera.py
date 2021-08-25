# -*- coding: utf-8 -*-
"""
Created on Sun Sep 27 14:39:11 2020

@author: gustavo.bedendo
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Sep 16 13:45:26 2020

@author: gustavo.bedendo
"""
import tkinter #as tk
import time, re
from tkinter import ttk
import tkinter.font as tkfont
import fitz
import math
import multiprocessing as mp
import queue as queue
from PIL import Image, ImageTk
from tkinter.filedialog import askopenfilename, asksaveasfilename, askopenfilenames
import subprocess, os, platform
from pathlib import Path
import webbrowser
import clipboard
from io import BytesIO
import traceback
import sqlite3
import sys
import logging
from indexador_fera import showInfo
import indexador_fera
from functools import partial
import shutil
import csv
import xlsxwriter
import binascii, io
import struct
global version
import rtfunicode

#import imagetortf
#from PyRTF.Elements import Document
#import printer_interface
#from PyRTF.document.section import Section
#from PyRTF.document.paragraph import Cell, Paragraph, Table
try:
    from win32api import GetMonitorInfo, MonitorFromPoint
    import win32clipboard
except Exception as ex:
    None
    #printlogexception(ex=ex)
    #logging.exception('!')
import xml.etree.ElementTree as ET




version = 'v1.46-24082021'
plt = platform.system()

global processes, searchprocesses, expertmode, lockmanipulation, lockzoom, iduser, env
iduser = -1
env = None
if(plt == "Linux"):
    env = dict(os.environ)  # make a copy of the environment
    lp_key = 'LD_LIBRARY_PATH'  # for GNU/Linux and *BSD.
    lp_orig = env.get(lp_key + '_ORIG')
    if lp_orig is not None:
        env[lp_key] = lp_orig  # restore the original, unmodified value
    else:
        # This happens when LD_LIBRARY_PATH was not set.
        # Remove the env var as a last resort:
        env.pop(lp_key, None)
expertmode = True
lockmanipulation = False
lockzoom = False
processes = {}
searchprocesses = {}
printorlog = 'none'

def popupcomandook(sair, window):
    if(sair):
        window.destroy()
        on_quit()
    else:
        window.destroy()
    
def popup_window(texto, sair):
    global warningimage
    window = tkinter.Toplevel()
    label = tkinter.Label(window, text=texto, image=warningimage, compound='top')
    label.pack(fill='x', padx=50, pady=20)
    button_close = tkinter.Button(window, text="OK", command= lambda : popupcomandook(sair, window))
    button_close.pack(fill='y', pady=20) 

class Observation():
    def __init__(self, paginainit, paginafim, p0x, p0y, p1x, p1y, tipo, pathpdf, idobs):
        self.paginainit = paginainit
        self.paginafim = paginafim
        self.p0x = p0x
        self.p0y = p0y
        self.p1x = p1x
        self.p1y = p1y
        self.tipo = tipo
        self.pathpdf = pathpdf
        self.idobs = idobs

class CreateToolTip(object):
    '''
    create a tooltip for a given widget
    '''
    def __init__(self, widget, text='widget info', istreeview=False, classe=''):
        try:
            self.istreeview = istreeview
            self.widget = widget
            self.text = text
            self.tw = None
            if(istreeview):
                self.widget.bind_class(classe,"<Motion>",self.enter)
                self.widget.bind_class(classe,"<Enter>",self.enter)
                self.widget.bind_class(classe,"<Leave>",self.close)
            else:
                self.widget.bind("<Enter>", self.enter)
                self.widget.bind("<Leave>", self.close)
                
        except Exception as ex:
            printlogexception(ex=ex)
        

    def enter(self, event=None):
        try:
            if self.tw:
                self.tw.destroy()
            x = y = 0
            x = event.x
            y = event.y
            x += self.widget.winfo_rootx() + 25
            y += self.widget.winfo_rooty() + 20
            
            if(self.istreeview):
                iid = self.widget.identify_row(event.y)
                if(self.widget.tag_has('resultsearch', iid)):
                    texto = self.widget.item(iid, 'values')
                    if(len(texto)<=1):
                       return
                    self.tw = tkinter.Toplevel(self.widget)
                    self.tw.rowconfigure(0, weight=1)
                    self.tw.columnconfigure((0, 2), weight=1)
                    # Leaves only the label and removes the app window
                    self.tw.wm_overrideredirect(True)
                    self.tw.wm_geometry("+%d+%d" % (x, y))
                    label1 = tkinter.Label(self.tw, text=texto[0], justify='left', padx = 0,
                                   background='#ededd3', relief='solid', borderwidth=0,
                                   font=("times", "10", "normal"))
                    label2 = tkinter.Label(self.tw, text=texto[1], justify='left',
                                   background='#ededd3', relief='solid', borderwidth=0,padx = 0,
                                   font=("times", "10", "bold"))
                    label3 = tkinter.Label(self.tw, text=texto[2], justify='left',
                                   background='#ededd3', relief='solid', borderwidth=0,padx = 0,
                                   font=("times", "10", "normal"))
                    label1.grid(row=0, column=0, sticky='ew', padx=0)
                    label2.grid(row=0, column=1, sticky='ew', padx=0)
                    label3.grid(row=0, column=2, sticky='ew', padx=0)
                    return
                else:
                    if(len(self.widget.item(iid, 'text'))<=1):
                       return
                    self.text = self.widget.item(iid, 'text')    
            self.tw = tkinter.Toplevel(self.widget)
            # Leaves only the label and removes the app window
            self.tw.wm_overrideredirect(True)
            self.tw.wm_geometry("+%d+%d" % (x, y))
            label = tkinter.Label(self.tw, text=self.text, justify='left',
                           background='#ededd3', relief='solid', borderwidth=1,
                           font=("times", "8", "normal"))
            label.pack(ipadx=1)
        except Exception as ex:
            printlogexception(ex=ex)

    def close(self, event=None):
        if self.tw:
            self.tw.destroy()

class PlaceholderEntry(ttk.Entry):
    def __init__(self, container, placeholder, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.placeholder = placeholder
        self.insert("0", self.placeholder)
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)

    def _clear_placeholder(self, e):
        if(super().get()=='Buscar...' or super().get()=="Aguarde, pesquisando..."):
            self.delete("0", "end")

    def _add_placeholder(self, e):
        if not self.get():
            self.insert("0", self.placeholder)
        
 
class querySqlWindow():
    def __init__(self,master, valor):
        self.value=None
        top=self.top=tkinter.Toplevel(master)
        self.top.rowconfigure((0,1,2,3,4), weight=1)
        self.top.columnconfigure((0,1), weight=1)
        self.l=tkinter.Label(top,text="SELECT (........) FROM (......) WHERE (.....) MATCH <CONTINUAR ABAIXO>")
        self.l.grid(row=0, column=0, columnspan=2, sticky='ns', pady=5)
        self.cattextvariable = tkinter.StringVar()
        self.cattextvariable.set(valor)
        self.e=tkinter.Entry(top, width=100, textvariable=self.cattextvariable, justify='center')
        self.e.focus_set()
        self.e.grid(row=1, column=0, columnspan=2, sticky='nsew', pady=5)
        if getattr(sys, 'frozen', False):
            application_path = sys._MEIPASS
        elif __file__:
            application_path = os.path.dirname(os.path.abspath(__file__))
        try:
            fts5tut = os.path.join(application_path,"fts4tutorial.png")
            self.imgtutorial = ImageTk.PhotoImage(file=fts5tut)
            self.tutorial = tkinter.Label(top, image=self.imgtutorial)
            self.tutorial.grid(row=2, column=0, sticky='nsew', columnspan=2, pady=5)
        except Exception as ex:
            fts5tut = os.path.join(os.getcwd(),"fts4tutorial.png")
            self.imgtutorial = ImageTk.PhotoImage(file=fts5tut)
            self.tutorial = tkinter.Label(top, image=self.imgtutorial)
            self.tutorial.grid(row=2, column=0, sticky='nsew', columnspan=2, pady=5)
        self.aviso = tkinter.Label(top, text='As aspas simples EXTERNAS não são necessárias, pois são adicionadas automaticamente!')
        self.aviso.grid(row=3, column=0, sticky='ns', columnspan=2, pady=5)
        self.bok=tkinter.Button(top,text='Ok',command=self.ok)
        self.bok.grid(row=4, column=0, sticky='ns', pady=5)
        self.bcancel=tkinter.Button(top,text='Cancelar',command=self.cancel)
        self.bcancel.grid(row=4, column=1, sticky='ns', pady=5)
        
    def ok(self):
        self.value=self.cattextvariable.get()
        self.top.destroy()
    def cancel(self):
        self.value=None
        self.top.destroy()

class popupWindow(object):
    def __init__(self,master, valor):
        self.value=None
        top=self.top=tkinter.Toplevel(master)
        self.top.rowconfigure((0,1,2), weight=1)
        self.top.columnconfigure((0,1), weight=1)
        self.l=tkinter.Label(top,text="Nome da categoria:")
        self.l.grid(row=0, column=0, columnspan=2, sticky='ns', pady=20)
        self.cattextvariable = tkinter.StringVar()
        self.cattextvariable.set(valor)
        self.e=tkinter.Entry(top, width=100, textvariable=self.cattextvariable, justify='center')
        self.e.focus_set()
        self.e.grid(row=1, column=0, columnspan=2, sticky='nsew')
        self.bok=tkinter.Button(top,text='Ok',command=self.ok)
        self.bok.grid(row=2, column=0, sticky='ns', pady=20)
        self.bcancel=tkinter.Button(top,text='Cancelar',command=self.cancel)
        self.bcancel.grid(row=2, column=1, sticky='ns', pady=20)
        self.e.bind('<Return>',  lambda e: self.ok())
    def ok(self):
        self.value=self.cattextvariable.get()
        self.top.destroy()
    def cancel(self):
        self.value=None
        self.top.destroy()

class CustomFrame(tkinter.Frame):
    def __init__(self, master=None, cnf={}, **kw):
        super(CustomFrame, self).__init__(master=master, cnf={}, **kw)

class CustomCanvas(tkinter.Canvas):
    def __init__(self, master=None, scroll=None, **kw):
        super(CustomCanvas, self).__init__(master=master, **kw)        
    def yview(self, *args):
        """Query and change the vertical position of the view."""
        global infoLaudo, pathpdfatual, zoom
        res = self.tk.call(self._w, 'yview', *args)
        atual = (self.program.vscrollbar.get()[0]*infoLaudo[pathpdfatual].len)
        restoemdeslocy = (atual%1.0)*infoLaudo[pathpdfatual].pixorgh
        flooratual = math.floor(atual)
        pai = Path(Path(pathpdfatual).parent).parent
        paibase = os.path.basename(pai)
        tocx = None
        for eq in self.program.treeviewEqs.get_children():
            valorespai = (self.program.treeviewEqs.item(eq, 'values'))
            if(valorespai[1]==paibase):
                #self.program.treeviewEqs.item(eq, open=True)
                for rel in self.program.treeviewEqs.get_children(eq):
                    valoresrel = (self.program.treeviewEqs.item(rel, 'values'))
                    if(os.path.basename(valoresrel[1])==os.path.basename(pathpdfatual)):
                        
                        #self.program.treeviewEqs.item(rel, open=True)
                        for toc in self.program.treeviewEqs.get_children(rel):
                            valorestoc = (self.program.treeviewEqs.item(toc, 'values'))
                            
                            if(int(valorestoc[3])*infoLaudo[pathpdfatual].pixorgh+int(valorestoc[4]) > flooratual*infoLaudo[pathpdfatual].pixorgh+restoemdeslocy):
                                break
                            tocx = toc
        if(tocx!=None):
            if(self.program.treeviewEqs.item(self.program.treeviewEqs.parent(tocx), 'open')):
                self.program.treeviewEqs.selection_set(tocx)
            else:
                self.program.treeviewEqs.selection_set(self.program.treeviewEqs.parent(tocx))                          
        #atual = round(atual)
        #self.program.pagVar.set(str(atual+1))    
        atual = round((self.program.vscrollbar.get()[0]*infoLaudo[pathpdfatual].len))
        self.program.pagVar.set(atual+1)
        if not args:
            return self._getdoubles(res)        
        
    def yview_moveto(self, fraction, qlpdf=None):
        global infoLaudo, pathpdfatual
        """Adjusts the view in the window so that FRACTION of the
        total height of the canvas is off-screen to the top."""
        self.tk.call(self._w, 'yview', 'moveto', fraction)
        
        atual = (self.program.vscrollbar.get()[0]*infoLaudo[pathpdfatual].len)
        restoemdeslocy = (atual%1.0)*infoLaudo[pathpdfatual].pixorgh
        flooratual = math.floor(atual)
        pai = Path(Path(pathpdfatual).parent).parent
        paibase = os.path.basename(pai)
        tocx = None
        for eq in self.program.treeviewEqs.get_children():
            valorespai = (self.program.treeviewEqs.item(eq, 'values'))
            if(valorespai[1]==paibase):
                
                #self.program.treeviewEqs.item(eq, open=True)
                for rel in self.program.treeviewEqs.get_children(eq):
                    valoresrel = (self.program.treeviewEqs.item(rel, 'values'))
                    
                    if(os.path.basename(valoresrel[1])==os.path.basename(pathpdfatual)):
                        
                        #self.program.treeviewEqs.item(rel, open=True)
                        for toc in self.program.treeviewEqs.get_children(rel):
                            valorestoc = (self.program.treeviewEqs.item(toc, 'values'))
                            
                            if(int(valorestoc[3])*infoLaudo[pathpdfatual].pixorgh+int(valorestoc[4]) > flooratual*infoLaudo[pathpdfatual].pixorgh+restoemdeslocy):
                                break
                            tocx = toc
        if(tocx!=None):
            if(self.program.treeviewEqs.item(self.program.treeviewEqs.parent(tocx), 'open')):
                self.program.treeviewEqs.selection_set(tocx)
            else:
                self.program.treeviewEqs.selection_set(self.program.treeviewEqs.parent(tocx))                             
        atual = round((self.program.vscrollbar.get()[0]*infoLaudo[pathpdfatual].len))
        self.program.pagVar.set(atual+1)
        #root.update_idletasks()
        
        

    def yview_scroll(self, number, what):
        global infoLaudo, pathpdfatual
        """Shift the y-view according to NUMBER which is measured in
        "units" or "pages" (WHAT)."""
        self.tk.call(self._w, 'yview', 'scroll', number, what)
        
        atual = (self.program.vscrollbar.get()[0]*infoLaudo[pathpdfatual].len)
        restoemdeslocy = (atual%1.0)*infoLaudo[pathpdfatual].pixorgh
        flooratual = math.floor(atual)
        pai = Path(Path(pathpdfatual).parent).parent
        paibase = os.path.basename(pai)
        tocx = None
        for eq in self.program.treeviewEqs.get_children():
            valorespai = (self.program.treeviewEqs.item(eq, 'values'))            
            if(valorespai[1]==paibase):
                for rel in self.program.treeviewEqs.get_children(eq):
                    valoresrel = (self.program.treeviewEqs.item(rel, 'values'))
                    if(os.path.basename(valoresrel[1])==os.path.basename(pathpdfatual)):                        
                        for toc in self.program.treeviewEqs.get_children(rel):
                            valorestoc = (self.program.treeviewEqs.item(toc, 'values'))                            
                            if(int(valorestoc[3])*infoLaudo[pathpdfatual].pixorgh+int(valorestoc[4]) > flooratual*infoLaudo[pathpdfatual].pixorgh+restoemdeslocy):
                                break
                            tocx = toc
        if(tocx!=None):
            if(self.program.treeviewEqs.item(self.program.treeviewEqs.parent(tocx), 'open')):
                self.program.treeviewEqs.selection_set(tocx)
            else:
                self.program.treeviewEqs.selection_set(self.program.treeviewEqs.parent(tocx))                          
        atual = round((self.program.vscrollbar.get()[0]*infoLaudo[pathpdfatual].len))
        self.program.pagVar.set(atual+1)
        #if(str(atual+1)!=self.program.pagVar.get()):
        #    self.program.pagVar.set(str(atual+1)) 
        #root.update_idletasks()
    def scan_mark(self, x, y):
        """Remember the current X, Y coordinates."""
        self.tk.call(self._w, 'scan', 'mark', x, y)
    def scan_dragto(self, x, y, gain=10):
        """Adjust the view of the canvas to GAIN times the
        difference between X and Y and the coordinates given in
        scan_mark."""
        self.tk.call(self._w, 'scan', 'dragto', x, y, gain)
        
        atual = (self.program.vscrollbar.get()[0]*infoLaudo[pathpdfatual].len)
        restoemdeslocy = (atual%1.0)*infoLaudo[pathpdfatual].pixorgh
        flooratual = math.floor(atual)
        pai = Path(Path(pathpdfatual).parent).parent
        paibase = os.path.basename(pai)
        tocx = None
        for eq in self.program.treeviewEqs.get_children():
            valorespai = (self.program.treeviewEqs.item(eq, 'values'))
            if(valorespai[1]==paibase):
                #self.program.treeviewEqs.item(eq, open=True)
                for rel in self.program.treeviewEqs.get_children(eq):
                    valoresrel = (self.program.treeviewEqs.item(rel, 'values'))
                    if(os.path.basename(valoresrel[1])==os.path.basename(pathpdfatual)):
                        for toc in self.program.treeviewEqs.get_children(rel):
                            valorestoc = (self.program.treeviewEqs.item(toc, 'values'))                            
                            if(int(valorestoc[3])*infoLaudo[pathpdfatual].pixorgh+int(valorestoc[4]) > flooratual*infoLaudo[pathpdfatual].pixorgh+restoemdeslocy):
                                break
                            tocx = toc
        if(tocx!=None):
            if(self.program.treeviewEqs.item(self.program.treeviewEqs.parent(tocx), 'open')):
                self.program.treeviewEqs.selection_set(tocx)
            else:
                self.program.treeviewEqs.selection_set(self.program.treeviewEqs.parent(tocx))
        atual = round((self.program.vscrollbar.get()[0]*infoLaudo[pathpdfatual].len))
        self.program.pagVar.set(atual+1)  
        #if(str(atual+1)!=self.program.pagVar.get()):
        #    self.program.pagVar.set(str(atual+1))
        #root.update_idletasks()

class ResultSearch():
    def __init__(self):
        self.idtermopdf = None
        self.idtermo = None
        self.idpdf = None
        self.snippet = None
        self.init = None
        self.fim = None
        self.pathpdf =None
        self.pagina = None
        self.termo = None
        self.advanced = None
        self.counter = None
        self.fixo = None
        self.lenresults = None
        self.toc = None

class Rect():
    def __init__(self):
        self.image = None
        self.photoimage = None
        self.idrect = None
        self.x0 = None
        self.x1 = None
        self.y0 = None
        self.y1 = None
        self.quads = []
        self.quadsCanvas = []
        self.pagina = None
        self.offset = None
        self.char = []        

class Relatorio():
    def __init__(self):
        self.id = None
        self.toc = []
        self.len = None
        self.pixorgw = None
        self.pixorgh = None 
        self.mt = None
        self.mb = None
        self.me = None
        self.md = None
        self.mapeamento = {}
        self.quadspagina = {}
        self.links = {}
        self.linkscustom = {}
        self.linksporpagina = {}
        self.retangulosDesenhados = {}
        self.widgets = {}
        self.ultimaPosicao = {}
        self.ref_to_page = {}
        self.name_to_dest = {}
        self.tipo = None
        
class RespostaDePaginaXML():
    def __init__(self):
        self.qualPagina = None
        self.mapeamento = None
        self.quadspagina = None
        self.links = None
        self.widgets = None
        self.qualPdf = None        

class RespostaDePagina():
    def __init__(self):
        self.pix = None
        self.imgdata = None
        self.qualPagina = None
        self.qualLabel = None
        self.qualGrid = None
        self.qualPdf = None
        self.zoom = None
        
class PedidoDePagina():
     def __init__(self, qualLabel = None, qualPdf = None, qualPagina = None, matriz = None, \
                  pixheight = None, pixwidth = None, zoom = None, scrollvalue = None ,\
                      scrolltotal = None, canvash = None, mt = None, mb = None, me = None, md = None):
        self.qualLabel = qualLabel
        self.qualPdf = qualPdf
        self.qualPagina = qualPagina
        self.matriz = matriz
        self.pixheight = pixheight
        self.pixwidth = pixwidth
        self.zoom = zoom
        self.scrollvalue = scrollvalue
        self.scrolltotal = scrolltotal
        self.canvash = canvash
        self.mt = mt
        self.mb = mb
        self.me = me
        self.md = md
        
     
def printlogexception(printorlog='none', ex=None):
        if(printorlog=='log'):
            logging.exception('!')
        elif(printorlog=='print'):
            print(ex)
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_tb)
        else:
            None   

class MainWindow():
    
    def fixed_map(self, option):
        # Fix for setting text colour for Tkinter 8.6.9
        # From: https://core.tcl.tk/tk/info/509cafafae
        #
        # Returns the style map for 'option' with any styles starting with
        # ('!disabled', '!selected', ...) filtered out.
    
        # style.map() returns an empty list for missing options, so this
        # should be future-safe.
        return [elm for elm in self.style.map('Treeview', query_opt=option) if
          elm[:2] != ('!disabled', '!selected')]
    
    def __init__(self):
        global  zoom, divididoEm, uniquesearchprocess
        uniquesearchprocess = None
        self.paginaSearchSimple = -1
        self.termossimplespesquisados = {}
        self.primeiroresetbuscar = True
        self.somasnippet = 0
        self.alreadyenhanced = set()
        self.othertags = []
        self.allimages = {}
        self.totalMov = 16
        self.globalFrame = tkinter.PanedWindow(sashwidth=8)
        self.positions = [None] * 10
        self.indiceposition = 0
        self.globalFrame.grid(row=0, column=0, sticky="nsew")
        self.globalFrame.rowconfigure(1, weight=1)
        self.globalFrame.columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        self.ininCanvasesid = [None] * minMaxLabels * divididoEm
        self.tkimgs = [None] * minMaxLabels * divididoEm
        self.fakeImage = None
        self.fakePages = [None] * minMaxLabels
        self.fakeLines = [None] * minMaxLabels
        self.initialPos = None
        self.bg = "#%02x%02x%02x" % (145, 145, 145)
        self.resultfont = tkfont.Font(family='Arial', size=10, weight='normal')
        self.maiorresult = 0
        self.linkscustom = []
        
        
        self.style = ttk.Style()
        self.style.configure("Treeview.Heading", font=(None,10,'bold'), foreground='#525252')
        self.style.configure("Treeview", rowheight=25, indent=10)
        self.style.configure("boldify-results", font=(None, None, 'bold'))
        self.style.configure("unboldify-results", font=(None, None, 'normal'))
        self.style.configure("TNotebook.Tab", font=('Arial', 11, 'bold'))
        self.style.configure("TNotebook.Tab", borderwidth=1)
        self.style.configure("TNotebook", tabposition='n')
        self.style.map('Treeview', foreground=self.fixed_map('foreground'), background=self.fixed_map('background'))
        self.simplesearching = False
        self.lupab = b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAA5UlEQVRIie2TMQqDQBBFH1h7BT1BwMK0Hk1rvUTSxeN4gRgrj5BCBVPsX0IgRnbFFCEDy4D79791dgb+sSESoAZ6YFCu9X1TBEAh0/nNGrQf+AIKGY1ACaRAqFwCk/ZzH/NENxyBbEGTCTLgUa5atytXdJV0F1dAr4Ppiu4oXe8KsA8bruhC6e6uANc/aFwBrm9wcgXYLppY76IROLgC4HUOKkw5QuWK5xycfczBTGjO8iSPMp+BDoh9QQmmz3tMtzSYmtuydILctkA+RSzzGWiBaC9I+03IdS9IJMhuAAvZzfyH4wFOjlR1M/uyZwAAAABJRU5ErkJggg==+EoeDnCAQXM5jkuWfOXJgXXrhwf5zn3Mv9QzgPcYFfOfoXrRnr3qYdu9WGMvIdndWGHqCQE9hGKXSiiCv5bsu1f7flK7pDwDhmc+56B88rx1/QU09gC72pQBGfI50KAJt4kQo8wXCkgwFgA30xoAGNNfR/YB0vY8AIThK7HwDW0B8D8uQusIqBGPAKe4ndDgArlTUygSa0JbYlACzjdQwooCuxzwLAEoZiQB++JXY5ACzgbQzIk7vAPN7FgFHpH7mDAPAJ7+t5BXOVTd7LBH5iGjOxwSrALMZCQx04x0flq5nEnxqBgvK78SFrsAOneIxmHNUILOJY+Zebmaf4rfyM/6gRSE4JZzisFwBvcCntcb3Eo9AiN8RCeHqaVonMAAAAAElFTkSuQmCC'
        self.lupa = tkinter.PhotoImage(data=self.lupab)
        self.resultdocb = b'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAABLElEQVQ4jcXVLUsEURTG8R8YLcKC1tm2UQyiIDLFoH6BbQpm0SJG9wv4LQSbwWiybRQ0alhtvlSTr2HOZcd115llgweeMJfn/M+995zLwNcY6iFTEV/YxUqFErCHZhUwr6oavjVc4P4v6DjAXawH8H5S4HtJH5E3EbAc+b8Ac3RqKHkrgdu4rKEdbEXe0E7XPfIUDvHk57BfY2MYsKP6pbziCC00sIwTfCpG6gcw07+fQZ0GbDFy5uP4KQ4U47RQBqZdDtNL7CxFFuvl6EbhyqZchadVSp7x+9738FgGjorV8DRKa7nfY9PGWx1gMzzLFcAO7uoA4UbRzVHAaTzguC5wM3wH8Z3pN2Ua53jGXALuGz0ySWfh7Soa0A7oQ8CWUvVxfgGDuo1jzibYNyink2I3SlM0AAAAAElFTkSuQmCC'
        self.resultdoc = tkinter.PhotoImage(data=self.resultdocb)
        self.snippetb = b'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAc0lEQVQ4jdWUMQqAMAxF39zZOYfQrl6k0FHPVG/rEnAJSmMU/fCWQh582gb+kAI0pUTMN6ACGRCHUHS2qoumB3eTHxcKsDkRS5iA0Ul6pfIArJ3MV8Klk1NheOUETE7MSxGOL9SL+WzCK4cKQ5dD+Pr6dnbKM0DHGZ8hpQAAAABJRU5ErkJggg=='
        self.snippet = tkinter.PhotoImage(data=self.snippetb)
        self.afterpaint = None
        self.afterquads = None
        self.logoNormalb = b'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'
        self.logoNormal2b = b'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'
        self.tkphotologo= tkinter.PhotoImage(data=self.logoNormalb)
        self.tkphotologo2= tkinter.PhotoImage(data=self.logoNormal2b)
        self.initUI()        
        self.color = (103, 245, 134, 75)
        self.colorehnahcebookmark = (103, 245, 134, 35)
        self.colorquad = (21, 71, 150, 85)
        self.colorlink = (175, 200, 240, 95)
        self.winfox = self.docInnerCanvas.winfo_x()
        self.docInnerCanvas.bind("<Configure>", self.configureWindow)
        self.labeldocname.config(text=os.path.basename(pathpdfatual))
        root.focus_set()
        
    def buildLinks(self):
        global pathdb
        sobraEspaco = 0
        select_all_pdfs = '''SELECT P.id_pdf, P.rel_path_pdf FROM Anexo_Eletronico_Pdfs P'''
        sqliteconn =  connectDB(str(pathdb), 5)
        cursor = sqliteconn.cursor()
        #cursor.execute("PRAGMA journal_mode=WAL")
        try:
            sqliteconn.execute("PRAGMA foreign_keys = ON")
            cursor.execute(select_all_pdfs)
            pdfs = cursor.fetchall()
            cursor.close()
            for pdf in pdfs:
                cursor = sqliteconn.cursor()
                #cursor.execute("PRAGMA journal_mode=WAL")
                pdfbefore = os.path.join(os.sep, pathdb.parent, pdf[1])
                if plt == "Linux":
                    pdfrep = pdfbefore.replace("\\","/")
                elif plt=="Windows":
                    pdfrep = pdfbefore.replace("/","\\")
                abs_path_pdf = os.path.normpath(pdfrep)
                if(self.docFrame.winfo_width() > infoLaudo[abs_path_pdf].pixorgw * self.zoom_x * zoom):
                    sobraEspaco = self.docInnerCanvas.winfo_x()
                select_all_links = '''SELECT  L.id_link, L.paginainit, L.p0x, L.p0y, L.paginafim, L.p1x, L.p1y, L.tipo, L.id_obs, L.fixo FROM 
                Anexo_Eletronico_Links L WHERE L.id_pdf = ? ORDER BY 1
                '''  
                cursor.execute(select_all_links, (pdf[0],))
                links = cursor.fetchall() 
                cursor.close()
                for link in links:                    
                    pp = link[1]
                    up = link[4]
                    enhancearea = False
                    enhancetext = False
                    if(link[7]=='area'):
                        enhancearea = True
                    elif(link[7]=='texto'):
                        enhancetext = True
                    for p in range(pp, up+1):
                        
                        if(p==pp and p==up):
                            if 'falta'+str(p) not in infoLaudo[abs_path_pdf].linkscustom:
                                infoLaudo[abs_path_pdf].linkscustom['falta'+str(p)] = []
                            infoLaudo[abs_path_pdf].linkscustom['falta'+str(p)].append((p, link[2], link[3], link[5], link[6], pp, up, sobraEspaco, enhancetext, \
                                                                             enhancearea, (175,200,240,95), link[0], link[8], link[9], pdf[0]))
                                
                        elif(pp < p):
                            if(p < up):
                                if 'falta'+str(p) not in infoLaudo[abs_path_pdf].linkscustom:
                                    infoLaudo[abs_path_pdf].linkscustom['falta'+str(p)] = []
                                infoLaudo[abs_path_pdf].linkscustom['falta'+str(p)].append((p, 0, 0, infoLaudo[abs_path_pdf].pixorgw , infoLaudo[abs_path_pdf].pixorgh, pp, up, \
                                                                                 sobraEspaco, enhancetext, enhancearea, (175,200,240,95),  link[0], link[8], link[9], pdf[0]))
                            else:
                                if 'falta'+str(p) not in infoLaudo[abs_path_pdf].linkscustom:
                                    infoLaudo[abs_path_pdf].linkscustom['falta'+str(p)] = []
                                infoLaudo[abs_path_pdf].linkscustom['falta'+str(p)].append((p, 0, 0, link[5], link[6], pp, up, sobraEspaco, enhancetext, enhancearea, (175,200,240,95),\
                                                                                 link[0], link[8], link[9], pdf[0]))
                        else:
                            if 'falta'+str(p) not in infoLaudo[abs_path_pdf].linkscustom:
                                    infoLaudo[abs_path_pdf].linkscustom['falta'+str(p)] = []
                            infoLaudo[abs_path_pdf].linkscustom['falta'+str(p)].append((p, link[2], link[3], infoLaudo[abs_path_pdf].pixorgw , infoLaudo[abs_path_pdf].pixorgh , pp, up, sobraEspaco, \
                                                                                 enhancetext, enhancearea,(175,200,240,95), link[0], link[8], link[9], pdf[0]))
        except Exception as ex:
            printlogexception(ex=ex)
        finally:
            try:
                if(cursor):
                    cursor.close()
                if(sqliteconn):
                    sqliteconn.close()
            except Exception as ex:
                None
                
    def initUI(self):
        global result_queue, pathdb, erros, initsearchprocess, root, processes, queuesair, processed_pages, update_queue, searchqueue
        try:
            
            self.searchedTerms = []
            self.leftPanel()
            self.createTopBar()
            self.drawCanvas()
            self.buildLinks()
            root.update_idletasks()
            root.resizable(True, True)
            self.selectReport(self.primeiro)
            self.checkUpdates()
            self.checkPages()
            
            
            self.getlastPos()
            #self.docInnerCanvas.yview_moveto(0.99) 
        except Exception as ex:
            printlogexception(ex=ex)
 
    def loadDocOnCanvas(self):
        global request_queue, processed_pages, zoom, listaZooms, posicaoZoom, request_queue_parsing, pathpdfatual, infoLaudo, processed_requests
        try:
            #zoom = listaZooms[posicaoZoom]
            
            #pedido1.pixheight = infoLaudo[pathpdfatual].pixorgh
            #pedido1.pixwidth = infoLaudo[pathpdfatual].pixorgw
            #pedido1.mt = infoLaudo[pathpdfatual].mt
            #pedido1.mb = infoLaudo[pathpdfatual].mb
            #pedido1.me = infoLaudo[pathpdfatual].me
            #pedido1.md = infoLaudo[pathpdfatual].md
            #pedido1.qualLabel = 0
            #pedido1.qualPagina = 0
            #pedido1.matriz = self.mat
            processed_pages[0] = 0
            pathpdfatual2 = pathpdfatual
            #pedido1.qualPdf = pathpdfatual2
            #pedido1.scrollvalue = self.vscrollbar.get()[0]
            #pedido1.zoom = self.zoom_x*zoom
            #pedido1.scrolltotal = self.scrolly
            #pedido1.canvash = self.canvash
            pedido1 = PedidoDePagina(qualLabel = 0, qualPdf = pathpdfatual2, qualPagina = 0, matriz = self.mat, \
                  pixheight = infoLaudo[pathpdfatual].pixorgh, pixwidth = infoLaudo[pathpdfatual].pixorgw, zoom = self.zoom_x*zoom, \
                      scrollvalue = self.vscrollbar.get()[0] ,\
                      scrolltotal = self.scrolly, canvash = self.canvash, mt = infoLaudo[pathpdfatual].mt, \
                          mb = infoLaudo[pathpdfatual].mb, me = infoLaudo[pathpdfatual].me, md = infoLaudo[pathpdfatual].md)
            request_queuexml.put(pedido1)
            request_queue.put(pedido1)
            processed_requests[0] = pedido1
        except Exception as ex:
            printlogexception(ex=ex)
        
        
        
    def checkLink(self, event):
        global pathpdfatual, zoom, infoLaudo
        try:
            try:
                if self.tw:
                    self.tw.destroy()
            except Exception as ex:
                None
            texto_extra= " "
            if(not self.selectionActive and not self.areaselectionActive and not self.areaselectionActiveCustom):
                pagina = math.floor(self.docInnerCanvas.canvasy(event.y) / (infoLaudo[pathpdfatual].pixorgh *self.zoom_x*zoom))
                ehLinkCustom = False
                listaquads = self.docInnerCanvas.find_withtag("link")
                
                for quadelement in listaquads:
                    bbox = self.docInnerCanvas.bbox(quadelement)
                    if(self.docInnerCanvas.canvasx(event.x) >= bbox[0] and self.docInnerCanvas.canvasy(event.y) >= bbox[1] \
                       and self.docInnerCanvas.canvasx(event.x) <= bbox[2] and self.docInnerCanvas.canvasy(event.y) <= bbox[3]):
                        self.docInnerCanvas.config(cursor='hand2')
                        ehLinkCustom=True
                        break
                if(not ehLinkCustom):
                    posicaoRealY0Canvas = self.vscrollbar.get()[0] * self.scrolly + event.y
                    posicaoRealX0Canvas = self.hscrollbar.get()[0] * (infoLaudo[pathpdfatual].pixorgw * self.zoom_x * zoom) + event.x
                    posicaoRealY0 = (posicaoRealY0Canvas % (infoLaudo[pathpdfatual].pixorgh * self.zoom_x*zoom)) / (self.zoom_x*zoom)
                    posicaoRealX0 = posicaoRealX0Canvas / (self.zoom_x*zoom)
                    pagina = math.floor(posicaoRealY0Canvas / (infoLaudo[pathpdfatual].pixorgh *self.zoom_x*zoom))
                    ehLink = False
                    if(pagina in infoLaudo[pathpdfatual].links):
                        for link in infoLaudo[pathpdfatual].links[pagina]:
                            
                            r = link['from']
                            if(posicaoRealX0 >= r.x0 and posicaoRealX0 <= r.x1 and posicaoRealY0 >= r.y0 and posicaoRealY0 <= r.y1):
                                self.docInnerCanvas.config(cursor='hand2')
                                ehLink=True
                                x = event.x_root + 15
                                y = event.y_root + 10
                                try:
                                   
                                    text = link['file']
                                    texto_extra += link['file'] + " "
                                    #self.tw = tkinter.Toplevel(self.docInnerCanvas)
                                    #self.tw.wm_overrideredirect(True)
                                    #self.tw.wm_geometry("+%d+%d" % (x, y))
                                    #label = tkinter.Label(self.tw, text=link['file'], justify='left',
                                    #               background='#ededd3', relief='solid', borderwidth=1,
                                    #               font=("times", "8", "normal"))
                                    #label.pack(ipadx=1)
                                except Exception as ex:
                                    None
                                break
                    if(not ehLink):
                        if(not self.areaselectionActive):
                            self.docInnerCanvas.config(cursor='fleur')
            posicaoRealY0Canvas = self.vscrollbar.get()[0] * self.scrolly + event.y
            pagina = math.floor(posicaoRealY0Canvas / (infoLaudo[pathpdfatual].pixorgh *self.zoom_x*zoom))
            listaquads = self.docInnerCanvas.find_withtag('enhanceobs'+pathpdfatual+str(pagina))
            
            if(pagina in infoLaudo[pathpdfatual].widgets):
               for wid in infoLaudo[pathpdfatual].widgets[pagina]:
                   
                   
                   posicaoRealX0Canvas = self.hscrollbar.get()[0] * (infoLaudo[pathpdfatual].pixorgw * self.zoom_x * zoom) + event.x
                   posicaoRealY0 = (posicaoRealY0Canvas % (infoLaudo[pathpdfatual].pixorgh * self.zoom_x*zoom)) / (self.zoom_x*zoom)
                   posicaoRealX0 = posicaoRealX0Canvas / (self.zoom_x*zoom)
                   if(posicaoRealX0 >= wid[1][0] and posicaoRealX0 <= wid[1][2] and posicaoRealY0 >= wid[1][1] and posicaoRealY0 <= wid[1][3]):
                       texto_extra += wid[0]+ " "
                       
            for quadelement in listaquads:
                bbox = self.docInnerCanvas.bbox(quadelement)
                if(self.docInnerCanvas.canvasx(event.x) >= bbox[0] and self.docInnerCanvas.canvasy(event.y) >= bbox[1] \
                   and self.docInnerCanvas.canvasx(event.x) <= bbox[2] and self.docInnerCanvas.canvasy(event.y) <= bbox[3]):
                    tags = self.docInnerCanvas.gettags(quadelement)
                    try:
                        iiditem = "obsitem"+tags[1].split("enhanceobs")[1]
                        iidantespai = iiditem
                        iidpai = self.treeviewObs.parent(iiditem)
                        #pai = self.treeviewObs.parent(iiditem)                    
                        while(iidpai!=""):
                           iidantespai = iidpai
                           iidpai = self.treeviewObs.parent(iidpai) 
                        texto = self.treeviewObs.item(iidantespai, 'text')
                        texto_extra += "- "+texto
                    except Exception as ex:
                        None
                        printlogexception(ex=ex)
                    #obsobject = Observation(paginainit, paginafim, p0x, p0y, p1x, p1y, tipo, pathpdf, iiditem)
                    #self.allobs[pathpdf].append(obsobject)
            if(len(texto_extra)>=2):
                x = event.x_root + 15
                y = event.y_root + 10
                # creates a toplevel window
                self.tw = tkinter.Toplevel(self.docInnerCanvas)
                # Leaves only the label and removes the app window
                self.tw.wm_overrideredirect(True)
                self.tw.wm_geometry("+%d+%d" % (x, y))
                label = tkinter.Label(self.tw, text=texto_extra, justify='left',
                               background='#ededd3', relief='solid', borderwidth=1,
                               font=("times", "8", "normal"))
                label.pack(ipadx=1)
                        
        except Exception as ex:
            None
            printlogexception(ex=ex)
            
    def configureWindow(self, event=None):
        global infoLaudo, pathpdfatual, zoom, minMaxLabels
        
        
        sobraEspaco = 0
        if(self.docFrame.winfo_width() > infoLaudo[pathpdfatual].pixorgw * self.zoom_x * zoom):
            sobraEspaco = self.docInnerCanvas.winfo_x()
        self.maiorw = self.docFrame.winfo_width()
        if(infoLaudo[pathpdfatual].pixorgw*self.zoom_x*zoom>self.maiorw):
            self.maiorw = infoLaudo[pathpdfatual].pixorgw*self.zoom_x *zoom           
        self.scrolly = infoLaudo[pathpdfatual].pixorgh*self.zoom_x*zoom*infoLaudo[pathpdfatual].len  - 35
        self.docInnerCanvas.config(scrollregion=(sobraEspaco, 0, sobraEspaco+infoLaudo[pathpdfatual].pixorgw * self.zoom_x * zoom, self.scrolly))
        dx = 0
        try:
            for indice in range(minMaxLabels):
                coords = self.docInnerCanvas.coords(self.ininCanvasesid[indice])
                pos_h = self.docInnerCanvas.winfo_x()
                dx = pos_h - coords[0] 
                self.docInnerCanvas.move(self.ininCanvasesid[indice], dx, 0)
        except Exception as ex:
            printlogexception(ex=ex)
        
        for quad in self.docInnerCanvas.find_withtag('quad'):
            coords = self.docInnerCanvas.coords(self.ininCanvasesid[indice])
            self.docInnerCanvas.move(quad, dx, 0)        
        for link in self.docInnerCanvas.find_withtag('link'):            
            self.docInnerCanvas.move(link, dx, 0)
        for simplesearch in self.docInnerCanvas.find_withtag('simplesearch'):            
            self.docInnerCanvas.move(simplesearch, dx, 0)
        for search in self.docInnerCanvas.find_withtag('obsitem'):            
            self.docInnerCanvas.move(search, dx, 0)
        listaobj = self.docInnerCanvas.find_all()
        for tag in self.allimages:
            if 'enhanceobs' in tag:
                for search in self.docInnerCanvas.find_withtag(tag):            
                    self.docInnerCanvas.move(search, dx, 0)
        atual = round((self.vscrollbar.get()[0]*infoLaudo[pathpdfatual].len))
        
        #self.pagVar.set(str(atual+1))
    def getlastPos(self):
        infoLaudo[pathpdfatual].ultimaPosicao=(self.vscrollbar.get()[0])
        root.after(1000, self.getlastPos)
        
    def paintLink(self, respostaPagina, first=True):
        global processed_pages
        if(respostaPagina.qualPagina not in infoLaudo[pathpdfatual].mapeamento):
            if(first or respostaPagina.qualPagina in processed_pages):
                root.after(300, lambda : self.paintLink(respostaPagina, first=False))
        else:
            for i in range(len(infoLaudo[pathpdfatual].linkscustom['falta'+str(respostaPagina.qualPagina)])): 
                pagina = infoLaudo[pathpdfatual].linkscustom['falta'+str(respostaPagina.qualPagina)][i][0]
                p0x = infoLaudo[pathpdfatual].linkscustom['falta'+str(respostaPagina.qualPagina)][i][1]
                p0y = infoLaudo[pathpdfatual].linkscustom['falta'+str(respostaPagina.qualPagina)][i][2]+1
                p1x = infoLaudo[pathpdfatual].linkscustom['falta'+str(respostaPagina.qualPagina)][i][3]
                p1y = infoLaudo[pathpdfatual].linkscustom['falta'+str(respostaPagina.qualPagina)][i][4]-1
                pp = infoLaudo[pathpdfatual].linkscustom['falta'+str(respostaPagina.qualPagina)][i][5]
                up = infoLaudo[pathpdfatual].linkscustom['falta'+str(respostaPagina.qualPagina)][i][6]
                sobraEspaco = infoLaudo[pathpdfatual].linkscustom['falta'+str(respostaPagina.qualPagina)][i][7]
                enhancetext = infoLaudo[pathpdfatual].linkscustom['falta'+str(respostaPagina.qualPagina)][i][8]
                enhancearea = infoLaudo[pathpdfatual].linkscustom['falta'+str(respostaPagina.qualPagina)][i][9]
                cor = infoLaudo[pathpdfatual].linkscustom['falta'+str(respostaPagina.qualPagina)][i][10]
                link0 = infoLaudo[pathpdfatual].linkscustom['falta'+str(respostaPagina.qualPagina)][i][11]
                link8 = infoLaudo[pathpdfatual].linkscustom['falta'+str(respostaPagina.qualPagina)][i][12]
                idpdf =  infoLaudo[pathpdfatual].linkscustom['falta'+str(respostaPagina.qualPagina)][i][14]
                fixo =  infoLaudo[pathpdfatual].linkscustom['falta'+str(respostaPagina.qualPagina)][i][13]
                sobraEspaco = 0
                if(self.docFrame.winfo_width() > infoLaudo[pathpdfatual].pixorgw * self.zoom_x * zoom):
                    sobraEspaco = self.docInnerCanvas.winfo_x()
                listaq = self.docInnerCanvas.find_withtag("quadp"+str(link0))
                for quadelement in listaq:
                    try:
                        del infoLaudo[pathpdfatual].linkscustom[quadelement]
                    except Exception as ex:
                        None
                self.docInnerCanvas.delete('quadp'+str(link0))
                if('quadp'+str(link0) in self.allimages):
                    del self.allimages['quadp'+str(link0)]                              
                #var aqui, tags!!!!!! Pode ficar sobrando ali
                self.prepararParaQuads(pagina, p0x, p0y, p1x, p1y, color=cor, tag=['quadp'+str(link0)], apagar=False, enhancetext=enhancetext, enhancearea=enhancearea, alt=False)                                    
                self.docInnerCanvas.addtag_withtag("link"+str(link0),"quadp"+str(link0))
                self.docInnerCanvas.addtag_withtag("link","quadp"+str(link0))
                
                listaquads = self.docInnerCanvas.find_withtag("quadp"+str(link0))   
                for quadelement in listaquads:
                    box = (self.docInnerCanvas.bbox(quadelement))
                    pagina = math.floor(box[1] / (infoLaudo[pathpdfatual].pixorgh *self.zoom_x*zoom))
                    getleafs =  self.treeviewObs.tag_has('obsitem')
                    for obsitem in getleafs:  
                        if(str(self.treeviewObs.item(obsitem, 'values')[8])==str(link8)):
                            imagem = (self.create_rectanglex(box[0], box[1], box[2], box[3], (175, 200, 240, 95), link=True))
                            infoLaudo[pathpdfatual].linkscustom[quadelement] = []
                            infoLaudo[pathpdfatual].linkscustom[quadelement].append((box, pagina, obsitem, link0, link8, idpdf, fixo,)    )                                            
                            self.linkscustom.append(imagem)
                            self.docInnerCanvas.itemconfig(quadelement, image=imagem)
                            break
    def paintObservations(self):
        None
        
    def checkUpdates(self, event=None):
        global processed_pages, minMaxLabels, divididoEm, zoom, listaZooms, \
            posicaoZoom, exitFlag, erros, response_queue, comandos_queue, result_queue, infoLaudo, pathpdfatual, initsearchprocess, uniquesearchprocess, searchqueue, totalpaginas,\
                update_queue, searchResultsDict, render_process, render_processxml, listadeobs, listaRELS
        atual = round((self.vscrollbar.get()[0]*infoLaudo[pathpdfatual].len))      
        #at = round(self.vscrollbar.get()[0]*infoLaudo[pathpdfatual].len)
        
        if(uniquesearchprocess==None):
            
            uniquesearchprocess = mp.Process(target=searchProcess, args=(result_queue, pathdb, erros,\
                                                                         queuesair, searchqueue, update_queue, infoLaudo, listaRELS, listaTERMOS, True,), daemon=True)
            self.uniquesearchprocess2 = mp.Process(target=searchProcess, args=(result_queue, pathdb, erros,queuesair,\
                                                                               searchqueue, update_queue, infoLaudo, listaRELS, listaTERMOS, False,), daemon=True)
            self.uniquesearchprocess3 = mp.Process(target=searchProcess, args=(result_queue, pathdb, erros,queuesair, searchqueue, update_queue, \
                                                                               infoLaudo, listaRELS, listaTERMOS, False,), daemon=True)
            #self.uniquesearchprocess4 = mp.Process(target=searchProcess, args=(result_queue, pathdb, erros,queuesair, searchqueue, update_queue, infoLaudo, False,), daemon=True)
            #self.uniquesearchprocess5 = mp.Process(target=searchProcess, args=(result_queue, pathdb, erros,queuesair, searchqueue, update_queue, infoLaudo, False,), daemon=True)
            #self.uniquesearchprocess6 = mp.Process(target=searchProcess, args=(result_queue, pathdb, erros,queuesair, searchqueue, update_queue, infoLaudo, False,), daemon=True)
            processes['BUSCA'] = uniquesearchprocess
            uniquesearchprocess.start()  
            self.uniquesearchprocess2.start() 
            self.uniquesearchprocess3.start() 
            #self.uniquesearchprocess4.start() 
            #self.uniquesearchprocess5.start() 
            #self.uniquesearchprocess6.start() 
            self.primeiroresetbuscar = True
        '''    
        if(not self.uniquesearchprocess2.is_alive() and \
             not self.uniquesearchprocess3.is_alive()):
             #not self.uniquesearchprocess4.is_alive() and\
             #not self.uniquesearchprocess5.is_alive() and\
             #not self.uniquesearchprocess6.is_alive()):
                if(self.primeiroresetbuscar):
                    self.primeiroresetbuscar = False
                    self.searchVar.set("Buscar...")
                self.entrysearch.config(state='normal')
                self.searchbutton.config(state='normal')
                self.bfromFile.config(state='normal')
                self.btoFile.config(state='normal')
                self.querysql.config(state='normal')
                self.saveresulttocsv.config(state='normal')
        
        else:
            self.searchVar.set("Aguarde, pesquisando...")
            self.entrysearch.config(state='disabled')
            self.searchbutton.config(state='disabled')
            self.bfromFile.config(state='disabled')
            self.btoFile.config(state='disabled')
            self.querysql.config(state='disabled')
            self.saveresulttocsv.config(state='disabled')
        '''       
        
        if(not render_process.is_alive()):
            popup_window("O processo de RENDERIZAÇÃO DE IMAGENS apresentou problema e foi reiniciado!", False)
            render_process = mp.Process(target=backgroundRendererImage, args=(processed_pages, request_queue, response_queue, queuesair, infoLaudo, erros,), daemon=True)
            render_process.start()
        if(not render_processxml.is_alive()):
            popup_window("O processo de EXTRAÇÂO DE INFORMAÇÕES apresentou problema e foi reiniciado!", False)
            render_processxml = mp.Process(target=backgroundRendererXML, args=(request_queuexml, response_queuexml, queuesair, infoLaudo, erros, listadeobs,), daemon=True)
            render_processxml.start()
        if(not uniquesearchprocess.is_alive()):
            popup_window("O processo de BUSCA apresentou problema e foi reiniciado!", False)
            uniquesearchprocess = mp.Process(target=searchProcess, args=(result_queue, pathdb, erros,queuesair,\
                                                                         searchqueue, update_queue, infoLaudo, listaRELS, listaTERMOS, True,), daemon=True)
            uniquesearchprocess.start()
        
                
        
        if(len(infoLaudo[pathpdfatual].mapeamento)>= 5):
            remove = [previous for previous in infoLaudo[pathpdfatual].mapeamento if not previous in processed_pages]
            for previous in remove: 
                del infoLaudo[pathpdfatual].links[previous]
                del infoLaudo[pathpdfatual].widgets[previous]
                del infoLaudo[pathpdfatual].mapeamento[previous]
                del infoLaudo[pathpdfatual].quadspagina[previous]
        
        if(not exitFlag):
            try:        
                atual = round((self.vscrollbar.get()[0]*infoLaudo[pathpdfatual].len))                
                cl = math.ceil((self.vscrollbar.get()[0]*infoLaudo[pathpdfatual].len))     
                fl = math.floor((self.vscrollbar.get()[0]*infoLaudo[pathpdfatual].len))        
                coords = self.docInnerCanvas.coords(self.fakeLines[0])
                coords1 = self.docInnerCanvas.coords(self.fakeLines[1])
                dy = ((atual) * infoLaudo[pathpdfatual].pixorgh * self.zoom_x * zoom)  - coords[1]                
                dy1 = ((atual+1) * infoLaudo[pathpdfatual].pixorgh * self.zoom_x * zoom)  - coords1[1]
                
                if(atual >= infoLaudo[pathpdfatual].len-1):
                    dy1 = (self.scrolly-(self.hscrollbar.winfo_height()/2)  - coords1[1])
                    self.docInnerCanvas.move(self.fakeLines[0], 0, dy)
                else:
                    self.docInnerCanvas.move(self.fakeLines[0], 0, dy)
                    self.docInnerCanvas.move(self.fakeLines[1], 0, dy1)                
                if(not erros.empty()):
                    errochegou = erros.get()
                    if(errochegou[0]=='testeprint'):
                        None
                    if(errochegou[0]=='errosqlbusca'):
                        popup_window(errochegou[1], False)   
                if(not response_queuexml.empty()):
                    #self.docInnerCanvas.find_withtag("enhanceobs")
                    respostaPagina = response_queuexml.get()
                    if((respostaPagina.qualPagina >= (atual-math.floor(minMaxLabels/2)) and \
                            respostaPagina.qualPagina <= (atual+math.ceil(minMaxLabels/2))) and \
                            respostaPagina.qualPdf == pathpdfatual):  
                        infoLaudo[pathpdfatual].links[respostaPagina.qualPagina] = respostaPagina.links
                        infoLaudo[pathpdfatual].widgets[respostaPagina.qualPagina] = respostaPagina.widgets
                        infoLaudo[pathpdfatual].mapeamento[respostaPagina.qualPagina] = respostaPagina.mapeamento
                        infoLaudo[pathpdfatual].quadspagina[respostaPagina.qualPagina] = respostaPagina.quadspagina
                        if(self.showbookmarsboolean):
                            
                            if(pathpdfatual in self.allobs):
                                
                                
                                for observation in self.allobs[pathpdfatual]:
                                    None
                                    if(observation.paginainit in processed_pages and observation.paginafim in processed_pages):
                                        enhancearea = False
                                        enhancetext = False
                                        
                                        if(observation.tipo=='area'):
                                            enhancearea = True
                                        elif(observation.tipo=='texto'):
                                            enhancetext = True
                                        for p in range(observation.paginainit, observation.paginafim+1): 
                                            if(p != respostaPagina.qualPagina):
                                                continue
                                            posicaoRealX0 = observation.p0x
                                            posicaoRealY0 = observation.p0y
                                            posicaoRealX1 = observation.p1x
                                            posicaoRealY1 = observation.p1y
                                            iiditem = observation.idobs
                                            #listacompage = self.docInnerCanvas.find_withtag('enhanceobs'+pathpdfatual+str(p))
                                            
                                            if(p==observation.paginainit and p==observation.paginafim):
                                                self.prepararParaQuads(p, posicaoRealX0, posicaoRealY0, posicaoRealX1, posicaoRealY1, color=self.colorehnahcebookmark, \
                                                                       tag=['enhanceobs'+pathpdfatual+str(p),'enhanceobs'+str(iiditem)], \
                                                                           apagar=False,  enhancetext=enhancetext, enhancearea=enhancearea, withborder=False, alt=False)
                                            elif(observation.paginainit < p):
                                                if(p < observation.paginafim):
                                                    self.prepararParaQuads(p, 0, 0, infoLaudo[pathpdfatual].pixorgw, infoLaudo[pathpdfatual].pixorgh, \
                                                                           color=self.colorehnahcebookmark, tag=['enhanceobs'+pathpdfatual+str(p),'enhanceobs'+str(iiditem)], \
                                                                           apagar=False,  enhancetext=enhancetext, enhancearea=enhancearea, withborder=False, alt=False)                            
                                                else:
                                                    self.prepararParaQuads(p, 0, 0, posicaoRealX1, posicaoRealY1, color=self.colorehnahcebookmark, \
                                                                           tag=['enhanceobs'+pathpdfatual+str(p),'enhanceobs'+str(iiditem)], \
                                                                           apagar=False,  enhancetext=enhancetext, enhancearea=enhancearea, withborder=False, alt=False)                            
                                            else:
                                                self.prepararParaQuads(p, posicaoRealX0, posicaoRealY0, infoLaudo[pathpdfatual].pixorgw,  infoLaudo[pathpdfatual].pixorgh, \
                                                                       color=self.colorehnahcebookmark, tag=['enhanceobs'+pathpdfatual+str(p),'enhanceobs'+str(iiditem)], \
                                                                           apagar=False,  enhancetext=enhancetext, enhancearea=enhancearea, withborder=False, alt=False) 
                                    
                if(not response_queue.empty()):
                    respostaPagina = response_queue.get()
                    if((respostaPagina.qualPagina >= (atual-math.floor(minMaxLabels/2)) and \
                            respostaPagina.qualPagina <= (atual+math.ceil(minMaxLabels/2))) and \
                            respostaPagina.qualPdf == pathpdfatual and respostaPagina.zoom == self.zoom_x*zoom):                        
                        
                        indice = (respostaPagina.qualLabel * divididoEm) + respostaPagina.qualGrid
                        zoom = listaZooms[posicaoZoom]
                        altura = math.floor((respostaPagina.qualPagina*infoLaudo[pathpdfatual].pixorgh*self.zoom_x*zoom) + \
                                            ((respostaPagina.qualGrid/divididoEm)*infoLaudo[pathpdfatual].pixorgh*self.zoom_x*zoom))
                        coords = self.docInnerCanvas.coords(self.ininCanvasesid[indice])
                        pos_h = self.docInnerCanvas.winfo_x()
                        self.docInnerCanvas.coords(self.ininCanvasesid[indice], pos_h, altura)                        
                        self.tkimgs[indice] = tkinter.PhotoImage(data = respostaPagina.imgdata)
                        self.docInnerCanvas.itemconfig(self.ininCanvasesid[indice], image = self.tkimgs[indice])
                        try:
                            
                            if 'falta'+str(respostaPagina.qualPagina) in  infoLaudo[pathpdfatual].linkscustom and pathpdfatual == respostaPagina.qualPdf:      
                            
                                self.paintLink(respostaPagina)
                        except Exception as ex:
                            printlogexception(ex=ex)
                else:   
                    contagem = 0
                    starttime = time.process_time_ns()
                    endtime = time.process_time_ns()
                    while(((endtime-starttime)/1000000) < 75):  
                        if(not update_queue.empty()):
                            updatechegou = update_queue.get()
                            if(updatechegou[0]=='updatecontpdf'):
                                try:
                                    idtermo = updatechegou[5]
                                    pathpdfbase = str(os.path.basename(updatechegou[2]))
                                    idtermopdf = updatechegou[1]
                                    if(not self.treeviewSearches.exists('tp'+str(updatechegou[1]))):
                                        self.treeviewSearches.insert(parent='t'+idtermo, index='end', iid='tp'+idtermopdf, text=pathpdfbase, tag=('relsearch'), \
                                                                     image=self.resultdoc, values=(pathpdfbase,))  
                                    porcentagem = " ( {porcent}%)".format(porcent=round(updatechegou[3]/updatechegou[4]*100, 2))
                                    texto = os.path.basename(updatechegou[2] + porcentagem ) 
                                    self.treeviewSearches.item('tp'+str(updatechegou[1]), text=texto) 
                                except Exception as ex:
                                    printlogexception(ex=ex)
                        if(not result_queue.empty()):
                            try:
                                contagem +=1
                                res = result_queue.get()
                                if(res[0]==0): 
                                    resultsearch = res[1]
                                    idtermo = str(resultsearch.idtermo)
                                    termo = resultsearch.termo
                                    adv = 0
                                    if(resultsearch.advanced):
                                        adv = 1
                                    if(not self.treeviewSearches.exists('t'+idtermo)):
                                        self.treeviewSearches.insert(parent='', index='0', iid='t'+idtermo, text=termo, tag='termosearch', image=self.lupa, \
                                                                     values=(termo.upper(), str(adv),))
                                        searchResultsDict['t'+idtermo] = resultsearch
                                elif(res[0]==1):
                                    try:
                                        resultsearch = res[1]
                                        idtermo = str(resultsearch.idtermo)
                                        termo = resultsearch.termo
                                        idtermopdf = str(resultsearch.idtermopdf)
                                        pathpdfbase = str(os.path.basename(resultsearch.pathpdf))
                                        snippet = resultsearch.snippet[0] + resultsearch.snippet[1] + resultsearch.snippet[2]
                                        pagina = resultsearch.pagina                                        
                                        if(not self.treeviewSearches.exists('tp'+idtermopdf)):                                            
                                            self.treeviewSearches.insert(parent='t'+idtermo, index='end', iid='tp'+idtermopdf, \
                                                                         text=pathpdfbase, tag=('relsearch'), image=self.resultdoc, values=(pathpdfbase,)) 
                                        
                                        try:
                                            desloc = resultsearch.pagina * infoLaudo[resultsearch.pathpdf].pixorgh
                                            #tocname = str(self.locateToc(resultsearch.pagina, resultsearch.pathpdf, init=resultsearch.init))
                                            tocname = resultsearch.toc
                                            if(not self.treeviewSearches.exists('tp'+idtermopdf+tocname)):
                                                 self.treeviewSearches.insert(parent='tp'+idtermopdf, iid='tp'+idtermopdf+tocname, text=tocname, index='end', tag=('relsearchtoc'),)                                            
                                            idx = self.treeviewSearches.insert(parent='tp'+idtermopdf+tocname, index='end', text=str(pagina+1)+' - '+snippet, tag='resultsearch', \
                                                                                image=self.snippet, values=(resultsearch.snippet[0], resultsearch.snippet[1], resultsearch.snippet[2],))
                                            tamanho = self.resultfont.measure(str(pagina+1)+' - '+snippet)+150
                                            if(tamanho>self.maiorresult):
                                                self.maiorresult = tamanho                                                
                                                self.treeviewSearches.column("#0", width=self.maiorresult, stretch=True, minwidth=self.maiorresult, anchor="w")
                                            resultsearch.snippet = ""
                                            searchResultsDict[idx] = resultsearch
                                        except Exception as ex:
                                            printlogexception(ex=ex)
                                            idx = self.treeviewSearches.insert(parent='tp'+idtermopdf, index='end', text=' '+str(pagina+1)+' - '+snippet, tag='resultsearch', \
                                                                                image=self.snippet, values=(resultsearch.snippet[0], resultsearch.snippet[1], resultsearch.snippet[2],))
                                            tamanho = self.resultfont.measure(str(pagina+1)+' - '+snippet)+150
                                            if(tamanho>self.maiorresult):
                                                self.maiorresult = tamanho                                                
                                                self.treeviewSearches.column("#0", width=self.maiorresult, stretch=True, minwidth=self.maiorresult, anchor="w")
                                            resultsearch.snippet = ""
                                            searchResultsDict[idx] = resultsearch
                                            
                                    except Exception as ex:
                                        None
                                        
                                elif(res[0]==2):
                                    idx = 't'+str(res[1])
                                    resultsearch = searchResultsDict[idx]
                                    termo = resultsearch.termo
                                    self.treeviewSearches.tag_configure('resultsearch', font=self.resultfont)
                                    self.treeviewSearches.tag_configure('termosearch', background='#c9c9c9', font=('Arial', 10, 'bold'))
                                    if(not self.treeviewSearches.exists('t'+str(res[1]))):
                                        self.treeviewSearches.insert(parent='', index='0', iid='t'+str(res[1]), text=termo, tag='termosearch', image=self.lupa)
                                    
                                    
                                    th = 0
                                    termo  = resultsearch.termo.upper()
                                    pdfs = self.treeviewSearches.get_children(idx)
                                    for pdf in pdfs:
                                        
                                        possiveltoc = self.treeviewSearches.get_children(pdf)[0]
                                        if(len(self.treeviewSearches.get_children(possiveltoc))==0): #nao tem toc
                                            hitpdf = 0
                                            for results in self.treeviewSearches.get_children(pdf):
                                                hitpdf += 1
                                                th+=1                                                
                                            textopdf = self.treeviewSearches.item(pdf, 'values')[0]
                                            if(hitpdf==1000):
                                                self.treeviewSearches.item(pdf, text=textopdf + ' (' + str(hitpdf) + ')*') 
                                            else:  
                                                self.treeviewSearches.item(pdf, text=textopdf + ' (' + str(hitpdf) + ')') 
                                        else:
                                            hitpdf = 0
                                            for toc in self.treeviewSearches.get_children(pdf):
                                                hittoc = 0
                                                for results in self.treeviewSearches.get_children(toc):
                                                    hittoc += 1
                                                    th+=1
                                                textotoc = self.treeviewSearches.item(toc, 'text')
                                                if(hittoc==1000):
                                                    self.treeviewSearches.item(toc, text=textotoc + ' (' + str(hittoc) + ')*') 
                                                else:
                                                    self.treeviewSearches.item(toc, text=textotoc + ' (' + str(hittoc) + ')') 
                                                hitpdf += hittoc
                                            textopdf = self.treeviewSearches.item(pdf, 'values')[0]
                                            self.treeviewSearches.item(pdf, text=textopdf + ' (' + str(hitpdf) + ')') 
                                        
                                    advanced = resultsearch.advanced                                    
                                    tipo = 'LIKE'
                                    if(advanced):
                                        tipo = 'MATCH'
                                    self.treeviewSearches.item(idx, text=termo + ' (' + str(th) + ')'  + " - "+tipo)                                    
                            except Exception as ex:
                                printlogexception(ex=ex)
                        else:
                            break
                        endtime = time.process_time_ns()
            except Exception as ex:
                printlogexception(ex=ex)
            finally:
                
                root.after(10, self.checkUpdates)
    
    def locateToc(self, pagina, pdf, p0y=None, init=None):
            if plt == "Linux":
                pdf = str(pdf).replace("\\","/")
            elif plt=="Windows":
                pdf = str(pdf).replace("/","\\")
            pdfx = (str(Path(pdf)))
            t = 0
            napagina = False
            naoachou = True
            if(init!=None):
                for t in range(len(infoLaudo[pdfx].toc)-1):
                    if(pagina >= infoLaudo[pdfx].toc[t][1] and pagina < infoLaudo[pdfx].toc[t+1][1]):
                        naoachou = False
                        break   
                    elif(pagina >= infoLaudo[pdfx].toc[t][1] and pagina <= infoLaudo[pdfx].toc[t+1][1]):
                        napagina = True
                        
                    if(napagina and infoLaudo[pdfx].toc[t+1][3] > init  ):  
                        naoachou = False
                        break
                
                if(naoachou):
                    if(pagina==0):
                        t=0
                    else:
                        t=len(infoLaudo[pdfx].toc)-1
                        
            elif(p0y!=None):
                 for t in range(len(infoLaudo[pdfx].toc)-1):
                    if(pagina >= infoLaudo[pdfx].toc[t][1] and pagina < infoLaudo[pdfx].toc[t+1][1]):
                        naoachou = False
                        break   
                    elif(pagina >= infoLaudo[pdfx].toc[t][1] and pagina <= infoLaudo[pdfx].toc[t+1][1]):
                        napagina = True
                        
                    if(napagina and infoLaudo[pdfx].toc[t+1][2] > p0y  ):  
                        naoachou = False
                        break
                
                 if(naoachou):
                    if(pagina==0):
                        t=0
                    else:
                        t=len(infoLaudo[pdfx].toc)-1
            
            t = min(t, len(infoLaudo[pdfx].toc)-1)
            t = max(0, t)
            tocc = infoLaudo[pdfx].toc[t][0]
            return tocc
          
    def checkPages(self):
        global processed_pages, minMaxLabels, zoom, listaZooms, posicaoZoom, pathpdfatual, infoLaudo, processed_requests
        try:
            atual = math.ceil((self.vscrollbar.get()[0]*infoLaudo[pathpdfatual].len))
            if(atual not in processed_pages): 
                #self.docInnerCanvas.delete("quad")
                #self.docInnerCanvas.delete("simplesearch")
                #self.docInnerCanvas.delete("obsitem")
                #self.docInnerCanvas.delete("link")
                #self.docInnerCanvas.delete("enhanceobs")
               # self.clearSomeImages(["quad", "simplesearch", "obsitem", "link"]) 
                #self.clearAllImages()
                self.alreadyenhanced = set()
                for i in range(minMaxLabels):
                   processed_pages[i] = -1
                while not request_queuexml.empty():
                    try:
                        request_queuexml.get(0)
                    except Exception as ex:
                        None
                
                while not request_queue.empty():
                    try:
                        request_queue.get(0) 
                    except Exception as ex:
                        None
                while not response_queue.empty():
                    try:
                        response_queue.get(0) 
                    except Exception as ex:
                        None
                
                #pedido2 = PedidoDePagina()
                #pedido2.qualLabel = atual % minMaxLabels
                #pedido2.pixheight = infoLaudo[pathpdfatual].pixorgh
                #pedido2.pixwidth = infoLaudo[pathpdfatual].pixorgw
                #pedido2.mt = infoLaudo[pathpdfatual].mt
                #pedido2.mb = infoLaudo[pathpdfatual].mb
                #pedido2.me = infoLaudo[pathpdfatual].me
                #pedido2.md = infoLaudo[pathpdfatual].md
                #pedido2.qualPagina = atual
                pathpdfatual2 = pathpdfatual
                #pedido2.qualPdf = pathpdfatual2
                #pedido2.matriz = self.mat
                #pedido2.zoom = self.zoom_x*zoom
                #pedido2.scrolltotal = self.scrolly
                #pedido2.scrollvalue = self.vscrollbar.get()[0]
                self.docInnerCanvas.delete("enhanceobs"+pathpdfatual+str(processed_pages[atual % minMaxLabels]))
                self.clearSomeImages(["enhanceobs"+pathpdfatual+str(processed_pages[atual % minMaxLabels])])
                #self.docInnerCanvas.delete("enhanceobs"+pathpdfatual+str(processed_pages[pedido.qualLabel]))
                processed_pages[atual % minMaxLabels] = atual
                #pedido2.canvash = self.canvash
                pedido2 = PedidoDePagina(qualLabel = atual % minMaxLabels, qualPdf = pathpdfatual2, qualPagina = atual, matriz = self.mat, \
                  pixheight = infoLaudo[pathpdfatual].pixorgh, pixwidth = infoLaudo[pathpdfatual].pixorgw, zoom = self.zoom_x*zoom, \
                      scrollvalue = self.vscrollbar.get()[0] ,\
                      scrolltotal = self.scrolly, canvash = self.canvash, mt = infoLaudo[pathpdfatual].mt, \
                          mb = infoLaudo[pathpdfatual].mb, me = infoLaudo[pathpdfatual].me, md = infoLaudo[pathpdfatual].md)
                request_queuexml.put(pedido2)
                request_queue.put(pedido2) 
                processed_requests[pedido2.qualLabel] = pedido2
            for i in range(1, math.ceil(minMaxLabels/2)):                  
                if(atual + i < infoLaudo[pathpdfatual].len):
                    if((atual + i) not in processed_pages):                      
                        #pedido3 = PedidoDePagina()
                        #pedido3.mt = infoLaudo[pathpdfatual].mt
                        #pedido3.mb = infoLaudo[pathpdfatual].mb
                        #pedido3.me = infoLaudo[pathpdfatual].me
                        #pedido3.md = infoLaudo[pathpdfatual].md
                        #pedido3.pixheight = infoLaudo[pathpdfatual].pixorgh
                        #pedido3.pixwidth = infoLaudo[pathpdfatual].pixorgw
                        #pedido3.qualLabel = (atual + i) % minMaxLabels
                        #pedido3.qualPagina = atual + i
                        #pedido3.matriz = self.mat
                        
                        pathpdfatual2 = pathpdfatual
                        #pedido3.qualPdf = pathpdfatual2
                        self.docInnerCanvas.delete("enhanceobs"+pathpdfatual+str(processed_pages[(atual + i) % minMaxLabels]))
                        self.clearSomeImages(["enhanceobs"+pathpdfatual+str(processed_pages[(atual + i) % minMaxLabels])])
                        if(processed_pages[(atual + i) % minMaxLabels] in self.alreadyenhanced):
                            self.alreadyenhanced.remove(processed_pages[(atual + i) % minMaxLabels])
                        processed_pages[(atual + i) % minMaxLabels] = (atual+i)
                        #pedido3.zoom = self.zoom_x*zoom
                        #pedido3.scrollvalue = self.vscrollbar.get()[0]
                        #pedido3.scrolltotal = self.scrolly
                        #pedido3.canvash = self.canvash
                        pedido3 = PedidoDePagina(qualLabel = (atual + i) % minMaxLabels, qualPdf = pathpdfatual2, qualPagina = atual + i, matriz = self.mat, \
                                                 pixheight = infoLaudo[pathpdfatual].pixorgh, pixwidth = infoLaudo[pathpdfatual].pixorgw, zoom = self.zoom_x*zoom, \
                                                     scrollvalue = self.vscrollbar.get()[0] ,\
                                                         scrolltotal = self.scrolly, canvash = self.canvash, mt = infoLaudo[pathpdfatual].mt, \
                                                             mb = infoLaudo[pathpdfatual].mb, me = infoLaudo[pathpdfatual].me, md = infoLaudo[pathpdfatual].md)
                        request_queuexml.put(pedido3)
                        request_queue.put(pedido3) 
                        processed_requests[pedido3.qualLabel] = pedido3
                if(atual-i >= 0):
                    if((atual - i) not in processed_pages):
                        #pedido4 = PedidoDePagina()
                        #pedido4.mt = infoLaudo[pathpdfatual].mt
                        #pedido4.mb = infoLaudo[pathpdfatual].mb
                        #pedido4.me = infoLaudo[pathpdfatual].me
                        #pedido4.md = infoLaudo[pathpdfatual].md
                        #pedido4.pixheight = infoLaudo[pathpdfatual].pixorgh
                        #pedido4.pixwidth = infoLaudo[pathpdfatual].pixorgw
                        #pedido4.qualLabel = (atual - i) % minMaxLabels
                        #pedido4.qualPagina = atual -i
                        #pedido4.matriz = self.mat
                        pathpdfatual2 = pathpdfatual
                        #pedido4.qualPdf = pathpdfatual2
                        #pedido4.scrollvalue = self.vscrollbar.get()[0]
                        #pedido4.zoom = self.zoom_x*zoom
                        self.docInnerCanvas.delete("enhanceobs"+pathpdfatual+str(processed_pages[(atual - i) % minMaxLabels]))
                        self.clearSomeImages(["enhanceobs"+pathpdfatual+str(processed_pages[(atual - i) % minMaxLabels])])
                        if(processed_pages[(atual - i) % minMaxLabels] in self.alreadyenhanced):
                            self.alreadyenhanced.remove(processed_pages[(atual - i) % minMaxLabels])
                            
                        pedido4 = PedidoDePagina(qualLabel = (atual - i) % minMaxLabels, qualPdf = pathpdfatual2, qualPagina = atual -i, matriz = self.mat, \
                                                 pixheight = infoLaudo[pathpdfatual].pixorgh, pixwidth = infoLaudo[pathpdfatual].pixorgw, zoom = self.zoom_x*zoom, \
                                                     scrollvalue = self.vscrollbar.get()[0] ,\
                                                         scrolltotal = self.scrolly, canvash = self.canvash, mt = infoLaudo[pathpdfatual].mt, \
                                                             mb = infoLaudo[pathpdfatual].mb, me = infoLaudo[pathpdfatual].me, md = infoLaudo[pathpdfatual].md)
                        processed_pages[(atual - i) % minMaxLabels] = (atual-i)
                        
                        #pedido4.scrolltotal = self.scrolly
                        #pedido4.canvash = self.canvash
                        request_queuexml.put(pedido4)
                        request_queue.put(pedido4)
                        processed_requests[(atual - i) % minMaxLabels] = pedido4
        except Exception as ex:
            printlogexception(ex=ex)
        finally:
            root.after(10, self.checkPages)
            
    
            
    def treeview_selection(self, event=None, item=None):
        global minMaxLabels, processed_pages, infoLaudo, pathpdfatual, zoom, docatual
        if(event!=None):
            iid = self.treeviewEqs.identify_row(event.y)
            if(iid==None or iid==''):
                return
        try:            
            for pdf in infoLaudo:
                infoLaudo[pdf].retangulosDesenhados = {}
            selecao = None
            if(item==None):
                selecao = self.treeviewEqs.focus()                
            else:
                selecao = item
            pai =  (self.treeviewEqs.parent(selecao))
            if(pai==''):
                children = self.treeviewEqs.get_children(selecao)
                if(len(children)==1):
                    self.treeviewEqs.focus(children[0])
                    self.treeviewEqs.selection_set(children[0])
                    selecao = children[0]
            valores = (self.treeviewEqs.item(selecao, 'values'))
            opcao = None       
            
            if(valores!=None and valores!='' and len(valores)>0):
                opcao = valores[0] 
            
            if(opcao=='pdf'):
                newpath = valores[1]
                try:
                    self.positions[self.indiceposition] = (pathpdfatual, self.vscrollbar.get()[0])
                    self.indiceposition += 1
                    if(self.indiceposition>=10):
                        self.indiceposition = 0
                except Exception as ex:
                    None
                if(pathpdfatual!=newpath or item!=None):
                    
                    #self.clearSomeImages(["enhanceobs"])
                    #self.docInnerCanvas.yview_moveto(infoLaudo[newpath].ultimaPosicao)
                    #infoLaudo[pathpdfatual].ultimaPosicao=(self.vscrollbar.get()[0])
                    for i in range(minMaxLabels):
                        processed_pages[i] = -1
                    sobraEspaco = 0
                    if(self.docFrame.winfo_width() > infoLaudo[pathpdfatual].pixorgw * self.zoom_x * zoom):
                        sobraEspaco = self.docInnerCanvas.winfo_x()
                    self.maiorw = self.docFrame.winfo_width()
                    if(infoLaudo[newpath].pixorgw*self.zoom_x*zoom>self.maiorw):
                        self.maiorw = infoLaudo[newpath].pixorgw*self.zoom_x *zoom           
                    self.scrolly = infoLaudo[newpath].pixorgh*self.zoom_x*zoom*infoLaudo[newpath].len  - 35
                    self.docInnerCanvas.config(scrollregion=(sobraEspaco, 0, sobraEspaco+ (infoLaudo[newpath].pixorgw*zoom*self.zoom_x), self.scrolly))
                    pagina = round(infoLaudo[newpath].ultimaPosicao*infoLaudo[newpath].len)   
                    self.docInnerCanvas.yview_moveto(infoLaudo[newpath].ultimaPosicao)
                    if(str(pagina+1)!=self.pagVar.get()):
                        self.pagVar.set(str(pagina+1))
                    #root.update_idletasks()
                    pathpdfatual =newpath
                    try:
                        docatual.close()
                    except Exception as ex:
                        None
                    docatual = fitz.open(pathpdfatual)
                    self.labeldocname.config(text=os.path.basename(pathpdfatual))
                    #self.docInnerCanvas.delete("quad")
                    #self.docInnerCanvas.delete("simplesearch")
                    #self.docInnerCanvas.delete("obsitem")
                    #self.docInnerCanvas.delete("link")
                    #self.clearSomeImages(["quad", "simplesearch", "obsitem", "link"])  
                    self.clearAllImages()
                    self.totalPgg.config(text="/ "+str(infoLaudo[pathpdfatual].len))                    
                    for pdf in infoLaudo:
                        infoLaudo[pdf].retangulosDesenhados = {}  
                if(event!=None):
                    self.treeviewEqs.selection_set(iid)
                else:
                    self.treeviewEqs.selection_set(item)
                                    
            elif(opcao=="toc"): 
                newpath = valores[1]
                eq = selecao[3]
                toc = selecao[2]
                self.positions[self.indiceposition] = (pathpdfatual, self.vscrollbar.get()[0])
                self.indiceposition += 1
                if(self.indiceposition>=10):
                    self.indiceposition = 0
                if(pathpdfatual!=newpath):
                    pathpdfatual =newpath
                    try:
                        docatual.close()
                    except Exception as ex:
                        None
                    docatual = fitz.open(pathpdfatual)
                    self.clearAllImages()
                    self.docwidth = self.docOuterFrame.winfo_width()
                    for i in range(minMaxLabels):
                        processed_pages[i] = -1
                    sobraEspaco = 0
                    if(self.docFrame.winfo_width() > infoLaudo[pathpdfatual].pixorgw * self.zoom_x * zoom):
                        sobraEspaco = self.docInnerCanvas.winfo_x() 
                    self.maiorw = self.docFrame.winfo_width()
                    if(infoLaudo[pathpdfatual].pixorgw*self.zoom_x*zoom>self.maiorw):
                        self.maiorw = infoLaudo[pathpdfatual].pixorgw*self.zoom_x *zoom           
                    self.scrolly = infoLaudo[pathpdfatual].pixorgh*self.zoom_x*zoom*infoLaudo[pathpdfatual].len  - 35
                    self.docInnerCanvas.config(scrollregion=(sobraEspaco, 0, sobraEspaco+ (infoLaudo[pathpdfatual].pixorgw*zoom*self.zoom_x), self.scrolly))
                pagina = float(valores[3])
                deslocy = float(valores[4])
                ondeir = (pagina / (infoLaudo[pathpdfatual].len)+(deslocy*self.zoom_x*zoom)/self.scrolly)
                self.docInnerCanvas.yview_moveto(ondeir)
                if(str(pagina+1)!=self.pagVar.get()):
                    self.pagVar.set(str(pagina+1))
                #root.update_idletasks()
                if(event!=None):
                    self.treeviewEqs.selection_set(iid)
                else:
                    self.treeviewEqs.selection_set(item)
            for rel in self.treeviewEqs.get_children(''):
                self.treeviewEqs.item(rel, open=True)
        except Exception as ex:
            printlogexception(ex=ex)
            
    def tabOpened(self, event=None):
        texto = (self.notebook.tab(self.notebook.select(), 'text'))        
        if(texto=='Buscas (*)'):
            self.notebook.tab(self.notebook.select(), text="Buscas")
    
    def treeview_obs_right(self, event=None):
        
        iid = self.treeviewObs.identify_row(event.y)  
        if(self.treeviewObs.tag_has('obscat',iid)):
            self.editdelcat = tkinter.Menu(root, tearoff=0)
            
            self.editdelcat.add_command(label="Editar Categoria", image=self.editcat, compound='left', command=lambda: self.addcatpopup(None, 'edit', self.treeviewObs.item(self.treeviewObs.selection()[0], 'text')))
            self.editdelcatmove = tkinter.Menu(self.editdelcat, tearoff=0)
            self.editdelcatmove.add_command(label="Mover para o topo", image=self.movecattop, compound='left', command=lambda: self.moveCategory('top', self.treeviewObs.selection()[0]))
            self.editdelcatmove.add_command(label="Mover para cima", image=self.movecatup, compound='left', command=lambda: self.moveCategory('up', self.treeviewObs.selection()[0]))
            self.editdelcatmove.add_command(label="Mover para baixo", image=self.movecatdown, compound='left', command=lambda: self.moveCategory('down', self.treeviewObs.selection()[0]))
            self.editdelcatmove.add_command(label="Mover para o fundo", image=self.movecatbottom, compound='left', command=lambda: self.moveCategory('bottom', self.treeviewObs.selection()[0]))
            self.editdelcat.add_cascade(label='Mover Categoria', menu=self.editdelcatmove, image=self.movecat, compound='left')  
            self.copyobsto = tkinter.Menu(self.editdelcat, tearoff=0)
            self.copyobsto.add_command(label="Para o clipboard", image=self.copycat, compound='left', command=lambda: self.addcatpopup(None, 'copiarclip', self.treeviewObs.item(self.treeviewObs.selection()[0], 'values')))       
            self.copyobsto.add_command(label="Em formato CSV", image=self.copycat, compound='left', command=lambda: self.addcatpopup(None, 'copiarcsv', self.treeviewObs.item(self.treeviewObs.selection()[0], 'values')))       
            self.copyobsto.add_command(label="Clipboard (RTF - Especial)", image=self.copycat, compound='left', command=lambda: self.addcatpopup(None, 'copiarespecial', self.treeviewObs.item(self.treeviewObs.selection()[0], 'values')))
            
            self.editdelcat.add_cascade(label='Copiar Páginas', menu=self.copyobsto, image=self.copycat, compound='left')  
            if(self.treeviewObs.item(iid,'values')[0]=='0' or expertmode):                
                self.editdelcat.add_separator()
                self.editdelcat.add_command(label="Excluir Categoria", image=self.delcat, compound='left', command=lambda: self.addcatpopup(None, 'exclude', self.treeviewObs.item(self.treeviewObs.selection()[0], 'text')))
            
            self.treeviewObs.selection_set(iid)
            self.treeviewObs.focus(iid)
            try:
                if(isinstance(event.widget, ttk.Treeview)):
                    #if(self.treeviewObs.tag_has('obscat',iid ) or self.treeviewObs.tag_has('relobs',iid ) or self.treeviewObs.tag_has('tocobs',iid )):
                    self.editdelcat.tk_popup(event.x_root, event.y_root) 
                    ##if(self.treeviewObs.item(self.treeviewObs.selection()[0],'values')[0])=='0':
                     #   #item = self.treeviewObs.selection()[0]
                        
                    #    self.editdelcat.tk_popup(event.x_root, event.y_root) 
                    #    
                    #elif(expertmode):
                    #    
                    #    self.editdelcat.tk_popup(event.x_root, event.y_root) 
            except Exception as ex:
                printlogexception(ex=ex) 
            finally:
                self.editdelcat.grab_release()
        elif(self.treeviewObs.tag_has('tocobs',iid) or self.treeviewObs.tag_has('relobs',iid)):
            self.editdelcat = tkinter.Menu(root, tearoff=0)
              
            self.copyobsto = tkinter.Menu(self.editdelcat, tearoff=0)
            
            self.copyobsto.add_command(label="Para o clipboard", image=self.copycat, compound='left', command=lambda: self.addcatpopup(None, 'copiarclip',  self.treeviewObs.item(self.treeviewObs.selection()[0], 'values')))      
            self.copyobsto.add_command(label="Em formato CSV", image=self.copycat, compound='left', command=lambda: self.addcatpopup(None, 'copiarcsv',  self.treeviewObs.item(self.treeviewObs.selection()[0], 'values')))       
            self.copyobsto.add_command(label="Clipboard (RTF - Especial)", image=self.copycat, compound='left', command=lambda: self.addcatpopup(None, 'copiarespecial',  self.treeviewObs.item(self.treeviewObs.selection()[0], 'values')))
            
            self.editdelcat.add_cascade(label='Copiar Páginas', menu=self.copyobsto, image=self.copycat, compound='left')  
            #self.editdelcat.add_separator()
            
            self.treeviewObs.selection_set(iid)
            self.treeviewObs.focus(iid)
            try:
                if(isinstance(event.widget, ttk.Treeview)):
                    #if(self.treeviewObs.tag_has('obscat',iid ) or self.treeviewObs.tag_has('relobs',iid ) or self.treeviewObs.tag_has('tocobs',iid )):
                    self.editdelcat.tk_popup(event.x_root, event.y_root) 
                    ##if(self.treeviewObs.item(self.treeviewObs.selection()[0],'values')[0])=='0':
                     #   #item = self.treeviewObs.selection()[0]
                        
                    #    self.editdelcat.tk_popup(event.x_root, event.y_root) 
                    #    
                    #elif(expertmode):
                    #    
                    #    self.editdelcat.tk_popup(event.x_root, event.y_root) 
            except Exception as ex:
                printlogexception(ex=ex) 
            finally:
                self.editdelcat.grab_release()
        elif(self.treeviewObs.tag_has('obsitem', iid)):
            self.treeviewObs.selection_set(iid)
            self.treeviewObs.focus(iid)
            try:
                if(isinstance(event.widget, ttk.Treeview)):
                    tagsss = self.treeviewObs.item(iid, 'tags')
                    alterado = False
                    self.delitemcat = tkinter.Menu(root, tearoff=0)
                    if(self.treeviewObs.item(iid,'values')[0]=='0' or expertmode):  
                        self.delitemcat.add_command(label="Excluir Marcação", image=self.delcat, compound='left', command=lambda: self.addcatpopup(None, 'excludeitem', self.treeviewObs.item(self.treeviewObs.selection()[0], 'text')))
                    self.delitemcat.add_command(label="Alterar Categoria", image=self.editcat, compound='left', command=lambda: self.addcatpopup(None, 'changecat', self.treeviewObs.item(self.treeviewObs.selection()[0])))
                    self.copyobsto = tkinter.Menu(self.delitemcat, tearoff=0)
                    #self.copyobsto.add_command(label="Para o clipboard", image=self.copycat, compound='left', command=lambda: self.addcatpopup(None, 'copiarclip',  self.treeviewObs.item(self.treeviewObs.selection()[0], 'values')))      
                    #self.copyobsto.add_command(label="Em formato CSV", image=self.copycat, compound='left', command=lambda: self.addcatpopup(None, 'copiarcsv',  self.treeviewObs.item(self.treeviewObs.selection()[0], 'values')))       
                    self.copyobsto.add_command(label="Clipboard (RTF - Especial)", image=self.copycat, compound='left', command=lambda: self.addcatpopup(None, 'copiarespecial',  self.treeviewObs.item(self.treeviewObs.selection()[0], 'values')))
                    
                    self.delitemcat.add_cascade(label='Copiar Páginas', menu=self.copyobsto, image=self.copycat, compound='left')  
                    for tg in tagsss:
                        if('alterado' in tg):
                            alterado = True
                    if(self.treeviewObs.item(self.treeviewObs.selection()[0],'values')[9])=='0':
                        #alterado = self.treeviewObs.tag_has('alterado', (iid,))
                        if(not alterado):
                            None
                            #self.delitemcat.entryconfig("Validar Observação", state='disabled')
                        else:
                            self.delitemcat.add_command(label="Validar Observação", image=self.checki, compound='left', command=lambda: self.addcatpopup(None, 'validarobs', self.treeviewObs.item(self.treeviewObs.selection()[0])))

                        self.delitemcat.tk_popup(event.x_root, event.y_root) 
                    elif(expertmode):
                        #alterado = self.treeviewObs.tag_has('alterado', (iid,))
                        if(not alterado):
                            None
                            #self.delitemcat.entryconfig("Validar Observação", state='disabled')
                        else:
                            self.delitemcat.add_command(label="Validar Observação", image=self.checki, compound='left', command=lambda: self.addcatpopup(None, 'validarobs', self.treeviewObs.item(self.treeviewObs.selection()[0])))

                        self.delitemcat.tk_popup(event.x_root, event.y_root) 
            except Exception as ex:
               None 
            finally:
                self.delitemcat.grab_release()            
            
    def treeview_search_right(self, event=None):
        iid = self.treeviewSearches.identify_row(event.y)  
        if(self.treeviewSearches.parent(iid)=='' and self.treeviewSearches.item(iid, 'text') != '' and False):
            self.treeviewSearches.selection_set(iid)
            try:
                if(isinstance(event.widget, ttk.Treeview)):
                    resultsearch = searchResultsDict[iid]
                    if(resultsearch.fixo):
                        self.menuexcludesearch.tk_popup(event.x_root, event.y_root) 
                    elif(expertmode):
                        self.menuexcludesearch.tk_popup(event.x_root, event.y_root) 
            except Exception as ex:
                printlogexception(ex=ex)
            finally:
                self.menuexcludesearch.grab_release()
        elif(iid != ''):
            self.treeviewSearches.selection_set(iid)
            try:
                if(isinstance(event.widget, ttk.Treeview)):
                    self.menuexportsearchtobs = tkinter.Menu(root, tearoff=0)
                    getobscatas =  self.treeviewObs.get_children('')
                    menucats = tkinter.Menu(self.menuexportsearchtobs, tearoff=0)
                    for obscat in getobscatas:
                        texto = self.treeviewObs.item(obscat, 'text')
                        menucats.add_command(label=texto, image=self.itemimage, compound='left', command=partial(self.addmarkerFromSearch,obscat,event))
                    self.menuexportsearchtobs.add_cascade(label='Enviar para:', menu=menucats, image=self.catimage, compound='left')
                    if(self.treeviewSearches.tag_has('termosearch', iid)):
                        self.menuexportsearchtobs.add_separator()
                        self.menuexportsearchtobs.add_command(label="Excluir Busca", image=self.delcat, compound='right', command=self.exclude_search)   
                    self.menuexportsearchtobs.tk_popup(event.x_root, event.y_root)
            except Exception as ex:
                printlogexception(ex=ex)
            finally:
                self.menuexportsearchtobs.grab_release()

        
    def exclude_search(self, event=None, lista=None):
        global queuesair, processes, delsearchprocess, listaTERMOS
        try:
            #if(lista!=None):
            #    for iid in lista:
            #        None
            #else:
            #    selecao = self.treeviewSearches.selection()[0]
            listadel = []
            for selecao in self.treeviewSearches.selection():
                if(selecao in searchResultsDict):
                    resultsearch = searchResultsDict[selecao]
                    tipobusca = resultsearch.advanced            
                    oldqueue = []
                    if((resultsearch.termo.upper(), tipobusca) in searchqueue):
                        searchqueue.remove((resultsearch.termo.upper(), tipobusca))                
                    queuesair.put(('pararbusca', resultsearch.idtermo))
                    try:
                        listadel.append(resultsearch.idtermo)
                        #deleteSearchProcess(result_queue, pathdb, resultsearch.idtermo, erros, queuesair)
                        self.termosearchVar.set("")
                            
                        del listaTERMOS[(resultsearch.termo.strip().lower(), resultsearch.advanced)]
                        self.searchedTerms.remove((resultsearch.termo.strip().upper(),resultsearch.advanced))   
                        del searchResultsDict[selecao]
                    except Exception as ex:
                        printlogexception(ex=ex)
            self.treeviewSearches.delete(*self.treeviewSearches.selection())
            deleteSearchProcess(result_queue, pathdb, listadel, erros, queuesair)
        except Exception as ex:
            printlogexception(ex=ex)     
            
    def querySql(self):
        self.w=querySqlWindow(root,'')
        self.querysql["state"] = "disabled" 
        root.wait_window(self.w.top)
        self.querysql["state"] = "normal"
        if(self.w.value!=None and self.w.value.strip()!=''):
            self.searchTerm(event=None, advancedsearch=True, termo=self.w.value)
            
    
    def changecatpopupresult(self, event=None, operacao=None, window=None, valornovo=None, item=None, novacatset=None):
        if(operacao=='ok'):
            iiditem = self.treeviewObs.item(item, 'values')[8]
            iidantigo = self.treeviewObs.item(item, 'values')[10]
            iidnovo = self.treeviewObs.item(novacatset[valornovo], 'values')[1]
            if(str(iidantigo!=str(iidnovo))):
                paginainit = self.treeviewObs.item(item, 'values')[2]
                relpath = self.treeviewObs.item(item, 'values')[1]
                p0y = self.treeviewObs.item(item, 'values')[4]
                basepdf = os.path.normpath(os.path.join(pathdb.parent, relpath))
                sqliteconn =  connectDB(str(pathdb), 5)
                cursor = sqliteconn.cursor()
                #cursor.execute("PRAGMA journal_mode=WAL")
                try:
                    updateinto2 = "UPDATE Anexo_Eletronico_Obsitens set id_obscat = ? WHERE id_obs = ?"
                    ##cursor.execute("PRAGMA journal_mode=WAL")
                    cursor.execute(updateinto2, (iidnovo,iiditem,))
                    sqliteconn.commit()
                    cursor.close()
                    try:
                        tocname = self.locateToc(int(paginainit), basepdf, p0y=p0y)
                        novoiidtoc = str(iidnovo)+basepdf+tocname
                        ident= '     '
                        if(not self.treeviewObs.exists(str(iidnovo)+basepdf)):
                            self.treeviewObs.insert(parent=str(iidnovo), iid=(str(iidnovo)+basepdf), text=ident+os.path.basename(basepdf), index='end', tag=('relobs'))
                            self.treeviewObs.tag_configure('relobs', background='#e3e1e1')
                        if(not self.treeviewObs.exists(str(iidnovo)+basepdf+tocname)):
                            novoiidtoc = self.treeviewObs.insert(parent=str(iidnovo)+basepdf, iid=(str(iidnovo)+basepdf+tocname), text=ident+ident+tocname, index='end',\
                                                                 tag=('tocobs'))
                        
                        novoiidtocindex = self.qualIndexTreeObs( paginainit, (str(iidnovo)+basepdf+tocname))
                        parenteantigo = self.treeviewObs.parent(item)
                        self.treeviewObs.move(item, novoiidtoc, novoiidtocindex)
                        children = self.treeviewObs.get_children(parenteantigo)
                        if(len(children)==0 and self.treeviewObs.parent(parenteantigo)!=''):
                            self.treeviewObs.delete(parenteantigo)
                    except Exception as ex:
                        printlogexception(ex=ex)
                        if(not self.treeviewObs.exists(str(iidnovo)+basepdf)):
                            self.treeviewObs.insert(parent=str(iidnovo), iid=(str(iidnovo)+basepdf), text=ident+os.path.basename(basepdf), index='end', tag=('relobs'))
                            self.treeviewObs.tag_configure('relobs', background='#e3e1e1')
                        novoiidindex = self.qualIndexTreeObs( paginainit, (str(iidnovo)+basepdf))
                        self.treeviewObs.move(item, (str(iidnovo)+basepdf), novoiidindex)
                        parenteantigo = self.treeviewObs.parent(item)
                        #self.treeviewObs.move(item, novoiidtoc, novoiidtocindex)
                        children = self.treeviewObs.get_children(parenteantigo)
                        if(len(children)==0 and self.treeviewObs.parent(parenteantigo)!=''):
                            self.treeviewObs.delete(parenteantigo)
                except Exception as ex:
                    printlogexception(ex=ex)
                finally:
                    if(cursor):
                        cursor.close()
                    if(sqliteconn):
                        sqliteconn.close()
                
            window.destroy()
        elif(operacao=='cancel'):
            window.destroy()        
    
            
    def addcatpopup(self, event=None, operacao=None,valor=None) :
        
        global root
        try:
            iid = self.treeviewObs.selection()[0]
        except Exception as ex:
            iid = None
        #valor = self.treeviewObs.item(iid, 'values')
        if(operacao=='excludeitem'):
            item = self.treeviewObs.selection()[0]
            valores = self.treeviewObs.item(item, 'values')
            sqliteconn =  connectDB(str(pathdb), 5)
            
            try:
                for pdf in infoLaudo:
                    deletar = []
                    for falta in infoLaudo[pdf].linkscustom:
                        if(isinstance(falta, str) and 'falta' in falta):
                            for link in infoLaudo[pdf].linkscustom[falta]:                                
                                if(str(link[12])==str(valores[8])):
                                    cursor = sqliteconn.cursor()
                                    #cursor.execute("PRAGMA journal_mode=WAL")
                                    cursor.execute("DELETE FROM Anexo_Eletronico_Links WHERE id_link = ?", (link[11],))
                                    cursor.close()
                                    listaquads = self.docInnerCanvas.find_withtag("link"+str(link[11]))
                                    self.docInnerCanvas.delete("link"+str(link[11]))
                                    deletar.append(falta)
                                    for quadelement in listaquads:
                                        deletar.append(quadelement)
                    for delete in deletar:
                        if(isinstance(delete, str) and 'falta' in delete):
                            novalista = []
                            for link in infoLaudo[pdf].linkscustom[delete]:
                                if(str(link[12])!=str(valores[8])):
                                    novalista.append(link)
                            infoLaudo[pdf].linkscustom[delete] = novalista
                        else:
                            del infoLaudo[pdf].linkscustom[delete]
                sqliteconn.execute("PRAGMA foreign_keys = ON")
                deletefrom = "DELETE FROM Anexo_Eletronico_Obsitens WHERE id_obs = ?"
                cursor = sqliteconn.cursor()
                #cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute(deletefrom, (valores[8],))
                cursor.close()
                parenteantigo = self.treeviewObs.parent(item)
                
                self.treeviewObs.delete(item)
                children = self.treeviewObs.get_children(parenteantigo)

                while(parenteantigo!=''):
                    children = self.treeviewObs.get_children(parenteantigo)
                    temp = self.treeviewObs.parent(parenteantigo)
                    if(len(children)>0 or temp==''):
                        break
                    self.treeviewObs.delete(parenteantigo)
                    parenteantigo = temp
                    
                    
                sqliteconn.commit()
                
                            
               
            except Exception as ex:
                printlogexception(ex=ex)
            finally:
                #cursor.close()
                if(sqliteconn):
                    sqliteconn.close()
        elif(operacao=='exclude'):
            sqliteconn =  connectDB(str(pathdb), 5)
            cursor = sqliteconn.cursor()
            #cursor.execute("PRAGMA journal_mode=WAL")
            try:
                sqliteconn.execute("PRAGMA foreign_keys = ON")
                deletefrom2 = "DELETE FROM Anexo_Eletronico_Obscat WHERE obscat = ?"
                cursor.execute(deletefrom2, (valor.upper(),))
                self.treeviewObs.delete(self.treeviewObs.selection()[0])
                sqliteconn.commit()
            except Exception as ex:
                printlogexception(ex=ex)
            finally:
                cursor.close()
                if(sqliteconn):
                    sqliteconn.close()
        elif(operacao=='changecat'):
            window = tkinter.Toplevel()
            window.rowconfigure((0,1), weight=1)
            window.columnconfigure((0,1), weight=1)
            label = tkinter.Label(window, text='Nova Categoria')
            label.grid(row=0, column=0, padx=50, pady=20, sticky='ns')            
            n = tkinter.StringVar() 
            novacat = ttk.Combobox(window, width = 27,  
                            textvariable = n, exportselection=0, state="readonly")
            values = []
            filhos = self.treeviewObs.get_children('')
            novacatset = {}
            for filho in filhos:
                texto = self.treeviewObs.item(filho, 'text')  
                novacatset[texto] = filho
                values.append(texto)
            novacat['values'] = (values)
            novacat.current(0)
            novacat.grid(row=0, column=1, padx=50, pady=20, sticky='ns')
            item = self.treeviewObs.focus()
            button_ok = tkinter.Button(window, text="OK", command= lambda : self.changecatpopupresult(event=None, operacao='ok', window=window, valornovo=n.get(), item=item, novacatset=novacatset))
            button_ok.grid(row=1, column=0, padx=50, pady=20, sticky='ns')
            button_close = tkinter.Button(window, text="Cancelar", command= lambda : self.changecatpopupresult(event=None, operacao='cancel', window=window, valornovo=None, item=None, novacatset=None))
            button_close.grid(row=1, column=1, padx=50, pady=20, sticky='ns')
        elif(operacao=='copiarclip'):
            texto = ""
            if(self.treeviewObs.tag_has('obscat', iid)):
                children = self.treeviewObs.get_children(valor[1])
                
                for pdf in children:
                    paginas = set()
                    texto += self.treeviewObs.item(pdf, 'text').strip() + "\n"
                    children2 = self.treeviewObs.get_children(pdf)
                    if(len(children2)>0):
                        for toc in children2: 
                            texto += self.treeviewObs.item(toc, 'text').strip() + "\n"
                            children3 = self.treeviewObs.get_children(toc)
                            primeiro = True
                            for child2 in children3:
                                pagi = int(self.treeviewObs.item(child2, 'values')[2].strip())+1                            
                                if(not pagi in paginas):
                                    if(primeiro):                                    
                                        texto += str(int(self.treeviewObs.item(child2, 'values')[2].strip())+1)
                                        primeiro = False
                                    else:
                                        texto += ", "+  str(int(self.treeviewObs.item(child2, 'values')[2].strip())+1)
                                paginas.add(pagi)
                            texto += "\n"
                    else:
                        primeiro = True
                        for child2 in children2:
                            pagi = int(self.treeviewObs.item(child2, 'values')[2].strip())+1                        
                            if(not pagi in paginas):
                                if(primeiro):                                
                                    texto += str(int(self.treeviewObs.item(child2, 'values')[2].strip())+1)
                                    primeiro = False
                                else:
                                    texto += ", "+ str(int(self.treeviewObs.item(child2, 'values')[2].strip())+1)
                            paginas.add(pagi)
                            texto += "\n"
                    texto += "\n"
            elif(self.treeviewObs.tag_has('relobs', iid)):
                pdf = iid
                children2 = self.treeviewObs.get_children(pdf)
                if(len(children2)>0):
                    paginas = set()
                    for toc in children2: 
                        texto += self.treeviewObs.item(toc, 'text').strip() + "\n"
                        children3 = self.treeviewObs.get_children(toc)
                        primeiro = True
                        for child2 in children3:
                            pagi = int(self.treeviewObs.item(child2, 'values')[2].strip())+1                            
                            if(not pagi in paginas):
                                if(primeiro):                                    
                                    texto += str(int(self.treeviewObs.item(child2, 'values')[2].strip())+1)
                                    primeiro = False
                                else:
                                    texto += ", "+  str(int(self.treeviewObs.item(child2, 'values')[2].strip())+1)
                            paginas.add(pagi)
                        texto += "\n"
                else:
                    paginas = set()
                    primeiro = True
                    for child2 in children2:
                        pagi = int(self.treeviewObs.item(child2, 'values')[2].strip())+1                        
                        if(not pagi in paginas):
                            if(primeiro):                                
                                texto += str(int(self.treeviewObs.item(child2, 'values')[2].strip())+1)
                                primeiro = False
                            else:
                                texto += ", "+ str(int(self.treeviewObs.item(child2, 'values')[2].strip())+1)
                        paginas.add(pagi)
                        texto += "\n"
                texto += "\n"
            elif(self.treeviewObs.tag_has('tocobs', iid)):
                paginas = set()
                primeiro = True
                pdf = self.treeviewObs.parent(iid)
                toc = iid
                children3 = self.treeviewObs.get_children(toc)
                for child2 in children3:
                    pagi = int(self.treeviewObs.item(child2, 'values')[2].strip())+1                            
                    if(not pagi in paginas):
                        if(primeiro):                                    
                            texto += str(int(self.treeviewObs.item(child2, 'values')[2].strip())+1)
                            primeiro = False
                        else:
                            texto += ", "+  str(int(self.treeviewObs.item(child2, 'values')[2].strip())+1)
                    paginas.add(pagi)
                texto += "\n"
            #elif(self.treeviewObs.tag_has('obsitem', iid)):
                
            clipboard.copy(texto.strip())
        
        elif(operacao=='copiarcsv'):
            tipos = [('CSV', '*.csv')]
            path = (asksaveasfilename(filetypes=tipos, defaultextension=tipos))
            if(path!=None and path!=''):
                with open(path, mode='w', newline='', encoding='utf-8') as csv_file:
                    writer = csv.writer(csv_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    writer.writerow(['Documento', 'Seção', 'Página'])
                    children = self.treeviewObs.get_children(iid)
                    if(self.treeviewObs.tag_has('obscat', iid)):
                        for pdf in children:
                            paginas = set()
                            children2 = self.treeviewObs.get_children(pdf)
                            if(len(children2)>0):
                                for toc in children2:
                                    children3 = self.treeviewObs.get_children(toc)
                                    for child2 in children3:
                                        pagi = int(self.treeviewObs.item(child2, 'values')[2].strip())+1                            
                                        if(not pagi in paginas):
                                            writer.writerow([self.treeviewObs.item(pdf, 'text').strip(), self.treeviewObs.item(toc, 'text').strip(), int(self.treeviewObs.item(child2, 'values')[2].strip())+1])
                                        paginas.add(pagi)
                            else:
                                for child2 in children2:
                                    pagi = int(self.treeviewObs.item(child2, 'values')[2].strip())+1                        
                                    if(not pagi in paginas):
                                        writer.writerow([self.treeviewObs.item(pdf, 'text').strip(), '-', int(self.treeviewObs.item(child2, 'values')[2].strip())+1])
                                    paginas.add(pagi)
                    elif(self.treeviewObs.tag_has('relobs', iid)):
                        pdf = iid
                        children2 = self.treeviewObs.get_children(pdf)
                        if(len(children2)>0):
                            paginas = set()
                            for toc in children2:
                                children3 = self.treeviewObs.get_children(toc)
                                for child2 in children3:
                                    pagi = int(self.treeviewObs.item(child2, 'values')[2].strip())+1                            
                                    if(not pagi in paginas):
                                        writer.writerow([self.treeviewObs.item(pdf, 'text').strip(), self.treeviewObs.item(toc, 'text').strip(), int(self.treeviewObs.item(child2, 'values')[2].strip())+1])
                                    paginas.add(pagi)
                        else:
                            paginas = set()
                            for child2 in children2:
                                pagi = int(self.treeviewObs.item(child2, 'values')[2].strip())+1                        
                                if(not pagi in paginas):
                                    writer.writerow([self.treeviewObs.item(pdf, 'text').strip(), '-', int(self.treeviewObs.item(child2, 'values')[2].strip())+1])
                                paginas.add(pagi)
                    elif(self.treeviewObs.tag_has('tocobs', iid)):
                        pdf = self.treeviewObs.parent(iid)
                        toc = iid
                        children3 = self.treeviewObs.get_children(toc)
                        paginas = set()
                        for child2 in children3:
                            pagi = int(self.treeviewObs.item(child2, 'values')[2].strip())+1                            
                            if(not pagi in paginas):
                                writer.writerow([self.treeviewObs.item(pdf, 'text').strip(), self.treeviewObs.item(toc, 'text').strip(), int(self.treeviewObs.item(child2, 'values')[2].strip())+1])
                            paginas.add(pagi)
                        
        elif(operacao=="validarobs"):
            item = self.treeviewObs.selection()[0]
            valores = self.treeviewObs.item(item, 'values')
            iiditem = valores[8]
            sqliteconn =  connectDB(str(pathdb), 5)
            cursor = sqliteconn.cursor()
            try:
                #cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("UPDATE Anexo_Eletronico_Obsitens SET status = 'ok' WHERE id_obs = ?", (iiditem,))
                #self.treeviewObs.tag_configure(status+str(obsitem[8]), background='#ad0202')
                self.treeviewObs.tag_configure('alterado'+str(iiditem), background='#ffffff')
                self.treeviewObs.item(item, tags=('obsitem', 'ok'+str(iiditem),))
                
                sqliteconn.commit()
                
            except Exception as ex:
                printlogexception(ex=ex)
            finally:
                cursor.close()
                if(sqliteconn):
                    sqliteconn.close()
        elif(operacao=='copiarespecial'):
            docespecial = None
            try:
                rtftotal = bytearray("", 'utf8')
                
                pathdocespecial = None
                
                pagatual = None
                xmlatual = None
                rootxml = None
                textonatabela = ""
                cont = 1  
                if(self.treeviewObs.tag_has('obscat', iid)):
                    children = self.treeviewObs.get_children(valor[1])
                    for pdf in children:                    
                        children2 = self.treeviewObs.get_children(pdf)
                        if(len(children2)>0):
                            for toc in children2:
                                children3 = self.treeviewObs.get_children(toc)
                                for child2 in children3:
                                    valoresPecial = self.treeviewObs.item(child2, 'values')
                                    pagi = int(valoresPecial[2].strip())+1
                                    if(pathdocespecial!=valoresPecial[1]):
                                        pathdocespecial = valoresPecial[1]
                                        pagatual = None
                                        if(docespecial!=None):
                                            docespecial.close()
                                        if plt == "Linux":                           
                                            pathdocespecial1 = str(pathdocespecial).replace("\\","/")
                                        elif plt=="Windows":                 
                                            pathdocespecial1 = str(pathdocespecial).replace("/","\\")
                                        docespecial = fitz.open(pathdocespecial1)
                                    tiposelecao = valoresPecial[0]
                                    pinit = int(valoresPecial[2])
                                    pfim = int(valoresPecial[5])
                                    p0xinit = (int(float(valoresPecial[3])))
                                    p0yinit = (int(float(valoresPecial[4])))
                                    p1xinit = (int(float(valoresPecial[6])))
                                    p1yinit = (int(float(valoresPecial[7])))
                                    if(tiposelecao=='area'):
                                        textonatabela += self.ObstoRTf(pagi, docespecial, pathdocespecial1, tiposelecao, pinit, pfim, p0xinit, p0yinit, p1xinit, p1yinit)
                                    elif(tiposelecao=='texto'):
                                        textonatabela += self.ObstoRTf(pagi, docespecial, pathdocespecial1, tiposelecao, pinit, pfim, p0xinit, p0yinit, p1xinit, p1yinit) 
                elif(self.treeviewObs.tag_has('relobs', iid)):
                    pdf = iid
                    children2 = self.treeviewObs.get_children(pdf)
                    if(len(children2)>0):
                        for toc in children2:
                            children3 = self.treeviewObs.get_children(toc)
                            for child2 in children3:
                                valoresPecial = self.treeviewObs.item(child2, 'values')
                                pagi = int(valoresPecial[2].strip())+1
                                if(pathdocespecial!=valoresPecial[1]):
                                    pathdocespecial = valoresPecial[1]
                                    pagatual = None
                                    if(docespecial!=None):
                                        docespecial.close()
                                    if plt == "Linux":                           
                                        pathdocespecial1 = str(pathdocespecial).replace("\\","/")
                                    elif plt=="Windows":                 
                                        pathdocespecial1 = str(pathdocespecial).replace("/","\\")
                                    docespecial = fitz.open(pathdocespecial)
                                tiposelecao = valoresPecial[0]
                                pinit = int(valoresPecial[2])
                                pfim = int(valoresPecial[5])
                                p0xinit = (int(float(valoresPecial[3])))
                                p0yinit = (int(float(valoresPecial[4])))
                                p1xinit = (int(float(valoresPecial[6])))
                                p1yinit = (int(float(valoresPecial[7])))
                                if(tiposelecao=='area'):
                                    textonatabela += self.ObstoRTf(pagi, docespecial, pathdocespecial1, tiposelecao, pinit, pfim, p0xinit, p0yinit, p1xinit, p1yinit)
                                elif(tiposelecao=='texto'):
                                    textonatabela += self.ObstoRTf(pagi, docespecial, pathdocespecial1, tiposelecao, pinit, pfim, p0xinit, p0yinit, p1xinit, p1yinit) 
                elif(self.treeviewObs.tag_has('tocobs', iid)):
                    pdf = self.treeviewObs.parent(iid)
                    toc = iid
                    children3 = self.treeviewObs.get_children(toc)
                    for child2 in children3:
                        valoresPecial = self.treeviewObs.item(child2, 'values')
                        pagi = int(valoresPecial[2].strip())+1
                        if(pathdocespecial!=valoresPecial[1]):
                            pathdocespecial = valoresPecial[1]
                            pagatual = None
                            if(docespecial!=None):
                                docespecial.close()
                            if plt == "Linux":                           
                                pathdocespecial1 = str(pathdocespecial).replace("\\","/")
                            elif plt=="Windows":                 
                                pathdocespecial1 = str(pathdocespecial).replace("/","\\")
                            docespecial = fitz.open(pathdocespecial1)
                        tiposelecao = valoresPecial[0]
                        pinit = int(valoresPecial[2])
                        pfim = int(valoresPecial[5])
                        p0xinit = (int(float(valoresPecial[3])))
                        p0yinit = (int(float(valoresPecial[4])))
                        p1xinit = (int(float(valoresPecial[6])))
                        p1yinit = (int(float(valoresPecial[7])))
                        if(tiposelecao=='area'):
                            textonatabela += self.ObstoRTf(pagi, docespecial, pathdocespecial1, tiposelecao, pinit, pfim, p0xinit, p0yinit, p1xinit, p1yinit)
                        elif(tiposelecao=='texto'):
                            textonatabela += self.ObstoRTf(pagi, docespecial, pathdocespecial1, tiposelecao, pinit, pfim, p0xinit, p0yinit, p1xinit, p1yinit) 
                elif(self.treeviewObs.tag_has('obsitem', iid)):
                    pdf = self.treeviewObs.parent(iid)
                    child2 = iid
                    while(self.treeviewObs.parent(pdf)!=''):
                        pdf = self.treeviewObs.parent(pdf)
                    valoresPecial = self.treeviewObs.item(child2, 'values')
                    pagi = int(valoresPecial[2].strip())+1
                    if(pathdocespecial!=valoresPecial[1]):
                        pathdocespecial = valoresPecial[1]
                        #searchlist = os.path.join(application_path, "ListasDeBusca", categoria)
                        if plt == "Linux":                           
                            pathdocespecial1 = str(pathdocespecial).replace("\\","/")
                        elif plt=="Windows":                 
                            pathdocespecial1 = str(pathdocespecial).replace("/","\\")
                        pagatual = None
                        if(docespecial!=None):
                            docespecial.close()
                        docespecial = fitz.open(pathdocespecial1)
                    tiposelecao = valoresPecial[0]
                    pinit = int(valoresPecial[2])
                    pfim = int(valoresPecial[5])
                    p0xinit = (int(float(valoresPecial[3])))
                    p0yinit = (int(float(valoresPecial[4])))
                    p1xinit = (int(float(valoresPecial[6])))
                    p1yinit = (int(float(valoresPecial[7])))
                    if(tiposelecao=='area'):
                        textonatabela += self.ObstoRTf(pagi, docespecial, pathdocespecial1, tiposelecao, pinit, pfim, p0xinit, p0yinit, p1xinit, p1yinit)
                    elif(tiposelecao=='texto'):
                        textonatabela += self.ObstoRTf(pagi, docespecial, pathdocespecial1, tiposelecao, pinit, pfim, p0xinit, p0yinit, p1xinit, p1yinit) 
                    
                textofinal = ("{{\\rtf1\\ansi\\deff0{{\\fonttbl{{\\f0\\froman\\fprq2\\fcharset0 Times New Roman;}}{{\\f1\\froman\\fprq2\\fcharset2 Symbol;}}"+
               "{{\\f2\\fswiss\\fprq2\\fcharset0 Arial;}}}}{{\\colortbl;\\red240\\green240\\blue240;\\red221\\green221\\blue221;\\red255\\green255\\blue255;}} {}}}").format(textonatabela)
                rtf = bytearray(textofinal, 'utf8')
                if platform.system() == 'Windows':
                    
                    CF_RTF = win32clipboard.RegisterClipboardFormat("Rich Text Format")
                    win32clipboard.OpenClipboard(0)
                    win32clipboard.EmptyClipboard()
                    win32clipboard.SetClipboardData(CF_RTF, rtf)
                    win32clipboard.CloseClipboard()
                elif platform.system() == 'Linux':
                    subprocess.Popen(['xclip', '-selection', 'clipboard', '-t', 'text/rtf'], stdin=subprocess.PIPE).communicate(rtf)
                    #content = {'UTF8_STRING': 'string'.encode(), 'text/html': textofinal.encode()}
                    #klembord.set(content)
                    #klembord.set_with_rich_text('plain text',textofinal)
                    

            except Exception as ex:
                printlogexception(ex=ex)
            finally:
                try:
                    docespecial.close()
                except Exception as ex:
                    None
        else:
            self.w=popupWindow(root,valor)            
            self.menuaddcat["state"] = "disabled" 
            root.wait_window(self.w.top)
            self.menuaddcat["state"] = "normal"
            if(self.w.value!=None and self.w.value.strip()!=''):
                newcat = (self.w.value.upper())                
                check_previous_search =  "SELECT COUNT(*) FROM Anexo_Eletronico_Obscat C WHERE C.obscat = ?"
                sqliteconn = connectDB(str(pathdb), 5)
                cursor = sqliteconn.cursor()
                sqliteconn.execute("PRAGMA foreign_keys = ON")
                try:
                    #cursor.execute("PRAGMA journal_mode=WAL")
                    cursor.execute(check_previous_search, (newcat.upper(),))
                    termos = cursor.fetchone()
                    if(termos[0]==0):
                        if(operacao=='add'):
                            insertinto =  "INSERT INTO Anexo_Eletronico_Obscat (obscat, fixo, ordem) values (?,?,0)"
                            fixo = 0
                            if(expertmode):
                                fixo = 1
                            cursor.execute(insertinto, (newcat.upper(), fixo,))
                            idnovo = cursor.lastrowid
                            self.treeviewObs.insert(parent='', index='end', iid=idnovo, text=newcat.upper(), values=(str(fixo), idnovo,), image=self.catimage, tag='obscat')
                            self.treeviewObs.tag_configure('obscat', background='#a1a1a1', font=('Arial', 12, 'bold', 'underline'))
                            sqliteconn.commit()
                        elif(operacao=='edit'):
                            updateinto2 = "UPDATE Anexo_Eletronico_Obscat set obscat = ? WHERE obscat = ?"
                            cursor.execute(updateinto2, (newcat.upper(),valor.upper(),))
                            self.treeviewObs.item(self.treeviewObs.selection()[0], text=newcat.upper())
                            sqliteconn.commit()
                        
                except Exception as ex:
                    printlogexception(ex=ex)
                finally:
                    cursor.close()
                    if(sqliteconn):
                        sqliteconn.close()
                        
                        
    def rtf_encode_char(unichar):
        code = ord(unichar)
        
        return '\\u' + str(code if code <= 32767 else code-65536) + '?'
    
    def ObstoRTf(self, pagi, docespecial, pathdocespecial, tiposelecao, pinit, pfim, p0xinit, p0yinit, p1xinit, p1yinit):
         textonatabela = ""
         if(tiposelecao=='area'):
             
             margemsup = (infoLaudo[pathdocespecial].mt/25.4)*72
             margeminf = infoLaudo[pathdocespecial].pixorgh-((infoLaudo[pathdocespecial].mb/25.4)*72)
             margemesq = (infoLaudo[pathdocespecial].me/25.4)*72
             margemdir = infoLaudo[pathdocespecial].pixorgw-((infoLaudo[pathdocespecial].md/25.4)*72)                                  
             images = []
             for pagina in range(pinit, pfim+1):
                 #p0x = max(int(float(valoresPecial[3])), margemesq)
                 p0x = max(p0xinit, margemesq)
                 if(pagina>pinit):  
                     p0y = int(float(margemsup))
                 else:
                     #p0y = max(int(float(valoresPecial[4]))-10, margemsup)   
                     p0y = max(p0yinit, margemsup)                                          
                 #p1x = min(int(float(valoresPecial[6])), margemdir)
                 p1x = min(p1xinit, margemdir)
                 if(pagina < pfim):
                     p1y = int(float(margeminf))
                 else:
                     #p1y = min(int(float(valoresPecial[7]))+10, margeminf)
                     p1y = min(p1yinit, margeminf)
                 loadedPage = docespecial[pagina]
                 box = fitz.Rect(p0x, p0y, p1x, p1y)
                 matriz = fitz.Matrix(self.zoom_x*1.05, self.zoom_x*1.05)
                 pix = loadedPage.getPixmap(alpha=False, matrix=matriz, clip=box)
                 mode = "RGBA" if pix.alpha else "RGB"
                 imgdata = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
                 pix = None
                 images.append(imgdata)
             if(len(images) > 0):
                 imagem = self.concatVertical(images)
                
                 if platform.system() == 'Windows' or  platform.system() == 'Linux':    # Windows
                     output = io.BytesIO()
                     imagem.save('teste.png','PNG')
                     with open('teste.png', 'rb') as f:
                         content = f.read()
                     os.remove('teste.png')
                     pngtohex = binascii.hexlify(content).decode('utf8')
                     
                     width, height = imagem.size
                     pict = "\\par{{\\pict\\picscalex100\\picscaley100\\piccropl0\\piccropr0\\piccropt0\\piccropb0\\picw{}\\pich{}\\pngblip\n{}}}".format(width, height, pngtohex)
                     docname = os.path.basename(pathdocespecial)
                     docpagina = "{{\\fs22\\f2{{ Relat}}\\\'F3rio \\\'22{}\\\'22 -- Fls. {}}}".format(docname, pagi)
                     textonatabela += ("\\par\\trowd\\clbrdrb\\brdrs\\clbrdrt\\brdrs\\clbrdrl\\brdrs\\clbrdrr\\brdrs\\trautofit1\\intbl\\clftsWidth3\\clwWidth9070\\cellx9070 {}\\cell\\row"+\
                         "\\trowd\\clbrdrb\\brdrs\\clbrdrt\\brdrs\\clbrdrr\\brdrs\\clbrdrl\\brdrs\\trautofit1\\intbl\\clftsWidth3\\clwWidth9070\\cellx9070{{\\loch\\i\\b\\fs22\\f2 Figura }}{{\\qc\\field{{\\fldinst  SEQ Figura \\\\* ARABIC }}}}"+\
                     "{{\\qc\\i:{}}}\\cell\\row\\pard\\line").format(pict, docpagina) + "\n"
                     return textonatabela
         elif(tiposelecao=='texto'):
             #reg1 = "\[[0-9]{2}\/[0-9]{2}\/[0-9]{4}\s[0-9]{2}:[0-9]{2}:[0-9]{2}\]\s<[0-9]{12}\@s\.whatsapp\.net>:"
             #reg11 = "\[[0-9]{2}\/[0-9]{2}\/[0-9]{4}\s[0-9]{2}:[0-9]{2}:[0-9]{2}\]\s<[0-9]*\@s\.whatsapp\.net>:"
             reg12 = "\[[0-9]{2}\/[0-9]{2}\/[0-9]{4}\s[0-9]{2}:[0-9]{2}:[0-9]{2}\]\s<.*>:\s"
             reg2 = "\[[0-9]{2}\/[0-9]{2}\/[0-9]{4}\s[0-9]{2}:[0-9]{2}:[0-9]{2}\]\s<este\saparelho>:"
             #pinit = int(valoresPecial[2])
             #pfim = int(valoresPecial[5])
             estaselecao = ""
             pagatual = None
             for pagina in range(pinit, pfim+1):
                 if(pagina!=pagatual):
                     pagatual = docespecial[pagina]
                     xmlatual = pagatual.get_text("xml")
                     rootxml = ET.fromstring(xmlatual)
                 realce = False
                 
                 margemsup = (infoLaudo[pathdocespecial].mt/25.4)*72
                 margeminf = infoLaudo[pathdocespecial].pixorgh-((infoLaudo[pathdocespecial].mb/25.4)*72)
                 margemesq = (infoLaudo[pathdocespecial].me/25.4)*72
                 margemdir = infoLaudo[pathdocespecial].pixorgw-((infoLaudo[pathdocespecial].md/25.4)*72)
                 #p0x = max(int(float(valoresPecial[3])), margemesq)
                 p0x = max(p0xinit, margemesq)
                 if(pagina>pinit):  
                     p0y = int(float(margemsup))
                 else:
                     #p0y = max(int(float(valoresPecial[4]))+5, margemsup)   
                     p0y = max(p0yinit+2, margemsup)                                             
                 #p1x = min(int(float(valoresPecial[6])), margemdir)
                 p1x = min(p1xinit, margemdir)
                 if(pagina < pfim):
                     p1y = int(float(margeminf))
                     
                 else:
                     #p1y = min(int(float(valoresPecial[7]))-5, margeminf)
                     p1y = min(p1yinit-2, margeminf)
                 for block in rootxml.iter('block'):
                     pontosBlock = block.attrib['bbox'].split(" ")
                     if(float(pontosBlock[1]) > p1y):
                         break
                     for line in block.iter('line'):
                         pontosLine = line.attrib['bbox'].split(" ")
                         x0l = float(pontosLine[0] )
                         y0l = float(pontosLine[1])
                         x1l = float(pontosLine[2])
                         y1l = float(pontosLine[3])
                         linha = ""
                         linhaorg = ""
                         if(float(pontosLine[1]) > p1y):
                              break
                         elif(float(pontosLine[3]) < p0y):
                             continue
                         else:
                             
                             if(p0y > y0l and p1y < y1l): 
                                 primeiroemoji = True
                                 x0 = min(p0x, p1x)
                                 x1 = max(p0x, p1x)
                                 for char in line.iter('char'):
                                     
                                     quad = char.attrib['quad'].split(" ")
                                     c = char.attrib['c']
                                     
                                     if(ord(c)>=55296 and primeiroemoji):
                                         primeiroemoji = False
                                         c = ' ' + c
                                     '''
                                     if(ord(c)>=55296):
                                          emhex = int(hex(ord(c)),16)
                                          subs = emhex - 0x10000
                                          high = subs / 0x400 + 0xD800
                                          low = subs % 0x400 + 0xDC00
                                          c1 = '\\u{} \\\'2E\\u{} \\\'2E'.format(str(math.floor(high)), str(math.floor(low)))
                                     else:
                                             #int(hex(ord(c)),16)
                                          c1 = '\\\'{}'.format(hex(ord(c)).split('x')[-1])
                                          '''
                                     if(float(quad[2]) <= x1 and (float(quad[0])+float(quad[2]))/2 >= x0):                  
                                         #linha += c1
                                         linhaorg += c
                             elif(p0y <= y0l and p1y >= y1l):    
                                 primeiroemoji = True
                                 for char in line.iter('char'):
                                     
                                     quad = char.attrib['quad'].split(" ")
                                     c = char.attrib['c']
                                     
                                     if(ord(c)>=55296 and primeiroemoji):
                                         primeiroemoji = False
                                         c = ' ' + c
                                     '''
                                     if(ord(c)>=55296):
                                          emhex = int(hex(ord(c)),16)
                                          subs = emhex - 0x10000
                                          high = subs / 0x400 + 0xD800
                                          low = subs % 0x400 + 0xDC00
                                          c1 = '\\u{} \\\'2E\\u{} \\\'2E'.format(str(math.floor(high)), str(math.floor(low)))
                                     else:
                                         #int(hex(ord(c)),16)
                                          c1 = '\\\'{}'.format(hex(ord(c)).split('x')[-1])
                                          '''
                                     #linha += c1
                                     linhaorg += c
                             elif(p0y <= y1l and p1y > y1l):  
                                 primeiroemoji = True
                                 for char in line.iter('char'):
                                    
                                     quad = char.attrib['quad'].split(" ")
                                     if((float(quad[0])+float(quad[2]))/2 >= p0x):  
                                         c = char.attrib['c'] 
                                         if(ord(c)>=55296 and primeiroemoji):
                                             primeiroemoji = False
                                             c = ' ' + c
                                         '''
                                         if(ord(c)>=55296):
                                              emhex = int(hex(ord(c)),16)
                                              subs = emhex - 0x10000
                                              high = subs / 0x400 + 0xD800
                                              low = subs % 0x400 + 0xDC00
                                              c1 = '\\u{} \\\'2E\\u{} \\\'2E'.format(str(math.floor(high)), str(math.floor(low)))
                                         else:
                                              #int(hex(ord(c)),16)
                                              c1 = '\\\'{}'.format(hex(ord(c)).split('x')[-1])
                                              '''
                                         #linha += c1
                                         linhaorg += c
                             elif(p1y >= y0l and p0y < y0l):
                                 primeiroemoji = True
                                 for char in line.iter('char'):
                                     
                                     quad = char.attrib['quad'].split(" ")  
                                     if((float(quad[0])+float(quad[2]))/2 <= p1x):  
                                         c = char.attrib['c'] 
                                         
                                         if(ord(c)>=55296 and primeiroemoji):
                                             primeiroemoji = False
                                             c = ' ' + c
                                         '''
                                             emhex = int(hex(ord(c)),16)
                                             subs = emhex - 0x10000
                                             high = subs / 0x400 + 0xD800
                                             low = subs % 0x400 + 0xDC00
                                             c1 = '\\u{} \\\'2E\\u{} \\\'2E'.format(str(math.floor(high)), str(math.floor(low)))
                                         else:
                                             #int(hex(ord(c)),16)
                                             c1 = '\\\'{}'.format(hex(ord(c)).split('x')[-1])
                                             '''
                                         #linha += c  
                                         linhaorg += c
                        
                         matchorigem = re.search(reg2, linhaorg)
                         #matchdestino= re.search(reg1, linhaorg)
                         matchdestino2= re.search(reg12, linhaorg)
                         if(matchorigem!=None):
                             realce = True
                             linha1 = '{\\rtlch \\ltrch\\loch\\fs20\\li72\\f2\\highlight1'+ linhaorg[:matchorigem.start()].encode('rtfunicode').decode('ascii')+ '}'
                             linha2 = '{\\rtlch \\ltrch\\loch\\fs20\\li72\\f2\\highlight1'+linhaorg[matchorigem.start():matchorigem.end()].encode('rtfunicode').decode('ascii')+ '}'
                             linha3 = '{\\rtlch \\ltrch\\loch\\fs20\\li72\\f2\\highlight1'+linhaorg[matchorigem.end():].encode('rtfunicode').decode('ascii') + '\\line}'
                             #estaselecao += "{\\fs20\\highlight1\\li30\\f2\\hich" + linha.encode('rtfunicode').decode('ascii') + "\\line}" 
                             estaselecao += linha1+linha2+linha3 
                         else:
                             #if(matchdestino!=None):
                             #    realce = False
                             #    #estaselecao += '{\\fs20\\li30\\f2\\hich'+linha.encode('rtfunicode').decode('ascii') + "\\line}" 
                             #    linha1 = '{\\rtlch \\ltrch\\loch\\fs20\\li30\\f2'+ linhaorg[:matchdestino.start()].encode('rtfunicode').decode('ascii')+ '}'
                             #    linha2 = '{\\rtlch \\ltrch\\loch\\fs20\\li30\\f2'+linhaorg[matchdestino.start():matchdestino.end()].encode('rtfunicode').decode('ascii')+ '}'
                             ##    linha3 = '{\\rtlch \\ltrch\\loch\\fs20\\li30\\f2'+linhaorg[matchdestino.end():].encode('rtfunicode').decode('ascii') + '\\line}'
                                 #estaselecao += "{\\fs20\\highlight1\\li30\\f2\\hich" + linha.encode('rtfunicode').decode('ascii') + "\\line}" 
                             #    estaselecao += linha1+linha2+linha3  
                             if(matchdestino2!=None):
                                 realce = False
                                 #estaselecao += '{\\fs20\\li30\\f2\\hich'+linha.encode('rtfunicode').decode('ascii') + "\\line}" 
                                 linha1 = '{\\rtlch \\ltrch\\loch\\fs20\\li72\\f2'+ linhaorg[:matchdestino2.start()].encode('rtfunicode').decode('ascii')+ '}'
                                 linha2 = '{\\rtlch \\ltrch\\loch\\fs20\\li72\\f2'+linhaorg[matchdestino2.start():matchdestino2.end()].encode('rtfunicode').decode('ascii')+ '}'
                                 linha3 = '{\\rtlch \\ltrch\\loch\\fs20\\li72\\f2'+linhaorg[matchdestino2.end():].encode('rtfunicode').decode('ascii') + '\\line}'
                                 #estaselecao += "{\\fs20\\highlight1\\li30\\f2\\hich" + linha.encode('rtfunicode').decode('ascii') + "\\line}" 
                                 estaselecao += linha1+linha2+linha3
                             elif(realce):
                                 #estaselecao += "{\\fs20\\highlight1\\f2\\hich" + linha.encode('rtfunicode').decode('ascii') + "\\line}" 
                                 #linha1 = '{\\fs20\\li30\\f2\\highlight1'+ linhaorg[:matchorigem.start()].encode('rtfunicode').decode('ascii')+ '}'
                                 #linha2 = '{\\fs20\\li30\\f2\\highlight1'+linhaorg[matchorigem.start():matchorigem.end()].encode('rtfunicode').decode('ascii')+ '}'
                                 linha3 = '{\\rtlch \\ltrch\\loch\\fs20\\li72\\f2\\highlight1'+linhaorg.encode('rtfunicode').decode('ascii') + '\\line}'
                                 #estaselecao += "{\\fs20\\highlight1\\li30\\f2\\hich" + linha.encode('rtfunicode').decode('ascii') + "\\line}" 
                                 estaselecao += linha3 
                             else:
                                 realce = False 
                                 #estaselecao += '{\\fs20\\f2\\hich'+linha.encode('rtfunicode').decode('ascii') + "\\line}" 
                                 #linha1 = '{\\fs20\\li30\\f2'+ linhaorg[:matchorigem.start()].encode('rtfunicode').decode('ascii')+ '}'
                                 #linha2 = '{\\fs20\\li30\\f2'+linhaorg[matchorigem.start():matchorigem.end()].encode('rtfunicode').decode('ascii')+ '}'
                                 linha3 = '{\\rtlch \\ltrch\\loch\\fs20\\li72\\f2'+linhaorg.encode('rtfunicode').decode('ascii') + '\\line}'
                                 #estaselecao += "{\\fs20\\highlight1\\li30\\f2\\hich" + linha.encode('rtfunicode').decode('ascii') + "\\line}" 
                                 estaselecao += linha3 
                        
             docname = os.path.basename(pathdocespecial)
             docpagina = "{{\\fs22\\f2{{ Relat}}\\\'F3rio \\\'22{}\\\'22 -- Fls. {}}}".format(docname, pagina+1)
             textonatabela += ("\\par\\trowd\\clbrdrb\\brdrs\\clbrdrt\\brdrs\\clbrdrl\\brdrs\\clbrdrr\\brdrs\\trautofit1\\intbl\\clftsWidth3\\clwWidth9070\\cellx9070{{\\cbpat2\\qc\\loch\\i\\b\\fs22\\f2 TABELA }}{{\\qc\\field{{\\fldinst  SEQ Tabela \\\\* ARABIC }}}}"+\
             "{{\\qc:\\i{}}}\\cell\\row"+\
                # "\\trowd\\clftsWidth1\\clbrdrb\\brdrs\\clbrdrt\\brdrs\\clbrdrl\\brdrs\\clbrdrr\\brdrs\\cellx1\\intbl{{\\cbpat2\\qc\\loch\\b{{TABELA}}}}\\cell\\row"+\
                 "\\par\\trowd\\clbrdrb\\brdrs\\clbrdrt\\brdrs\\clbrdrl\\brdrs\\clbrdrr\\brdrs\\trautofit1\\intbl\\clftsWidth3\\clwWidth9070\\cellx9070 {}\\cell\\row\\pard\\line").format(docpagina, estaselecao) + "\n"
             #cont += 1
             return textonatabela
            
    def treeview_selection_obs(self, event=None, item=None):
        global minMaxLabels, processed_pages, infoLaudo, pathpdfatual, pathdb, docatual
        try:
           
            valores = None
            if(item==None):
                selecao = self.treeviewObs.focus()
                valores = (self.treeviewObs.item(selecao, 'values'))
            else:
                valores = (self.treeviewObs.item(item, 'values'))            
            if(len(valores)>2): 
                for pdf in infoLaudo:
                    infoLaudo[pdf].retangulosDesenhados = {}                
                self.docInnerCanvas.delete("quad")
                self.docInnerCanvas.delete("simplesearch")
                self.docInnerCanvas.delete("obsitem")
                self.docInnerCanvas.delete("link")
                self.clearSomeImages(["quad", "simplesearch", "obsitem", "link"])
                sobraEspaco = 0
                if(self.docFrame.winfo_width() > infoLaudo[pathpdfatual].pixorgw * self.zoom_x * zoom):
                    sobraEspaco = self.docInnerCanvas.winfo_x()
                posicaoRealY1 = round(float(valores[7]))
                posicaoRealX1 = round(float(valores[6]))
                posicaoRealY0 = round(float(valores[4]))
                posicaoRealX0 = round(float(valores[3]))                
                pp = round(float(valores[2]))
                up = round(float(valores[5]))
                pathpdf = os.path.normpath(valores[1])
                try:
                    self.positions[self.indiceposition] = (pathpdfatual, self.vscrollbar.get()[0])
                    self.indiceposition += 1
                    if(self.indiceposition>=10):
                        self.indiceposition = 0
                except Exception as ex:
                    None
                
                if(pathpdf!=pathpdfatual):
                    self.docwidth = self.docOuterFrame.winfo_width()
                    
                    self.clearAllImages()
                    for i in range(minMaxLabels):
                        processed_pages[i] = -1
                    if plt == "Linux":                           
                        pathpdf = pathpdf.replace("\\","/")
                    elif plt=="Windows":             
                        pathpdf = pathpdf.replace("/","\\")
                    pathpdfatual =pathpdf 
                    try:
                        docatual.close()
                    except Exception as ex:
                        None
                    docatual = fitz.open(pathpdfatual)
                    self.labeldocname.config(text=os.path.basename(pathpdfatual))
                    self.totalPgg.config(text="/ "+str(infoLaudo[pathpdfatual].len))                    
                    if(infoLaudo[pathpdfatual].pixorgw*self.zoom_x*zoom>self.maiorw):
                        self.maiorw = infoLaudo[pathpdfatual].pixorgw*self.zoom_x *zoom           
                    self.scrolly = round((infoLaudo[pathpdfatual].pixorgh*self.zoom_x*zoom), 16)*infoLaudo[pathpdfatual].len - 35
                    self.docInnerCanvas.config(scrollregion=(sobraEspaco, 0, sobraEspaco+ (infoLaudo[pathpdfatual].pixorgw*zoom*self.zoom_x), self.scrolly))                
                atual = ((self.vscrollbar.get()[0]*infoLaudo[pathpdfatual].len))
                ondeir = (pp / (infoLaudo[pathpdfatual].len)+(posicaoRealY0*self.zoom_x*zoom- infoLaudo[pathpdfatual].pixorgw/2*self.zoom_x*zoom)/self.scrolly)
                
                
                    
                    
                deslocy = (math.floor(pp) * infoLaudo[pathpdfatual].pixorgh * self.zoom_x*zoom) + (posicaoRealY0 *  self.zoom_x * zoom)                    
                desloctotalmenor =  (atual * infoLaudo[pathpdfatual].pixorgh * self.zoom_x*zoom) 
                desloctotalmaior =   desloctotalmenor + self.docFrame.winfo_height()
                if(deslocy < desloctotalmenor or deslocy > desloctotalmaior):
                    ondeir = ((pp) / (infoLaudo[pathpdfatual].len)) + (posicaoRealY0*self.zoom_x*zoom-self.docFrame.winfo_height()/2)/self.scrolly
                    self.docInnerCanvas.yview_moveto(ondeir)
                    if(str(pp+1)!=self.pagVar.get()):
                        self.pagVar.set(str(pp+1))
                    
                    
                enhancearea = False
                enhancetext = False
                if(valores[0]=='area'):
                    enhancearea = True
                elif(valores[0]=='texto'):
                    enhancetext = True
                for p in range(pp, up+1): 
                    if(p==pp and p==up):
                        self.prepararParaQuads(p, posicaoRealX0, posicaoRealY0, posicaoRealX1, posicaoRealY1, self.color, tag=['obsitem'], apagar=True, \
                                               enhancetext=enhancetext, enhancearea=enhancearea, alt=False)
                    elif(pp < p):
                        if(p < up):
                            self.prepararParaQuads(p, 0, 0, infoLaudo[pathpdfatual].pixorgw, infoLaudo[pathpdfatual].pixorgh, self.color, tag=['obsitem'], \
                                                   apagar=True,  enhancetext=enhancetext, enhancearea=enhancearea, alt=False)                            
                        else:
                            self.prepararParaQuads(p, 0, 0, posicaoRealX1, posicaoRealY1, self.color, tag=['obsitem'], apagar=True,  enhancetext=enhancetext, enhancearea=enhancearea, alt=False)                            
                    else:
                        self.prepararParaQuads(p, posicaoRealX0, posicaoRealY0, infoLaudo[pathpdfatual].pixorgw,  infoLaudo[pathpdfatual].pixorgh, \
                                               self.color, tag=['obsitem'], apagar=True,  enhancetext=enhancetext, enhancearea=enhancearea, alt=False)                       
        except Exception as ex:
            printlogexception(ex=ex)

    def moveCategory(self, operacao, item):
        if(operacao=='top'):
            self.treeviewObs.move(item, '', 0)
        elif(operacao=='bottom'):
            self.treeviewObs.move(item, '', 'end')
        elif(operacao=='up'):
            self.treeviewObs.move(item, '', self.treeviewObs.index(item)-1)
        elif(operacao=='down'):
            self.treeviewObs.move(item, '', self.treeviewObs.index(item)+1)

    def showhideresults(self):
        try:
            if(self.hideresultsvar.get()):
                termos = self.treeviewSearches.get_children('')
                for termo in termos:
                    results = self.treeviewSearches.get_children(termo)
                    if(len(results)==0):
                        indice = self.treeviewSearches.index(termo)
                        self.detachedSearchResults.append((termo, indice))
                        self.treeviewSearches.detach(termo)
            else:
                for tupla in self.detachedSearchResults:
                    self.treeviewSearches.move(tupla[0], '', tupla[1])
                self.detachedSearchResults = []
        except Exception as ex:
            printlogexception(ex=ex)
            
    def importNativeSearchList(self, categoria):
        global listaRELS
        if getattr(sys, 'frozen', False):
            application_path = sys._MEIPASS
        elif __file__:
            application_path = os.path.dirname(os.path.abspath(__file__))
        searchlist = os.path.join(application_path, "ListasDeBusca", categoria)
        if plt == "Linux":                           
            searchlist = str(searchlist).replace("\\","/")
        elif plt=="Windows": 
            searchlist = str(searchlist).replace("/","\\")
        with open(searchlist, "r", encoding='utf8', errors='ignore') as a_file:
            
            try:
                for line in a_file:                  
                    stripped_line = line.strip()
                    tipo = stripped_line.split(" ")[0]
                    if("LIKE" in tipo.upper()):
                        termo = stripped_line[len(tipo):len(stripped_line)].strip().upper()
                        if(len(termo)>=3):
                            if(not (termo, 0) in self.searchedTerms):
                                self.searchedTerms.append((termo, 0))
                                searchqueue.append((termo, False, None))
                    elif("MATCH" in tipo.upper()):
                        termo = stripped_line[len(tipo):len(stripped_line)].strip().upper()
                        if(not (termo, 1) in self.searchedTerms):
                            self.searchedTerms.append((termo, 1))
                            searchqueue.append((termo, True, None))
                    else:
                        termo = stripped_line.strip().upper()
                        if(len(termo)>=3):
                            if(not (termo, 0) in self.searchedTerms):
                                self.searchedTerms.append((termo, 0))
                                searchqueue.append((termo, False, None))
                self.uniquesearchprocess2 = mp.Process(target=searchProcess, args=(result_queue, pathdb, erros,queuesair,
                                                                                   searchqueue, update_queue, infoLaudo, listaRELS, listaTERMOS, False,), daemon=True)
                #self.uniquesearchprocess3 = mp.Process(target=searchProcess, args=(result_queue, pathdb, erros,queuesair, searchqueue, update_queue, infoLaudo, False,), daemon=True)
                #self.uniquesearchprocess4 = mp.Process(target=searchProcess, args=(result_queue, pathdb, erros,queuesair, searchqueue, update_queue, infoLaudo, False,), daemon=True)
                #self.uniquesearchprocess5 = mp.Process(target=searchProcess, args=(result_queue, pathdb, erros,queuesair, searchqueue, update_queue, infoLaudo, False,), daemon=True)
                #self.uniquesearchprocess6 = mp.Process(target=searchProcess, args=(result_queue, pathdb, erros,queuesair, searchqueue, update_queue, infoLaudo, False,), daemon=True)
                
                self.uniquesearchprocess2.start() 
                #self.uniquesearchprocess3.start() 
                #self.uniquesearchprocess4.start() 
                #self.uniquesearchprocess5.start() 
                #self.uniquesearchprocess6.start() 
                self.primeiroresetbuscar = True
            except Exception as ex:
                printlogexception(ex=ex)  
            
    def importListPopUp(self):   
        try:
            self.opcaoimportlist = tkinter.Menu(root, tearoff=0)
            self.opcaoimportlist.add_command(label='Pornografia Infantil', image=self.childpornb, compound='left', command=partial(self.importNativeSearchList, "lista_vulneraveis.txt"))
            self.opcaoimportlist.add_command(label='Armas/Drogas', image=self.gunb, compound='left', command=partial(self.importNativeSearchList, "lista_reupreso.txt"))
            #self.opcaoimportlist.add_command(label='Drogas', image=self.drugb, compound='left', command=None)
            self.opcaoimportlist.add_command(label='Violência', image=self.violenceb, compound='left', command=partial(self.importNativeSearchList, "lista_homicidios.txt"))
            #self.opcaoimportlist.add_command(label='Corrupção / Crime Organizado', image=self.corruptionb, compound='left', command=None)
            self.opcaoimportlist.add_separator()
            self.opcaoimportlist.add_command(label='Arquivo de texto', image=self.textb, compound='left', command=self.openSearchlist)
            self.opcaoimportlist.tk_popup(self.bfromFile.winfo_rootx()+50,self.bfromFile.winfo_rooty())         
        except Exception as ex:
            printlogexception(ex=ex)
            logging.exception('!')
        finally:
            self.opcaoimportlist.grab_release()
            
    def filterdocWindow(self, event=None):
        global infoLaudo
        if(self.windowfilter==None):
            docs = []
            tupla = []
            linha = 0
            for eq in self.treeviewEqs.get_children(""):
                for doc in self.treeviewEqs.get_children(eq):
                    nomedoc = self.treeviewEqs.item(doc, "text")
                    docs.append(nomedoc)
                    tupla.append(linha)
                    linha += 1
            tupla.append(linha+1)
            tupla.append(linha+2)
            self.windowfilter = tkinter.Toplevel()  
            self.windowfilter.rowconfigure(0, weight=1)
            self.windowfilter.columnconfigure((0,1), weight=1)
            self.filterframedcanvas = tkinter.Canvas(self.windowfilter)
            self.filterframedcanvas.grid(row=0, column=0, columnspan=2, sticky='nsew', pady=(0,10))
            self.filterframedoc = tkinter.Frame(self.windowfilter)
            self.filterframedoc.grid(row=0, column=0, sticky='nsew')
            self.filterframedoc.rowconfigure(tuple(tupla), weight=1)
            self.filterframedoc.columnconfigure(0, weight=1)
            
            self.filterframedcanvasreturn = self.filterframedcanvas.create_window((0,0), window=self.filterframedoc, anchor = "nw")
            
            
            self.vsbfilter = tkinter.Scrollbar(self.windowfilter, orient="vertical")            
            self.vsbfilter.config(command=self.filterframedcanvas.yview)
            self.vsbfilter.grid(row=0, column=2, sticky='ns')
            self.filterframedcanvas.config(yscrollcommand = self.vsbfilter.set)
            linha = 0
            alldocs = tkinter.Checkbutton(self.filterframedoc, text="SELECIONAR TODOS")
            nonedocs = tkinter.Checkbutton(self.filterframedoc, text="DESMARCAR TODOS")
            self.cbsfilters = []
            self.cbsfilters.append(alldocs, None)
            self.cbsfilters.append(nonedocs, None)
            for nomedoc in docs:
                cb = tkinter.Checkbutton(self.filterframedoc, text="{}".format(nomedoc.strip()))
                self.cbsfilters.append(cb, nomedoc)
                cb.grid(row=linha+2, column=0, sticky='w', pady=(0,10))
                linha += 1
          
            self.windowfilter.title("Filtrar observações por documento")
            
            botaoaplicar = tkinter.button(self.windowfilter, text='Aplicar', image=self.checki, compound='right', command= self.applyFilterDoc)
            botaocancelar = tkinter.button(self.windowfilter, text='Cancelar', image=self.checki, compound='right', command= lambda: self.windowfilter.withdraw())
            
        self.windowfilter.deiconify()  
    #def changeValueOfExportCsv(self, var):
    #    global exportrestocsv
        
        
        
    
    def saveSearchResults(self):
        global exportrestocsv
        window = tkinter.Toplevel()
        try:
           
            window.geometry("800x600")
            var = tkinter.BooleanVar()
            window.protocol("WM_DELETE_WINDOW", lambda: var.set(False))
        
            window.title("Exportar resultados (CSV)")
            window.rowconfigure(1, weight=1)
            window.columnconfigure((0,1), weight=1)
            
            labeltermos = tkinter.Label(window, text="Termos a serem exportados:")
            labeltermos.grid(row=0, column=0, sticky='ns', pady=5)
            labeldocs = tkinter.Label(window, text="Nos documentos:")
            labeldocs.grid(row=0, column=1, sticky='ns', pady=5)
            
            frametermos = tkinter.Frame(window)
            frametermos.rowconfigure(0, weight=1)
            frametermos.columnconfigure(0, weight=1)
            frametermos.grid(row=1, column=0, sticky='nsew', pady=5)
            termosvar = tkinter.StringVar()
            lbtermos = tkinter.Listbox(frametermos, listvariable = termosvar, selectmode=tkinter.EXTENDED, exportselection=False)
            lbtermos.grid(row=0, column=0, sticky='nsew', pady=2)
            
            
            framedocs = tkinter.Frame(window)
            framedocs.rowconfigure(0, weight=1)
            framedocs.columnconfigure(0, weight=1)
            framedocs.grid(row=1, column=1, sticky='nsew', pady=5, padx=10)
            docsvar = tkinter.StringVar()
            lbdocs = tkinter.Listbox(framedocs, listvariable = docsvar, selectmode=tkinter.EXTENDED, exportselection=False)
            lbdocs.grid(row=0, column=0, sticky='nsew', pady=5)
            insertdocs = []
            
            scroltermos = ttk.Scrollbar(frametermos, orient="vertical")
            scroltermos.grid(row=0, column=1, sticky='ns')
            scroltermos.config( command = lbtermos.yview )
            lbtermos.configure(yscrollcommand=scroltermos.set)
            #--
            scroltermos2 = ttk.Scrollbar(frametermos, orient="horizontal")
            scroltermos2.grid(row=1, column=0, sticky='ew')
            scroltermos2.config( command = lbtermos.xview )
            lbtermos.configure(xscrollcommand=scroltermos2.set)
            
            
            scroldocs = ttk.Scrollbar(framedocs, orient="vertical")
            scroldocs.grid(row=0, column=1, sticky='ns')
            scroldocs.config( command = lbdocs.yview )
            lbdocs.configure(yscrollcommand=scroldocs.set)
            #--
            scroldocs2 = ttk.Scrollbar(framedocs, orient="horizontal")
            scroldocs2.grid(row=1, column=0, sticky='ew')
            scroldocs2.config( command = lbdocs.xview )
            lbdocs.configure(xscrollcommand=scroldocs2.set)
            
            #self.scrolltoc.config( command = self.treeviewEqs.yview )
            #self.treeviewEqs.configure(yscrollcommand=self.scrolltoc.set)
            termosdict = []
            docsdict = []
            index = 0
            for child in self.treeviewEqs.get_children(''):
                for child2 in self.treeviewEqs.get_children(child):
                    pdf = os.path.basename(self.treeviewEqs.item(child2, 'values')[1])
                    #insertdocs.append(texto)
                    lbdocs.insert(tkinter.END, pdf)
                    docsdict.append(pdf)
                
            inserttermos = []
            for child in self.treeviewSearches.get_children(''):
                texto = self.treeviewSearches.item(child, 'text')
                #inserttermos.append(texto)
                lbtermos.insert(tkinter.END, texto)
                termosdict.append(child)
            
            
            
            answeryes = tkinter.Button(window, text="Exportar", command = lambda: var.set(True))
            #answerno = tkinter.Button(window, text="NÃO", command=  partial(self.defineMargins,window, False))
            answeryes.grid(row=2, column=0, columnspan=4, sticky='ns', pady=15)
            root.wait_variable(var)
            if(var.get()):
                tipos = [('XLSX', '*.xls')]
                path = (asksaveasfilename(filetypes=tipos, defaultextension=tipos))
                if(path!=None and path!=''):
                    workbook = xlsxwriter.Workbook(path)
                    try:
                    #with open(path, mode='w', newline='', encoding='utf-8') as csv_file:
                        worksheet = workbook.add_worksheet()
                        bold = workbook.add_format({'bold': True})
                        cell_formatdarkgray = workbook.add_format()                       
                        cell_formatdarkgray.set_bg_color("#bfbfbf")
                        cell_formatdarkgray.set_bold()
                        cell_formatlightgray = workbook.add_format()                       
                        cell_formatlightgray.set_bg_color("#e6e6e6")
                        
                        #writer = csv.writer(csv_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        #writer.writerow(['Termo', 'Documento', 'Seção', 'Página', 'Página'])
                        worksheet.write(0, 0, "Termo", cell_formatdarkgray )
                        worksheet.write(0, 1, "Tipo de busca", cell_formatdarkgray )
                        worksheet.write(0, 2, "Documento", cell_formatdarkgray )
                        worksheet.write(0, 3, "Seção", cell_formatdarkgray )
                        worksheet.write(0, 4, "Página", cell_formatdarkgray )
                        worksheet.write(0, 5, "Trecho", cell_formatdarkgray )
                        termosexport = lbtermos.curselection()
                        docsexport = lbdocs.curselection()
                        linha= 1
                        gray = False
                        if(len(termosexport)>0 and len(docsexport) > 0):
                            docsselecionados = []
                            for docindex in docsexport:
                                docsselecionados.append(docsdict[docindex])
                            for term in termosexport:
                                childsearched = termosdict[term]
                                valores = self.treeviewSearches.item(childsearched, 'values')
                                termo = valores[0]
                                tipo = " LIKE"
                                if(valores[1]=='1' or valores[1]=='True'):
                                    tipo = ' MATCH'
                                filhospdf = self.treeviewSearches.get_children(childsearched)
                                for pdfsearched in filhospdf:
                                    nomepdf = os.path.basename(self.treeviewSearches.item(pdfsearched, 'values')[0])
                                    if(nomepdf in docsselecionados):
                                        childofpdf = self.treeviewSearches.get_children(pdfsearched)
                                        for child in childofpdf:
                                            if(self.treeviewSearches.tag_has('relsearchtoc', child)):
                                                toc = self.treeviewSearches.get_children(child)
                                                toctext = self.treeviewSearches.item(child, 'text')
                                                for res in toc:
                                                    valoresres = self.treeviewSearches.item(res, 'values')
                                                    textores =  self.treeviewSearches.item(res, 'text')
                                                    pagina = textores.split(" - ")[0]
                                                    snippet = valoresres[0] + " <b>" + valoresres[1] + "<\\b> " + valoresres[2]
                                                    if(gray):
                                                        worksheet.write(linha, 0, termo, cell_formatlightgray )
                                                        worksheet.write(linha, 1, tipo, cell_formatlightgray )
                                                        worksheet.write(linha, 2, nomepdf, cell_formatlightgray )
                                                        worksheet.write(linha, 3, toctext, cell_formatlightgray )
                                                        worksheet.write(linha, 4, pagina, cell_formatlightgray )
                                                        worksheet.write_rich_string(linha, 5, valoresres[0], bold, valoresres[1], valoresres[2], cell_formatlightgray )
                                                        linha += 1
                                                        gray = not gray
                                                    else:
                                                        worksheet.write(linha, 0, termo )
                                                        worksheet.write(linha, 1, tipo)
                                                        worksheet.write(linha, 2, nomepdf )
                                                        worksheet.write(linha, 3, toctext )
                                                        worksheet.write(linha, 4, pagina )
                                                        worksheet.write_rich_string(linha, 5, valoresres[0], bold, valoresres[1], valoresres[2] )
                                                        linha += 1
                                                        gray = not gray
                                                    #writer.writerow([termo+tipo, nomepdf, toctext, pagina, snippet])
                                            elif(self.treeviewSearches.tag_has('resultsearch', child)):
                                                res = child
                                                valoresres = self.treeviewSearches.item(res, 'values')
                                                textores =  self.treeviewSearches.item(res, 'text')
                                                pagina = textores.split(" - ")[0]
                                                snippet = valoresres[0] + " <b>" + valoresres[1] + "<\\b> " + valoresres[2]
                                                # writer.writerow([termo+tipo, nomepdf, "-", pagina, snippet])
                                                if(gray):
                                                    worksheet.write(linha, 0, termo, cell_formatlightgray )
                                                    worksheet.write(linha, 1, tipo, cell_formatlightgray )
                                                    worksheet.write(linha, 2, nomepdf, cell_formatlightgray )
                                                    worksheet.write(linha, 3, toctext, cell_formatlightgray )
                                                    worksheet.write(linha, 4, pagina, cell_formatlightgray )
                                                    worksheet.write_rich_string(linha, 5, valoresres[0], bold, valoresres[1], valoresres[2], cell_formatlightgray )
                                                    linha += 1
                                                    gray = not gray
                                                else:
                                                    worksheet.write(linha, 0, termo )
                                                    worksheet.write(linha, 1, tipo)
                                                    worksheet.write(linha, 2, nomepdf )
                                                    worksheet.write(linha, 3, toctext )
                                                    worksheet.write(linha, 4, pagina )
                                                    worksheet.write_rich_string(linha, 5, valoresres[0], bold, valoresres[1], valoresres[2] )
                                                    linha += 1
                                                    gray = not gray
                    except Exception as ex:
                        printlogexception(ex=ex)
                    finally:
                        workbook.close()
        except Exception as ex:
            printlogexception(ex=ex) 
        finally:
            window.destroy()
            #answerno.grid(row=1, column=1, sticky='ns', pady=5)
        
    def leftPanel(self):
        global infoLaudo, pathpdfatual, listaTERMOS, docatual
        pathpdfatual = None
        try:
            self.windowfilter = None
            childpornb = b'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAABA0lEQVQ4jcXTPStGYRgH8F9SjyhksFgsPgATGZ4yKaVkeLJZfABWKYvNk8cX8CWcMlmFwWowkJckL4uXxcDgOnXkeDnnDP71r7vrnPtX16nDP6Qd49H2qlgXDvAW3Y9Z6SxlsLSLVcBmDtisAtZzwHoVEBrYizaqQJ1YxjaSTNfRXwRqwzwufV037RPW0PMbNoijuPSImxzsHFdxvsfIT+A0XtCKtZIcMEENCz6+6+hfVk7zHVg6CTaxGm1VAWfxgGMMoBu7uMBEUWzF5zUnMaXCH7MRl06xgxMcxvk2nm0VAXtxjTv0ZeZDeMZZvFMoM3jFcGY2F+BYUSxNLWfWURYrlXeF5lmw+U5kPwAAAABJRU5ErkJggg=='
            gunb = b'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAyklEQVQ4jeXSIWtCYRQG4AdxY0ZZMWxpYLMPWTHK8sIYGBYHw+IfELQPbEvLwyRWYcUwGKhlYFlcWl7Ywl0QwXBg3uttvvCm75ynnI+9zzFuU+5cohY9NDDADL0UneAZHRTX2BWSHHoOBSxzAi+gmhP2ixM4xOKf4Rd8YoinoI9obh6khPcA+sAN2njFgS1TwFcADlDGA7rbYlAPsARzjNBKg0E/wL5xlBZaZxaA46xYJcAS3GUFzwLsB6dZQbjHFG9Wf+56F2zP8geUt3u8qnMQ3wAAAABJRU5ErkJggg=='
            drugb = b'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAC2ElEQVQ4jZXPSU8TYQDG8RdjvJh48qIxnP0AGBMO7LSsLS1M6bQdaCkMlE2gpQtMaSlQMBwIicaDIrJ6k6WlIhoSjXiGFqKG0tKZKYmJHkg4+3hoA0GMDP8P8MvzEHLF5Ab2jrKW+VZO0UGZ0pBNCMm4qnEOq2Ea9t8EAhgcG0cZpUNtvfm4SEU5rwynMPP+UiCA5zMzsHEedDpcCL3fgHtoFPkKtf1KGJXGXszMwsZ5EUvE8WnrC8xtXVjbeAelvu5Y0kqFtuEuVde4vxQMYmp2Dr3uQcQScQiiAF7k8fHzFizWXhRUVqNUrb8nCVtOY3bPIOKJw1MsISSwHd5Gm82O3BJV96WYtp6NLgeDeDk3D4fHl8KSAgRROMXaex0SMSMbXVlbS2FeH+L8RazD7kBumRTMlMKm5xfgGhw+w5ICeIHHdmQHHXanNIxubI6uroUwPb+APt/IeUzksRPZQafDhcIKqkcy9mphEf1Dfhz+je2GpWNMkyW6Gkpjw34c8gmISfEc1uXqQ6FCAmZotByshkKYWVwENzz6b8zJXY4RQojW2PR9em4Bs4uvwY2ksSMRYlIEL/II74bR7eIgV2usl2KEEKJkjGW0qfnHgH8Mh8IZJogCwrsR9Ljc0jFCCKFYNrPT0XeGHaWxvQh6+gdQqtZLx9JlmDt6TqKxaApLpjAr50GpWm9lGNvNIo1GXknTtwnBNZlCnSOrpu//V6zWmwYeT0xi7+seIrsR2NwelGt0tpIqmlZoDOHxySdQG+qPCiprPnDDfrCPrMiRKZ0URd0o1etvPSwsac0qljNer/f66UqF1sTVsR0nbJcV5RqdrbiKNjg8PqyE3oIXeWxsbiKwvo6EkMBBPIZKrQFKmvmdLS//NfH0Gfp9I3iQJ5u7cJ+i2ExCCJHX0FO0uQXG1k7UW9rBNLdC32SBrrEFWnMzqhkTKKMZeRUqqBkTVAYjsvKLf/4BiWFK8zNC/Q0AAAAASUVORK5CYII='
            violenceb = b'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAABsUlEQVQ4jdXTzysEYRgH8FeclIuDEyFy8h9IuJollKFQ5p2NPXg3SrmIWlFWKQqR/D5xUC4cllVjrXd3WbOz49eBxcrv2oM2ZuhxkEWsncXFt57Tt+fTc3kQ+ndZPz1NpB55joo7AbtHtjgkKeVXmEOUtzZEL7yNfGTbOUyNGruaHs10fsLeULt7N00zdjkxnHHX2hx0utxfYCHUpxm97DVbFILBPzIAWzZbWHTV4QoMTczkRATBao27MXccKASDQjBcd5vCopa1DbV/fDo3Mjo7G3tjNoVQtyCERZdtNHr0bLAPNu00LDq/aLkv0uvTtaHdpn2FYFCMPNx2tQPdlj5gK3Tzrrq+CZhK7CupNaRFhxIMonUlhFGP90Sg21m6Cm6JYTlgKrGvqFzrpeaOPYVguOjrAbcgABW9Jy5JykAIoeJinFBYzosMy4GO5Y6jRoMt5PF8aizvfV9WpU/WsZyfYbFcWmpIigi+ote9nU7/5EDBVz1TY8jWjCGEEBB9smrkLx4auC7NS9/liXBtCsGgGvl7qKuL/zWoNhryVcIHHo3cAiAU8wc3vrzmn0A/yTPaVJraSoOHnQAAAABJRU5ErkJggg=='
            corruptionb = b'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAACHUlEQVQ4ja2TQWhTQRCGXxSstEWDVCh4qOix4iUU+2bfwxCLUiSQg4FeCt4KQvEi3j238MzMxhoU40EQcvEi9SJID9bizr6kkUakahEPllJKLylFUtdDTJpEkzxpB/bwdv/9dv6ZeZYVIBJePpzw8uEg2q4RyXAvEG8C8WYkw70HBt7MvjluE38Vkr9Mz5ueQ8jRsgDVayB+cSiw2NynM4B6D4h/xmd54MBASKu7gGwA2djEtwNdSuZyR9sCkT/UgIJ0oSsjmdvoB9RrtuQl50Hx3KX7+qKdeg+Q5qsC1VQNVoeimoqSikbnli+MZFcGkzlzTKB+B6jXkrmNfis+ywNAXG69WF/E2yA5BZJTQLzdQVeu13j8iX8aMnzeQfWqORu9K2RhuGZLyMKwQL3bBJL+85HsyuC/G2bMERv9e0D6V1WsFv6qqVQL1XpyxU7xnUBNcpGvC9JbQHrVMibU8GAISK8K0luj6I8FgtXtkVoEZOOi8iZn1vsmZ9b7XFReNXNd+i9YwsuHBXFlf1y40vgNyCbq5c8GBrppdaOli98F8ufGPSfNt4LbRX5U/zskP41k+GQkw71Vy3rvz5i8DASrDip/c4h/XE7reOs5PCzaQPwRiMvjz5ZOdISNoj8GyDtAXLz2ePFUO930vOkB9N8C8o4tl6+0BbrSnwBk46CS3Zw4qCQgG1f6Ex2FMVkaapq9dmFMKCZLQ63bvwETunBo1/Wd0gAAAABJRU5ErkJggg=='
            textb = b'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAkUlEQVQ4je3TvQmAMBCG4XcU3cMijYVbZAHBETKXlaPoHoo2CQaE3J0pbPzg6y5PID8Ap6Er0CDkBEagE5rAFWgl0Em7xrkemIGthFrAERgiuNWCe9YjrqsC87hPQAcERdOsCHpgUdRrQUtUYED3W4IWbLjPp9Q0V30peVSgp3wZZtCSH3yCE7onkzpJ4Ns+cgHRQXiS3dSliQAAAABJRU5ErkJggg=='
            self.childpornb = tkinter.PhotoImage(data=childpornb)
            self.gunb = tkinter.PhotoImage(data=gunb)
            self.drugb = tkinter.PhotoImage(data=drugb)
            self.violenceb = tkinter.PhotoImage(data=violenceb)
            self.corruptionb = tkinter.PhotoImage(data=corruptionb)
            self.textb = tkinter.PhotoImage(data=textb)
            self.detachedSearchResults = []
            catimageb = b'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAN0lEQVQ4jWNgQANKSkr/SaFxAiUlpf/kYpwGUkLjNJBUMGrgUDSQ1PQ36sJRF9LChYPbQGqU2ACtyKdZJrmRYgAAAABJRU5ErkJggg=='
            itemimageb = b'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAwUlEQVQ4ja3TQWoCMRQG4A+ly3HtAYSKFKEglC57g/YYHsI7uHPZu6h4goonkG66dtnpIgwdBjHJmAf/6iUfScgjvR4ww9OVTDHIsIzxhfpGtqnoGKcI1mRSEquFJ8nGLljiHcdOb97nZOvWurdO77nPNT9baz86vUUuVuMXG6zw0+m95GKxvJbEzhgRJiD2aWP5FqYFPJbECOOyK4U1VeFQCuuDRrEcNBlLQbOxW2hvrI3u/X/au7CmhsLAV6kb/gAc58y6Y0YKkQAAAABJRU5ErkJggg=='
            self.itemimage = tkinter.PhotoImage(data=itemimageb)
            self.catimage = tkinter.PhotoImage(data=catimageb)
            self.infoFrame = tkinter.Frame(borderwidth=2, bg='white', relief='ridge')            
            editcatbin= b'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAA0ElEQVQ4jaXTS0oDYQwA4M8X2vq4itALiAewtysUQYsIIiIym4KiiNJSjyMuXY2LTsUpY/P/00Agq48kJLSPTQzxhbM1nF/sEmWV3+ivA/YqpFRHszs9wmlV9xvQz1zsQ328ZXSQih1ipnlnC7TAVgp2gKn6aMvoCTqp2KQB+4sep0Cwj/cVWGl+hxspWBdvAXaeinXwGmAXOdhLgI3MPyWMPTwH2FUO9hRg16nYLh4D7Ebi0cI4wG5zMAF2l4utAu+xnYv9Bz60xZrAAjttsR81vIahodwr/wAAAABJRU5ErkJggg=='
            self.editcat = tkinter.PhotoImage(data=editcatbin)
            delcatbin= b'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAoElEQVQ4jdWUMQqDQBBFH/EUadZecpXcRlLbKx4iSZnKg1jZxguoZ9DmC4uJMK5F4sCD2b/LYxaWhaNXAmQLkq2SEniJDhgXdN5+aRE2XyRrNNYpL0bMZZ3wP4T9Sh8kvAEOeAunLFh4B04SOfWPPcIRyL28YOeVWyAGIhErCxZeJXqKSFmwcAAqb10p+/07rA2yeovwDKR8fl0zqc4csCbGlHcxgB7i5gAAAABJRU5ErkJggg=='
            self.delcat = tkinter.PhotoImage(data=delcatbin)
            addcatbin= b'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAABEUlEQVQ4je3UsUoDQRDG8V9voRCwTplKgogiKFzpI9hpbxGb1DnQNuATiIWgtU8QbOytrewkdaqosbg5cqxnzih2fvAVNzf3n9nZveWPdIFR4u5vgCPMEmf/wKXUDcBpBbb2G2CpLIDV5zxx9hNgFr7yeRRn2MA+2t8Fvobfa4Bp7BEHTcBSefLxBAN00MIurqPIybLACbYj3lWcjFL9WNFmEzDDeXQwWJAHD7hpArZxFLGO+uOVRV4PL03A3HzJLfU/wCzyDjH9Cljn3QWFy+JPKXAVexVfVoDXC4AreMYwBabKky77EW/HuxJ2hzHWm4DH5hfuPd4Uu9lTzCyPzsbYaYLVaQu3it2cKmY2rHb2ASupfMvDJMfRAAAAAElFTkSuQmCC'
            self.addcat = tkinter.PhotoImage(data=addcatbin)
            copycatbin = b'iVBORw0KGgoAAAANSUhEUgAAABMAAAAUCAYAAABvVQZ0AAAAmUlEQVQ4je3UoQ6BURgG4Ce4BptNknXVBZhG5SJcgSQIis7mcgThbwTTmaz8glP82+GcTfO/29vO94TvbB+0sEeZ0bZI5uHBCYfENmPYKmD92IOcVLEGhpgmdILeJ2wjb38lRjHsihtmCV2G2W0Mu+Mc38pbumF2V2M19gUbYIHOL7Bq/gS74IEioceArWPY2OtqpJ6fQvi8J5AaiePLQabWAAAAAElFTkSuQmCC'
            self.copycat = tkinter.PhotoImage(data=copycatbin)            
            self.menuexcludesearch = tkinter.Menu(root, tearoff=0)
            self.menuexcludesearch.add_command(label="Excluir Busca", image=self.delcat, compound='right', command=self.exclude_search)            
            movecat = b'iVBORw0KGgoAAAANSUhEUgAAABIAAAAUCAYAAACAl21KAAAAw0lEQVQ4je3UPW7CMBiA4ad3YaoqZWGoegF+yiHauWKPBJdALRLiImw9EVI7MHQqDEmQE2KbkYFX8uLPehZb5rIHFD37Td94TszPyBZ/eI2cOWB8DfKPYwJLQg2yxwK/KCNYFAqRArMaEsGi0CZAdKAQG+WgN+1b6kLwgUEO6tYHhd2hW4ceMc9AQ7znoLHqMZYRaIgfrHIQTDtYAzXIZx/SB8EkwA5Y1shXDIlBIXas1zqFpKAQyyLwgl1i/qT6elqdAJ61TArGdOPlAAAAAElFTkSuQmCC'
            self.movecat = tkinter.PhotoImage(data=movecat)
            movecattop = b'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAjUlEQVQ4je3RMQqEMBSE4X/B9B7Y0ltsbeEq6ylc8Aa2niTbzOLjsU0StMrAg5BkPgKBmjsSgCdwaF2MzUDUTCVoEBCBRROBVw4aVLSA32tSwEHF0RUtOqSAuwr/XtHobE8BbVrgo1e1uYjFNs5f3kpQi/WabNRjD002ujrsF4uuKeAb6Bxm0U53ai7IF048K+/R09fYAAAAAElFTkSuQmCC'
            self.movecattop = tkinter.PhotoImage(data=movecattop)
            movecatbottom = b'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAlUlEQVQ4je3RsQ2DMBCF4d+S3WdgSlZIRe0iEAEzRKJgA7YhRU7iZBnByaHjlffOn2UZ7lyVHqgAl+mcdL0FnIAVqBPUyWyVndN5AHOCamyWHVNStAjLocWYRj+l2AJEwGc6L91iASO/J74SNACtdNECenWwFSgA3c5Fp6KBARjVBWZMo2+2X+5kVpQAPIHmH9id43wBGXgraIZdr74AAAAASUVORK5CYII='
            self.movecatbottom = tkinter.PhotoImage(data=movecatbottom)
            movecatdown = b'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAUUlEQVQ4jWNgGAUjE2hAMTHq1Ikx8DgDA8MXBgYGWzxqbKFqjhNjIEwxLkMJyZNkKFmG4dJMkWHohv6HYooMQzYUZiDFhsGAEgNxSWkUjAgAANXFGf4QxtRGAAAAAElFTkSuQmCC'
            self.movecatdown = tkinter.PhotoImage(data=movecatdown)
            movecatup = b'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAATUlEQVQ4jWNgGAWjAAY0GBgYtKhlmC0DA8N/KLalhmFfkAz8QomhMMNghqDzKTKMkDhZhpFt6HEiFMMMPU6MgRpQTIw6dWIMHAXDDQAAibkaBrrWYQUAAAAASUVORK5CYII='
            self.movecatup = tkinter.PhotoImage(data=movecatup)  
            checkb = b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAUCAYAAACXtf2DAAAAbElEQVQ4je3TMQ6AIBBE0X8Sz+EFUO5ja8Gp1U4rkg2JCrpTmDg1eb9ZQLMIzCKbCGzADiQl7h4Y1fj64+WGVrxT4hOwAEGB9+bxXaQZz0sVkfAUr4m8xq8ibvhZRHLnNiL5RGXEHbcRGf6NHQZTUJjSNZBnAAAAAElFTkSuQmCC'
            self.checki = tkinter.PhotoImage(data=checkb)  
           
            self.infoFrame.rowconfigure(1, weight=1)
            self.infoFrame.columnconfigure(0, weight=1)
            
            self.logoframe = tkinter.Frame(self.infoFrame, highlightthickness=0)
            self.logoframe.rowconfigure(0, weight=1)
            self.logoframe.columnconfigure(0, weight=1)
            self.logoframe.grid(row=0, column=0, sticky='nswe')
            self.labelpcp = tkinter.Label(self.logoframe, image=self.tkphotologo2)
            self.labelpcp.grid(row=0, column=0, sticky='n')
            
            self.notebook = ttk.Notebook(self.infoFrame, padding=8)
            self.notebook.bind("<ButtonRelease-1>", self.tabOpened)
            self.notebook.grid(row=1, column=0, sticky='nsew')
            self.tocOuterFrame = tkinter.Frame()
            self.tocOuterFrame.rowconfigure(0, weight=1)
            self.tocOuterFrame.columnconfigure(0, weight=1)
            self.canvastoc = tkinter.Canvas(self.tocOuterFrame)
            self.canvastoc.grid(row=0, column=0, sticky="nsew")
            self.tocFrame = tkinter.Frame(borderwidth=2, relief='ridge')
            self.tocFrame.rowconfigure(1, weight=1)
            self.tocFrame.columnconfigure(0, weight=1)
            self.treeviewEqs = ttk.Treeview(self.tocFrame, selectmode='browse')
            collapseb = b'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAj0lEQVQ4je3OMQrCQBAF0BdyEQtrG8E0mto7WHgF8RyWNqbW6P1MYWkzCyHdRkGEfPgw7DKPYcpfpsApWnwDa/CKNp+gfWwbHY0OsZTR6HGALaJ99JADzrGMuUYXreOtwiwHTEnYHY+YN2MgsdihRRlt8cQ6F6ti8RpQSolb/K1ywD3OA6yPXrDLvXLKj/IGvPcfcN5Qmi8AAAAASUVORK5CYII='
            self.collapseimg = tkinter.PhotoImage(data=collapseb)
            self.collapseeqs = tkinter.Button(self.tocFrame, text='Colapsar todos', image=self.collapseimg, compound="right", command=self.collapsealleqs)
            self.collapseeqs.grid(row=0, column=0,sticky='n', padx=10, pady=15)
            
            
            self.treeviewEqs.grid(row=1, column=0, sticky='nsew')
            self.treeviewEqs.heading("#0", text="Equipamentos / Relatorios", anchor="w")
            self.scrolltoc = ttk.Scrollbar(self.tocFrame, orient="vertical")
            self.scrolltoc.config( command = self.treeviewEqs.yview )
            self.treeviewEqs.configure(yscrollcommand=self.scrolltoc.set)
            self.scrolltoch = ttk.Scrollbar(self.tocFrame, orient="horizontal")
            self.scrolltoch.config( command = self.treeviewEqs.xview )
            self.treeviewEqs.configure(xscrollcommand=self.scrolltoch.set)
            self.scrolltoch.grid(row=2, column=0, sticky='ew')
            self.treeviewEqs.bindtags(('.self.treeviewEqs', 'Treeview', 'post-tree-bind','.','all'))
            self.treeviewEqs.bind_class('post-tree-bind', "<1>", lambda e: self.treeview_selection(e))
            self.treeviewEqs.bind_class('post-tree-bind','<Right>',lambda e: self.treeview_selection(e))
            self.treeviewEqs.bind_class('post-tree-bind','<Left>',lambda e: self.treeview_selection(e))
            self.treeviewEqs.bind_class('post-tree-bind','<Up>', lambda e: self.treeview_selection(e))
            self.treeviewEqs.bind_class('post-tree-bind','<Down>', lambda e: self.treeview_selection(e))
            treevieweqtt = CreateToolTip(self.treeviewEqs, "Equipamentos / Relatórios", istreeview=True, classe='post-tree-bind')
            self.scrolltoc.grid(row=1, column=1, sticky='ns')
            maiorresult = 0
            imageequipb = b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAvElEQVRIie3VMW7CUBCE4U9K4/SWOENSQE5gSnIFuEMKaKDiCqG0LwDIp6TgRSArYfETSCk80jSr2f2lLXa5aI7jgzzX0RuabvGXzCR5FGQbvF8XJtgFTduU2eEzyH7j4y9AhVmmqwhQ4YBNpveY3gLMUvALLcpgFV2tndcXAlqM8fIsQJkxvBcgVwNgAAyA/wJo5J/rOgIUWMk/10u83gJEKpIjZQOmyb0B9zz9Pqp1nj4snN/lI7z4GXoCuI1sSc8cgJwAAAAASUVORK5CYII='
            self.imageequip = tkinter.PhotoImage(data=imageequipb)
            imagereportb = b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAABU0lEQVRIibXVT0tUURwG4Cdx6SJkCEQL3UXkjCKGhGglkamEW12KCxdmiYooIiJGSRuXLkQQQnCRKxetQz+EoeDnCAQXM5jkuWfOXJgXXrhwf5zn3Mv9QzgPcYFfOfoXrRnr3qYdu9WGMvIdndWGHqCQE9hGKXSiiCv5bsu1f7flK7pDwDhmc+56B88rx1/QU09gC72pQBGfI50KAJt4kQo8wXCkgwFgA30xoAGNNfR/YB0vY8AIThK7HwDW0B8D8uQusIqBGPAKe4ndDgArlTUygSa0JbYlACzjdQwooCuxzwLAEoZiQB++JXY5ACzgbQzIk7vAPN7FgFHpH7mDAPAJ7+t5BXOVTd7LBH5iGjOxwSrALMZCQx04x0flq5nEnxqBgvK78SFrsAOneIxmHNUILOJY+Zebmaf4rfyM/6gRSE4JZzisFwBvcCntcb3Eo9AiN8RCeHqaVonMAAAAAElFTkSuQmCC'
            self.imagereportb = tkinter.PhotoImage(data=imagereportb)
            self.primeiro = None
            regeq = "(EQ|eq|Eq)(\s?\.?)*[0-9]+"
            
            for relatorio in infoLaudo:
                p = Path(relatorio)
                pai = p.parent
                paibase = os.path.basename(pai)
                ok = False
                for k in range(2):
                    if(re.match(regeq, paibase)):
                        ok = True
                        break
                    else:
                        pai = pai.parent
                        paibase = os.path.basename(pai)
                if(not ok):
                    paibase = "Outros documentos"
                    pai = p.parent
                pdfbase = os.path.basename(p)
                tipo = "pdf"
                try:
                    if(infoLaudo[relatorio].tipo=='laudo'):
                        self.treeviewEqs.insert(parent='', index='end', iid=pai, text='LAUDO', image=self.imageequip, tag='equipmentlp', values=('eq', str(paibase),))
                    else:
                        self.treeviewEqs.insert(parent='', index='end', iid=pai, text=paibase.upper(), image=self.imageequip, tag='equipmentlp', values=('eq', str(paibase),))
                except Exception as ex:
                    None
                self.treeviewEqs.insert(parent=pai, index='end', iid=str(p), text=pdfbase, tag='reportlp', image=self.imagereportb, values=(tipo, str(p),))                
                self.treeviewEqs.see(str(p))
                for t in infoLaudo[relatorio].toc:
                    nivel = t[0].split(' ')[0].split('.')
                    ident = ''
                    for k in range(len(nivel)):
                        ident += '     '
                    self.treeviewEqs.insert(parent=str(p), index='end', text=ident+t[0], values=('toc', str(p), t[0], t[1], t[2],))
                    somatexto = paibase.upper()+pdfbase+t[0]
                    tamanho = self.resultfont.measure(pdfbase)+150
                    if(tamanho>maiorresult):
                        maiorresult = tamanho
                        self.treeviewEqs.column("#0", width=maiorresult, stretch=True, minwidth=maiorresult, anchor="w")
                if(pathpdfatual==None):
                    pathpdfatual = relatorio  
                    
                    self.primeiro = str(p)
                    try:
                        docatual.close()
                    except Exception as ex:
                        None
                    docatual = fitz.open(pathpdfatual)
            self.treeviewEqs.tag_configure('equipmentlp', background='#a1a1a1', font=('Arial', 12, 'bold', 'underline'))
            self.treeviewEqs.tag_configure('reportlp', background='#ebebeb', font=('Arial', 10, 'bold'))            
            self.canvastoc.create_window((0,0), window=self.tocFrame, anchor="nw")            
            self.searchFrame = tkinter.Frame(borderwidth=2, bg='white')
            self.searchFrame.rowconfigure(1, weight=1)
            self.searchFrame.columnconfigure(0, weight=1)
            self.searchBox = tkinter.Frame(self.searchFrame, borderwidth=2, relief='ridge')
            self.searchBox.grid(row=0, column=0, sticky='new', pady=(0, 10))
            self.searchBox.rowconfigure((0,1,2,3), weight=1)
            self.searchBox.columnconfigure((0,1), weight=1)
            self.searchVar = tkinter.StringVar()
            self.searchVar.set("")
            self.entrysearch = PlaceholderEntry(self.searchBox, placeholder='Buscar...', justify='center', textvariable=self.searchVar, state='normal', exportselection=False)
            self.entrysearch.bind('<Return>',  lambda e: self.searchTerm(event=e, advancedsearch=False))
            self.entrysearch.grid(row=1, column=0, sticky='nsew', columnspan=2, pady=5)            
            self.querysqlimb = b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAABbUlEQVRIie3UPUtcQRTG8R/E3YArKtbRFGoQTK99CBFTSGoL8QuoiK1iwBix9BMkJFZJ70vERixibBREUUwdTSeClZpiRnDdu3ddvZjGPxy4zMvz3DlnzvCfeIoezOIHfuMUFzFOcYhlzOAN8rcRrsN7/MUmpvEOnWhEDk/QgA70YQo/455JFMqJP8c+vsTN1dKOT9hDS9KCVYzdQfgmI0JaS7hAfQYGhahVwiWGMzAYjVqJBrv4LOSzWl4I9dtJM6jFBI6wofgWNaEmRhNexrlp/MIfjEeNsga5+J3Da3zEIg5wgvMYJ3FsAR/w6trefJrBYw0q1uCK+9TgplbRYGvy6auiLc1gS8jlXenAdprBII7xFb1CPitRwFvMC7UbSDMgPMvDWMeZcKpvmBOe5qn4/T3OnWENQ8Izfl2riHPFhbr6u270C/d7PMZoHOtKOGU+apWwIrtGW0qaaJZdoz0rtyirRqvIfRvt4fgHJ0GAl9R3WWIAAAAASUVORK5CYII='
            self.querysqlim = tkinter.PhotoImage(data=self.querysqlimb)
            self.limitSearchFrame = tkinter.Frame(self.searchBox)
            self.limitSearchFrame.grid(row=0, column=0, sticky='w', pady=5)
            self.limitSearchFrame.rowconfigure(0, weight=1)
            self.limitSearchFrame.columnconfigure(0, weight=1)
            self.limitsearchVar = tkinter.IntVar()
            self.limitsearchVar.set(1000)
            self.limitsearchlabel = tkinter.Label(self.limitSearchFrame, text='*Max. Resultados por seção: 1000')
            self.limitsearchlabel.grid(row=0, column=0, sticky='w', pady=5)
            ##self.limitsearch = tkinter.Entry(self.limitSearchFrame, justify='center', textvariable=self.limitsearchVar, exportselection=False, state='disabled')
            #self.limitsearch.grid(row=0, column=1, sticky='e', pady=5)
            self.querysql = tkinter.Button(self.searchBox, text='Query', image=self.querysqlim, compound="right", command=self.querySql)
            self.querysql.grid(row=0, column=1, sticky='e', pady=5)
            self.searchbutton = tkinter.Button(self.searchBox, text='Pesquisar', state='normal', command= lambda: self.searchTerm(advancedsearch=False))
            self.searchbutton.grid(row=2, column=0, columnspan=2, sticky='n', pady=5)
            sep = ttk.Separator(self.searchBox)
            sep.grid(row=3, column=0, columnspan=2, sticky='nsew', pady=5)            
            fromFile = b'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAlklEQVQ4je3PPQrCQBgG4aez849cwdOl9QAWWmihpdiJF9FCQUHQk6i9EGxWEE2yW1hm4G0+hmGXNIZhf2MU1gSbYBN800GeEMyDG6WFA+Y1wQX2wf1hXXJr44RpSXCGY3C+2cCz4qVdnDH+CE7CreqrRV0Q+rhiix0u6NX40SBkeIRlETcpCIOwGMnBVApY4faH3bF8AVGxOrC5VQTqAAAAAElFTkSuQmCC'
            imfromFile = tkinter.PhotoImage(data=fromFile)
            toFile = b'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAmklEQVQ4je3PzQoBQBRA4c/fws+at5WFtaxZsGDBWkpRPIeN91CycJUsGExJOXVqunc6zfCcCg5hJeH+Q8qYYx/OYvYWJUyxQjdcYRK7lyhijDWq6IRVbDCKO8mxIbaoxewahDp2GKCQEmy5fLVxM7sNit0UzdRX3nMf/Jh/8NeDi4zBJRwzBk9fC7bDbMFWmC2Yygn6cchh7wxyaDw75WhqDgAAAABJRU5ErkJggg=='
            imtoFile = tkinter.PhotoImage(data=toFile)
            copyrestoblipb = b'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAA7klEQVQ4jc2VMQ6CQBBFX6MFp6AlofUEngACBbUXgW09ijfhCF4BOwotSLCYQYlxZzeGwp9MSCY/j2FmdoG3dkAG5EYkROoI3IA5EA/gFILtFXYFHNB6ogN6YAJSC5jp213ElzTqLSxTrqY2AngARn1uAoxSCJgDlRElHz21gGfCk5+RQb2m7wMu+QtQGxU2yPTv6J76gJXma08r1urUm6+BnQdYRQDbNTBBTkCv5S8r8TMQpKGTJsctgCCjL7aq8Jv+H1iqqYkAOvVmlilFBtUjK9V6wiFX34Bc0qZOyAkIHb0BuaSjlGD/FrJ1ZU/XOGyY7pNbbwAAAABJRU5ErkJggg=='
            copyrestoblip = tkinter.PhotoImage(data=copyrestoblipb)
            #toFile
            self.searchlistframe = tkinter.Frame(self.searchBox)
            self.searchlistframe.grid(row=4, column=0, columnspan=2, sticky='nsew', pady=(0, 10))
            self.searchlistframe.rowconfigure((0,1), weight=1)
            self.searchlistframe.columnconfigure((0,1), weight=1)
            #self.bfromFile = tkinter.Button(self.searchlistframe, text="Importar Lista", image=imfromFile, compound="right", state='disabled', command=self.openSearchlist)
            self.bfromFile = tkinter.Button(self.searchlistframe, text="Importar Lista", image=imfromFile, compound="right", state='normal', command=self.importListPopUp)
            #importListPopUp
            self.bfromFile.image = imfromFile
            self.bfromFile.grid(row=0, column=0, pady=5, sticky='n')  
            self.btoFile = tkinter.Button(self.searchlistframe, text="Exportar Lista", image=imtoFile, compound="right", state='normal', command=self.saveSearchlist)
            self.btoFile.image = imtoFile
            self.btoFile.grid(row=0, column=1, sticky='n', pady=5) 
            self.saveresulttocsv = tkinter.Button(self.searchlistframe, text="Salvar resultados (CSV)", image=copyrestoblip, compound="right", state='normal', command=self.saveSearchResults)
            self.saveresulttocsv.image = copyrestoblip
            self.saveresulttocsv.grid(row=1, column=0, columnspan=2, sticky='n', pady=5) 
            self.searchEnv = tkinter.Frame(self.searchFrame, borderwidth=2, relief='ridge')
            self.searchEnv.grid(row=1, column=0, sticky='nsew')
            self.searchEnv.rowconfigure(1, weight=1)
            self.searchEnv.columnconfigure(0, weight=1)
            self.searchbuttonsframe = tkinter.Frame(self.searchEnv, borderwidth=2, relief='ridge')
            self.searchbuttonsframe.grid(row=0, column=0, sticky='nsew')
            self.searchbuttonsframe.rowconfigure((0,1,2,3), weight=1)
            self.searchbuttonsframe.columnconfigure((0,1,2), weight=1)
            nextfind = b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAABrUlEQVRIS73WO2gVURDG8d9VMNj4KJLgA7TTSglGIdhom3RJEQsTLbTwgVqZGAkEBIM2EvIgkDRCmgQstQnYxUZEtNJOERUUfFSCIIYJu7Dc3Lu7iaxTLXvmnP85M3PmOzXFtgWdOIw9iftnvMFz/M1bopYzGIuNoBfv8BqfEv+9OIKDeIRxBHSdNQLEvyFcwxTm8aXJRtpwAVcxgfv1J6oHbMdD7MAAvhZHcM2jFQv4iXP4lc7LAuJ7Cd9wGX8yi8dYbqyxFTPYjf7UPwsYxin01C0enFtowVjBiQLyBE9xL3xTQCT0BY42CcsuLONxCUiE6xWOReJTwGRSBXdzdrgRyG20R6EEIOr8AzpyqiXlloVEdb3E/gCcwAOcLFkxZSHPcCMAg+jCpZKAcCsDmcVKeqm24c4GAGUgo/j9XwCVh6jyJFdeppGwSi9aACpvFQGJZnca3VU0u7TxLeL7P7bruIRnGrXrgKSCsxNnNyE4P3C+meBkRegmrmMacwWSeRFXEslc04CsFYl+CE0f3iei/zGZvC8R/QObEf1GmziOQ4jXRFi8Lt6WebasAm+reS8h0IWJAAAAAElFTkSuQmCC'
            imnextfind = tkinter.PhotoImage(data=nextfind)
            bnextfind = tkinter.Button(self.searchbuttonsframe, image=imnextfind, text="Próximo", compound='top', command=lambda: self.iterateSearchList(None, 'proximo'))
            bnextfind.image = imnextfind
            bnextfind.grid(column=2, row=0, sticky='ns', padx=10, pady=5, rowspan=2) 
            self.ocorrenciasLabel = tkinter.Label(self.searchbuttonsframe, text="-- de -----")
            self.ocorrenciasLabel.grid(row=1, column=1, sticky='nsew', pady=5)            
            self.termosearchVar = tkinter.StringVar(self.searchbuttonsframe)
            self.termosearchVar.set("")
            self.termosearched = tkinter.Entry(self.searchbuttonsframe, justify='center', textvariable=self.termosearchVar, state='disabled', exportselection=False)
            self.termosearched.grid(row=0, column=1, sticky='nsew', pady=5)            
            showhideb = b'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAABDklEQVQ4je3TvyvEcRzH8UfHleWKQ0oG/4qFwWCxKfkxSImBTcpgUxZS/gmDDCYrGY5kkkEpGZhukb5kuPe3u85dPinbveqzvF+fnu/X+/ODjv5bw1jFHvaxhIHwpjGeCurBIT7xiBMc4x7z2EIW0F9VxhWeMYlCk7+Ar2hUToFVcIuhqJUw1gDL1I6hEqstNIfdqJ9TCQ+ReCOSLTftbwkthnGN/ob6BC4iUYYqFluEqATjB7BVt/WALeMNsynAdiPkF1AN2B16U0Zuhu6oX8BKpJtBX+wbTIHlKmI7kh2hq8ErYAovuEyBUXusGc7wjiec4xSv+MAmulNg1L5T/gNGMIddHGANo6mgjv6mb/8sRH+eNnsIAAAAAElFTkSuQmCC'
            self.showhide = tkinter.PhotoImage(data=showhideb)     
            self.hideresultsvar = tkinter.BooleanVar()
            self.hideresultsvar.set(0)
            self.hideshow = ttk.Checkbutton(self.searchbuttonsframe,text='Esconder termos sem resultados', command=lambda:self.showhideresults(), \
                                            image=self.showhide, compound='right', variable=self.hideresultsvar)
            self.hideshow.grid(column=0, row=2, sticky='ns', padx=10, pady=5, columnspan=3)
            
            self.collapse = tkinter.Button(self.searchbuttonsframe, text='Colapsar todos', image=self.collapseimg, compound="right", command=self.collapseall)
            self.collapse.grid(row=3, column=1,sticky='ns', padx=10, pady=5)
            prevfind = b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAABtklEQVRIS73WO2gVURAG4C8KgTRGixiSCNpppQQfENLEwka7WGjhq9DCKGqleRAICCbaBNEEQRvBRsHW0k4bkRAr7RRJAgZ8VIogyoQ9cLnuvbu5sp5q2TPz/3Nm5sx/2hSvDdiHXejJzFfwFq/wuxlEW5PNABvHMN7jDZYz+17sxg48xTSC9K+VRxD/ruES7uIBPjUIZCvO4iJu41b9ieoJOvAQm3ASq8UZXLPowiN8w2l8T361BPH9BJ8xgl8lwZPZRsxjC46lk9QSjGIIR0qAT+EHZuqCCJJneI6bsZcIoqCvsadEWgI8gjiErzmnjHQtYm8UPhHcybrgRkFaisCT+wS6o1GCIPr8I/qbdEs4lgUP2+iuBWwLggOYxWCT6NcDnmBe4koQnMIAzjcgaAU8oO7hRbpU7bieQ9AqeEBN4ud/Iag8RZUXufI2jYJUetGCoPJRESQx7A7icBXDLg2+x/jyj+N6M47njesgSYLTiRMlJmu6m0lwYrqeaSQ4tSJ0FZcxh/sFknkOFzLJXNOA2lUk+mM4ig+Z6C9lzn2Z6G9vRfTzgtiPnYjXRKx4Xbwr82z5A++beS8KTDgFAAAAAElFTkSuQmCC'
            imprevfind = tkinter.PhotoImage(data=prevfind)
            bprevfind = tkinter.Button(self.searchbuttonsframe, image=imprevfind, text="Anterior", compound='top', command=lambda: self.iterateSearchList(None, 'anterior'))
            bprevfind.image = imprevfind
            bprevfind.grid(column=0, row=0, sticky='ns', padx=10, pady=5, rowspan=2)  
            self.searchtreeframe = tkinter.Frame(self.searchEnv, borderwidth=2, relief='ridge')
            self.searchtreeframe.grid(row=1, column=0, sticky='nsew')
            self.searchtreeframe.rowconfigure(0, weight=1)
            self.searchtreeframe.columnconfigure(0, weight=1)
            self.treeviewSearches = ttk.Treeview(self.searchtreeframe, selectmode='extended')
            self.treeviewSearches.bindtags(('.self.treeviewEqs', 'Treeview', 'post-tree-bind-search','.','all'))
            self.treeviewSearches.bind_class('post-tree-bind-search', "<1>", lambda e: self.treeview_selection_search(e))
            self.treeviewSearches.bind_class('post-tree-bind-search', "<3>", self.treeview_search_right)
            #self.treeviewSearches.bind_class('post-tree-bind','<Right>',lambda e: self.treeview_selection(e))
            #self.treeviewSearches.bind_class('post-tree-bind','<Left>',lambda e: self.treeview_selection(e))
            self.treeviewSearches.bind_class('post-tree-bind-search','<Up>', lambda e: self.treeview_selection_search())
            self.treeviewSearches.bind_class('post-tree-bind-search','<Down>', lambda e: self.treeview_selection_search())
            treeviewsearchtt = CreateToolTip(self.treeviewSearches, "Buscas", istreeview=True, classe='post-tree-bind-search')
            self.treeviewSearches.heading("#0", text="Termo Buscado", anchor="w")
            self.treeviewSearches.column("#0", width=200, stretch=True, minwidth=200, anchor="w")
            self.treeviewSearches.grid(row=0, column=0, sticky='nsew')
            self.scrolltreeviewSearches = ttk.Scrollbar(self.searchtreeframe, orient="vertical")
            self.scrolltreeviewSearches.grid(row=0, column=1, sticky='ns')
            self.scrolltreeviewSearches.config( command = self.treeviewSearches.yview )
            self.treeviewSearches.configure(yscrollcommand=self.scrolltreeviewSearches.set)
            self.scrolltreeviewSearchesH = ttk.Scrollbar(self.searchtreeframe, orient="horizontal")
            self.scrolltreeviewSearchesH.config(command = self.treeviewSearches.xview )
            self.treeviewSearches.configure(xscrollcommand=self.scrolltreeviewSearchesH.set)
            self.scrolltreeviewSearchesH.grid(row=1, column=0, sticky='ew')
            self.obsFrame = tkinter.Frame(borderwidth=2, bg='white')
            self.obsFrame.rowconfigure(1, weight=1)
            self.obsFrame.columnconfigure(0, weight=1)
            self.treeviewSearches.bind_class('post-tree-bind-search', '<Delete>', lambda e: self.deleteSearchDel(e))            
            self.obsButtonFrame = tkinter.Frame(self.obsFrame, borderwidth=2, relief='ridge', pady=10)
            self.obsButtonFrame.rowconfigure(0, weight=1)
            self.obsButtonFrame.columnconfigure((0,1), weight=1)
            self.obsButtonFrame.grid(row=0, column=0, sticky='nsew')
            self.menuaddcat = tkinter.Button(self.obsButtonFrame, text="Adicionar Categoria  ", image=self.addcat, compound='right', command=lambda: self.addcatpopup(None, 'add',''))
            self.menuaddcat.grid(row=0, column=0, columnspan=2, sticky='ns')    
            filterdocb = b'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAA9ElEQVQ4jeXUvUrDYBTG8V/QqaCdFRR1Exy6KoiDrjqZQe/Cjg7S3o2D4KYXoWMHd0VQ1MnByTjkBFrQNGnTyQceCOfj/x7O+xJmoAS7SHE8oVPsB8sKsoa8Wkx5HYG3mpOmeI/ex2JCmMdtJM5qrKsbPTfBGFEbA3zjsALsKGoHWPyraB2v+ESnBNaJmhesjTt5B1/ynSz9kl/GU9Rsj4MVOpXv5g6toXgL95E7qQor1I/GK/ntJfGdoVcXJgDPAdgMZxFLSvpK1QvIVnji6f4x8CIgl9hrAriBB6N/lP40QJiTP/SPAJ5PCxwGH2ChKWAl/QDbtVhT52qtCwAAAABJRU5ErkJggg=='
            #self.filterdoc = tkinter.PhotoImage(data=filterdocb)
            #self.menufilterobs = tkinter.Button(self.obsButtonFrame, text='Filtrar por documento', image=self.filterdoc, compound="right", command=self.filterdocWindow)
            #self.menufilterobs.grid(row=0, column=1, sticky='ns') 
            #self.menufilterobs.image = filterdoc
            self.TreeviewobsFrame = tkinter.Frame(self.obsFrame, borderwidth=2, bg='white', relief='ridge')
            self.TreeviewobsFrame.rowconfigure(0, weight=1)
            self.TreeviewobsFrame.columnconfigure(0, weight=1)
            self.TreeviewobsFrame.grid(row=1, column=0, sticky='nsew')
            self.treeviewObs = ttk.Treeview(self.TreeviewobsFrame, selectmode='browse')
            self.treeviewObs.heading("#0", text="Categorias", anchor="w")
            self.treeviewObs.bindtags(('.self.treeviewObs', 'Treeview', 'post-tree-bind-obs','.','all'))
            self.treeviewObs.bind_class('post-tree-bind-obs', "<3>", self.treeview_obs_right)
            self.treeviewObs.bind_class('post-tree-bind-obs', "<1>", lambda e: self.treeview_selection_obs(e))
            self.treeviewObs.bind_class('post-tree-bind-obs','<Up>', lambda e: self.treeview_selection_obs(e))
            self.treeviewObs.bind_class('post-tree-bind-obs','<Down>', lambda e: self.treeview_selection_obs(e))
            treeviewobstt = CreateToolTip(self.treeviewObs, "Observações", istreeview=True, classe='post-tree-bind-obs')
            self.treeviewObs.grid(row=0, column=0, sticky='nsew')
            self.scrolltreeviewObs = ttk.Scrollbar(self.TreeviewobsFrame, orient="vertical")
            self.scrolltreeviewObs.grid(row=0, column=1, sticky='ns')
            self.scrolltreeviewObs.config( command = self.treeviewObs.yview )
            self.treeviewObs.configure(yscrollcommand=self.scrolltreeviewObs.set)
            self.scrolltreeviewObsH = ttk.Scrollbar(self.TreeviewobsFrame, orient="horizontal")
            self.scrolltreeviewObsH.config( command = self.treeviewObs.xview )
            self.treeviewObs.configure(xscrollcommand=self.scrolltreeviewObsH.set)
            self.scrolltreeviewObsH.grid(row=1, column=0, sticky='ew')
            self.repiconb = b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAqUlEQVRIie3VwQ2EIBAF0LEHNFQASDyMEz1rOdsFlGCJduJe9MYKw5g9+ZN/M3nxQwLAv6OHadWeYq6dHT8A0PABT7G1eBS1p42NXMDdNyKEBfS0sREOAAANGykBlBv31JmcBy8HUjettXhoT/ERIJUqQBkMuauqDIZ6wM2LMhhu6+alGuDknSibd6JsHp3omkUO/JronEUMcMIGaloGFD76yQ7Tyv1zcb4rsPqGqRcMYwAAAABJRU5ErkJggg==+ZN/M3nxQwLAv6OHadWeYq6dHT8A0PABT7G1eBS1p42NXMDdNyKEBfS0sREOAAANGykBlBv31JmcBy8HUjettXhoT/ERIJUqQBkMuauqDIZ6wM2LMhhu6+alGuDknSibd6JsHp3omkUO/JronEUMcMIGaloGFD76yQ7Tyv1zcb4rsPqGqRcMYwAAAABJRU5ErkJggg==/WzjfzPXwES2thYaEx9CIikcV8BlGTpGl6C0srhGIhEQuvnJm4nXf0du/Uf3t/3XvqQjxvzA64KksBySiBNFAGEpqD80A2JOADU6CgAfqAFwBDIKfoJ4AGGqAngBFQVPQbBugKwAe+HP1/RhXQEcAWmDs6WYA2+h0sLUAL/Q5WFqApgFlwo1dtLEBDAHtg4ehsAeoCGAMlR6Yn8oh4BzUBfAOfjtYWoCqAA+4dXCxARQATHk/2LNMNPgSg/U1DARnu3/UxKiCeP3MDV2rgabrWLnIAAAAASUVORK5CYII='
            self.repicon = tkinter.PhotoImage(data=self.repiconb)
            self.searchiconb = b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAABHklEQVRIidXWsUrDUBjF8V/p6AuIKA4uvoMKDg6OgnRw0l0fQHARRPsISgdLX8KhgwqCiyi+gSCiIOIgLkq1DrkZDEmluVHwwBnuzeH8Ez5yE4q1hn5JXw/oBQ18hHAH20M4hQws7+EqBOd/upuMToMHlh9jsWrAMj5xg90QqhSQFmY9XSUg98K/B8yhLRn8IWaqAtSwJ5nDPc7wENY7VQBWQtkm6mGvjq2w34gFXBYEa5KnuYgF9CTvQ56aeI8FPOGgoKSFx1hAC88Yy+Sm8Ir9WMAo7nCLdSxgAy+SI2U1FgCT6Pp+dHRxjjcsxQJSTWAW42E9gpMCSClAnooglQFSyJFkPr8CGKrnTwB9w33g89wvAnSU/03Jup2WfgH0L6l3L2w+QgAAAABJRU5ErkJggg=='
            self.searchicon = tkinter.PhotoImage(data=self.searchiconb)
            self.commenticonb = b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAdElEQVRIie3UsQnAMAxE0T9jspA3yhYZKimSyiCMg4h91/lAjQs/JIQATuAR1kET5ee1uoAiKWAZVwQs4+oBiixAB4zu/+rgfweft2QW6J0HKZA+OoCRuoAtA2av6R0Q5TQAKAHZHUCLWICI2IAWsaUi1pQXDcnofAiAy1cAAAAASUVORK5CYII='
            self.commenticon = tkinter.PhotoImage(data=self.commenticonb)
            self.notebook.add(self.tocFrame, text="Relatorios", sticky='nsew', image=self.repicon, compound='top')
            self.notebook.add(self.searchFrame, text="Buscas", sticky='nsew', image=self.searchicon, compound='top')
            self.notebook.add(self.obsFrame, text="Marcadores", sticky='nsew', image=self.commenticon, compound='top')
            self.globalFrame.add(self.infoFrame, minsize=100)
            sqliteconn =  connectDB(str(pathdb), 5)
            cursor = sqliteconn.cursor()   
            self.treeviewObs.tag_configure('relobs', background='#e3e1e1')
            self.allobs = {}
            #self.treeviewObs.tag_configure('alterado', background='#ad0202')
            try:
                check_previous_search =  "SELECT DISTINCT C.termo, C.advancedsearch, C.id_termo, C.fixo  FROM Anexo_Eletronico_SearchTerms C ORDER by 3"
                #cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute(check_previous_search)
                termos = cursor.fetchall()
                cursor.close()
                for termox in termos:
                    advanced = False
                    tipobusca = 0
                    
                    termo = termox[0].strip().upper()
                    
                    if(termox[1]==1):
                        tipobusca = 1
                        advanced=True
                    if(not (termo, tipobusca) in self.searchedTerms):
                        listaTERMOS[(termox[0].strip().lower(), tipobusca)]=termox[2]
                        self.searchedTerms.append((termo, tipobusca))
                        searchqueue.append((termo, tipobusca, None))
                    
                        
         
                check_previous_obscat =  "SELECT C.obscat, C.id_obscat, C.fixo, C.ordem FROM Anexo_Eletronico_Obscat C ORDER BY 4"
                sqliteconn.execute("PRAGMA foreign_keys = ON")
                cursor = sqliteconn.cursor() 
                #cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute(check_previous_obscat)
                obscats = cursor.fetchall()
                cursor.close()
                for obscat in obscats:
                    self.treeviewObs.insert(parent='', index='end', iid=str(obscat[1]), text=obscat[0].upper(), values=(str(obscat[2]), obscat[1],), image=self.catimage, tag='obscat')
                    self.treeviewObs.tag_configure('obscat', background='#a1a1a1', font=('Arial', 12, 'bold', 'underline'))
                    check_previous_obsitens =  '''SELECT P.rel_path_pdf, O.paginainit, O.p0x, O.p0y, O.paginafim, O.p1x, O.p1y, O.tipo, O.id_obs, O.fixo, O.status FROM Anexo_Eletronico_Obsitens O, 
                    Anexo_Eletronico_Pdfs P  WHERE
                        O.id_pdf  = P.id_pdf AND
                        O.id_obscat = ? ORDER BY 2,9'''
                    cursor = sqliteconn.cursor()  
                    cursor.execute(check_previous_obsitens, (obscat[1],))
                    obsitens = cursor.fetchall()
                    cursor.close()
                    
                    
                    for obsitem in obsitens:
                        paginainit = obsitem[1]
                        p0x = obsitem[2]
                        p0y = obsitem[3]
                        paginafim = obsitem[4]
                        p1x = obsitem[5]
                        p1y = obsitem[6]
                        tipo = obsitem[7]
                        relpath = obsitem[0]
                        status = obsitem[10]
                        ident = ' '
                        basepdf = os.path.normpath(os.path.join(pathdb.parent, relpath))
                        beforereplace = basepdf
                        
                        if plt == "Linux":                           
                            pathpdf = str(beforereplace).replace("\\","/")
                        elif plt=="Windows":
             
                            pathpdf = str(beforereplace).replace("/","\\")
                        if(pathpdf in infoLaudo and pathpdf not in self.allobs):
                            self.allobs[pathpdf] = []
                        obsobject = Observation(paginainit, paginafim, p0x, p0y, p1x, p1y, tipo, pathpdf, obsitem[8])
                        self.allobs[pathpdf].append(obsobject)
                        try:
                            tocname = self.locateToc(int(paginainit), basepdf, p0y=p0y)
                            if(not self.treeviewObs.exists(str(obscat[1])+basepdf)):
                                
                                
                                self.treeviewObs.insert(parent=str(obscat[1]), iid=(str(obscat[1])+basepdf), text=ident+os.path.basename(basepdf), index='end', tag=('relobs'))
                                
                            if(not self.treeviewObs.exists(str(obscat[1])+basepdf+tocname)):
                                self.treeviewObs.insert(parent=(str(obscat[1])+basepdf), iid=(str(obscat[1])+basepdf+tocname), text=ident+ident+tocname, tag=('tocobs'), index='end')
                            novoiidindex = self.qualIndexTreeObs( paginainit, (str(obscat[1])+basepdf+tocname))
                            if(paginainit==paginafim):
                                self.treeviewObs.insert(parent=(str(obscat[1])+basepdf+tocname), index=novoiidindex, iid='obsitem'+str(obsitem[8]), \
                                                    text=ident+ident+ident+'Pg.'+str(paginainit+1)+' - '+\
                                                    os.path.basename(basepdf), \
                                                    image=self.itemimage, values=(tipo, basepdf,str(paginainit), str(p0x), str(p0y), str(paginafim), str(p1x), str(p1y), str(obsitem[8]), \
                                                    str(obsitem[9]), str(obscat[1]),), \
                                                        tags=(('obsitem', status+str(obsitem[8]),)))
                            else:
                                self.treeviewObs.insert(parent=(str(obscat[1])+basepdf+tocname), index=novoiidindex, iid='obsitem'+str(obsitem[8]), \
                                                    text=ident+ident+ident+'Pg.'+str(paginainit+1)+' - '+'Pg.'+str(paginafim+1)+' - '+\
                                                    os.path.basename(basepdf), \
                                                    image=self.itemimage, values=(tipo, basepdf,str(paginainit), str(p0x), str(p0y), str(paginafim), str(p1x), str(p1y), str(obsitem[8]), \
                                                    str(obsitem[9]), str(obscat[1]),), tags=(('obsitem', status+str(obsitem[8]),)))
                            
                            
                        except Exception as ex:
                            printlogexception(ex=ex)
                            if(not self.treeviewObs.exists(str(obscat[1])+basepdf)):
                                self.treeviewObs.insert(parent=str(obscat[1]), iid=(str(obscat[1])+basepdf), text=ident+os.path.basename(basepdf), index='end', tag=('relobs'))
                                self.treeviewObs.tag_configure('relobs', background='#e3e1e1')
                            novoiidindex = self.qualIndexTreeObs( paginainit, (str(obscat[1])+basepdf))
                            if(paginainit==paginafim):
                                self.treeviewObs.insert(parent=(str(obscat[1])+basepdf), index=novoiidindex, iid='obsitem'+str(obsitem[8]), \
                                                    text=ident+ident+'Pg.'+str(paginainit+1)+' - '+\
                                                    os.path.basename(basepdf), \
                                                    image=self.itemimage, values=(tipo, basepdf,str(paginainit), str(p0x), str(p0y), str(paginafim), str(p1x), str(p1y), str(obsitem[8]), \
                                                    str(obsitem[9]), str(obscat[1]),), tags=(('obsitem', status+str(obsitem[8]),)))
                            else:
                                self.treeviewObs.insert(parent=(str(obscat[1])+basepdf), index=novoiidindex, iid='obsitem'+str(obsitem[8]), \
                                                    text=ident+ident+'Pg.'+str(paginainit+1)+' - '+'Pg.'+str(paginafim+1)+' - '+\
                                                    os.path.basename(basepdf), \
                                                    image=self.itemimage, values=(tipo, basepdf,str(paginainit), str(p0x), str(p0y), str(paginafim), str(p1x), str(p1y), str(obsitem[8]), \
                                                    str(obsitem[9]), str(obscat[1]),), tags=(('obsitem', status+str(obsitem[8]),)))
                        if(status=='alterado'):
                            self.treeviewObs.tag_configure(status+str(obsitem[8]), background='#ff4747')
                            
            except Exception as ex:
                printlogexception(ex=ex)
            finally:
                self.treeviewObs.tag_configure('relobs', background='#e3e1e1')
                
                try:
                    cursor.close() 
                except Exception as ex:
                    None
                try:
                    sqliteconn.close()
                except Exception as ex:
                    None

        except Exception as ex:
            printlogexception(ex=ex)
    
    def collapsealleqs(self, event=None):
        for child in self.treeviewEqs.get_children(''):
            for child2 in self.treeviewEqs.get_children(child): 
                self.treeviewEqs.item(child2, open=False)
    
    def collapseall(self, event=None):
        for child in self.treeviewSearches.get_children(''):
            self.treeviewSearches.item(child, open=False)
    
    def exportsearchtobs(obscat):
        None
    
    def deleteSearchDel(self, event=None):
        iids = self.treeviewSearches.selection()
        if(len(iids)==1):
            self.treeviewSearches.selection_set(iids[0])
            if(self.treeviewSearches.parent(iids)=='' and self.treeviewSearches.item(iids[0], 'text') != ''):
                #self.treeviewSearches.selection_set(iid)
                nxt = self.treeviewSearches.next(iids[0])
                prev = self.treeviewSearches.prev(iids[0])
                try:
                    if(isinstance(event.widget, ttk.Treeview)):
                        self.exclude_search(event)
                        
                        if(nxt!=''):
                            self.treeviewSearches.selection_set(nxt)
                            self.treeviewSearches.focus(nxt)
                        elif(prev!=''):
                            self.treeviewSearches.selection_set(prev)
                            self.treeviewSearches.focus(prev)
                except Exception as ex:
                    printlogexception(ex=ex) 
        elif(len(iids)>1):
            lista = []
            for item in iids:
                if(self.treeviewSearches.parent(item)=='' and self.treeviewSearches.item(item, 'text') != ''):
                    lista.append(item)
                
               
            
            self.exclude_search(lista=lista)
            nxt = self.treeviewSearches.next(iids[-1])
            prev = self.treeviewSearches.prev(iids[-1])
            try:
                if(isinstance(event.widget, ttk.Treeview)):
                    if(nxt!=''):
                        self.treeviewSearches.selection_set(nxt)
                        self.treeviewSearches.focus(nxt)
                    elif(prev!=''):
                        self.treeviewSearches.selection_set(prev)
                        self.treeviewSearches.focus(prev)
            except Exception as ex:
                printlogexception(ex=ex)

    def openSearchlist(self):
        global listaRELS
        searchlist = None
        searchlist = Path(askopenfilename(filetypes=(("Texto", "*.txt"), ("Todos os arquivos", "*"))))
        if(searchlist!=None and searchlist!=''):
            with open(searchlist, "r", encoding='utf8') as a_file:
                try:
                    for line in a_file:    
                        stripped_line = line.strip()
                        tipo = stripped_line.split(" ")[0]
                        if("LIKE" in tipo.upper()):
                            termo = stripped_line[len(tipo):len(stripped_line)].strip().upper()
                            if(len(termo)>=3):
                                if(not (termo, 0) in self.searchedTerms):
                                    self.searchedTerms.append((termo, 0))
                                    #listaTERMOS[]
                                    searchqueue.append((termo, False, None))
                        elif("MATCH" in tipo.upper()):
                            termo = stripped_line[len(tipo):len(stripped_line)].strip().upper()
                            if(not (termo, 1) in self.searchedTerms):
                                self.searchedTerms.append((termo, 1))
                                searchqueue.append((termo, True, None))
                        else:
                            termo = stripped_line.strip().upper()
                            if(len(termo)>=3):
                                if(not (termo, 0) in self.searchedTerms):
                                    self.searchedTerms.append((termo, 0))
                                    searchqueue.append((termo, False, None))
                    self.uniquesearchprocess2 = mp.Process(target=searchProcess, args=(result_queue, pathdb,\
                                                                                       erros,queuesair, searchqueue, \
                                                                                           update_queue, infoLaudo, listaRELS, listaTERMOS, False,), daemon=True)
                    #self.uniquesearchprocess3 = mp.Process(target=searchProcess, args=(result_queue, pathdb, erros,queuesair, searchqueue, update_queue, infoLaudo, False,), daemon=True)
                    #self.uniquesearchprocess4 = mp.Process(target=searchProcess, args=(result_queue, pathdb, erros,queuesair, searchqueue, update_queue, infoLaudo, False,), daemon=True)
                    #self.uniquesearchprocess5 = mp.Process(target=searchProcess, args=(result_queue, pathdb, erros,queuesair, searchqueue, update_queue, infoLaudo, False,), daemon=True)
                    #self.uniquesearchprocess6 = mp.Process(target=searchProcess, args=(result_queue, pathdb, erros,queuesair, searchqueue, update_queue, infoLaudo, False,), daemon=True)
                    
                    self.uniquesearchprocess2.start() 
                    #self.uniquesearchprocess3.start() 
                    #self.uniquesearchprocess4.start() 
                    #self.uniquesearchprocess5.start() 
                    #self.uniquesearchprocess6.start() 
                    self.primeiroresetbuscar = True
                except Exception as ex:
                    printlogexception(ex=ex)       
                        
    def saveSearchlist(self):
        tipos = [('Texto', '*.txt')]
        path = (asksaveasfilename(filetypes=tipos, defaultextension=tipos))
        try:
            if(path!=None and path!=''):
                with open(path, "w", encoding='utf8') as a_file:
                    for termo in self.searchedTerms:
                        if(termo[1]==0):
                            a_file.write('LIKE {}\n'.format(termo[0]))
                        elif(termo[1]==1):
                            a_file.write('MATCH {}\n'.format(termo[0]))
        except Exception as ex:
            printlogexception(ex=ex)             
                        
            
    def iterateSearchList(self, event=None, tipo=None):
        global minMaxLabels, processed_pages, infoLaudo, pathpdfatual, pathdb, realce

        try:
            for pdf in infoLaudo:
                infoLaudo[pdf].retangulosDesenhados = {}
            
            mudar=''
            if(tipo=='proximo'):
                mudar = self.treeviewSearches.next(self.treeviewSearches.selection()[0])
            elif(tipo=='anterior'):
                mudar = self.treeviewSearches.prev(self.treeviewSearches.selection()[0])

            if(mudar==''):
                paiultimo = self.treeviewSearches.parent(self.treeviewSearches.selection()[0])
                if(tipo=='proximo'):
                    proximopai =  self.treeviewSearches.next(paiultimo)
                elif(tipo=='anterior'):
                    proximopai =  self.treeviewSearches.prev(paiultimo)
                
                if(proximopai==''):
                    return
                
                if(tipo=='proximo'):
                    mudar =  self.treeviewSearches.get_children(proximopai)[0]
                elif(tipo=='anterior'):
                    mudar =  self.treeviewSearches.get_children(proximopai)[-1]
            self.treeviewSearches.see(mudar)
            self.treeviewSearches.selection_set(mudar)
            self.treeview_selection_search()
            
        except Exception as ex:
            printlogexception(ex=ex)
            
            
    def treeview_selection_search(self, event=None):
        global minMaxLabels, processed_pages, infoLaudo, pathpdfatual, pathdb, zoom, realce, searchResultsDict, docatual
        try:
            for pdf in infoLaudo:
                infoLaudo[pdf].retangulosDesenhados = {}
            if(event!=None):
                searchresultiid = self.treeviewSearches.identify_row(event.y)
            else:
                searchresultiid = self.treeviewSearches.selection()[0]
            try:
                resultsearch = searchResultsDict[searchresultiid]
            except Exception as ex:
                return
            
            parent = self.treeviewSearches.parent(searchresultiid)
            if(len(self.treeviewSearches.get_children(searchresultiid))==0 and parent != ''):  
                
                raiz = self.treeviewSearches.parent(searchresultiid)
                
                while(raiz!=''):
                    if(self.treeviewSearches.parent(raiz)==''):
                        break
                    raiz = self.treeviewSearches.parent(raiz)
                newpath = os.path.normpath(resultsearch.pathpdf)
                sobraEspaco = 0
                if(self.docFrame.winfo_width() > infoLaudo[pathpdfatual].pixorgw * self.zoom_x * zoom):
                    sobraEspaco = self.docInnerCanvas.winfo_x()  
                self.maiorw = self.docFrame.winfo_width()
                self.positions[self.indiceposition] = (pathpdfatual, self.vscrollbar.get()[0])
                self.indiceposition += 1
                if(self.indiceposition>=10):
                    self.indiceposition = 0
                if(pathpdfatual!=newpath):
                    self.docInnerCanvas.delete("quad")
                    self.docInnerCanvas.delete("simplesearch")
                    self.docInnerCanvas.delete("obsitem")
                    self.docInnerCanvas.delete("link")
                    self.clearSomeImages(["quad", "simplesearch", "obsitem", "link"])
                    self.docwidth = self.docOuterFrame.winfo_width()
                    pathpdfatual =newpath  
                    try:
                        docatual.close()
                    except Exception as ex:
                        None
                    docatual = fitz.open(pathpdfatual)
                    self.labeldocname.config(text=os.path.basename(pathpdfatual))
                    for i in range(minMaxLabels):
                        processed_pages[i] = -1
                    #self.docInnerCanvas.yview_moveto(0)
                    #self.pagVar.set("1") 
                    self.totalPgg.config(text="/ "+str(infoLaudo[pathpdfatual].len))
                    if(infoLaudo[pathpdfatual].pixorgw*self.zoom_x*zoom>self.maiorw):
                        self.maiorw = infoLaudo[pathpdfatual].pixorgw*self.zoom_x *zoom           
                    self.scrolly = round((infoLaudo[pathpdfatual].pixorgh*self.zoom_x*zoom), 16)*infoLaudo[pathpdfatual].len  - 35
                    self.docInnerCanvas.config(scrollregion=(sobraEspaco, 0, sobraEspaco + (infoLaudo[pathpdfatual].pixorgw*zoom*self.zoom_x), self.scrolly))
                    self.docInnerCanvas.update_idletasks()
                
                totalhits = self.treeviewSearches.item(parent, 'text').split(' ')
                self.ocorrenciasLabel.config(text=str(self.treeviewSearches.index(searchresultiid)+1) + ' de ' + totalhits[len(totalhits)-1])
                self.termosearchVar.set(self.treeviewSearches.item(raiz, 'text'))
                self.docInnerCanvas.delete("simplesearch")
                self.clearSomeImages(["simplesearch"])
                pagina = int(resultsearch.pagina)-1
                if(self.afterpaint!=None):
                    root.after_cancel(self.afterpaint)
                if(pagina in processed_pages):
                    listaresultados = [resultsearch]
                    
                    self.paintsearchresult(listaresultados)
                else:
                    ondeir = ((pagina) / (infoLaudo[pathpdfatual].len))
                    self.docInnerCanvas.yview_moveto(ondeir)
                    if(str(pagina+1)!=self.pagVar.get()):
                        self.pagVar.set(str(pagina+1))
                    listaresultados = [resultsearch]
                    
                    self.paintsearchresult(listaresultados)
              
        except Exception as ex:
            printlogexception(ex=ex)
            
    def paintsearchresult(self, listaresultados, simplesearch=False, first=True):
        global pathpdfatual, infoLaudo
        if(len(listaresultados)>0):
            pagina = int(listaresultados[0].pagina)
            if(pagina not in processed_pages):
                 ondeir = ((pagina) / (infoLaudo[pathpdfatual].len))
                 self.docInnerCanvas.yview_moveto(ondeir)
                 if(str(pagina+1)!=self.pagVar.get()):
                     self.pagVar.set(str(pagina+1))
            
            if(pagina not in infoLaudo[pathpdfatual].quadspagina):
                if(first or pagina in processed_pages):
                    self.afterpaint = root.after(100, lambda: self.paintsearchresult(listaresultados, simplesearch, first=False))
            else:
                self.docInnerCanvas.delete("simplesearch")
                self.clearSomeImages(["simplesearch"])
                for resultsearch in reversed(listaresultados):
                    sobraEspaco = 0
                    if(self.docFrame.winfo_width() > infoLaudo[pathpdfatual].pixorgw * self.zoom_x * zoom):
                        sobraEspaco = self.docInnerCanvas.winfo_x() 
                    posicoes = infoLaudo[pathpdfatual].quadspagina[pagina]
                    init = posicoes[resultsearch.init]
                    fim = posicoes[resultsearch.fim-1]
                    p0x = init[0]
                    p0y = (init[1]+5)
                    p1x = fim[2]
                    p1y = (fim[3]-5)
                    self.prepararParaQuads(pagina, int(p0x), int(p0y), math.ceil((p1x)), int(p1y), color=self.color, tag=["simplesearch"], apagar=False, enhancetext=True, enhancearea=False, alt=False)
                    atual = ((self.vscrollbar.get()[0]*infoLaudo[pathpdfatual].len))
                    deslocy = (math.floor(pagina) * infoLaudo[pathpdfatual].pixorgh * self.zoom_x*zoom) + (p0y *  self.zoom_x * zoom)                    
                    desloctotalmenor =  (atual * infoLaudo[pathpdfatual].pixorgh * self.zoom_x*zoom) 
                    desloctotalmaior =   desloctotalmenor + self.docFrame.winfo_height() - self.hscrollbar.winfo_height() -  self.labeldocname.winfo_height()
                    if(deslocy < desloctotalmenor or deslocy > desloctotalmaior):
                        ondeir = ((pagina) / (infoLaudo[pathpdfatual].len)) + (p0y*self.zoom_x*zoom-self.docFrame.winfo_height()/2)/self.scrolly
                        self.docInnerCanvas.yview_moveto(ondeir)
                        if(str(pagina+1)!=self.pagVar.get()):
                            self.pagVar.set(str(pagina+1))
                    if(simplesearch):
                        self.simplesearching = False
                        self.nhp.config(relief='raised', state='normal')
                        self.php.config(relief='raised', state='normal')
        


    def _on_mousewheel(self, event):
        self.docInnerCanvas.yview_scroll(-1*int((event.delta/120)), "units")
        try:
            if (event.num==4):
                 self.docInnerCanvas.yview_scroll(-1, "units")
                 
            elif(event.num==5):
                 self.docInnerCanvas.yview_scroll(1, "units")
        except Exception as ex:
            None
        finally:
            at = round(self.vscrollbar.get()[0]*infoLaudo[pathpdfatual].len)
            #self.pagVar.set(max(at+1, infoLaudo[pathpdfatual].len))
            #printlogexception(ex=ex)
         
    def addImagetoList(self, tag, image, obsitem=None):
        
        if(not tag in self.allimages):
            self.allimages[tag] = []
        if(obsitem!=None):
            self.allimages[tag].append((image, obsitem))
        else:            
            self.allimages[tag].append(image)
        
        
    def clearEnhanceObs(self):
        apagar = []
        for tag in self.allimages:
            
            if "enhanceobs" in tag:
                
                self.docInnerCanvas.delete(tag)
                if tag in self.allimages:
                    apagar.append(tag)
        for tag in apagar:
            del self.allimages[tag]
                
    def clearAllImages(self):        
        for tag in self.allimages:
            self.docInnerCanvas.delete(tag)
        self.allimages = {}
    def clearSomeImages(self, listatags):
        for tag in listatags:
            if tag in self.allimages:
                del self.allimages[tag]
                
                
    def clearSelectedTextByCLick(self, tipo, event):
       global infoLaudo, pathpdfatual, docatual, envlinux     
       try:
           if(event.widget!=None):
               event.widget.focus_set()
           
           if(isinstance(event.widget, CustomCanvas) or isinstance(event.widget, CustomFrame)):
               self.docInnerCanvas.focus_set()
               posicaoRealY0Canvas = self.vscrollbar.get()[0] * (self.scrolly) + event.y
               posicaoRealX0Canvas = self.hscrollbar.get()[0] * (infoLaudo[pathpdfatual].pixorgw * self.zoom_x * zoom) + event.x
               posicaoRealY0 = (posicaoRealY0Canvas % (infoLaudo[pathpdfatual].pixorgh * self.zoom_x*zoom)) / (self.zoom_x*zoom)
               posicaoRealX0 = posicaoRealX0Canvas / (self.zoom_x*zoom)    
               if(self.selectionActive):
                   if(tipo=="press"):
                       
                       for pdf in infoLaudo:
                           infoLaudo[pdf].retangulosDesenhados = {}
                           
                       self.docInnerCanvas.delete("simplesearch")
                       self.docInnerCanvas.delete("quad")
                       self.docInnerCanvas.delete("obsitem")
                       self.clearSomeImages(["simplesearch", "quad", "obsitem"])
                       
                       posicaoRealY0Canvas = self.docInnerCanvas.canvasy(event.y)
                       posicaoRealX0Canvas = self.docInnerCanvas.canvasx(event.x)
                       
                       pagina = math.floor(posicaoRealY0Canvas / (infoLaudo[pathpdfatual].pixorgh *self.zoom_x*zoom))
                       self.initialPos = (posicaoRealX0Canvas, posicaoRealY0Canvas, posicaoRealX0, posicaoRealY0, pagina)
                   elif(tipo=="release"):
                       self.paginaSearchSimple = -1
                       self.initialPos = None
               elif(self.areaselectionActive or self.areaselectionActiveCustom):
                   if(tipo=="press"):
                       for pdf in infoLaudo:
                           infoLaudo[pdf].retangulosDesenhados = {}
                           
                       self.docInnerCanvas.delete("simplesearch")
                       self.docInnerCanvas.delete("quad")
                       self.docInnerCanvas.delete("obsitem")
                       self.clearSomeImages(["simplesearch", "quad", "obsitem"])

                       pagina = math.floor(posicaoRealY0Canvas / (infoLaudo[pathpdfatual].pixorgh *self.zoom_x*zoom))
                       self.initialPos = (posicaoRealX0Canvas, posicaoRealY0Canvas, posicaoRealX0, posicaoRealY0, pagina)
                   elif(tipo=="release"):
                       self.paginaSearchSimple = -1
                       if(self.areaselectionActiveCustom):
                           listaquads = self.docInnerCanvas.find_withtag("quad")
                           for quadelement in listaquads:
                               bbox = self.docInnerCanvas.bbox(quadelement)
                               sobraEspaco = 0
                               if(self.docFrame.winfo_width() > infoLaudo[pathpdfatual].pixorgw * self.zoom_x * zoom):
                                   sobraEspaco = self.docInnerCanvas.winfo_x()  
                               pagina = math.floor(posicaoRealY0Canvas / (infoLaudo[pathpdfatual].pixorgh *self.zoom_x*zoom))
                               deslocy = pagina * infoLaudo[pathpdfatual].pixorgh * self.zoom_x*zoom
                               infoLaudo[pathpdfatual].mt = math.floor(((bbox[1]-deslocy) / (self.zoom_x * zoom) /72) * 25.4)
                               infoLaudo[pathpdfatual].mb = math.floor((infoLaudo[pathpdfatual].pixorgh-((bbox[3]-deslocy) / (self.zoom_x * zoom))) /72 * 25.4)
                               infoLaudo[pathpdfatual].me = math.floor(((bbox[0]-sobraEspaco) / (self.zoom_x * zoom) /72) * 25.4)
                               infoLaudo[pathpdfatual].md = math.floor((infoLaudo[pathpdfatual].pixorgw-((bbox[2]-sobraEspaco) / (self.zoom_x * zoom))) /72 * 25.4)
                           for pdf in infoLaudo:
                               infoLaudo[pdf].retangulosDesenhados = {}
                               
                           self.docInnerCanvas.delete("quad")
                           self.clearSomeImages(["quad"])
                       self.initialPos = None
               else:
                   if(tipo=="press"):
                       self.docInnerCanvas.scan_mark(event.x, event.y)
 
                       pagina = math.floor(posicaoRealY0Canvas / (infoLaudo[pathpdfatual].pixorgh *self.zoom_x*zoom))
                       self.initialPos = (posicaoRealX0Canvas, posicaoRealY0Canvas, posicaoRealX0, posicaoRealY0, pagina)
                   elif(tipo=="release"):
                       
                       if(posicaoRealX0Canvas == self.initialPos[0] and posicaoRealY0Canvas == self.initialPos[1]): 
                            linkcustom = False
                            self.initialPos = None
                            listaquads = self.docInnerCanvas.find_withtag("link")
                            if(event!=None):
                                for quadelement in listaquads:
                                    bbox = self.docInnerCanvas.bbox(quadelement)
                                    if(self.docInnerCanvas.canvasx(event.x) >= bbox[0] and self.docInnerCanvas.canvasy(event.y) >= bbox[1] \
                                       and self.docInnerCanvas.canvasx(event.x) <= bbox[2] and self.docInnerCanvas.canvasy(event.y) <= bbox[3]):
                                        self.treeviewObs.selection_set(infoLaudo[pathpdfatual].linkscustom[quadelement][0][2])
                                        self.treeview_selection_obs(item=infoLaudo[pathpdfatual].linkscustom[quadelement][0][2])
                                        linkcustom = True
                            if(not linkcustom):
                                pagina = math.floor(posicaoRealY0Canvas / (infoLaudo[pathpdfatual].pixorgh *self.zoom_x*zoom))
                                for link in infoLaudo[pathpdfatual].links[pagina]:
                                     r = link['from']
                                     
                                     if(posicaoRealX0 >= r.x0 and posicaoRealX0 <= r.x1 and posicaoRealY0 >= r.y0 and posicaoRealY0 <= r.y1):
                                         if('page' in link):
                                             pageint = int(link['page'])
                                             to = link['to']
                                             
                                             if(pageint > 0 and pageint<=infoLaudo[pathpdfatual].len):
                                                 ondeir = (pageint) / infoLaudo[pathpdfatual].len + (to.y / (infoLaudo[pathpdfatual].pixorgh*infoLaudo[pathpdfatual].len))
                                                 self.positions[self.indiceposition] = (pathpdfatual, self.vscrollbar.get()[0])
                                                 self.indiceposition += 1
                                                 if(self.indiceposition>=10):
                                                     self.indiceposition = 0
                                                 self.docInnerCanvas.yview_moveto(ondeir)
                                                 if(str(pageint+1)!=self.pagVar.get()):
                                                     self.pagVar.set(str(pageint+1))
                                                 
                                             else:
                                                 atual = round((self.vscrollbar.get()[0]*infoLaudo[pathpdfatual].len))
                                                 
                                         elif('file' in link):
                                             arquivo = link['file']
                                             arquivosplit = arquivo.split("#")
                                             if plt == "Linux":
                                                 arquivo = str(arquivosplit[0]).replace("\\","/")
                                             elif plt=="Windows":
                                                 arquivo = str(arquivosplit[0]).replace("/","\\")
                                                 
                                             #if(not os.path.exists(arquivo)):
                                             #    popup_window('O arquivo \n <{}> \n não existe!'.format(arquivo) , False)
                                             
                                             if(len(arquivosplit)>1):
                                                 arquivo = os.path.join(Path(pathpdfatual).parent, arquivosplit[0])
                                                 if plt == "Linux":                                                     
                                                     arquivo = str(arquivo).replace("\\","/")
                                                 elif plt=="Windows":
                                                     arquivo = str(arquivo).replace("/","\\")
                                                 aprocurar = arquivosplit[1]
                                                 if(arquivo in infoLaudo):
                                                 
                                                     if(arquivo!=pathpdfatual):
                                                         try:
                                                             docatual.close()
                                                         except Exception as ex:
                                                             None
                                                         docatual=fitz.open(arquivo)
                                                     retorno = processDocXREF(arquivo, docatual, aprocurar)
                                                     
                                                     if(retorno!=None):
                                                 
                                                         to = retorno[3]
                                                         page_dest = retorno[1]
                                                         #to =  infoLaudo[arquivo].name_to_dest[arquivosplit[1]][3]
                                                         #page_dest =  infoLaudo[arquivo].name_to_dest[arquivosplit[1]][1]
                                                         if(arquivo!=pathpdfatual):
                                                             sobraEspaco = 0
                                                             if(self.docFrame.winfo_width() > infoLaudo[pathpdfatual].pixorgw * self.zoom_x * zoom):
                                                                 sobraEspaco = self.docInnerCanvas.winfo_x()  
                                                             self.docwidth = self.docOuterFrame.winfo_width()
                                                             
                                                             self.clearAllImages()
                                                             for i in range(minMaxLabels):
                                                                 processed_pages[i] = -1
                                                             pathpdfatual =arquivo  
                                                             self.labeldocname.config(text=os.path.basename(pathpdfatual))
                                                             self.totalPgg.config(text="/ "+str(infoLaudo[pathpdfatual].len))                    
                                                             if(infoLaudo[pathpdfatual].pixorgw*self.zoom_x*zoom>self.maiorw):
                                                                 self.maiorw = infoLaudo[pathpdfatual].pixorgw*self.zoom_x *zoom           
                                                             self.scrolly = round((infoLaudo[pathpdfatual].pixorgh*self.zoom_x*zoom), 16)*infoLaudo[pathpdfatual].len  - 35
                                                             self.docInnerCanvas.config(scrollregion=(sobraEspaco, 0, sobraEspaco+ (infoLaudo[pathpdfatual].pixorgw*zoom*self.zoom_x), self.scrolly))                
                                                             self.treeviewEqs.selection_set(pathpdfatual)
                                                         ondeir = (page_dest) / infoLaudo[pathpdfatual].len + (to / (infoLaudo[pathpdfatual].pixorgh*infoLaudo[pathpdfatual].len))
                                                         self.positions[self.indiceposition] = (pathpdfatual, self.vscrollbar.get()[0])
                                                         self.indiceposition += 1
                                                         if(self.indiceposition>=10):
                                                             self.indiceposition = 0
                                                         self.docInnerCanvas.yview_moveto(ondeir)
                                                         if(str(page_dest+1)!=self.pagVar.get()):
                                                             self.pagVar.set(str(page_dest+1))
                                                 else:
                                                     if plt == "Linux":
                                                         arquivo = str(arquivo).replace("\\","/")
                                                         pdfatualnorm = str(pathpdfatual).replace("\\","/")
                                                     elif plt=="Windows":
                                                         arquivo = str(arquivo).replace("/","\\")
                                                         pdfatualnorm = str(pathpdfatual).replace("/","\\")
                                                     
                                                     filepath = str(Path(os.path.normpath(os.path.join(Path(os.path.normpath(pdfatualnorm)).parent,arquivo))))
                                                     try:
                                                         
                                                         if platform.system() == 'Darwin':       # macOS
                                                             subprocess.call(('open', filepath), shell=True)
                                                         elif platform.system() == 'Windows':    # Windows
                                                             os.startfile(filepath)
                                                         else:           
                                                             #ommand ='xdg-open {filepath}'.format(filepath=filepath)
                                                             #ommand = ['xdg-open', filepath]
                                                             
                                                             
                                                             openfile = ['xdg-open', filepath]
                                                             try:
                                                                 
                                                                 myenv = dict(os.environ)  # make a copy of the environment
                                                                 HOME = os.path.expanduser("~")
    
                                                                 # Single directory where user-specific data files should be written
                                                                 XDG_DATA_HOME = os.environ.get("XDG_DATA_HOME", os.path.join(HOME, ".local", "share"))
                                                                
                                                                 # Single directory where user-specific configuration files should be written
                                                                 XDG_CONFIG_HOME = os.environ.get("XDG_CONFIG_HOME", os.path.join(HOME, ".config"))
                                                                
                                                                 # List of directories where data files should be searched.
                                                                 XDG_DATA_DIRS_LIST = [XDG_DATA_HOME] + "/usr/local/share:/usr/share".split(":")
                                                                 XDG_DATA_DIRS = ':'.join((t) for t in XDG_DATA_DIRS_LIST)
                                                                 # List of directories where configuration files should be searched.
                                                                 XDG_CONFIG_DIRS_LIST = [XDG_CONFIG_HOME] + "/etc/xdg".split(":")
                                                                 XDG_CONFIG_DIRS = ':'.join((t) for t in XDG_CONFIG_DIRS_LIST)
                                                                 #lp_key = 'LD_LIBRARY_PATH'  # for GNU/Linux and *BSD.
                                                                 myenv['XDG_DATA_HOME'] = XDG_DATA_HOME
                                                                 myenv['XDG_CONFIG_HOME'] = XDG_CONFIG_HOME
                                                                 myenv['XDG_DATA_DIRS'] = XDG_DATA_DIRS
                                                                 myenv['XDG_CONFIG_DIRS'] = XDG_CONFIG_DIRS
                                                                 
                                                                 subprocess.run(openfile, check=True, env=myenv)
                                                                 #outs, errs = proc.communicate()
                                                             except Exception as ex:
                                                                 webbrowser.open_new_tab(filepath)
                                                                 printlogexception(ex=ex)
                                                                 popup_window('O arquivo não possui um \nprograma associado para abertura!', False)
                                                         
                                                             
                                                     except Exception as ex:
                                                         printlogexception(ex=ex)
                                                         popup_window('O arquivo não possui um \nprograma associado para abertura!', False)
                                                              
                                             else:
                                                 if plt == "Linux":
                                                     arquivo = str(arquivo).replace("\\","/")
                                                     pdfatualnorm = str(pathpdfatual).replace("\\","/")
                                                 elif plt=="Windows":
                                                     arquivo = str(arquivo).replace("/","\\")
                                                     pdfatualnorm = str(pathpdfatual).replace("/","\\")
                                                 
                                                 filepath = str(Path(os.path.normpath(os.path.join(Path(os.path.normpath(pdfatualnorm)).parent,arquivo))))
                                                 try:
                                                     
                                                     if platform.system() == 'Darwin':       # macOS
                                                         subprocess.call(('open', filepath), shell=True)
                                                     elif platform.system() == 'Windows':    # Windows
                                                         os.startfile(filepath)
                                                     else:           
                                                         #ommand ='xdg-open {filepath}'.format(filepath=filepath)
                                                         #ommand = ['xdg-open', filepath]
                                                         
                                                         
                                                         openfile = ['xdg-open', filepath]
                                                         try:
                                                             
                                                             myenv = dict(os.environ)  # make a copy of the environment
                                                             HOME = os.path.expanduser("~")

                                                             # Single directory where user-specific data files should be written
                                                             XDG_DATA_HOME = os.environ.get("XDG_DATA_HOME", os.path.join(HOME, ".local", "share"))
                                                            
                                                             # Single directory where user-specific configuration files should be written
                                                             XDG_CONFIG_HOME = os.environ.get("XDG_CONFIG_HOME", os.path.join(HOME, ".config"))
                                                            
                                                             # List of directories where data files should be searched.
                                                             XDG_DATA_DIRS_LIST = [XDG_DATA_HOME] + "/usr/local/share:/usr/share".split(":")
                                                             XDG_DATA_DIRS = ':'.join((t) for t in XDG_DATA_DIRS_LIST)
                                                             # List of directories where configuration files should be searched.
                                                             XDG_CONFIG_DIRS_LIST = [XDG_CONFIG_HOME] + "/etc/xdg".split(":")
                                                             XDG_CONFIG_DIRS = ':'.join((t) for t in XDG_CONFIG_DIRS_LIST)
                                                             #lp_key = 'LD_LIBRARY_PATH'  # for GNU/Linux and *BSD.
                                                             myenv['XDG_DATA_HOME'] = XDG_DATA_HOME
                                                             myenv['XDG_CONFIG_HOME'] = XDG_CONFIG_HOME
                                                             myenv['XDG_DATA_DIRS'] = XDG_DATA_DIRS
                                                             myenv['XDG_CONFIG_DIRS'] = XDG_CONFIG_DIRS
                                                             
                                                             subprocess.run(openfile, check=True, env=myenv)
                                                             #outs, errs = proc.communicate()
                                                         except Exception as ex:
                                                             webbrowser.open_new_tab(filepath)
                                                             printlogexception(ex=ex)
                                                             popup_window('O arquivo não possui um \nprograma associado para abertura!', False)
                                                     
                                                         
                                                 except Exception as ex:
                                                     printlogexception(ex=ex)
                                                     popup_window('O arquivo não possui um \nprograma associado para abertura!', False)
                                         elif('uri' in link):
                                             webbrowser.open(link['uri'])
                       self.initialPos = None
                       
       except Exception as ex:
           printlogexception(ex=ex)

    def my_preexec_fn():
        os.setuid(os.getuid())
    def rightClickOnOpenableFile(self, event=None):
        posicaoRealY0Canvas = self.vscrollbar.get()[0] * (self.scrolly) + event.y
        posicaoRealX0Canvas = self.hscrollbar.get()[0] * (infoLaudo[pathpdfatual].pixorgw * self.zoom_x * zoom) + event.x
        posicaoRealY0 = (posicaoRealY0Canvas % (infoLaudo[pathpdfatual].pixorgh * self.zoom_x*zoom)) / (self.zoom_x*zoom)
        posicaoRealX0 = posicaoRealX0Canvas / (self.zoom_x*zoom)   
        pagina = math.floor(posicaoRealY0Canvas / (infoLaudo[pathpdfatual].pixorgh *self.zoom_x*zoom))
        for link in infoLaudo[pathpdfatual].links[pagina]:
             r = link['from']
             if(posicaoRealX0 >= r.x0 and posicaoRealX0 <= r.x1 and posicaoRealY0 >= r.y0 and posicaoRealY0 <= r.y1):
                 if('file' in link):
                     arquivo = link['file']
                     filepath = Path(os.path.normpath(os.path.join(Path(pathpdfatual).parent,arquivo)))
                     self.menuSaveas(os.path.basename(filepath), filepath, event)                     

        
    def pintarQuads(self, pagina, p0x, p0y, p1x, p1y, sobraEspaco, enhancetext=False, enhancearea=False, color=None, tag=["quad"], apagar=True, custom=False, altpressed=False, withborder=True, alt=True):
        global zoom, listaZooms, posicaoZoom, doc4
        if(custom):
            margemsup = 0
            margeminf = infoLaudo[pathpdfatual].pixorgh
            margemesq = 0
            margemdir = infoLaudo[pathpdfatual].pixorgw
        else:
            margemsup = (infoLaudo[pathpdfatual].mt/25.4)*72
            margeminf = infoLaudo[pathpdfatual].pixorgh-((infoLaudo[pathpdfatual].mb/25.4)*72)
            margemesq = (infoLaudo[pathpdfatual].me/25.4)*72
            margemdir = infoLaudo[pathpdfatual].pixorgw-((infoLaudo[pathpdfatual].md/25.4)*72)
        p0x = max(p0x, margemesq)
        p0y = max(p0y, margemsup+1)
        p1x = min(p1x, margemdir)
        p1y = min(p1y, margeminf-1)
    
        try:
            zoom = listaZooms[posicaoZoom]
            infoLaudo[pathpdfatual].retangulosDesenhados[pagina] = {}            
            if(enhancetext):                
                infoLaudo[pathpdfatual].retangulosDesenhados[pagina]['text']=[]
                for block in infoLaudo[pathpdfatual].mapeamento[pagina]:
                    x0b = block[0]
                    y0b = block[1]
                    x1b = block[2]
                    y1b = block[3]
                    if(self.altpressed and alt):
                        
                        for line in infoLaudo[pathpdfatual].mapeamento[pagina][block]:
                            x0l = line[0] 
                            y0l = line[1]
                            x1l = line[2] 
                            y1l = line[3] 
                            if(y1l < p0y or y0l > p1y):
                                continue
                            x0 = min(p0x, p1x)
                            x1 = max(p0x, p1x)
                            rects = []
                            for quad in infoLaudo[pathpdfatual].mapeamento[pagina][block][line]:
                                qtosrects = len(rects)
                                if( (quad[0]+quad[2])/2 <= x1 and (quad[0]+quad[2])/2 >= x0 and quad[3] >= p0y and quad[1] <= p1y):                                    
                                    if(qtosrects==0):
                                        rect = Rect()
                                        rect.x0 = quad[0]
                                        rect.y0 = quad[1]
                                        rect.x1 = quad[2]
                                        rect.y1 = quad[3]
                                        rect.char.append(quad[4])
                                        rects.append(rect)
                                    else:
                                        ultimorect = rects[qtosrects-1]
                                        if(ultimorect.x1+100 >= quad[0]):
                                            ultimorect.char.append(quad[4])
                                            ultimorect.x1 = quad[2]
                                        else:
                                            rect = Rect()
                                            rect.x0 = quad[0]
                                            rect.y0 = quad[1]
                                            rect.x1 = quad[2]
                                            rect.y1 = quad[3]
                                            rect.char.append(quad[4])
                                            rects.append(rect)
                            for r in rects:
                                deslocy = pagina * infoLaudo[pathpdfatual].pixorgh * self.zoom_x*zoom
                                x0k = math.floor(r.x0*self.zoom_x*zoom +sobraEspaco)
                                x1k = math.ceil(r.x1*self.zoom_x*zoom +sobraEspaco)
                                y0k = math.ceil(((r.y0*self.zoom_x*zoom)  +deslocy))
                                y1k = math.ceil(((r.y1*self.zoom_x*zoom)  +deslocy))
                                r.image = self.create_rectanglex(min(x0k, x1k), min(y0k, y1k), max(x0k, x1k), max(y0k,y1k), color, withborder=withborder)                                
                                r.idrect = self.docInnerCanvas.create_image(min(x0k, x1k), min(y0k, y1k), image=r.image, anchor='nw', tags=(tag))
                                self.addImagetoList(tag[0], r.image)                                
                                infoLaudo[pathpdfatual].retangulosDesenhados[pagina]['text'].append((line, r))
                    else:
                        linetop = True
                        linebottom = True
                        for line in infoLaudo[pathpdfatual].mapeamento[pagina][block]:
                            x0l = line[0] 
                            y0l = line[1]
                            x1l = line[2] 
                            y1l = line[3]
                            if(y1l < p0y):
                                continue
                            if(y0l > p1y):
                                break                            
                            if(p0y > y0l and p1y < y1l):                               
                                x0 = min(p0x, p1x)
                                x1 = max(p0x, p1x)
                                rects = []
                                for quad in infoLaudo[pathpdfatual].mapeamento[pagina][block][line]:
                                    qtosrects = len(rects)
                                    if( quad[2] <= x1 and (quad[0]+quad[2])/2 >= x0):                                        
                                        if(qtosrects==0):
                                            rect = Rect()
                                            rect.x0 = quad[0]
                                            rect.y0 = quad[1]
                                            rect.x1 = quad[2]
                                            rect.y1 = quad[3]
                                            rect.char.append(quad[4])
                                            rects.append(rect)
                                        else:
                                            ultimorect = rects[qtosrects-1]
                                            if(ultimorect.x1+100 >= quad[0]):
                                                ultimorect.char.append(quad[4])
                                                ultimorect.x1 = quad[2]
                                            else:
                                                rect = Rect()
                                                rect.x0 = quad[0]
                                                rect.y0 = quad[1]
                                                rect.x1 = quad[2]
                                                rect.y1 = quad[3]
                                                rect.char.append(quad[4])
                                                rects.append(rect)
                                for r in rects:
                                    deslocy = pagina * infoLaudo[pathpdfatual].pixorgh * self.zoom_x*zoom
                                    deslocx =  self.hscrollbar.get()[0] * self.canvasw
        
                                    x0k = math.floor(r.x0*self.zoom_x*zoom +sobraEspaco)
                                    x1k = math.ceil(r.x1*self.zoom_x*zoom +sobraEspaco)
                                    y0k = math.ceil(((r.y0*self.zoom_x*zoom)  +deslocy))
                                    y1k = math.ceil(((r.y1*self.zoom_x*zoom)  +deslocy))
                                    image = self.create_rectanglex(min(x0k, x1k), min(y0k, y1k), max(x0k, x1k), max(y0k,y1k), color, withborder=withborder)
                                    r.idrect = self.docInnerCanvas.create_image(min(x0k, x1k), min(y0k, y1k), image=image, anchor='nw', tags=(tag))
                                    self.addImagetoList(tag[0], image)
                                    infoLaudo[pathpdfatual].retangulosDesenhados[pagina]['text'].append((line, r))
                            elif(p0y < y0l and p1y > y1l):                                
                                rects = []
                                for quad in infoLaudo[pathpdfatual].mapeamento[pagina][block][line]:
                                    qtosrects = len(rects) 
                                    if(qtosrects==0):
                                        rect = Rect()
                                        rect.x0 = quad[0]
                                        rect.y0 = quad[1]
                                        rect.x1 = quad[2]
                                        rect.y1 = quad[3]
                                        rect.char.append(quad[4])
                                        rects.append(rect)
                                    else:
                                        ultimorect = rects[qtosrects-1]
                                        if(ultimorect.x1+100 >= quad[0]):
                                            ultimorect.char.append(quad[4])
                                            ultimorect.x1 = quad[2]
                                        else:
                                            rect = Rect()
                                            rect.x0 = quad[0]
                                            rect.y0 = quad[1]
                                            rect.x1 = quad[2]
                                            rect.y1 = quad[3]
                                            rect.char.append(quad[4])
                                            rects.append(rect)
                                for r in rects:
                                    deslocy = pagina * infoLaudo[pathpdfatual].pixorgh * self.zoom_x*zoom
                                    deslocx =  self.hscrollbar.get()[0] * self.canvasw        
                                    x0k = math.floor(r.x0*self.zoom_x*zoom +sobraEspaco)
                                    x1k = math.ceil(r.x1*self.zoom_x*zoom+sobraEspaco)
                                    y0k = math.ceil(((r.y0*self.zoom_x*zoom)  +deslocy))
                                    y1k = math.ceil(((r.y1*self.zoom_x*zoom)  +deslocy))
                                    image = self.create_rectanglex(min(x0k, x1k), min(y0k, y1k), max(x0k, x1k), max(y0k,y1k), color, withborder=withborder)
                                    r.idrect = self.docInnerCanvas.create_image(min(x0k, x1k), min(y0k, y1k), image=image, anchor='nw', tags=(tag))
                                    self.addImagetoList(tag[0], image)
                                    infoLaudo[pathpdfatual].retangulosDesenhados[pagina]['text'].append((line, r))
                            elif(p0y <= y1l and p1y >= y1l):
                                if(True):
                                    linetop = False
                                    rects = []
                                    for quad in infoLaudo[pathpdfatual].mapeamento[pagina][block][line]:
                                        qtosrects = len(rects)
                                        if((quad[0]+quad[2])/2 >= p0x):                                        
                                            if(qtosrects==0):
                                                rect = Rect()
                                                rect.x0 = quad[0]
                                                rect.y0 = quad[1]
                                                rect.x1 = quad[2]
                                                rect.y1 = quad[3]
                                                rect.char.append(quad[4])
                                                rects.append(rect)
                                            else:
                                                ultimorect = rects[qtosrects-1]
                                                if(ultimorect.x1+100 >= quad[0]):
                                                    ultimorect.char.append(quad[4])
                                                    ultimorect.x1 = quad[2]
                                                else:
                                                    rect = Rect()
                                                    rect.x0 = quad[0]
                                                    rect.y0 = quad[1]
                                                    rect.x1 = quad[2]
                                                    rect.y1 = quad[3]
                                                    rect.char.append(quad[4])
                                                    rects.append(rect)
                                    for r in rects:
                                        deslocy = pagina * infoLaudo[pathpdfatual].pixorgh * self.zoom_x*zoom                                    
                                        x0k = math.floor(r.x0*self.zoom_x*zoom +sobraEspaco)
                                        x1k = math.ceil(r.x1*self.zoom_x*zoom+sobraEspaco )
                                        y0k = math.ceil(((r.y0*self.zoom_x*zoom)  +deslocy))
                                        y1k = math.ceil(((r.y1*self.zoom_x*zoom)  +deslocy))
                                        image = self.create_rectanglex(min(x0k, x1k), min(y0k, y1k), max(x0k, x1k), max(y0k,y1k), color, withborder=withborder)
                                        r.idrect = self.docInnerCanvas.create_image(min(x0k, x1k), min(y0k, y1k), image=image, anchor='nw', tags=(tag))
                                        self.addImagetoList(tag[0], image)
                                        infoLaudo[pathpdfatual].retangulosDesenhados[pagina]['text'].append((line, r))   
                            elif(p1y >= y0l and p0y <= y0l):
                                if(True):
                                    linebottom = False
                                    rects = []
                                    for quad in infoLaudo[pathpdfatual].mapeamento[pagina][block][line]:
                                        qtosrects = len(rects)
                                        if((quad[0]+quad[2])/2 <= p1x):                                        
                                            if(qtosrects==0):
                                                rect = Rect()
                                                rect.x0 = quad[0]
                                                rect.y0 = quad[1]
                                                rect.x1 = quad[2]
                                                rect.y1 = quad[3]
                                                rect.char.append(quad[4])
                                                rects.append(rect)
                                            else:
                                                ultimorect = rects[qtosrects-1]
                                                if(ultimorect.x1+100 >= quad[0]):
                                                    ultimorect.char.append(quad[4])
                                                    ultimorect.x1 = quad[2]
                                                else:
                                                    rect = Rect()
                                                    rect.x0 = quad[0]
                                                    rect.y0 = quad[1]
                                                    rect.x1 = quad[2]
                                                    rect.y1 = quad[3]
                                                    rect.char.append(quad[4])
                                                    rects.append(rect)
                                    for r in rects:
                                        deslocy = pagina * infoLaudo[pathpdfatual].pixorgh * self.zoom_x*zoom                                    
                                        x0k = math.floor(r.x0*self.zoom_x*zoom +sobraEspaco)
                                        x1k = math.ceil(r.x1*self.zoom_x*zoom+sobraEspaco )
                                        y0k = math.ceil(((r.y0*self.zoom_x*zoom)  +deslocy))
                                        y1k = math.ceil(((r.y1*self.zoom_x*zoom)  +deslocy))
                                        image = self.create_rectanglex(min(x0k, x1k), min(y0k, y1k), max(x0k, x1k), max(y0k,y1k), color, withborder=withborder)
                                        r.idrect = self.docInnerCanvas.create_image(min(x0k, x1k), min(y0k, y1k), image=image, anchor='nw', tags=(tag))
                                        self.addImagetoList(tag[0], image)
                                        infoLaudo[pathpdfatual].retangulosDesenhados[pagina]['text'].append((line, r))
            elif(enhancearea):
                infoLaudo[pathpdfatual].retangulosDesenhados[pagina]['areaSelection'] = []
                deslocy = pagina * infoLaudo[pathpdfatual].pixorgh * self.zoom_x*zoom
                rect = Rect()
                rect.x0 = p0x
                rect.y0 = p0y
                rect.x1 = p1x
                rect.y1 = p1y    
                x0k = math.floor(rect.x0*self.zoom_x*zoom+ sobraEspaco)
                x1k = math.ceil(rect.x1*self.zoom_x*zoom+ sobraEspaco)
                y0k = math.ceil(((rect.y0*self.zoom_x*zoom)  +deslocy))
                y1k = math.ceil(((rect.y1*self.zoom_x*zoom)  +deslocy))
                image = self.create_rectanglex(min(x0k, x1k), min(y0k, y1k), max(x0k, x1k), max(y0k,y1k), color, withborder=withborder)
                rect.idrect = self.docInnerCanvas.create_image(min(x0k, x1k), min(y0k, y1k), image=image, anchor='nw', tags=(tag))
                self.addImagetoList(tag[0], image)
                infoLaudo[pathpdfatual].retangulosDesenhados[pagina]['areaSelection'].append((None, rect))
            elif(self.areaselectionActiveCustom):
                infoLaudo[pathpdfatual].retangulosDesenhados[pagina]['areaSelection'] = []
                deslocy = pagina * infoLaudo[pathpdfatual].pixorgh * self.zoom_x*zoom
                rect = Rect()
                rect.x0 = p0x
                rect.y0 = p0y
                rect.x1 = p1x
                rect.y1 = p1y    
                x0k = math.floor(rect.x0*self.zoom_x*zoom+ sobraEspaco)
                x1k = math.ceil(rect.x1*self.zoom_x*zoom+ sobraEspaco)
                y0k = math.ceil(((rect.y0*self.zoom_x*zoom)  +deslocy))
                y1k = math.ceil(((rect.y1*self.zoom_x*zoom)  +deslocy))
                image = self.create_rectanglex(min(x0k, x1k), min(y0k, y1k), max(x0k, x1k), max(y0k,y1k), color, withborder=withborder)
                rect.idrect = self.docInnerCanvas.create_image(min(x0k, x1k), min(y0k, y1k), image=image, anchor='nw', tags=(tag))
                self.addImagetoList(tag[0], image)
                infoLaudo[pathpdfatual].retangulosDesenhados[pagina]['areaSelection'].append((None, rect))
        except Exception as ex:
            printlogexception(ex=ex)
        

    def prepararParaQuads(self, pagina, posicaoRealX0, posicaoRealY0, posicaoRealX1, posicaoRealY1, \
                          color=(21, 71, 150, 85),tag=["quad"], apagar=True, enhancetext=False, enhancearea=False, withborder=True, alt=True, first=True):
        global zoom, doc4
        margemsup = (infoLaudo[pathpdfatual].mt/25.4)*72
        margeminf = infoLaudo[pathpdfatual].pixorgh-((infoLaudo[pathpdfatual].mb/25.4)*72)
        margemesq = (infoLaudo[pathpdfatual].me/25.4)*72
        margemdir = infoLaudo[pathpdfatual].pixorgw-((infoLaudo[pathpdfatual].md/25.4)*72)
        
            
        if(pagina not in infoLaudo[pathpdfatual].mapeamento):
            if(first or pagina in processed_pages):
                self.afterquads = root.after(500, lambda: self.prepararParaQuads( pagina, posicaoRealX0, posicaoRealY0, posicaoRealX1, \
                                                                         posicaoRealY1, color=color,tag=tag, apagar=apagar, enhancetext=enhancetext, enhancearea=enhancearea, withborder=withborder, alt=alt, first=False))
       
        else:  
            if("enhanceobs" in tag[0]):
                self.docInnerCanvas.delete(tag[1])
            if(posicaoRealX0 <= posicaoRealX1 and posicaoRealY0 <= posicaoRealY1):
                p0x = posicaoRealX0
                p0y = posicaoRealY0
                p1x = posicaoRealX1
                p1y = posicaoRealY1
            elif(posicaoRealX0 > posicaoRealX1 and posicaoRealY0 <= posicaoRealY1):                
                p0x = posicaoRealX0
                p0y = posicaoRealY0
                p1x = posicaoRealX1
                p1y = posicaoRealY1
            elif(posicaoRealX0 <= posicaoRealX1 and posicaoRealY0 > posicaoRealY1):
                p0x = posicaoRealX1
                p0y = posicaoRealY1
                p1x = posicaoRealX0
                p1y = posicaoRealY0
            elif (posicaoRealX0 > posicaoRealX1 and posicaoRealY0 > posicaoRealY1):
                p0x = posicaoRealX1
                p0y = posicaoRealY1
                p1x = posicaoRealX0
                p1y = posicaoRealY0

            sobraEspaco = self.docInnerCanvas.winfo_x()           
            p0x = max(p0x, margemesq)
            p0y = max(p0y, margemsup)
            p1x = min(p1x, margemdir)
            p1y = min(p1y, margeminf)
            self.pintarQuads(pagina=pagina, p0x=p0x, p0y=p0y, p1x=p1x, p1y=p1y, sobraEspaco=sobraEspaco, color=color, apagar=apagar, \
                             custom=False, tag=tag, altpressed=self.altpressed and alt, enhancetext=enhancetext, enhancearea=enhancearea, withborder=withborder, alt=alt)
        
        
        
    def _selectingText(self, evento):
        global infoLaudo, minMaxLabels, zoom, pathpdfatual
        if(self.selectionActive or self.areaselectionActive or self.areaselectionActiveCustom):            
            if(isinstance(evento.widget, tkinter.Canvas) and self.initialPos==None):
                None
                    
            if(self.initialPos!=None and isinstance(evento.widget, tkinter.Canvas)):
                self.docInnerCanvas.delete("simplesearch")
                self.docInnerCanvas.delete("quad")
                self.docInnerCanvas.delete("obsitem")
                self.clearSomeImages(["simplesearch", "quad", "obsitem"])
                posicaoRealY1Canvas = self.vscrollbar.get()[0] * (self.scrolly) + evento.y
                posicaoRealX1Canvas = self.hscrollbar.get()[0] * (infoLaudo[pathpdfatual].pixorgw * self.zoom_x * zoom) + evento.x
                posicaoRealY1 = (posicaoRealY1Canvas % (infoLaudo[pathpdfatual].pixorgh * self.zoom_x*zoom)) / (self.zoom_x*zoom)
                posicaoRealX1 = posicaoRealX1Canvas / (self.zoom_x*zoom)
                pagina = math.floor(posicaoRealY1Canvas / (infoLaudo[pathpdfatual].pixorgh *self.zoom_x*zoom))
                pp = min(self.initialPos[4],pagina)
                up = max(self.initialPos[4],pagina)
                if(self.areaselectionActiveCustom):
                    #desabilitado
                    self.prepararParaQuads(pp, posicaoRealX0=self.initialPos[2], posicaoRealY0=self.initialPos[3], posicaoRealX1=posicaoRealX1, posicaoRealY1=posicaoRealY1, \
                          color=(21, 71, 150, 85),tag=["quad"], apagar=True, enhancetext=False, enhancearea=True)
                else:
                    
                    if(pagina < 0 or pagina >= infoLaudo[pathpdfatual].len):
                        return
                    origemx = 0
                    origemx1 = infoLaudo[pathpdfatual].pixorgw
                    if(self.altpressed or self.areaselectionActive):
                        origemx=self.initialPos[2]
                        origemx1=posicaoRealX1
                    if(self.initialPos[4] < pagina):
                        for p in range(self.initialPos[4], pagina+1):                   
                            if(self.initialPos[4] < p):
                                if(p < pagina):
                                     self.prepararParaQuads(p, posicaoRealX0=origemx, posicaoRealY0=self.initialPos[3], posicaoRealX1=origemx1, posicaoRealY1=infoLaudo[pathpdfatual].pixorgh, \
                                                            color=(21, 71, 150, 85),tag=["quad"], apagar=True, enhancetext=self.selectionActive, enhancearea=self.areaselectionActive)
                                    
                                else:
                                    self.prepararParaQuads(p, posicaoRealX0=origemx, posicaoRealY0=0, posicaoRealX1=posicaoRealX1, posicaoRealY1=posicaoRealY1, \
                                                            color=(21, 71, 150, 85),tag=["quad"], apagar=True, enhancetext=self.selectionActive, enhancearea=self.areaselectionActive)
                                    
                            else:
                                self.prepararParaQuads(p, posicaoRealX0=self.initialPos[2], posicaoRealY0=self.initialPos[3], posicaoRealX1=origemx1, \
                                                       posicaoRealY1=infoLaudo[pathpdfatual].pixorgh, color=(21, 71, 150, 85),tag=["quad"], \
                                                           apagar=True, enhancetext=self.selectionActive, enhancearea=self.areaselectionActive)

                    elif(self.initialPos[4] > pagina):
                        for p in range(self.initialPos[4], pagina-1, -1):
                            if(p > pagina):
                                if(p < self.initialPos[4]):
                                    self.prepararParaQuads(p, posicaoRealX0=origemx, posicaoRealY0=0, posicaoRealX1=origemx1, posicaoRealY1=infoLaudo[pathpdfatual].pixorgh, \
                                                            color=(21, 71, 150, 85),tag=["quad"], apagar=True, enhancetext=False, enhancearea=True)
                                    
                                else:
                                    self.prepararParaQuads(p, posicaoRealX0=origemx, posicaoRealY0=0, posicaoRealX1=self.initialPos[2], \
                                                       posicaoRealY1=self.initialPos[3], color=(21, 71, 150, 85),tag=["quad"], \
                                                           apagar=True, enhancetext=self.selectionActive, enhancearea=self.areaselectionActive)
                                    
                            else:
                                self.prepararParaQuads(p, posicaoRealX0=origemx, posicaoRealY0=infoLaudo[pathpdfatual].pixorgh, posicaoRealX1=posicaoRealX1, \
                                                       posicaoRealY1=posicaoRealY1, color=(21, 71, 150, 85),tag=["quad"], \
                                                           apagar=True, enhancetext=self.selectionActive, enhancearea=self.areaselectionActive)
                    else:
                        
                        self.prepararParaQuads(pagina, posicaoRealX0=self.initialPos[2], posicaoRealY0=self.initialPos[3], \
                                               posicaoRealX1=posicaoRealX1, posicaoRealY1=posicaoRealY1, color=(21, 71, 150, 85),tag=["quad"], \
                                                           apagar=True, enhancetext=self.selectionActive, enhancearea=self.areaselectionActive)
                    
 
            else:
                None
        else:
            self.docInnerCanvas.scan_dragto(evento.x, evento.y, gain=1)
            
        
        
    def doubleClickSelection(self, evento):
         global infoLaudo, zoom, listaZooms, posicaoZoom, pathpdfatual
         zoom = listaZooms[posicaoZoom]
         if(isinstance(evento.widget, tkinter.Canvas)):
                self.docInnerCanvas.delete("simplesearch")
                self.docInnerCanvas.delete("quad")
                self.docInnerCanvas.delete("obsitem")
                self.clearSomeImages(["simplesearch", "quad", "obsitem"])
                posicaoRealY0Canvas = self.vscrollbar.get()[0] * (self.scrolly) + evento.y
                posicaoRealX0Canvas = self.hscrollbar.get()[0] * (infoLaudo[pathpdfatual].pixorgw * self.zoom_x * zoom) + evento.x

                posicaoRealY0 = (posicaoRealY0Canvas % (infoLaudo[pathpdfatual].pixorgh * self.zoom_x*zoom)) / (self.zoom_x*zoom)
                posicaoRealX0 = posicaoRealX0Canvas / (self.zoom_x*zoom)
                pagina = math.floor(posicaoRealY0Canvas / (infoLaudo[pathpdfatual].pixorgh *self.zoom_x*zoom))
                p0x = posicaoRealX0
                p0y = posicaoRealY0
                p1x = posicaoRealX0
                p1y = posicaoRealY0
                sobraEspaco = 0
                if(self.docFrame.winfo_width() > infoLaudo[pathpdfatual].pixorgw * self.zoom_x * zoom):
                    sobraEspaco = self.docInnerCanvas.winfo_x()
                if(self.selectionActive):
                    rect = None 
                    for block in infoLaudo[pathpdfatual].mapeamento[pagina]:
                        x0b = block[0]
                        y0b = block[1]
                        x1b = block[2]
                        y1b = block[3]
                        if(y0b <= p0y and y1b >= p1y):
                            for line in infoLaudo[pathpdfatual].mapeamento[pagina][block]:
                                x0l = line[0]
                                y0l = line[1]
                                x1l = line[2]
                                y1l = line[3]                                
                                if(y0l <= p0y and y1l >= p1y and x0l <= p0x and x1l >=p1x):
                                    for quad in infoLaudo[pathpdfatual].mapeamento[pagina][block][line]:
                                        if(quad[4] == " "):   
                                            if(quad[0] <= p0x):
                                                rect = None
                                            else:
                                                break
                                        else:
                                            if(rect==None):
                                                rect = Rect()
                                                rect.x0 = quad[0]
                                                rect.y0 = quad[1]
                                                rect.y1 = quad[3]
                                                rect.x1 = quad[2]
                                            rect.char.append(quad[4])
                                            rect.x0 = min(rect.x0, quad[0])
                                            rect.y0 = min(rect.y0, quad[1])
                                            rect.x1 = max(rect.x1, quad[2])
                                            rect.y1 = max(rect.y1, quad[3])
                    if(rect!=None):
                        deslocy = pagina * infoLaudo[pathpdfatual].pixorgh * self.zoom_x*zoom
                        x0k = math.floor(rect.x0*self.zoom_x*zoom + sobraEspaco)
                        x1k = math.ceil(rect.x1*self.zoom_x*zoom + sobraEspaco)
                        y0k = math.ceil(((rect.y0*self.zoom_x*zoom)  +deslocy))
                        y1k = math.ceil(((rect.y1*self.zoom_x*zoom)  +deslocy))
                        rect.image = self.create_rectanglex(min(x0k, x1k), min(y0k, y1k), max(x0k, x1k), max(y0k,y1k), (21, 71, 150, 85), withborder=False)
                        rect.idrect = self.docInnerCanvas.create_image(min(x0k, x1k), min(y0k, y1k), image=rect.image, anchor='nw', tags=("quad"))
                        self.addImagetoList("quad", rect.image)
                        infoLaudo[pathpdfatual].retangulosDesenhados[pagina] = {}
                        infoLaudo[pathpdfatual].retangulosDesenhados[pagina]['text'] = []
                        infoLaudo[pathpdfatual].retangulosDesenhados[pagina]['text'].append((line, rect))

    def create_rectanglex(self, x1, y1, x2, y2, color, link=False, withborder=True, **kwargs):
        try:
            if(link):
                dst = Image.new('RGBA', (x2-x1, y2-y1))
                border1 = Image.new('RGBA', (x2-x1, 1), (35, 129, 166,255)) 
                image = Image.new('RGBA', (x2-x1, y2-y1), color) 
                dst.paste(image, (0, 0))
                dst.paste(border1, (0,  y2-y1-1))
                return ImageTk.PhotoImage(dst)
            elif(not withborder):
                dst = Image.new('RGBA', (x2-x1, y2-y1))            
                image = Image.new('RGBA', (x2-x1, y2-y1), color)
                dst.paste(image, (0, 0))         
                return ImageTk.PhotoImage(dst)
            elif(withborder):
                dst = Image.new('RGBA', (x2-x1, y2-y1))            
                bordertopbottom = Image.new('RGBA', (x2-x1, 1), (0, 0, 0,255)) 
                bordersides = Image.new('RGBA', (1, (y2-y1)), (0, 0, 0,255)) 
                image = Image.new('RGBA', (x2-x1, y2-y1), color)
                dst.paste(image, (0, 0))
                dst.paste(bordertopbottom, (0,  y2-y1-1))
                dst.paste(bordertopbottom, (0,  0))
                dst.paste(bordersides, (x2-x1-1,  0))
                dst.paste(bordersides, (0,  0))            
                return ImageTk.PhotoImage(dst)
        except Exception as ex:
            self.docInnerCanvas.delete('quad')
            self.docInnerCanvas.delete('link')
            self.docInnerCanvas.delete('simplesearch')
            self.docInnerCanvas.delete('obsitem')
            #self.docInnerCanvas.delete('enhanceobs')
                 
        

                        
    def _clearClick(self, event):
        self.initialPos = None
    
    def zoomx(self, event=None, tipozoom=None):
        global processed_pages, minMaxLabels, zoom, listaZooms, posicaoZoom, divididoEm, pathpdfatual, realce, lockzoom
        
        if((tipozoom=='plus' and posicaoZoom < len(listaZooms)-1) or (tipozoom=='minus' and posicaoZoom > 0)):
            self.winfox = self.docInnerCanvas.winfo_x()
            valor = self.vscrollbar.get()[0]
            for k in range(minMaxLabels):
                self.docInnerCanvas.itemconfig(self.ininCanvasesid[k], image = None)
                self.tkimgs[k] = None
            

            #infoLaudo[pathpdfatual].ultimaPosicao = (listaZooms[posicaoZoom+1] * infoLaudo[pathpdfatual].ultimaPosicao) / listaZooms[posicaoZoom]
            oldzoom = listaZooms[posicaoZoom]
            if(tipozoom=='plus'):
                posicaoZoom += 1
            else:
                posicaoZoom -= 1
            zoom = listaZooms[posicaoZoom]

            self.mat = fitz.Matrix(self.zoom_x*zoom, self.zoom_x*zoom)
            
            sobraEspacoold = self.docInnerCanvas.winfo_x()
            self.docInnerCanvas.config(width= (infoLaudo[pathpdfatual].pixorgw * self.zoom_x * zoom))
            for i in range(minMaxLabels):
                processed_pages[i] = -1   
            self.docInnerCanvas.delete(self.fakeLines[0])
            self.docInnerCanvas.delete(self.fakeLines[1])
            self.fakeLines[0] = self.docInnerCanvas.create_line(0,0, max(self.docFrame.winfo_width(), infoLaudo[pathpdfatual].pixorgw*self.zoom_x*zoom), 0, width=5, fill=self.bg)
            self.fakeLines[1] = self.docInnerCanvas.create_line(0,infoLaudo[pathpdfatual].pixorgh * self.zoom_x * zoom, max(self.docFrame.winfo_width(), \
                                                            infoLaudo[pathpdfatual].pixorgh*self.zoom_x*zoom), \
                                                            infoLaudo[pathpdfatual].pixorgh * self.zoom_x * zoom, width=5, fill=self.bg) 
            sobraEspaco = self.docInnerCanvas.winfo_x()
            self.docInnerCanvas.configure(scrollregion = (sobraEspaco,0,sobraEspaco+infoLaudo[pathpdfatual].pixorgw * self.zoom_x*zoom, \
                                                          infoLaudo[pathpdfatual].pixorgh*self.zoom_x*zoom*infoLaudo[pathpdfatual].len))
            self.docInnerCanvas.yview_moveto(valor)
            
            self.scrolly = round((infoLaudo[pathpdfatual].pixorgh*self.zoom_x*zoom), 16)*infoLaudo[pathpdfatual].len  - 35
            try:  
                listasimplesearch = self.docInnerCanvas.find_withtag("simplesearch")
                listaquads = self.docInnerCanvas.find_withtag("quad")
                listalinks = self.docInnerCanvas.find_withtag("link")
                listaobs = self.docInnerCanvas.find_withtag("obsitem")
                self.clearSomeImages(["simplesearch", "quad", "link", "obsitem"])
                for quadelement in listasimplesearch:
                    box = (self.docInnerCanvas.bbox(quadelement))
                    pagina = math.floor(box[1]/(infoLaudo[pathpdfatual].pixorgh * self.zoom_x*oldzoom))
                    deslocy = pagina * infoLaudo[pathpdfatual].pixorgh * self.zoom_x*zoom
                    deslocyold = pagina * infoLaudo[pathpdfatual].pixorgh * self.zoom_x*oldzoom
                    x0novo = round(((box[0]-sobraEspacoold)/(self.zoom_x*oldzoom))*self.zoom_x*zoom + sobraEspaco)
                    x1novo = round(((box[2]-sobraEspacoold)/(self.zoom_x*oldzoom))*self.zoom_x*zoom + sobraEspaco)
                    y0novo =round(((box[1]-deslocyold)/(self.zoom_x*oldzoom))*self.zoom_x*zoom  +deslocy)
                    y1novo = round(((box[3]-deslocyold)/(self.zoom_x*oldzoom))*self.zoom_x*zoom  +deslocy)                       
                    tempimagem = (self.create_rectanglex(x0novo, y0novo, x1novo, y1novo, self.color, link=False))                    
                    self.docInnerCanvas.itemconfig(quadelement, image=tempimagem)#
                    self.addImagetoList("simplesearch", tempimagem)
                    coords = self.docInnerCanvas.coords(quadelement)
                    dx = x0novo -coords[0]
                    dy = y0novo -coords[1]
                    self.docInnerCanvas.move(quadelement, dx, dy)                    
                for quadelement in listaquads:                    
                    box = (self.docInnerCanvas.bbox(quadelement))  
                    
                    pagina = math.floor(box[1]/((infoLaudo[pathpdfatual].pixorgh * self.zoom_x*oldzoom)))
                    deslocy = pagina * infoLaudo[pathpdfatual].pixorgh * self.zoom_x*zoom
                    deslocyold = pagina * infoLaudo[pathpdfatual].pixorgh * self.zoom_x*oldzoom
                    x0novo = round(((box[0]-sobraEspacoold)/(self.zoom_x*oldzoom))*self.zoom_x*zoom + sobraEspaco)
                    x1novo = round(((box[2]-sobraEspacoold)/(self.zoom_x*oldzoom))*self.zoom_x*zoom + sobraEspaco)
                    y0novo = round(((box[1]-deslocyold)/(self.zoom_x*oldzoom))*self.zoom_x*zoom  +deslocy)
                    y1novo = round(((box[3]-deslocyold)/(self.zoom_x*oldzoom))*self.zoom_x*zoom  +deslocy)                       
                    tempimagem = (self.create_rectanglex(x0novo, y0novo, x1novo, y1novo, (21, 71, 150, 85), link=False))
                    self.docInnerCanvas.itemconfig(quadelement, image=tempimagem)
                    self.addImagetoList("quad", tempimagem)
                    coords = self.docInnerCanvas.coords(quadelement)
                    dx = x0novo -coords[0]
                    dy = y0novo -coords[1]
                    self.docInnerCanvas.move(quadelement, dx, dy) 
                for quadelement in listalinks:
                    box = (self.docInnerCanvas.bbox(quadelement))
                    pagina = math.floor(box[1]/((infoLaudo[pathpdfatual].pixorgh * self.zoom_x*oldzoom)))
                    deslocy = pagina * infoLaudo[pathpdfatual].pixorgh * self.zoom_x*zoom
                    deslocyold = pagina * infoLaudo[pathpdfatual].pixorgh * self.zoom_x*oldzoom
                    x0novo = round(((box[0]-sobraEspacoold)/(self.zoom_x*oldzoom))*self.zoom_x*zoom + sobraEspaco)
                    x1novo = round(((box[2]-sobraEspacoold)/(self.zoom_x*oldzoom))*self.zoom_x*zoom + sobraEspaco)
                    y0novo = round(((box[1]-deslocyold)/(self.zoom_x*oldzoom))*self.zoom_x*zoom  +deslocy)
                    y1novo = round(((box[3]-deslocyold)/(self.zoom_x*oldzoom))*self.zoom_x*zoom  +deslocy)                       
                    tempimagem = (self.create_rectanglex(x0novo, y0novo, x1novo, y1novo, (175, 200, 240, 95), link=True))
                    self.addImagetoList("link", tempimagem)
                    self.docInnerCanvas.itemconfig(quadelement, image=tempimagem)
                    coords = self.docInnerCanvas.coords(quadelement)
                    dx = x0novo -coords[0]
                    dy = y0novo -coords[1]
                    self.docInnerCanvas.move(quadelement, dx, dy)               
                for quadelementx in listaobs:                    
                    box = (self.docInnerCanvas.bbox(quadelementx))                    
                    pagina = math.floor(box[1]/((infoLaudo[pathpdfatual].pixorgh * self.zoom_x*oldzoom)))
                    deslocy = pagina * infoLaudo[pathpdfatual].pixorgh * self.zoom_x*zoom
                    deslocyold = pagina * infoLaudo[pathpdfatual].pixorgh * self.zoom_x*oldzoom
                    x0novo = round(((box[0]-sobraEspacoold)/(self.zoom_x*oldzoom))*self.zoom_x*zoom + sobraEspaco)
                    x1novo = round(((box[2]-sobraEspacoold)/(self.zoom_x*oldzoom))*self.zoom_x*zoom + sobraEspaco)
                    y0novo = round(((box[1]-deslocyold)/(self.zoom_x*oldzoom))*self.zoom_x*zoom  +deslocy)
                    y1novo = round(((box[3]-deslocyold)/(self.zoom_x*oldzoom))*self.zoom_x*zoom  +deslocy)                       
                    tempimagem = (self.create_rectanglex(x0novo, y0novo, x1novo, y1novo, self.color, link=False))
                    self.addImagetoList("obsitem", tempimagem)
                    self.docInnerCanvas.itemconfig(quadelementx, image=tempimagem)
                    coords = self.docInnerCanvas.coords(quadelementx)
                    dx = x0novo -coords[0]
                    dy = y0novo -coords[1]
                    self.docInnerCanvas.move(quadelementx, dx, dy)
                
            except Exception as ex:
                printlogexception(ex=ex)
     
    
    def freemanipulation(self):
        global lockmanipulation
        lockmanipulation = False
     
    
    def manipulatePagesByClick(self, tipo, event=None):
        global pathpdfatual, infoLaudo, lockmanipulation, zoom
        
        if(not lockmanipulation):
            lockmanipulation = True
            try:
                
                at = round(self.vscrollbar.get()[0]*infoLaudo[pathpdfatual].len)
                atfloor = math.floor((self.vscrollbar.get()[0]*infoLaudo[pathpdfatual].len))
                #self.pagVar.set(max(at+1, infoLaudo[pathpdfatual].len))
                if(tipo=="next"): 
                    if(at+1 > infoLaudo[pathpdfatual].len):
                       self.docInnerCanvas.yview_moveto(1.0)
                       self.pagVar.set(str(infoLaudo[pathpdfatual].len))
                       
                    else:
                        if(zoom>=1.3 and atfloor <= at):
                            self.docInnerCanvas.yview_scroll(10, "units")
                        else: 
                            self.docInnerCanvas.yview_moveto((at+1)/(infoLaudo[pathpdfatual].len))                       
                            self.pagVar.set(str(at+2))
                        
                elif(tipo=="prev"):
                    if(at-1 <= 0):
                        self.docInnerCanvas.yview_moveto(0)
                       
                        self.pagVar.set(str(1))
                       
                    else:
                        if(zoom>=1.3 and atfloor <= at):
                            self.docInnerCanvas.yview_scroll(-10, "units")
                        else:
                            
                            self.docInnerCanvas.yview_moveto((at-1)/(infoLaudo[pathpdfatual].len))
                           
                            self.pagVar.set(str(at))
                        
                elif(tipo=="next10"):
                    if(at+10 > infoLaudo[pathpdfatual].len):
                        self.docInnerCanvas.yview_moveto(1.0)
                        self.pagVar.set(str(infoLaudo[pathpdfatual].len))
                       
                    else:
                        self.docInnerCanvas.yview_moveto((at+10)/(infoLaudo[pathpdfatual].len))
                        
                        self.pagVar.set(str(at+11))
                       
                elif(tipo=="prev10"):
                    if(at-10 <= 0):
                        self.docInnerCanvas.yview_moveto(0)
                        
                        self.pagVar.set(str(1))
                        
                    else:
                        self.docInnerCanvas.yview_moveto((at-10)/(infoLaudo[pathpdfatual].len))
                        
                        self.pagVar.set(str(at-9))
                        
                elif(tipo=="first"):
                    self.docInnerCanvas.yview_moveto(0)
                    self.pagVar.set(str(1))
                    
                elif(tipo=="last"):
                    self.docInnerCanvas.yview_moveto(1.0)
                    self.pagVar.set(str(infoLaudo[pathpdfatual].len))
                
                   
            except Exception as ex:
                printlogexception(ex=ex)
                atual = round((self.vscrollbar.get()[0]*infoLaudo[pathpdfatual].len))
                
            finally:
                root.after(50, self.freemanipulation)
    
    def ssv(self, name=None, index=None, mode=None, sv=None):
        self.docInnerCanvas.delete("simplesearch")
        self.clearSomeImages(["simplesearch"])
        
    def dosearchsimple(self, tipo):
        global pathdb, erros, pathpdfatual, infoLaudo
        lowerCodeNoDiff = [ 
        #00-0F #0
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
         #00-0F #16
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
         #10-1F #32
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
         #20-2F #48
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
         #30-3F #64
         0,  32,  32,  32,  32,  32,  32,  32,  32,  32,  32,  32,  32,  32,  32,  32,\
         #40-4F #80
        32,  32,  32,  32,  32,  32,  32,  32,  32,  32,  32,   0,   0,   0,   0,   0,\
        #50-5F #96
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
         #60-6F #112
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
         #70-7F #128
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
         #80-8F #144
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
         #90-9F #160
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
         #A0-AF #176
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
         #B0-BF #192
         -95, -96, -97, -98, -99,-100,  32,-100, -99,-100,-101,-102, -99,-100,-101,-102,\
       #C0-CF #208
        32, -99, -99,-100,-101,-102,-103,   0,   0,-100,-101,-102,-103,-100,  32,   0,\
        #D0-DF #224
        -127,-128,-129,-130,-131,-132,   0,-132,-131,-132,-133,-134,-131,-132,-133,-134,\
      #E0-EF #240
         0,-131,-131,-132,-133,-134,-135,   0,   0,-132,-133,-134,-135,-132,   0,-134 \
         #F0-FF #256
         ]    
                    
        if(not self.simplesearching):            
            termo= self.simplesearchvar.get()
            if(len(termo)<3):
                return
            self.simplesearching = True
            self.nhp.config(relief='sunken', state='disabled')
            self.php.config(relief='sunken', state='disabled')
            novotermo = ""
            for char in termo:
                codePoint = ord(char)
                if(codePoint<256):
                    codePoint += lowerCodeNoDiff[codePoint]
                novotermo += chr(codePoint) 
            termo = novotermo
            try:
                window = tkinter.Toplevel()    
                label = tkinter.Label(window, text='Pesquisando...')            
                label.pack(fill='x', padx=50, pady=20)
                #window.update()
                root.update_idletasks()
                idpdf = infoLaudo[pathpdfatual].idpdf
                rects = []
                listapintados = self.docInnerCanvas.find_withtag("simplesearch") 
                recordsx = []
                if(tipo=='prev'):
                    atual = math.floor((self.vscrollbar.get()[0]*infoLaudo[pathpdfatual].len))
                    #if(listapintados != None and len(listapintados)==0):
                        #comando = 'SELECT C.pagina, C.texto  FROM Anexo_Eletronico_Conteudo_id_pdf_'+str(idpdf)+' C where C.texto like :termo AND C.pagina <= :pag ORDER BY 1 DESC LIMIT 1'
                    #    comando = 'SELECT C.pagina, C.texto  FROM Anexo_Eletronico_Conteudo_id_pdf_'+str(idpdf)+' C where C.texto like :termo AND C.pagina < :pag ORDER BY 1 DESC LIMIT 1'
                    #else:
                    if(termo in self.termossimplespesquisados and idpdf in self.termossimplespesquisados[termo]):
                        
                        listapaginas = self.termossimplespesquisados[termo][idpdf]
                        pagref = None
                        for i in range(len(listapaginas)-1, -1, -1):
                            pagnow = listapaginas[i]
                            if(self.paginaSearchSimple!= int(self.pagVar.get())-1):
                                if(pagnow[0]<=int(self.pagVar.get())-1):
                                    recordsx.append(pagnow)
                                    self.paginaSearchSimple = pagnow[0]
                                    break
                            else:
                                if(pagnow[0]<int(self.pagVar.get())-1):
                                    recordsx.append(pagnow)
                                    self.paginaSearchSimple = pagnow[0]
                                    break
                        
                    else:
                        sqliteconn =  connectDB(str(pathdb), 5)
                        cursor = sqliteconn.cursor()
                        comando = 'SELECT C.pagina, C.texto  FROM Anexo_Eletronico_Conteudo_id_pdf_'+str(idpdf)+' C where C.texto like :termo ORDER BY 1'
                        #cursor.execute("PRAGMA journal_mode=WAL")
                        cursor.execute(comando, {'termo':'%'+termo+'%', 'pag':int(self.pagVar.get())-1, 'escape': '\\'})
                        records2 = cursor.fetchall()
                        if(termo not in self.termossimplespesquisados):
                            self.termossimplespesquisados[termo] ={}
                        #if(idpdf not in self.termossimplespesquisados[termo]):
                        #    self.termossimplespesquisados[termo][idpdf] = []
                        self.termossimplespesquisados[termo][idpdf] = records2
                        cursor.close()
                        listapaginas = self.termossimplespesquisados[termo][idpdf]
                        pagref = None
                        for i in range(len(listapaginas)-1, -1, -1):
                            pagnow = listapaginas[i]
                            if(self.paginaSearchSimple!= int(self.pagVar.get())-1):
                                if(pagnow[0]<=int(self.pagVar.get())-1):
                                    recordsx.append(pagnow)
                                    self.paginaSearchSimple = pagnow[0]
                                    break
                            else:
                                if(pagnow[0]<int(self.pagVar.get())-1):
                                    recordsx.append(pagnow)
                                    self.paginaSearchSimple = pagnow[0]
                                    break
                        
                        

                elif(tipo=='next'):
                    atual = math.ceil((self.vscrollbar.get()[0]*infoLaudo[pathpdfatual].len))
                    #if(listapintados != None and len(listapintados)==0):
                        #comando = 'SELECT C.pagina, C.texto FROM Anexo_Eletronico_Conteudo_id_pdf_'+str(idpdf)+' C where C.texto like :termo AND C.pagina >= :pag ORDER BY 1 LIMIT 1 '
                    #    comando = 'SELECT C.pagina, C.texto FROM Anexo_Eletronico_Conteudo_id_pdf_'+str(idpdf)+' C where C.texto like :termo AND C.pagina > :pag ORDER BY 1 LIMIT 1 '
                    #else:
                    if(termo in self.termossimplespesquisados and idpdf in self.termossimplespesquisados[termo]):
                        listapaginas = self.termossimplespesquisados[termo][idpdf]
                        pagref = None
                        for i in range(len(listapaginas)):
                            pagnow = listapaginas[i]
                            if(self.paginaSearchSimple!= int(self.pagVar.get())-1):
                                if(pagnow[0]>=int(self.pagVar.get())-1):
                                    recordsx.append(pagnow)
                                    self.paginaSearchSimple = pagnow[0]
                                    break
                            else:
                                if(pagnow[0]>int(self.pagVar.get())-1):
                                    recordsx.append(pagnow)
                                    self.paginaSearchSimple = pagnow[0]
                                    break
                    else:
                        sqliteconn =  connectDB(str(pathdb), 5)
                        cursor = sqliteconn.cursor()
                        comando = 'SELECT C.pagina, C.texto FROM Anexo_Eletronico_Conteudo_id_pdf_'+str(idpdf)+' C where C.texto like :termo ORDER BY 1 '
                        #cursor.execute("PRAGMA journal_mode=WAL")
                        cursor.execute(comando, {'termo':'%'+termo+'%', 'pag':int(self.pagVar.get())-1, 'escape': '\\'})
                        records2 = cursor.fetchall()
                        if(termo not in self.termossimplespesquisados):
                            self.termossimplespesquisados[termo] ={}
                        self.termossimplespesquisados[termo][idpdf] = records2
                        cursor.close()
                        listapaginas = self.termossimplespesquisados[termo][idpdf]
                        pagref = None
                        for i in range(len(listapaginas)):
                            pagnow = listapaginas[i]
                            if(self.paginaSearchSimple!= int(self.pagVar.get())-1):
                                if(pagnow[0]>=int(self.pagVar.get())-1):
                                    recordsx.append(pagnow)
                                    self.paginaSearchSimple = pagnow[0]
                                    break
                            else:
                                if(pagnow[0]>int(self.pagVar.get())-1):
                                    recordsx.append(pagnow)
                                    self.paginaSearchSimple = pagnow[0]
                                    break
                        #comando = 'SELECT C.pagina, C.texto FROM Anexo_Eletronico_Conteudo_id_pdf_'+str(idpdf)+' C where C.texto like :termo AND C.pagina > :pag ORDER BY 1 LIMIT 1 '

                try:
                    if(len(recordsx)>0):
                        results = searchsqlite(0, termo, pathpdfatual, pathdb, idpdf, simplesearch=True, erros = erros, jarecords=recordsx)
                        if(results != None and len(results) >0):     
                            pagina = results[0].pagina
                            ondeir = ((pagina) / (infoLaudo[pathpdfatual].len))
                            self.docInnerCanvas.yview_moveto(ondeir)
                            if(str(pagina+1)!=self.pagVar.get()):
                               self.pagVar.set(str(pagina+1))
                            #self.pagVar.set(pagina+1)
                           
                            self.positions[self.indiceposition] = (pathpdfatual, self.vscrollbar.get()[0])
                            self.indiceposition += 1
                            if(self.indiceposition>=10):
                                self.indiceposition = 0
                            self.paintsearchresult(results, True)
                        else:
                            self.simplesearching = False
                            self.nhp.config(relief='raised', state='normal')
                            self.php.config(relief='raised', state='normal')                        
                            popup_window('<{}> - Nenhuma ocorrência encontrada!'.format(termo), False)
                    else:
                        self.simplesearching = False
                        self.nhp.config(relief='raised', state='normal')
                        self.php.config(relief='raised', state='normal')                        
                        popup_window('<{}> - Nenhuma ocorrência encontrada!'.format(termo), False)
                except Exception as ex:
                    exc_type, exc_value, exc_tb = sys.exc_info()
                    popup_window(traceback.format_exception(exc_type, exc_value, exc_tb), False)
                    self.nhp.config(relief='raised', state='normal')
                    self.php.config(relief='raised', state='normal')
                window.destroy()                    
            except Exception as ex:
                exc_type, exc_value, exc_tb = sys.exc_info()
                popup_window(traceback.format_exception(exc_type, exc_value, exc_tb), False)
                #printlogexception(ex=ex)
            finally:
                self.simplesearching = False
        
    def searchTerm(self, termo=None, event=None, advancedsearch=False):
        global pathdb, searchprocess, result_queue, erros, queuesair, processes, searchqueue, searchResultsDict
        
        try:
            if(termo==None):
                termo = self.searchVar.get().strip()

            lowerCodeNoDiff = [ 
            #00-0F #0
             0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
             #00-0F #16
             0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
             #10-1F #32
             0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
             #20-2F #48
             0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
             #30-3F #64
             0,  32,  32,  32,  32,  32,  32,  32,  32,  32,  32,  32,  32,  32,  32,  32,\
             #40-4F #80
            32,  32,  32,  32,  32,  32,  32,  32,  32,  32,  32,   0,   0,   0,   0,   0,\
            #50-5F #96
             0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
             #60-6F #112
             0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
             #70-7F #128
             0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
             #80-8F #144
             0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
             #90-9F #160
             0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
             #A0-AF #176
             0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
             #B0-BF #192
             -95, -96, -97, -98, -99,-100,  32,-100, -99,-100,-101,-102, -99,-100,-101,-102,\
           #C0-CF #208
            32, -99, -99,-100,-101,-102,-103,   0,   0,-100,-101,-102,-103,-100,  32,   0,\
            #D0-DF #224
            -127,-128,-129,-130,-131,-132,   0,-132,-131,-132,-133,-134,-131,-132,-133,-134,\
          #E0-EF #240
             0,-131,-131,-132,-133,-134,-135,   0,   0,-132,-133,-134,-135,-132,   0,-134 \
             #F0-FF #256
             ]
        
            novotermo = ""
            for char in termo:
                codePoint = ord(char)
                if(codePoint<256):
                    codePoint += lowerCodeNoDiff[codePoint]
                novotermo += chr(codePoint) 

            termo = novotermo.strip().upper()
            existe = False
            tipobusca = 0
            if(advancedsearch):
    
                tipobusca = 1
    
            if(not (termo, tipobusca) in self.searchedTerms):
                self.searchedTerms.append((termo, tipobusca))
                searchqueue.insert(0, (termo, advancedsearch, None, '0'))    
            else:
                for searched in self.treeviewSearches.get_children(''):
                    values = self.treeviewSearches.item(searched, 'values')
                    if(values[0]==termo and str(values[1])==str(tipobusca)):
                        self.treeviewSearches.selection_set(searched)
                        self.treeviewSearches.move(searched, '', 0)
                        self.treeviewSearches.focus(searched)
                        break
        except Exception as ex:
            printlogexception(ex=ex)
            
    def printer(self):
        _filename = pathpdfatual
        widthdoc = infoLaudo[pathpdfatual].pixorgw
        heightdoc = infoLaudo[pathpdfatual].pixorgh
        atual = math.floor((self.vscrollbar.get()[0]*infoLaudo[pathpdfatual].len))+1
        if getattr(sys, 'frozen', False):
            application_path = sys._MEIPASS
        elif __file__:
            application_path = os.path.dirname(os.path.abspath(__file__))
        try:
            if plt == "Linux":
                subprocess.Popen([os.path.join(application_path, 'printer_interface_linux', 'printer_interface'), str(_filename), str(widthdoc), str(heightdoc), str(atual)])
            elif plt=="Windows":
                subprocess.Popen([os.path.join(application_path, 'printer_interface_windows', 'printer_interface.exe'), str(_filename), str(widthdoc), str(heightdoc), str(atual)])
        except Exception as ex:
            printlogexception(ex=ex)
        #printer_margins
        #printer_interface.Printer().printFunction(pathpdfatual, infoLaudo[pathpdfatual].pixorgw, infoLaudo[pathpdfatual].pixorgh,  math.floor((self.vscrollbar.get()[0]*infoLaudo[pathpdfatual].len))+1, root) 
        
        
        
    def createTopBar(self):        
        global pathpdfatual, infoLaudo
        try:
            aboutimageb = b'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAABCklEQVQ4jbXTQU7CUBDG8d9FFAgJBo5iELSXIKYXwLA3inHlQhcuJGGhIgeRU7mYYkgbXivqP+miM/O+zvTNx34yzLDEZ/Esi9hF4lyFLta4xBi9ndxJEZtghU6d2DlecdTgwy28YZgSu2kgVGaOUTnYLTo7lJXo+Ju19JhzXCfybbxvXzJxASnGOKupyRWjz4oDvyXDFbFbvXStRzzU1PSxIBa2jmc8Najb/IvgUjjgt4IDvNDsUpoIZpgSRp/8gWC+21hl00vc4zaRrzitI4x+KB84LgeHwmI/5Q6n+5IjMX67gVC36Gyv2JaWMHoubq6/kxsUsVz8s8qYKUbCmwuxsBuxZ1OJNfsCVFcz4GUjHKoAAAAASUVORK5CYII='
            self.aboutimage = tkinter.PhotoImage(data=aboutimageb)
            helpimageb = b'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAABQ0lEQVQ4jZ3TvS5EYRDG8Z9G4xqwsgkhkXAJCo3IYiuNGtlCdGQ7GqFRaTQkS7AkbsMmrkDhDkQh0SrmrJzsni/+ySnemefMeefMM+TTRBsdvCRPJ4ltFLw3RB1P2MUaplO5mSS2jS6myoqt4w7jFT48iXusFhU7qVBokFM0BoP15Gb/pStu/MuT7DZHcIwPfOMGYxm6Gh76h6YYQBab+MQSFvGGoxxtS9J6W0wui2Vspc7neM7RNnFIeGs6R5RmDO/Yz8nP4powbBUu8YrRAk2vasEGvoSxi+gRLZcJL6SmmMMcrigeSp95LJRomjggFn27RLyDvRJNK32xIacPcInbgvzQpk2JRf8vj5gYDK6KRf8rZ1jJSzZE+7UKherJzXKL9ZkUFmmJyc2mcnNJrCX+2VCbRTTEbl4Lw/aEzw4U2OwHU2Y56cDh/+QAAAAASUVORK5CYII='
            self.helpimage = tkinter.PhotoImage(data=helpimageb)
            self.clipboardgtk = None
            self.swapframes = tkinter.Frame(bg=self.bg, highlightthickness=0)
            self.swapframes.rowconfigure(0, weight=1)
            self.swapframes.columnconfigure(0, weight=1)
            self.globalFrame.add(self.swapframes)            
            self.docOuterFrame = tkinter.Frame(self.swapframes, bg=self.bg, highlightthickness=0)
            self.docOuterFrame.grid(row=0, column=0, sticky='nsew', padx=0, pady=0)
            self.docOuterFrame.rowconfigure(1, weight=1)
            self.docOuterFrame.columnconfigure(0, weight=1)
            self.globalFrame.paneconfig(self.swapframes, minsize=root.winfo_screenwidth()/2)
            
            self.toolbar = tkinter.Frame(self.docOuterFrame, borderwidth=4, bg=self.bg, relief='groove')     
            self.toolbar.columnconfigure((0, 1, 2, 3 ,4), weight=1)
            self.toolbar.rowconfigure(0, weight=1)
            self.toolbar.grid(column=0, row=0, sticky='ew', padx=0, pady=0)   
            
            self.manipulationTool = tkinter.Frame(self.toolbar, bg=self.bg, borderwidth=4, relief='groove')
            self.manipulationTool.grid(row=0, column=0, sticky='ew')
            self.manipulationTool.columnconfigure((0,1,2,3,4,5,6,7), weight=1)
            
            self.basicTool = tkinter.Frame(self.toolbar, bg=self.bg)  
            self.basicTool.grid(row=0, column=2, sticky='ew')
            self.basicTool.columnconfigure((0,1,2,3,4,5,6,7), weight=1)
            
            self.rightFrame  = tkinter.Frame(self.toolbar, bg=self.bg)
            self.rightFrame.grid(row=0, column=4, sticky='e', padx=10)
            self.rightFrame.columnconfigure((0,1,2,3), weight=1)
            
            self.reportsiconb = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAnUlEQVRYhe3VsQnDMBCFYTcexOANNIN+8cASKbyLx0iV3rjOYpnApbNACsVcEMH3wav14Dhd1znn3AeSZmAHDqPsklRdAFgNHz+AI6V0ry5QShljjFtK6WmRGOOWcx7OTMO1EULogUnSbBFgCiH01QUkLdZbIGn5nwLNR+CayzkPwMPyKy6ljNUFfnGMgPWbAjfgZXyO5xPDcM5dwBsgU1sWmRfQTQAAAABJRU5ErkJggg=='
            self.reportsicon = tkinter.PhotoImage(data=self.reportsiconb)
            
            self.reportbut = tkinter.Menubutton(self.rightFrame, image=self.reportsicon, relief='raised')
            self.menuReports()
            self.reportbut.grid(row=0, column=3, sticky='e', padx=10)
            
            uphit = b'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAdklEQVQ4je3OvQqAIBSG4XcJAmlxqwtvrqmuxgsJuoeWI4hoP3qgxRe+oZLH4KcGmUoWOGRWA3PAKXM1qMccsMn882c0xCywyOL3RRgBmPuezWQOh2CMmjtwBNbEzTHo0R2Ynv4yVQqsqoENLGiWqdUBvSb4ugs27SaiA7GD8gAAAABJRU5ErkJggg====/IBA2/F8lEEII8WMM8Dr2RXkBzjplpURbXro9XaIvt5u3ZeVP/tLL0yXeBE+XiAROlfBgUCvhIwIb8UNjwAHsIwJCCCHSuQD50S+vRBI2FAAAAABJRU5ErkJggg=='
            downhit = b'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAcElEQVQ4je3OsQmAMBRF0VuKaSSdazuBVm7jIuIONi/wCcFoErTxwa38OQgfrVPNNqlmm9UP/uAb4AgsgL8Bet2OV6ADNmXRGPTmzuX+0h4H1IKp79nFjwJYhKXQVRVjMXqoKsyiu6rGwnpgaIU92gmziCaXWXs1WAAAAABJRU5ErkJggg====/4tVQYhhBCHU4AKWGBrvi1/AirQgGsywnzT/EaY/tBoRGSz7OBy+czhbfIRwXb5lyhN/haRKn+KSJf3EZX4oxJCCHEGN7QlL5lws1DLAAAAAElFTkSuQmCC'
            self.downhiti = tkinter.PhotoImage(data=downhit)
            self.uphiti = tkinter.PhotoImage(data=uphit)
            self.nhp = tkinter.Button(self.rightFrame, image=self.downhiti)
            self.nhp.image = self.downhiti
            self.nhp.grid(column=2, row=0, sticky='ns', padx=5) 
            self.nhp.config(command=lambda: self.dosearchsimple('next'))
            nhp = CreateToolTip(self.nhp, "Próxima página com ocorrências")
            
            self.php = tkinter.Button(self.rightFrame, image=self.uphiti)
            self.php.image = self.uphiti
            self.php.grid(column=0, row=0, sticky='ns', padx=5) 
            self.php.config(command=lambda: self.dosearchsimple('prev'))
            php = CreateToolTip(self.php, "Página anterior com ocorrências")
            
            self.simplesearchvar = tkinter.StringVar()
            self.simplesearch = tkinter.Entry(self.rightFrame, justify='center', textvariable=self.simplesearchvar, exportselection=False)
            self.simplesearchvar.set("")
            self.simplesearchvar.trace_add("write", self.ssv)
            self.simplesearch.grid(row=0, column=1, sticky='ns', padx=5)
            self.simplesearch.bind('<Return>',  lambda e: self.dosearchsimple('next'))
            
            zoomPlus = b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAADV0lEQVRIS62VXYgTVxTH/+dm4rquH3XXpZ9QWhBfCorVthRs42R9SMWX3Z0kT24mLmulCj6JUGylT4rQFpRVRDdjKZjkoqVdi33YJCOU7ouysJZSQcFCKaJLxSbWuMzcU6YSSSYzG5G9b3PPued3z8f/DiFkxQZHX4tE3e0MtZ4hesGoA3RLCGWX8tbPADjsbPM++Z3ig9k3WXOPuhAfCOJJYnGVgXsC3M3AOgAJEFYS+LNSwcp3grQAtiazQwo8rjEfdXswbltWPSiAnjbfh4sTILrRVe3JXL58/HEY6CnAC05wvxZMH01J63qnmxmGsWSOeiaYqbcftR1SSjfozP8AryyOxtNR5oFnCd4IZBhGZI5WXBLM0yWZ+yIUoCdHJDFNl6T1ZWBJhszfwCJRvnj2D789ZmReEsSzyolutC+e+dNvJ29aWHOv0TJ+PbTmQ+ZNFeUBO2/dDrxA0jwGoF4u5g61AeIpc7cCb64UrNGwuusdALF0dpNwnTNl+c2GNoCeGhkHR2bLxYlTzwvwenGXlv1Dd99YZduHnRYdbE2ZeTDJSnHigmcYMMZWKZr/vhVG74B5FuSJ7clips8rMnel8R0bHrmDaNdb9vnTc62ApGkJYKpUzH3rGd4eG4uuvu+82+zkEOcjjP0EutPYdzTt9+ZgHw6bD4i6X7XleM0HyB4i8JKgBjUcO/VgWzr7yrzimSvF3IvtTU5ntrCir8rF3Kbn7UHcyO5SgrdVCrl0GwAA6SnzBgiZcj73S4gOFhpT0o2dMwRxsCStn4IAiKcyaVZ0oA+196SU834nPWWOChWVU/L0gzabYe5lUqlK8dyWUCV7Bj2ZPc9Q7hp+OBL2rvgDxJPZAVY8qSJis104++uCgERiX9ej5bXviIiYlWlL6+nEBBwk3TA/AeMYBJYS+MdefjgYlH3Lc+0J5m8s/5RJ7QXEOSWo0O9WZxoZedOiXCQYzj4mqjJpeyLsHmHQ9jBI2w/Hu633PgnN3Q12d7hEa0mhyhDdEKgLQkUothoN9TKfX1G94EHA6lIf/h1qziQQ0FySWOywhpf/egGOVveLqOG3EKQjIEwb/v1miGJM9qM27GWyaAAP2JIJ8EMf14xFBfghRPh40QENSH1ldVelYJ38D+NvspCLX1p8AAAAAElFTkSuQmCC'
            im = tkinter.PhotoImage(data=zoomPlus)
            zoomp = tkinter.Button(self.manipulationTool, image=im, command= lambda: self.zoomx(tipozoom='plus'))
            zoomp.image = im
            zoomp.grid(column=4, row=0, sticky='n')  
            zoomp_ttp = CreateToolTip(zoomp, "Aumentar Zoom")            
            zoomMinus = b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAADEUlEQVRIS63VTWwMYRgH8P/z7qyq+mw1PhMhERcJoQ2RYE3rUI1LdXb3pDvbpgiuIhEfcSISJKRE6A6R6O6khBIOdnckohfSpBw4uIkIDWEXq9l5HxnJyn5Np6RznOed5/c879cQXJ5AR89Sn99uZ8g1DFEPRg6gt0JIKzlgPAXAbt8Wv6fyQS0d0RWs2KdtiC2CeIhYPGfgkwDXMrAKQBsIswl8LBk3BryQEmBbMLpLgvsU5tN2Hfosw8hVS6CG9U2wcRFEb2oydZGHDy/8coP+Ak5ygn1eMO14bBovvSrTNG3aGNX1M1N9I7I7TdO0q33zB3CmJa/wsJ+5dTLJC4k0TfON0az7gnk4acZOugJqsMskpuGkaZz1qrw8HtAiCwXxqMz711m3r74rj5OzW1ixX9AMXuY2516oGtTPAMilErGjFUBLSN8jwc3puNHjlch1S4ejTcLOX02ZN9ZWAGqoqw/sG00l+i//L+CsxUea8Y0+Lp9jWSfyJedgW0gfAJOZTvQPOoFWrXeOpPG7XhgzHU+bsSeFcYHOrg/w16y2bl0ZKwWCuiGAx8lE7KYTWN/b65/3Jb/BC8gryuviZFs79a9EtUsssy9bBkSPEnhatQXyQgrx7eHo4nHJI08SsQWVixyObGZJ51KJWNNkE1ZcL1q0Wwreno7HwhUAAFJD+hsQIqmB2LP/QEjVdo8QxOGkaTyqBqAlFAmzpEMNyG40TXP8XxBV0w8wyVA6cX2z60l2Amoweosh7fn8vcvtXqmYmmC0lSUPSZ9otuLXXk0ItLUdrPk5M3uHiIhZ6pZpfJigE1I1fT8YZyAwncAP6vl7R7XuS65r58B8xswjTPIAIK5LQfFGOzNS6MjZLdJGGyN/kIkyTMo+H9unGNTuhlT8cJyqnftJKPYesL3TJlpJEhmGqIVAThDSQrJRWFCn8/FZmUEHAcv7Dfixq7iTqkDx1AQCJxQsej8XeSVXfogK4yZCPIHJ7qhiRDKGGpHtdDqZMsAppKQT4F4DZ7UpBcoRIuydcqCA5GZnutNx49JvfsZzkMaBvsMAAAAASUVORK5CYII='
            im2 = tkinter.PhotoImage(data=zoomMinus)
            zoomm = tkinter.Button(self.manipulationTool, image=im2, command= lambda: self.zoomx(tipozoom='minus'))
            zoomm.image = im2
            zoomm.grid(column=5, row=0, sticky='n')  
            zoom_ttp = CreateToolTip(zoomm, "Dominuir Zoom")
            printerb = b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAABbElEQVRIS+3VP0hWURjH8c+rji0qCRGOgi1igg6NOTS4OQXSHDglBCoOEkpq0BDW2Nhim5O6udikOLg4SIOEJEq6ioo8cF645PV2b7zi4oE73HOe53zP8+f8Ts31MYH4LnLWiqaa8R4fska1HI/v+IqVioAhvMLLe8BNmbvbFL1ASzraJNawWbHI/XiOheR3jtXoolm0ozUtdOM3/lQEhH8HdpPfKQ4CsI3eipuVNd8OwHGKoKxTkV0XljGNJZw0GvAUG3iLL7cBiOhCMuoy0/AI/k5fLuAJRv9T7D5nuihguYAo0h52Kla9B50YzvjlAhqppoWAI4yXjGIOj3LkuhCwhb6SgJCVgZsAoTufMhuFFkWx9jHzD8B80q0wG8HrjBZFu47GRWvDFB6nzZ4lo2+Im1k0fiJSGeMNxvAj/f+KAxY9mWdYLJmiaOsHVZ/MdTwsCTjEYFXArT360ZpRk8uSp6+bNeEdPmb9rgDVpWGhF3umJgAAAABJRU5ErkJggg=='
            printeri = tkinter.PhotoImage(data=printerb)
            if(plt=="Linux"):
                 printb = tkinter.Button(self.manipulationTool, image=printeri, command= lambda: self.printer(), state='normal')
            elif(plt=='Windows'):
                 printb = tkinter.Button(self.manipulationTool, image=printeri, command= lambda: self.printer(), state='normal')
            printb.image = printeri
            printb.grid(column=7, row=0, sticky='n')  
            printb_ttp = CreateToolTip(printb, "Imprimir")   
            
            nextPage = b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAA3ElEQVRIS+3UUQqCQBAG4H/GA7QqnaOiO1RE0GN0x6jnlOpCzp5A2TAQIqidXfOpfPf/5p9dJQz80MD5+AEgHY/X1DS1tbaIWad3RSbPDwxs4dzeWnsIRbxAmqYjMJ8JmMcgXqCduA+iAvogaiAWCQJikGDgFSFgJSKXd7crGnDMBQMzJlpWVXX7GtDeqC6cgJ2InD59G0ENHuHOlZwkU014C6sBY4wBUISEq4E2nJlLEE20k3dr8zboE65qkOX5EcAmdHJ1gyzLFkRUi8g19E+qahAT+vyO9wz+wB0mD2MZRUQZ9AAAAABJRU5ErkJggg=='
            lastPage = b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAABbUlEQVRIS93VzU7CQBAH8JlZkPiRlC5LOZgQlahXzh5MQB/Bg08jvIlXH6O8gOInvoGxbFvudLtmjTWElCaky4Uem2Z+zX92ZhE2/OCG68MWA64Qt5poMguC56IYHc/rsCS5jKLoPu+7lRFxzseA2CbEaynl4yqEcz4AxEEUhrQW4LpuG4lGAOCkRFez6fQprwAXYghaGyD3ZwubXK/Xj4gxgxz8IeNlpBRgijmt1glLEh8A9nSa9uM4fllESgO/iOd1UKkRIda0UgZ5zRArgCnWbDZP50niM6Kq1roXRdG7eW8NMMWEEOdzpXyGSETUlVJ+bQQwWK1a7QZB8G0NEEKcJUr5oDUxxnphGE6sRZTlT4gVADD5f1hrcnaCGMDOYnOtAP8zgLi7fDxLA47jHLNKxQzYft6AlQZ4o2Em9jBlrF+0UTnnd4A4XHvZcc5vtNafcRy/Fa1rsxSBsYtYyoe1tqmtq3SLr0xbEf0AkgncGV5n0L4AAAAASUVORK5CYII='
            nextPage10 = b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAABpklEQVRIS+2Tz0tVQRzFz5lHPHgrZ+b+F9K/ofIwIojI/oOUpMwf2B9QYIZWJgitSgxE3AbSRnAhBa0Ft48Hjzczt9/t7jdu3LcJ353rDXfO9jtzPjNnziEuePGC9XEJiDpcZlE+k6hCZMNQgNb6VCn1wXs/PQCNJMlriFxllo2lafq1Cnw4wNrHBJYJbHrvZ3IxnSSTFNkX4DNFxkII32KQ0hQZY1ZBPhTgZer9bC5mrb0hwC6AT4ocd859L4NEY2qSZA0i90GuB+ce5GLGmJsg34E8vtJoTPR6vZ/DIFHAX2usfUHgHkRWQwgLBeQWyB0CR81ms93tdn+dBakEKKx5JcC0AEup9yvFn0xR5C3Ig+Bc+38BmwLcBTkfnHtWAO5Q5A2B9977a7UBWusNKjUjwJPU+0eF+G2KbEPksNVqTXY6nd+1AMba5wBmIfI0hLB4Hv/zveUxLRKUkWtfnJs7b4JKAcaYFZAL/3TgugB7AD42lBrv9/s/ahdNa30CpQ4GBStuvwWlRpFl7SotjloUu12VeeUeVBGrlaK6woNzly+IOvgHbIWmGSdw6N0AAAAASUVORK5CYII='
    
            firstPage = b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAABgklEQVRIS92VS07DMBCGZ5J0X8dOJbgAqni3Yk0OwpZz8LgLG64AbZHYwwGgFNi1aeME8VRjD4rUIoTSxBHtpt56PJ//8fxjhAUvXHB+WGKAK8ShjdgJguA+r4xCiIYCqMvh8CwrbmaJXM4JiI7CMDydBeCc7xHABWndlVI2ywMQT8Lh8DjroBCiqYkuAVGSUr6U8nlugKrn7VpatwDgRSu1H0XR0yyV+SXKUFD1vJ1J8tdJ8se8NyoFYIxtoWW1AeBdOY4f9/sPRT4yBjDGNtC2O5rok2zbjweDblHydN8IIIRY1VrfaqKk4jj7Ra37G2wKWBkrdYMAuuI4fhAEdya3N1aQBnLO60R0pRHHFctKIbkGnF7ASME02HXddUTsKIAv03coBUhBjLFNtO02EH2YdFJpQAqp1mrbllKp0d5UkvhxHPfmZrRpoj9u9qMoyjTcv4ZdOkk1UQsBeqPRqFFqFjHOD0ip67w581OuJFkLw/C8FMC0z4vilvjLLJJuuv8NJqHsGRXGYe0AAAAASUVORK5CYII='
            previousPage = b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAA30lEQVRIS+XUvQrCMBAH8Dv6BOb6fuLQQUdt8RUEvyYHN/EpxHcRnEsS4l6MtGihoCYXmkWzBv4/7oNDiPwwcj78N4BENKmS5HQry8unVoe2CIUQe0DMEGColDr2CbThYO1Ka118WxRuBazwGuYA7HAOEBTuCwSHewFCiCUg5j4DfTds5wyIaGEB5tGAehGIaGcBxmDtWmudc+6Xs4JnWDDiCzTzaitB3GgpZz6VcIAOckfcGimnLoQLsJEQoIMgwEgpdejz2L2ycJCmma2qszHmGgNwtb/5D22RV/hvAA91028ZZhfsxAAAAABJRU5ErkJggg=='
            previousPage10 = b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAABm0lEQVRIS+2UzUocQRSFz62lGKe7qmczj+BiUBAMuhLch4AocS8kEv9FFBcBEQ0IKgqKeQQVEUJwgm8gPkrd27qbjXOlQg+4cKaHnrizts09H3W+uk1440NvnI93QG7D/6uikKOv0ToGlEql2Bhza4y5Y+bZLIxskvx6Uh19ZO4vDIiiKArhIKpC9ZOI1ACQtfYMRDMg2hLvfxQCWGv7GkS3BhhQoonU+98hyDl3qsBXAn4y80YrGW0rSpLkQ0P1L4AhAiaZ+ToExc4dE/AdqnsistbOdEtAuVzufVKtQXWYgClmvgpBNkkOoLrYIDp48H457xm1BETOhVrGoPpFRC6yWjYV2AZwJMwLeeHhe0uAdS6IHIfqtIicZ9WsE7CrwHHKPN8VoFKp9NTr9RsQjWS3uPxXkbV7IFoF0aF4v5QHaSs583AD1Y+veQDRvni/Ukhyc6jbl9TRJr/YhUEl+px6/yeTfqLANwV2UubNQovWHIrjuNQwpmaA+5R5rvmrcM4FyKgwV7sC5MkstMlFQ1/OdeSgG9A7ILe9Z9RIqRl/rhaPAAAAAElFTkSuQmCC'
            
            imFP = tkinter.PhotoImage(data=firstPage)
            imPP = tkinter.PhotoImage(data=previousPage)
            imPP10 = tkinter.PhotoImage(data=previousPage10)
            imNP = tkinter.PhotoImage(data=nextPage)
            imNP10 = tkinter.PhotoImage(data=nextPage10)
            imLP = tkinter.PhotoImage(data=lastPage)
      
            self.fp = tkinter.Button(self.basicTool, image=imFP)
            self.fp.image = imFP
            self.fp.grid(column=0, row=0, sticky='e')  
            self.fp.config(command=lambda: self.manipulatePagesByClick('first'))
            fp_ttp = CreateToolTip(self.fp, "Ir para primeira página")
            
            self.pp10 = tkinter.Button(self.basicTool, image=imPP10)
            self.pp10.image = imPP10
            self.pp10.grid(column=1, row=0, sticky='n') 
            self.pp10.config(command=lambda: self.manipulatePagesByClick('prev10'))
            pp10_ttp = CreateToolTip(self.pp10, "Voltar DEZ páginas")
            
            self.pp = tkinter.Button(self.basicTool, image=imPP)
            self.pp.image = imPP
            self.pp.grid(column=2, row=0, sticky='w') 
            self.pp.config(command=lambda: self.manipulatePagesByClick('prev')) 
            pp_ttp = CreateToolTip(self.pp, "Pagina anterior")
            
            self.pagVar = tkinter.StringVar()
            self.pag = tkinter.Entry(self.basicTool, justify='right', textvariable=self.pagVar, exportselection=False)
            self.pagVar.set("1")
            self.pag.bind('<Return>', self.gotoPage)
            self.pag.grid(row=0, column=3, sticky='ns')
            
            self.totalPgg = tkinter.Label(self.basicTool, text="/ "+str(infoLaudo[pathpdfatual].len))
            self.totalPgg.grid(row=0, column=4, sticky='ns')
                
            self.np = tkinter.Button(self.basicTool, image=imNP)
            self.np.image = imNP
            self.np.grid(column=5, row=0, sticky='e') 
            self.np.config(command=lambda: self.manipulatePagesByClick('next'))
            np_ttp = CreateToolTip(self.np, "Pagina seguinte")
            
            self.np10 = tkinter.Button(self.basicTool, image=imNP10)
            self.np10.image = imNP10
            self.np10.grid(column=6, row=0, sticky='n') 
            self.np10.config(command=lambda: self.manipulatePagesByClick('next10'))
            np10_ttp = CreateToolTip(self.np10, "Avançar DEZ páginas")
            
            self.lp = tkinter.Button(self.basicTool, image=imLP)
            self.lp.image = imLP
            self.lp.grid(column=7, row=0, sticky='w') 
            self.lp.config(command=lambda: self.manipulatePagesByClick('last'))
            lp_ttp = CreateToolTip(self.lp, "Ir para última página")
                  
            drag = b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAABPUlEQVRIS7XVvytFYRgH8M8tme0y8A+YlB0xYJFSktlqIf8Biz/AJqXMBlmkSAaDJAaJgfJjIJJE9NRNt5tz33PPvU6d5byd7+d93/M85y3556v0z/lSwCLm8V10Iikgglcwg68iSB4gcjcwhY96kbxA5G5hDG/1IPUAkbuPYTzlReoFIvcYg7jLgxQBIvcC/bhOIUWByL3BAM5qIY0AkfuIIRxlIY0CkfuCEez+hTQDiNx3jGOzGikK7OAU9xX3LQ4bAV7xiTYsYzZVQTGedwXRWPExR7GAwDryNFwe4KFcjtFg7bhCC+awlFpFCoha78N5RdA6JhB73pn6AaaALlxWzbIXB+Vn01htpNGySjuqpQcn6K51IKVWkDW5SayVB+PHt120k7Pea8Ve+SCKE++52UCqeH7Hi25RbuAHimlFGfsF2RcAAAAASUVORK5CYII='
            imdrag = tkinter.PhotoImage(data=drag)
            self.bdrag = tkinter.Button(self.manipulationTool, image=imdrag, state='disabled', padx=20, command=self.activateDrag)
            self.bdrag.image = imdrag
            self.bdrag.grid(column=0, row=0, sticky='n')
            bdrag_ttp = CreateToolTip(self.bdrag, "Modo de navegação")
                   
            select = b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAABMUlEQVRIS+3WvytGcRQG8M87YGDB6EdSUjYlo7AoWcx6B4OUDP4Cs0VWZVBWMSjFQMmvEv+BEoPiL1CEvvqq18t17633bu8Zvz3nPM8553afU/J33KIXz7jBFrbxjmEsYASdaEAfQs6vKCUQbKAbHRhAwO3hAisx5yEWfcEcHvMQVGK7sI7J+HiHGVwmiPvxnNRBdW4zguK2OJrTLMUDJitBwB5hPM78rQiCA0zkFJWrgzpB6toKG9E05jGEdhziCsupkjJ+EUtYqyq2j6laEXzXKWxEdYIsq/rC1HeQOqpjjKERr6noCMjqBy3RcFoxipNaEvREywxeEOIeZZzhI40oqYPNCtPvj0V2cI7V+IsJJh8uiWD6s3lNPyQG5U+4jmfLblQ8iMXozeEgaPrvbPkEz9I8GVjHzH8AAAAASUVORK5CYII='
            imselect = tkinter.PhotoImage(data=select)
            self.bselect = tkinter.Button(self.manipulationTool, image=imselect, padx=20, command=self.activateSelection)
            self.bselect.image = imselect
            self.bselect.grid(column=1, row=0, sticky='n') 
            bselect_ttp = CreateToolTip(self.bselect, "Modo de seleção de texto")
            self.selectionActive = False
            self.areaselectionActive = False
            self.areaselectionActiveCustom = False
            self.bdrag.config(relief='sunken')
            
            areaselect = b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAzElEQVRIS73VsW0CQRSE4Y/IEoEJnRFDAS7AFdCNJTvxkUBANzTgAlwAxM4cQoBEBFqJtVZ7Agfs82YnrebfN/M0NxB8BsH6/g0wxDO/wB9siummeKqmvXXnhC8c8gRvWBQCe4yK7x0eK8Bfd9aYZUCHD7xcRO6d4BMrvNaAVpkki+boSovSFA+NtuqYxLHMgBTyGNtGgAm+y5DDAWmLQi3KWxQWcjgg3KLwkMMB4RaFhxxRdr0ual3X73UXhf5wGnVcX6ZVNVx9YDjgDL5WTBmcyOQ4AAAAAElFTkSuQmCC'
            imareaselect = tkinter.PhotoImage(data=areaselect)
            self.baselect = tkinter.Button(self.manipulationTool, image=imareaselect, padx=20, command=self.activateareaSelection)
            self.baselect.image = imareaselect
            baselect_ttp = CreateToolTip(self.baselect, "Modo de seleção de área")
            self.baselect.grid(column=2, row=0, sticky='n') 
            
            showbookmarksb = b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAsElEQVRIie3VIYpCURQG4E8Z0WLRZNNstJvdwHRtplmAC9ANmAWbINhtGkUmuwRhisXwHMSZ8F40XJ8iKO+Hk+5/+eCGc3nH5DDF6sZZoBgClPCHDWaBs07u1G8BuiHlJJ0MyIAMyIAnAS3x1tyi/Uighgku2OE7OZ+jcQ/QxwBHHPCFAvLoYY8TRvhMA/zijDGqV3plDBEl3WDgAz9YohnQb4ifK0IlBEiboO/y9fIPFcVWcGhosHYAAAAASUVORK5CYII='
            showbookmarksi = tkinter.PhotoImage(data=showbookmarksb)
            self.showbookmarks = tkinter.Button(self.manipulationTool, image=showbookmarksi, padx=20, command=self.showAllBookmarks)
            self.showbookmarks.image = showbookmarksi
            showbookmarks_ttp = CreateToolTip(self.showbookmarks, "Realçar Marcadores")
            self.showbookmarks.grid(column=3, row=0, sticky='n', padx=(10, 20)) 
            self.docwidth = self.docOuterFrame.winfo_width()
            self.showbookmarsboolean = False
            
            root.bind("1", lambda e : self.activateDrag(e))
            root.bind("2", lambda e : self.activateSelection(e))
            root.bind("3", lambda e :  self.activateareaSelection(e))
        except Exception as ex:
            printlogexception(ex=ex)
    
    
    def gotoPage(self,event):
        global pathpdfatual, infoLaudo
        page = self.pagVar.get()
        try:
            pageint = int(page)
            if(pageint > 0 and pageint<=infoLaudo[pathpdfatual].len):
                ondeir = (pageint-1) / infoLaudo[pathpdfatual].len
                self.docInnerCanvas.yview_moveto(ondeir)
                if(str(pageint)!=self.pagVar.get()):
                    self.pagVar.set(str(pageint) )
            else:
                atual = round((self.vscrollbar.get()[0]*infoLaudo[pathpdfatual].len))
                #self.pagVar.set(str(atual+1))
        except Exception as ex:
            atual = round((self.vscrollbar.get()[0]*infoLaudo[pathpdfatual].len))
            #self.pagVar.set(str(atual+1))
    def showAllBookmarks(self):
        if(self.showbookmarsboolean):
            self.showbookmarsboolean = False
            self.showbookmarks.config(relief='raised', state='normal')
            #self.docInnerCanvas.delete("enhanceobs")
            #self.clearSomeImages(["enhanceobs"]) 
            self.clearEnhanceObs()
            
        else:
            self.showbookmarsboolean = True
            self.showbookmarks.config(relief='sunken', state='normal')
            self.clearEnhanceObs()
            if(pathpdfatual in self.allobs):
                for observation in self.allobs[pathpdfatual]:
                    None
                    if(observation.paginainit in processed_pages and observation.paginafim in processed_pages):
                        enhancearea = False
                        enhancetext = False
                        if(observation.tipo=='area'):
                            enhancearea = True
                        elif(observation.tipo=='texto'):
                            enhancetext = True
                        for p in range(observation.paginainit, observation.paginafim+1): 
                            if(p not in processed_pages):
                                continue
                            posicaoRealX0 = observation.p0x
                            posicaoRealY0 = observation.p0y
                            posicaoRealX1 = observation.p1x
                            posicaoRealY1 = observation.p1y
                            iiditem = observation.idobs
                            if(p==observation.paginainit and p==observation.paginafim):
                                self.prepararParaQuads(p, posicaoRealX0, posicaoRealY0, posicaoRealX1, posicaoRealY1, self.colorehnahcebookmark, \
                                                       tag=['enhanceobs'+pathpdfatual+str(p),'enhanceobs'+str(iiditem)], apagar=False,  \
                                                           enhancetext=enhancetext, enhancearea=enhancearea, withborder=False, alt=False)
                            elif(observation.paginainit < p):
                                if(p < observation.paginafim):
                                    self.prepararParaQuads(p, 0, 0, infoLaudo[pathpdfatual].pixorgw, infoLaudo[pathpdfatual].pixorgh, \
                                                           self.colorehnahcebookmark, tag=['enhanceobs'+pathpdfatual+str(p),'enhanceobs'+str(iiditem)], \
                                                           apagar=False,  enhancetext=enhancetext, enhancearea=enhancearea, withborder=False, alt=False)                            
                                else:
                                    self.prepararParaQuads(p, 0, 0, posicaoRealX1, posicaoRealY1, self.colorehnahcebookmark, tag=['enhanceobs'+pathpdfatual+str(p),'enhanceobs'+str(iiditem)], \
                                                           apagar=False,  enhancetext=enhancetext, enhancearea=enhancearea, withborder=False, alt=False)                            
                            else:
                                self.prepararParaQuads(p, posicaoRealX0, posicaoRealY0, infoLaudo[pathpdfatual].pixorgw,  infoLaudo[pathpdfatual].pixorgh, \
                                                       self.colorehnahcebookmark, tag=['enhanceobs'+pathpdfatual+str(p),'enhanceobs'+str(iiditem)], \
                                                           apagar=False,  enhancetext=enhancetext, enhancearea=enhancearea, withborder=False, alt=False) 
    
    def activateareaSelectionCustom(self):
        self.bdrag.config(relief='raised', state='normal')
        self.bselect.config(relief='raised', state='normal')
        self.baselect.config(relief='raised', state='normal')
        self.docFrame.config(cursor="")
        self.docInnerCanvas.config(cursor="crosshair")
        self.selectionActive = False
        self.areaselectionActive = False
        self.areaselectionActiveCustom = True
            
    def activateareaSelection(self, event=None):
        self.bdrag.config(relief='raised', state='normal')
        self.bselect.config(relief='raised', state='normal')
        self.baselect.config(relief='sunken', state='disabled')
        self.docFrame.config(cursor="")
        self.docInnerCanvas.config(cursor="crosshair")
        self.selectionActive = False
        self.areaselectionActive = True
        self.areaselectionActiveCustom = False
        
    
    def activateSelection(self, event=None):
        self.bselect.config(relief='sunken', state='disabled')
        self.baselect.config(relief='raised', state='normal')
        self.bdrag.config(relief='raised', state='normal')
        self.docFrame.config(cursor="")
        self.docInnerCanvas.config(cursor="xterm")
        self.areaselectionActive = False
        self.selectionActive = True
        self.areaselectionActiveCustom = False
        
    def activateDrag(self, event=None):
        self.bdrag.config(relief='sunken', state='disabled')
        self.bselect.config(relief='raised', state='normal')
        self.baselect.config(relief='raised', state='normal')
        self.docFrame.config(cursor="fleur")
        self.docInnerCanvas.config(cursor="fleur")
        self.selectionActive = False
        self.areaselectionActive = False
        self.areaselectionActiveCustom = False
        
    def concatVertical(self, images):
        if(len(images) > 0):
            altura = 0
            for im in images:
                altura += im.height
            dst = Image.new('RGB', (images[0].width, altura))
            posicao = 0
            imagem = 0
            while(imagem < len(images)):
                dst.paste(images[imagem], (0, posicao))
                posicao += images[imagem].height
                imagem += 1                
            return dst
        else:
            return None
        
    def copiar(self, event=None):
        global infoLaudo, pathpdfatual
        doc = None
        try:
            pinit = min(infoLaudo[pathpdfatual].retangulosDesenhados)
            pfim = max(infoLaudo[pathpdfatual].retangulosDesenhados)
            if(self.selectionActive):
                tudo = []                
                for p in infoLaudo[pathpdfatual].retangulosDesenhados:
                    if(p in infoLaudo[pathpdfatual].retangulosDesenhados):
                        ultimatupla = None
                        for tupla in infoLaudo[pathpdfatual].retangulosDesenhados[p]['text']:
                            linha = tupla[0]
                            rect = tupla[1]
                            if(ultimatupla!=None):
                                if(ultimatupla[1].y0+2 >= rect.y0 and ultimatupla[1].y1-2 <= rect.y1):
                                    tudo.append(" ")
                                #elif((infoLaudo[pathpdfatual].pixorgw - ultimatupla[1].x1) > (rect.x1 - rect.x0)):
                                #    tudo.append(" ")
                                else:
                                    tudo.append("\n")
                            else:
                                tudo.append("\n")
                            for char in rect.char:
                                tudo.append(char)
                            
                            ultimatupla = tupla    
                string = ''.join(tudo)
                clipboard.copy(string.strip())
            if(self.areaselectionActive):
                images = []
                for p in range(pinit, pfim+1):
                    if(p in infoLaudo[pathpdfatual].retangulosDesenhados):
                        for tupla in infoLaudo[pathpdfatual].retangulosDesenhados[p]['areaSelection']:
                            linha = tupla[0]
                            rect = tupla[1]
                            pathpdf2 = pathpdfatual
                            if plt == "Linux":
                                pathpdf2 = pathpdf2.replace("\\","/")
                            elif plt=="Windows":
                                pathpdf2 = pathpdf2.replace("/","\\")
                            doc = fitz.open(pathpdf2)
                            loadedPage = doc[p]
                            box = fitz.Rect(rect.x0, rect.y0, rect.x1, rect.y1)
                            pix = loadedPage.getPixmap(alpha=False, matrix=self.mat, clip=box) 
                            mode = "RGBA" if pix.alpha else "RGB"
                            imgdata = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
                            pix = None
                            images.append(imgdata)
                if(len(images) > 0):
                    imagem = self.concatVertical(images)
                    if platform.system() == 'Darwin':       # macOS
                        None
                    elif platform.system() == 'Windows':    # Windows
                        output = BytesIO()
                        imagem.convert("RGB").save(output, "BMP")
                        data = output.getvalue()[14:]
                        output.close()
                        win32clipboard.OpenClipboard()
                        win32clipboard.EmptyClipboard()
                        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                        win32clipboard.CloseClipboard()
                    elif plt == "Linux": 
                        output = BytesIO()
                        imagem.save(output, format="png")
                        #imagem.convert("RGB").save(output, "PNG")
                        clip = subprocess.Popen(("xclip", "-selection", "clipboard", "-t", "image/png", "-i"), 
                          stdin=subprocess.PIPE)
                        # write image to stdin
                        clip.stdin.write(output.getvalue())
                        clip.stdin.close()
        except Exception as ex:
            printlogexception(ex=ex)
        finally:
            if(doc!=None):
                doc.close()
    
    
            
                
    def colectLeavesFromIteminit(self, item, leaves):
        children = self.treeviewSearches.get_children(item)
        if(len(children)>0):
            for child in children:
                self.colectLeavesFromIteminit(child, leaves)
        elif(item in searchResultsDict):
            leaves.append(item)
        
    def addSeveralMarkers(self, obscat, iteminit):
        leaves = []
        self.colectLeavesFromIteminit(iteminit, leaves)
        listadeitenscompleto = manager.list()
        allitens = []
        for leaf in leaves:
            pdf = searchResultsDict[leaf].pathpdf
            allitens.append((searchResultsDict[leaf], infoLaudo[pdf].mt, infoLaudo[pdf].mb, infoLaudo[pdf].me, infoLaudo[pdf].md, infoLaudo[pdf].pixorgw, infoLaudo[pdf].pixorgh))
        #processBatchInsertObs(self, listadeitenscompleto, allitens, mmtopxleft, mmtopxright, mmtopxtop, mmtopxbottom):
        addserveralobs = mp.Process(target=processBatchInsertObs, args=(listadeitenscompleto, allitens,), daemon=True)
        addserveralobs.start()  
        self.checkWhenAddSeveralIsDone(addserveralobs, listadeitenscompleto, obscat)
        
    def qualIndexTreeObs(self, paginaAinserir, imediateParent):
        children = self.treeviewObs.get_children(imediateParent)
        index = 0
        if(len(children)>0):
            for child in children:
                valores = self.treeviewObs.item(child, 'values')
                pagina = int(valores[2])
                if(pagina > int(paginaAinserir)):
                    return index
                else:
                    index += 1
            return index
                
        else:
            return index
        
        
    def checkWhenAddSeveralIsDone(self, processo, lista, obscat):
        if(processo.is_alive()):
            root.after(1000, lambda: self.checkWhenAddSeveralIsDone(processo, lista, obscat))
        else:
            
            try:
                sqliteconn =  connectDB(str(pathdb), 5)
                processo.join()
                #sqliteconn = None
                #cursor = sqliteconn.cursor()
                idobscat = self.treeviewObs.item(obscat, 'values')[1]
                try:
                    for itensproc in lista:
                        p0x = itensproc[0]
                        p0y = itensproc[1]
                        p1x = itensproc[2]
                        p1y = itensproc[3]
                        tipo = 'texto'
                        paginainit = itensproc[4]
                        paginafim  = itensproc[4]
                        sqliteconn.execute("PRAGMA foreign_keys = ON")
                        iid = idobscat
                        insert_query_pdf = """INSERT INTO Anexo_Eletronico_Obsitens
                                                (id_obscat, id_pdf, paginainit, p0x, p0y, paginafim, p1x, p1y, tipo, fixo) VALUES
                                                (?,?,?,?,?,?,?,?,?,?)
                        """
                        fixo = 0
                        if(expertmode):
                            fixo = 1
                        id_pdf = infoLaudo[os.path.normpath(itensproc[5])].id
                        cursor = sqliteconn.cursor()  
                        #cursor.execute("PRAGMA journal_mode=WAL")
                        cursor.execute(insert_query_pdf, (iid, id_pdf, paginainit, p0x, p0y, paginafim, p1x, p1y, tipo, fixo,))
                        iiditem = str(cursor.lastrowid)
                        cursor.close()
                        basepdf = os.path.normpath(itensproc[5])
                        ident = ' '
                        #basepdf = os.path.normpath(os.path.join(pathdb.parent, relpath))
                        beforereplace = basepdf
                        
                        if plt == "Linux":                           
                            pathpdf = str(beforereplace).replace("\\","/")
                        elif plt=="Windows":
             
                            pathpdf = str(beforereplace).replace("/","\\")
                        if(pathpdf in infoLaudo and pathpdf not in self.allobs):
                            self.allobs[pathpdf] = []
                        obsobject = Observation(paginainit, paginafim, p0x, p0y, p1x, p1y, tipo, pathpdf, iiditem)
                        self.allobs[pathpdf].append(obsobject)
                        try:
                            tocname = self.locateToc(paginainit, basepdf, p0y=p0y)
                            if(not self.treeviewObs.exists(str(iid)+basepdf)):
                                self.treeviewObs.insert(parent=str(iid), iid=(str(iid)+basepdf), text=ident+os.path.basename(basepdf), index='end', tag=('relobs'))
                                self.treeviewObs.tag_configure('relobs', background='#e3e1e1')
                            if(not self.treeviewObs.exists(str(iid)+basepdf+tocname)):
                                self.treeviewObs.insert(parent=str(iid)+basepdf, iid=(str(iid)+basepdf+tocname), text=ident+ident+tocname, index='end', tag=('tocobs'))
                            indexinserir = self.qualIndexTreeObs( paginainit, (str(iid)+basepdf+tocname))
                            if(paginainit==paginafim):
                                self.treeviewObs.insert(parent=(str(iid)+basepdf+tocname), index=indexinserir, iid='obsitem'+str(iiditem), text=ident+ident+ident+'Pg.'+str(paginainit+1)+' - '+\
                                                        os.path.basename(itensproc[5]), \
                                                image=self.itemimage, \
                                                    values=(tipo, itensproc[5],str(paginainit), str(p0x), str(p0y), str(paginafim), str(p1x), str(p1y), iiditem, str(fixo), str(iid),),\
                                                    tag=('obsitem',))
                            else:
                                self.treeviewObs.insert(parent=(str(iid)+basepdf+tocname), index=indexinserir, iid='obsitem'+str(iiditem), \
                                                        text=ident+ident+ident+'Pg.'+str(paginainit+1)+' - '+'Pg.'+str(paginafim+1)+' - '+os.path.basename(itensproc[5]), \
                                                image=self.itemimage, \
                                                    values=(tipo, itensproc[5],str(paginainit), str(p0x), str(p0y), str(paginafim), str(p1x), str(p1y), iiditem, str(fixo), str(iid),), \
                                                            tag=('obsitem',))
                        except Exception as ex:
                            printlogexception(ex=ex)
                            if(not self.treeviewObs.exists(str(iid)+basepdf)):
                                self.treeviewObs.insert(parent=str(iid), iid=(str(iid)+basepdf), text=os.path.basename(basepdf), index='end', tag=('relobs'))
                                self.treeviewObs.tag_configure('relobs', background='#e3e1e1')
                            indexinserir = self.qualIndexTreeObs( paginainit, (str(iid)+basepdf))
                            if(paginainit==paginafim):
                                self.treeviewObs.insert(parent=(str(iid)+basepdf), index=indexinserir, iid='obsitem'+str(iiditem), text=ident+ident+'Pg.'+str(paginainit+1)+' - '+\
                                                        os.path.basename(itensproc[5]), \
                                                image=self.itemimage, \
                                                    values=(tipo, itensproc[5],str(paginainit), str(p0x), str(p0y), str(paginafim), str(p1x), str(p1y), iiditem, str(fixo), str(iid),),\
                                                        tag=('obsitem',))
                            else:
                                self.treeviewObs.insert(parent=(str(iid)+basepdf), index=indexinserir, iid='obsitem'+str(iiditem), text=ident+ident+'Pg.'+str(paginainit+1)\
                                                        +' - '+'Pg.'+str(paginafim+1)+' - '+os.path.basename(itensproc[5]), \
                                                image=self.itemimage,\
                                                    values=(tipo, itensproc[5],str(paginainit), str(p0x), str(p0y), str(paginafim), str(p1x), str(p1y), iiditem, str(fixo), str(iid),),\
                                                       tag=('obsitem',) )
                    sqliteconn.commit()
                except Exception as ex:
                    printlogexception(ex=ex)
                finally:
                    #cursor.close()
                    if(sqliteconn):
                        sqliteconn.close()
            except sqlite3.OperationalError:
                root.after(1000, lambda: self.checkWhenAddSeveralIsDone(processo, lista, obscat))                                           
    
    def addmarkerFromSearch(self, obscat, event, first=True):
        item = self.treeviewSearches.identify_row(event.y)
        children = self.treeviewSearches.get_children(item)
        if(len(children)>0 and first):
            self.addSeveralMarkers(obscat, item)
        else:
            resultsearch = searchResultsDict[self.treeviewSearches.identify_row(event.y)]
            pagina = int(resultsearch.pagina)            
            if(pagina not in infoLaudo[pathpdfatual].quadspagina):
                if(first or pagina in processed_pages):
                    root.after(100, lambda: self.addmarkerFromSearch(obscat, event, first=False))
            else:
                try:
                    sqliteconn =  connectDB(str(pathdb), 5)
                    sobraEspaco = 0
                    if(self.docFrame.winfo_width() > infoLaudo[pathpdfatual].pixorgw * self.zoom_x * zoom):
                        sobraEspaco = self.docInnerCanvas.winfo_x() 
                    posicoes = infoLaudo[pathpdfatual].quadspagina[pagina]
                    init = posicoes[resultsearch.init]
                    fim = posicoes[resultsearch.fim-1]
                    p0x = round(init[0])
                    p0y = round((init[1]+init[3])/2)
                    p1x = round(fim[2])
                    p1y = round((fim[1]+fim[3])/2)
                    tipo = 'texto'
                    paginainit = pagina
                    paginafim  = pagina
                    
                    #cursor = sqliteconn.cursor()
                    idobscat = self.treeviewObs.item(obscat, 'values')[1]
                    try:
                        sqliteconn.execute("PRAGMA foreign_keys = ON")
                        iid = idobscat
                        insert_query_pdf = """INSERT INTO Anexo_Eletronico_Obsitens
                                                (id_obscat, id_pdf, paginainit, p0x, p0y, paginafim, p1x, p1y, tipo, fixo) VALUES
                                                (?,?,?,?,?,?,?,?,?,?)
                        """
                        fixo = 0
                        if(expertmode):
                            fixo = 1
                        id_pdf = infoLaudo[os.path.normpath(resultsearch.pathpdf)].id
                        cursor = sqliteconn.cursor() 
                        #cursor.execute("PRAGMA journal_mode=WAL")
                        cursor.execute(insert_query_pdf, (iid, id_pdf, paginainit, p0x, p0y, paginafim, p1x, p1y, tipo, fixo,))
                        iiditem = str(cursor.lastrowid)
                        cursor.close()
                        basepdf = os.path.normpath(resultsearch.pathpdf)
                        ident = ' '
                        #basepdf = os.path.normpath(os.path.join(pathdb.parent, relpath))
                        beforereplace = basepdf
                        
                        if plt == "Linux":                           
                            pathpdf = str(beforereplace).replace("\\","/")
                        elif plt=="Windows":
             
                            pathpdf = str(beforereplace).replace("/","\\")
                        if(pathpdf in infoLaudo and pathpdf not in self.allobs):
                            self.allobs[pathpdf] = []
                        obsobject = Observation(paginainit, paginafim, p0x, p0y, p1x, p1y, tipo, pathpdf, iiditem)
                        self.allobs[pathpdf].append(obsobject)
                        try:
                            tocname = self.locateToc(paginainit, basepdf, p0y=p0y)
                            if(not self.treeviewObs.exists(str(iid)+basepdf)):
                                self.treeviewObs.insert(parent=str(iid), iid=(str(iid)+basepdf), text=ident+os.path.basename(basepdf), index='end', tag=('relobs'))
                                self.treeviewObs.tag_configure('relobs', background='#e3e1e1')
                            if(not self.treeviewObs.exists(str(iid)+basepdf+tocname)):
                                self.treeviewObs.insert(parent=str(iid)+basepdf, iid=(str(iid)+basepdf+tocname), text=ident+ident+tocname, index='end', tag=('tocobs'))
                            indexinserir = self.qualIndexTreeObs( paginainit, (str(iid)+basepdf+tocname))
                            if(paginainit==paginafim):
                                self.treeviewObs.insert(parent=(str(iid)+basepdf+tocname), index=indexinserir, iid='obsitem'+str(iiditem), text=ident+ident+ident+'Pg.'+str(paginainit+1)+' - '+\
                                                        os.path.basename(resultsearch.pathpdf), \
                                                image=self.itemimage, \
                                                    values=(tipo, resultsearch.pathpdf,str(paginainit), str(p0x), str(p0y), str(paginafim), str(p1x), str(p1y), iiditem, str(fixo), str(iid),),\
                                                    tag=('obsitem',))
                            else:
                                self.treeviewObs.insert(parent=(str(iid)+basepdf+tocname), index=indexinserir, iid='obsitem'+str(iiditem), \
                                                        text=ident+ident+ident+'Pg.'+str(paginainit+1)+' - '+'Pg.'+str(paginafim+1)+' - '+os.path.basename(resultsearch.pathpdf), \
                                                image=self.itemimage, \
                                                    values=(tipo, resultsearch.pathpdf,str(paginainit), str(p0x), str(p0y), str(paginafim), str(p1x), str(p1y), iiditem, str(fixo), str(iid),), \
                                                            tag=('obsitem',))
                        except Exception as ex:
                            printlogexception(ex=ex)
                            if(not self.treeviewObs.exists(str(iid)+basepdf)):
                                self.treeviewObs.insert(parent=str(iid), iid=(str(iid)+basepdf), text=os.path.basename(basepdf), index='end', tag=('relobs'))
                                self.treeviewObs.tag_configure('relobs', background='#e3e1e1')
                            indexinserir = self.qualIndexTreeObs( paginainit, (str(iid)+basepdf))
                            if(paginainit==paginafim):
                                self.treeviewObs.insert(parent=(str(iid)+basepdf), index=indexinserir, iid='obsitem'+str(iiditem), text=ident+ident+'Pg.'+str(paginainit+1)+' - '+os.path.basename(resultsearch.pathpdf), \
                                                image=self.itemimage, \
                                                    values=(tipo, resultsearch.pathpdf,str(paginainit), str(p0x), str(p0y), str(paginafim), str(p1x), str(p1y), iiditem, str(fixo), str(iid),),\
                                                        tag=('obsitem',))
                            else:
                                self.treeviewObs.insert(parent=(str(iid)+basepdf), index=indexinserir, iid='obsitem'+str(iiditem), text=ident+ident+'Pg.'+str(paginainit+1)\
                                                        +' - '+'Pg.'+str(paginafim+1)+' - '+os.path.basename(resultsearch.pathpdf), \
                                                image=self.itemimage,\
                                                    values=(tipo, resultsearch.pathpdf,str(paginainit), str(p0x), str(p0y), str(paginafim), str(p1x), str(p1y), iiditem, str(fixo), str(iid),),\
                                                       tag=('obsitem',) )
                        sqliteconn.commit()
                    except Exception as ex:
                        printlogexception(ex=ex)
                            
                    finally:
                
                        #cursor.close()
                        
                        if(sqliteconn):
                            sqliteconn.close()
                except sqlite3.OperationalError:
                    root.after(1000, lambda: self.addmarkerFromSearch(obscat, event, first=False))    

    def addmarker(self, obscat=None, p0x = None, p0y = None, p1x = None, p1y = None, paginainit = None, paginafim = None, tipo = None):
        
        if(p0x==None):
            tipo = None
            p0x = None
            p0y = None
            p1x = None
            p1y = None
            paginainit = min(infoLaudo[pathpdfatual].retangulosDesenhados)
            paginafim = max(infoLaudo[pathpdfatual].retangulosDesenhados)
            if(self.selectionActive):
                tipo = 'texto'
                pagina =paginainit
                p0x = 1000000000000
                p0y = 1000000000000
                p1x = -100000000000
                p1y = -1000000000000
                for tupla in infoLaudo[pathpdfatual].retangulosDesenhados[pagina]['text']:
                    if(tupla[1].y0 <= p0y):
                        p0x = min(p0x, tupla[1].x0)
                        p0y = (tupla[1].y0+tupla[1].y1)/2
                pagina2 = paginafim
                for tupla in infoLaudo[pathpdfatual].retangulosDesenhados[pagina2]['text']:
                    if(tupla[1].y1>= p1y):
                        p1x = tupla[1].x1
                        p1y = (tupla[1].y0+tupla[1].y1)/2
            elif(self.areaselectionActive):
                p0x = infoLaudo[pathpdfatual].retangulosDesenhados[paginainit]['areaSelection'][0][1].x0
                p0y = infoLaudo[pathpdfatual].retangulosDesenhados[paginainit]['areaSelection'][0][1].y0         
                p1x = infoLaudo[pathpdfatual].retangulosDesenhados[paginafim]['areaSelection'][0][1].x1
                p1y = infoLaudo[pathpdfatual].retangulosDesenhados[paginafim]['areaSelection'][0][1].y1 
                tipo = 'area'   
        try:
            sqliteconn =  connectDB(str(pathdb), 5)
            cursor = sqliteconn.cursor()   
            #cursor.execute("PRAGMA journal_mode=WAL")
            try:
                sqliteconn.execute("PRAGMA foreign_keys = ON")
                select_query = "SELECT O.id_obscat, O.fixo FROM Anexo_Eletronico_Obscat O WHERE O.obscat = ?"
                cursor.execute(select_query, (obscat,))
                iid = cursor.fetchone()[0]
                insert_query_pdf = """INSERT INTO Anexo_Eletronico_Obsitens
                                        (id_obscat, id_pdf, paginainit, p0x, p0y, paginafim, p1x, p1y, tipo, fixo) VALUES
                                        (?,?,?,?,?,?,?,?,?,?)
                """
                fixo = 0
                if(expertmode):
                    fixo = 1
                relpath = os.path.relpath(pathpdfatual, pathdb.parent)
                id_pdf = infoLaudo[pathpdfatual].id
                cursor.execute(insert_query_pdf, (iid, id_pdf, paginainit, p0x, p0y, paginafim, p1x, p1y, tipo, fixo,))
                iiditem = str(cursor.lastrowid)
                sqliteconn.commit()
                try:
                    cursor.close() 
                except Exception as ex:
                    None
                try:
                    sqliteconn.close()
                except Exception as ex:
                    None
                enhancearea = False
                enhancetext = False
                if(tipo=='area'):
                    enhancearea = True
                elif(tipo=='texto'):
                    enhancetext = True
                for p in range(paginainit, paginafim+1): 
                    posicaoRealX0 = p0x
                    posicaoRealY0 = p0y
                    posicaoRealX1 = p1x
                    posicaoRealY1 = p1y
                    if(p==paginainit and p==paginafim):
                        self.prepararParaQuads(p, posicaoRealX0, posicaoRealY0, posicaoRealX1, posicaoRealY1, color=self.colorehnahcebookmark, \
                                               tag=['enhanceobs'+pathpdfatual+str(p),'enhanceobs'+str(iiditem)], apagar=False, \
                                                   enhancetext=enhancetext, enhancearea=enhancearea, withborder=False, alt=False)
                    elif(paginainit < p):
                        if(p < paginafim):
                            self.prepararParaQuads(p, 0, 0, infoLaudo[pathpdfatual].pixorgw, infoLaudo[pathpdfatual].pixorgh, \
                                                   color=self.colorehnahcebookmark, tag=['enhanceobs'+pathpdfatual+str(p),'enhanceobs'+str(iiditem)], \
                                                   apagar=False,  enhancetext=enhancetext, enhancearea=enhancearea, withborder=False, alt=False)                            
                        else:
                            self.prepararParaQuads(p, 0, 0, posicaoRealX1, posicaoRealY1, color=self.colorehnahcebookmark, tag=['enhanceobs'+pathpdfatual+str(p),'enhanceobs'+str(iiditem)], \
                                                   apagar=False,  enhancetext=enhancetext, enhancearea=enhancearea, withborder=False, alt=False)                            
                    else:
                        self.prepararParaQuads(p, posicaoRealX0, posicaoRealY0, infoLaudo[pathpdfatual].pixorgw,  infoLaudo[pathpdfatual].pixorgh, \
                                               color=self.colorehnahcebookmark, tag=['enhanceobs'+pathpdfatual+str(p),'enhanceobs'+str(iiditem)], \
                                                   apagar=False,  enhancetext=enhancetext, enhancearea=enhancearea, withborder=False, alt=False) 
                 
                basepdf = os.path.normpath(pathpdfatual)
                ident = ' '
               # basepdf = os.path.normpath(os.path.join(pathdb.parent, relpath))
                beforereplace = basepdf
                
                if plt == "Linux":                           
                    pathpdf = str(beforereplace).replace("\\","/")
                elif plt=="Windows":
     
                    pathpdf = str(beforereplace).replace("/","\\")
                if(pathpdf in infoLaudo and pathpdf not in self.allobs):
                    self.allobs[pathpdf] = []
                obsobject = Observation(paginainit, paginafim, p0x, p0y, p1x, p1y, tipo, pathpdf, iiditem)
                self.allobs[pathpdf].append(obsobject)
                try:
                    tocname = self.locateToc(paginainit, basepdf, p0y=p0y)
                    if(not self.treeviewObs.exists(str(iid)+basepdf)):
                        self.treeviewObs.insert(parent=str(iid), iid=(str(iid)+basepdf), text=ident+os.path.basename(basepdf), index='end', tag=('relobs'))
                        self.treeviewObs.tag_configure('relobs', background='#e3e1e1')
                    if(not self.treeviewObs.exists(str(iid)+basepdf+tocname)):
                        self.treeviewObs.insert(parent=str(iid)+basepdf, iid=(str(iid)+basepdf+tocname), text=ident+ident+tocname, index='end', tag=('tocobs'))
                    indexinserir = self.qualIndexTreeObs( paginainit, (str(iid)+basepdf+tocname))
                    if(paginainit==paginafim):
                        self.treeviewObs.insert(parent=(str(iid)+basepdf+tocname), index=indexinserir, iid='obsitem'+str(iiditem), text=ident+ident+ident+'Pg.'+str(paginainit+1)+' - '+os.path.basename(pathpdfatual), \
                                            image=self.itemimage, values=(tipo, pathpdfatual,str(paginainit), str(p0x), str(p0y), str(paginafim), str(p1x), str(p1y), iiditem, str(fixo), str(iid),),
                                            tag=('obsitem',))
                    else:
                        self.treeviewObs.insert(parent=(str(iid)+basepdf+tocname), index=indexinserir, iid='obsitem'+str(iiditem), text=ident+ident+ident+'Pg.'+str(paginainit+1)+' - '+'Pg.'+str(paginafim+1)+' - '+os.path.basename(relpath), \
                                            image=self.itemimage, values=(tipo, pathpdfatual,str(paginainit), str(p0x), str(p0y), str(paginafim), str(p1x), str(p1y), iiditem, str(fixo), str(iid),),
                                            tag=('obsitem',))
                except Exception as ex:
                    if(not self.treeviewObs.exists(str(iid)+basepdf)):
                        self.treeviewObs.insert(parent=str(iid), iid=(str(iid)+basepdf), text=ident+basepdf, index='end', tag=('relobs'))
                        self.treeviewObs.tag_configure('relobs', background='#e3e1e1')
                    indexinserir = self.qualIndexTreeObs( paginainit, (str(iid)+basepdf))
                    if(paginainit==paginafim):
                        self.treeviewObs.insert(parent=(str(iid)+basepdf), index=indexinserir, iid='obsitem'+str(iiditem), text=ident+ident+'Pg.'+str(paginainit+1)+' - '+os.path.basename(pathpdfatual), \
                                            image=self.itemimage, values=(tipo, pathpdfatual,str(paginainit), str(p0x), str(p0y), str(paginafim), str(p1x), str(p1y), iiditem, str(fixo), str(iid),),
                                            tag=('obsitem',))
                    else:
                        self.treeviewObs.insert(parent=(str(iid)+basepdf), index=indexinserir, iid='obsitem'+str(iiditem), text=ident+ident+'Pg.'+str(paginainit+1)+' - '+'Pg.'+str(paginafim+1)+' - '+os.path.basename(relpath), \
                                            image=self.itemimage, values=(tipo, pathpdfatual,str(paginainit), str(p0x), str(p0y), str(paginafim), str(p1x), str(p1y), iiditem, str(fixo), str(iid),),
                                            tag=('obsitem',))
                #sqliteconn.commit()
            except Exception as ex:
                printlogexception(ex=ex)                
            finally:    
                try:
                    cursor.close() 
                except Exception as ex:
                    None
                try:
                    sqliteconn.close()
                except Exception as ex:
                    None
        except sqlite3.OperationalError:
            root.after(1000, lambda: self.addmarker(obscat=obscat, p0x = p0x, p0y = p0y, p1x = p1x, p1y = p1y, paginainit = paginainit, paginafim = paginafim, tipo = tipo))    
                
    def selectReport(self, item):
        self.treeviewEqs.selection_set(item)
        self.treeview_selection(item=item)
    '''    
    def addrels(self, tipo):
        global searchqueue, totalpaginas
        #toplevelfromviewer = tkinter.Toplevel()
        maiorresult = 0
        ok = addrelfromfiewer(tipo, root)
        #root.wait_window(toplevelfromviewer)
        if(ok[0]):
            #toplevelfromviewer.destroy()
            if plt == "Linux":                   
                abs_path_pdf = str(ok[2]).replace("\\","/")
            elif plt=="Windows":     
                abs_path_pdf = str(ok[2]).replace("/","\\")
            abs_path_pdf = os.path.normpath(abs_path_pdf)
            pathpd = os.path.relpath(Path(abs_path_pdf).parent, pathdb.parent)
            novorelatorio = Relatorio()
            filename, file_extension = os.path.splitext(abs_path_pdf)
           
            doc = fitz.open(abs_path_pdf)   
            pdf = os.path.basename(abs_path_pdf)
            idpdf= ok[1]
            novorelatorio.mt = ok[3]
            novorelatorio.mb = ok[4]
            novorelatorio.me = ok[5]
            novorelatorio.md = ok[6]
            novorelatorio.id = idpdf
            novorelatorio.len = len(doc)
            totalpaginas += novorelatorio.len
            pageorg = doc[0]
            pixorg = pageorg.getPixmap()
            novorelatorio.pixorgw = pixorg.width
            novorelatorio.pixorgh = pixorg.height
            sqliteconn = sqlite3.connect(str(pathdb), timeout=30)
            cursor = sqliteconn.cursor()        
            try:
                select_tocs = SELECT  T.toc_unit, T.pagina, T.deslocy, T.init FROM 
                Anexo_Eletronico_Tocs T WHERE T.id_pdf = ? ORDER BY 2,3
                                
                cursor.execute(select_tocs, (idpdf,))
                tocs = cursor.fetchall()
                for toc in tocs:
                    novorelatorio.toc.append((toc[0], toc[1], toc[2], toc[3]))
                infoLaudo[abs_path_pdf] = novorelatorio
                infoLaudo[abs_path_pdf].ultimaPosicao=0.0
                infoLaudo[abs_path_pdf].tipo = tipo
                infoLaudo[abs_path_pdf].idpdf = idpdf
                teste = 'SELECT 1 FROM Anexo_Eletronico_Conteudo_id_pdf_' + str(idpdf) + ' LIMIT 1'
                
                cursor.execute(teste)                    
                relatorio = abs_path_pdf
                p = Path(relatorio)
                pai = Path(p.parent).parent
                paibase = os.path.basename(pai)
                pdfbase = os.path.basename(p)
                #tipo = "pdf"
            except Exception as ex:
                printlogexception(ex=ex)                
            finally:    
                cursor.close()            
                if(sqliteconn):
                    sqliteconn.close()
            try:
                if(infoLaudo[relatorio].tipo=='laudo'):
                    self.treeviewEqs.insert(parent='', index='end', iid=pai, text='LAUDO', image=self.imageequip, tag='equipmentlp', values=('eq', str(paibase),))
                else:
                    self.treeviewEqs.insert(parent='', index='end', iid=pai, text=paibase.upper(), image=self.imageequip, tag='equipmentlp', values=('eq', str(paibase),))
            except Exception as ex:
                None
            self.treeviewEqs.insert(parent=pai, index='end', iid=str(p), text=pdfbase, tag='reportlp', image=self.imagereportb, values=(tipo, str(p),))                
            self.treeviewEqs.see(str(p))
            for t in infoLaudo[relatorio].toc:
                nivel = t[0].split(' ')[0].split('.')
                ident = ''
                for k in range(len(nivel)):
                    ident += '     '
                self.treeviewEqs.insert(parent=str(p), index='end', text=ident+t[0], values=('toc', str(p), t[0], t[1], t[2],))
                somatexto = paibase.upper()+pdfbase+t[0]
                tamanho = self.resultfont.measure(pdfbase)+150
                if(tamanho>maiorresult):
                    maiorresult = tamanho
                    self.treeviewEqs.column("#0", width=maiorresult, stretch=True, minwidth=maiorresult, anchor="w")
            
            
            for busca in self.searchedTerms:
                termo = busca[0]
                tipobusca = busca[1]
                pdf = ok[1]
                searchqueue.put((termo, tipobusca, pdf))
    '''
    def showAbout(self, event=None):
        None
        
    def openHelp(self):
        arquivo = "FERA - Instruções de Uso.pdf"
        if getattr(sys, 'frozen', False):
            application_path = sys._MEIPASS
        elif __file__:
            application_path = os.path.dirname(os.path.abspath(__file__))
        
        filepath = os.path.join(application_path,arquivo)
    
        
        try:
            
            if platform.system() == 'Darwin':       # macOS
                subprocess.call(('open', filepath), shell=True)
            elif platform.system() == 'Windows':    # Windows
                os.startfile(filepath)
            else:           
                #ommand ='xdg-open {filepath}'.format(filepath=filepath)
                #ommand = ['xdg-open', filepath]
                
                
                openfile = ['xdg-open', filepath]
                resultmime = subprocess.run(openfile, check=True, text=True)
                
                
                    
        except Exception as ex:
            printlogexception(ex=ex)
            popup_window('O arquivo não possui um \nprograma associado para abertura!', False)

    def menuReports(self, event=None):
        try:
            #self.menueqsButton(root)
            self.reportbut.menu = tkinter.Menu(self.reportbut, tearoff=0)
            self.reportbut["menu"]= self.reportbut.menu  
            # = self.menueqs
            self.menureportsbyeq = {}
            geteqs =  self.treeviewEqs.get_children('')
            for eq in geteqs:
                patheq = self.treeviewEqs.item(eq, 'text')
                self.menureportsbyeq[patheq] = tkinter.Menu(root, tearoff=0)
                #self.menureportsbyeq[patheq].post(-100, 50)
                primeiracamada =  self.treeviewEqs.get_children(eq)
                for reports in primeiracamada:
                    self.menureportsbyeq[patheq].add_command(label=reports, image=self.catimage, compound='left', command=partial(self.selectReport,reports))
                   # self.menureportsbyeq[patheq].post(-100, 50)
                self.reportbut.menu.add_cascade(label=patheq, menu=self.menureportsbyeq[patheq], image=self.imageequip, compound='left')
            self.reportbut.menu.add_separator()
            #self.opcaoadd = tkinter.Menu(root, tearoff=0)
            #self.opcaoadd.add_command(label='Laudo', command=partial(self.addrels,'laudo'), image=self.imagereportb, compound='left')
            #self.opcaoadd.add_command(label='Relatorio', command=partial(self.addrels,'relatorio'), image=self.imagereportb, compound='left')
            texto = " FERA - Forensics Evidence Report Analyzer \n"+\
                    "* License: GNU Affero General Public License v3.0\n\n"+\
                    "STATE DEPARTMENT OF PUBLIC SECURITY -- SCIENTIFIC POLICE OF PARANÁ\n\n"+\
                    "  CODED BY by:\nGustavo Borelli Bedendo <gustavo.bedendo@gmail.com>\n\n"+\
                    "  SUPPORTERS :\nAlexandre Vrubel\nRoger Roberto Rocha Duarte\nWellerson Jeremias Colombari\n\n\n\n"+\
                    "  MAIN TESTERS AND USAGE IDEAS:\nConrado Pinto Rebessi\nJacson Gluzezak\nMarcus Fabio Fontenelle do Carmo\nRaphael Zago\n"+\
                    "\n\nApril 2021\n\n"+\
                    "It is a work in progress, the code, \ndespite the ugliness and some bugs, is available on:\n"+\
                    "https://github.com/gustavobedendo/FERA"
            self.reportbut.menu.add_command(label='Ajuda', image=self.helpimage , compound='left', command= self.openHelp)           

            self.reportbut.menu.add_separator()
            self.reportbut.menu.add_command(label='Sobre', image=self.aboutimage , compound='left', command= lambda: popup_window(texto, False, imagepcp=self.tkphotologo))
            self.reportbut.pack()
            #self.menueqs.tk_popup(self.reportbut.winfo_rootx()-100,self.reportbut.winfo_rooty())         
        except Exception as ex:
            printlogexception(ex=ex) 
        finally:
            None
            #self.menueqs.grab_release()  
            
    def addlink(self, item =None, p0x = None, p0y = None, p1x = None, p1y = None, paginainit = None, paginafim = None, tipo = None): 
        if(item==None):
            tipo = None
            p0x = None
            p0y = None
            p1x = None
            p1y = None
            paginainit = min(infoLaudo[pathpdfatual].retangulosDesenhados)
            paginafim = max(infoLaudo[pathpdfatual].retangulosDesenhados)
            if(self.selectionActive):
                tipo = 'texto'           
                p0x = 1000000000000
                p0y = 1000000000000
                p1x = -100000000000
                p1y = -1000000000000
                for tupla in infoLaudo[pathpdfatual].retangulosDesenhados[paginainit]['text']:
                    if(tupla[1].y0 <= p0y):
                        p0x = min(p0x, tupla[1].x0)
                        p0y = (tupla[1].y0+tupla[1].y1)/2
                pagina2 = paginafim
                for tupla in infoLaudo[pathpdfatual].retangulosDesenhados[paginafim]['text']:
                    if(tupla[1].y1>= p1y):
                        p1x = tupla[1].x1
                        p1y = (tupla[1].y0+tupla[1].y1)/2
            elif(self.areaselectionActive):
                p0x = infoLaudo[pathpdfatual].retangulosDesenhados[paginainit]['areaSelection'][0][1].x0
                p0y = infoLaudo[pathpdfatual].retangulosDesenhados[paginainit]['areaSelection'][0][1].y0            
                p1x = infoLaudo[pathpdfatual].retangulosDesenhados[paginafim]['areaSelection'][0][1].x1
                p1y = infoLaudo[pathpdfatual].retangulosDesenhados[paginafim]['areaSelection'][0][1].y1
                tipo = 'area'   
        try:
            sqliteconn =  connectDB(str(pathdb), 5)
            
            
            try:
                sqliteconn.execute("PRAGMA foreign_keys = ON")
                insert_query_pdf = """INSERT INTO Anexo_Eletronico_Links
                                        (paginainit, p0x, p0y, paginafim, p1x, p1y, tipo, id_obs, id_pdf, fixo) VALUES
                                        (?,?,?,?,?,?,?,?,?,?)
                """
                idpdf = infoLaudo[pathpdfatual].idpdf
                fixo = 0
                if(expertmode):
                    fixo = 1
                relpath = os.path.relpath(pathpdfatual, pathdb.parent)
                idobs = self.treeviewObs.item(item, 'values')[8]
                cursor = sqliteconn.cursor()
                #cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute(insert_query_pdf, (paginainit, p0x, p0y+2, paginafim, p1x, p1y-2, tipo, idobs, idpdf, fixo,))
                iid = str(cursor.lastrowid)
                sqliteconn.commit()
                cursor.close()            
                if(sqliteconn):
                    sqliteconn.close()
                self.docInnerCanvas.addtag_withtag("link","quad")
                self.docInnerCanvas.addtag_withtag("link"+str(iid),"quad")
                listaquads = self.docInnerCanvas.find_withtag("quad")
                for quadelement in listaquads:
                    self.docInnerCanvas.dtag(quadelement, "quad")
                    box = (self.docInnerCanvas.bbox(quadelement))
                    pagina = math.floor(box[1] / (infoLaudo[pathpdfatual].pixorgh *self.zoom_x*zoom))
                    infoLaudo[pathpdfatual].linkscustom[quadelement] = []
                    infoLaudo[pathpdfatual].linkscustom[quadelement].append((box, pagina, item, iid, idobs, idpdf, fixo,))
                    imagem = (self.create_rectanglex(box[0], box[1], box[2], box[3], (175, 200, 240, 95), link=True))
                    self.linkscustom.append(imagem)
                    self.docInnerCanvas.itemconfig(quadelement, image=imagem, )                
                pp = paginainit
                up = paginafim
                enhancearea = False
                enhancetext = False
                sobraEspaco = 0
                if(self.docFrame.winfo_width() > infoLaudo[pathpdfatual].pixorgw * self.zoom_x * zoom):
                    sobraEspaco = self.docInnerCanvas.winfo_x()
                if(tipo=='area'):
                    enhancearea = True
                elif(tipo=='texto'):
                    enhancetext = True
                for p in range(pp, up+1):                
                    if(p==pp and p==up):
                        if 'falta'+str(p) not in infoLaudo[pathpdfatual].linkscustom:
                            infoLaudo[pathpdfatual].linkscustom['falta'+str(p)] = []
                        infoLaudo[pathpdfatual].linkscustom['falta'+str(p)].append((p, p0x, p0y, p1x, p1y, pp, up, sobraEspaco, enhancetext, \
                                                                         enhancearea, (175,200,240,95), iid, idobs, fixo, idpdf))                        
                    elif(pp < p):
                        if(p < up):
                            if 'falta'+str(p) not in infoLaudo[pathpdfatual].linkscustom:
                                infoLaudo[pathpdfatual].linkscustom['falta'+str(p)] = []
                            infoLaudo[pathpdfatual].linkscustom['falta'+str(p)].append((p, 0, 0, infoLaudo[pathpdfatual].pixorgw , infoLaudo[pathpdfatual].pixorgh, pp, up, \
                                                                             sobraEspaco, enhancetext, enhancearea, (175,200,240,95),  iid, idobs, fixo, idpdf))
                        else:
                            if 'falta'+str(p) not in infoLaudo[pathpdfatual].linkscustom:
                                infoLaudo[pathpdfatual].linkscustom['falta'+str(p)] = []
                            infoLaudo[pathpdfatual].linkscustom['falta'+str(p)].append((p, 0, 0, p1x, p1y, pp, up, sobraEspaco, enhancetext, enhancearea, (175,200,240,95),\
                                                                             iid, idobs, fixo, idpdf))
                    else:
                        if 'falta'+str(p) not in infoLaudo[pathpdfatual].linkscustom:
                                infoLaudo[pathpdfatual].linkscustom['falta'+str(p)] = []
                        infoLaudo[pathpdfatual].linkscustom['falta'+str(p)].append((p, p0x, p0y, infoLaudo[pathpdfatual].pixorgw , infoLaudo[pathpdfatual].pixorgh , pp, up, sobraEspaco, \
                                                                             enhancetext, enhancearea,(175,200,240,95),iid, idobs, fixo, idpdf))
                
            except Exception as ex:
                printlogexception(ex=ex)                
            finally: 
                try:
                    #try:
                    #    cursor.close() 
                    #except Exception as ex:
                    #    None
                    try:
                        sqliteconn.close()
                    except Exception as ex:
                        None
                except Exception as ex:
                    None
        except sqlite3.OperationalError:
            root.after(1000, lambda: self.addlink(item=item, p0x = p0x, p0y = p0y, p1x = p1x, p1y = p1y, paginainit = paginainit, paginafim = paginafim, tipo = tipo))  
            
    def dellink(self, quaditem):
        valores = infoLaudo[pathpdfatual].linkscustom[quaditem]
        sqliteconn = None
        cursor = None
        notok = True        
        while(notok):
            try:
                sqliteconn = connectDB(str(pathdb), 5)
                cursor = sqliteconn.cursor()
                #cursor.execute("PRAGMA journal_mode=WAL")
                if(expertmode):
                    sqliteconn.execute("PRAGMA foreign_keys = ON")
                    cursor.execute("DELETE FROM Anexo_Eletronico_Links WHERE id_link = ?", (valores[3],))
                    listaquads = self.docInnerCanvas.find_withtag("link"+str(valores[3]))
                    self.docInnerCanvas.delete("link"+str(valores[3]))
                    for quadelement in listaquads:
                        del infoLaudo[pathpdfatual].linkscustom[quadelement]
                    sqliteconn.commit()   
                else:
                    if(valores[6]==0):
                        sqliteconn.execute("PRAGMA foreign_keys = ON")
                        cursor.execute("DELETE FROM Anexo_Eletronico_Links WHERE id_link = ?", (valores[3],))
                        listaquads = self.docInnerCanvas.find_withtag("link"+str(valores[3]))
                        self.docInnerCanvas.delete("link"+str(valores[3]))
                        for quadelement in listaquads:
                            del infoLaudo[pathpdfatual].linkscustom[quadelement]
                        sqliteconn.commit() 
                notok = False
            except sqlite3.OperationalError:
                    time.sleep(2)            
            except Exception as ex:
                printlogexception(ex=ex)
            finally:
                if(cursor):
                    cursor.close()
                if(sqliteconn):
                    sqliteconn.close()
    
    def saveas(self, initialf, asbpathfile):
        path = (asksaveasfilename(initialfile=initialf))
        if(path!=None and path!=''):
            shutil.copyfile(asbpathfile, path)
                
    def menuSaveas(self, initialf, asbpathfile, event=None):
        self.menusaveas = tkinter.Menu(root, tearoff=0)
        try:
            self.menusaveas.add_command(label="Salvar como", command= lambda : self.saveas(initialf, asbpathfile))
            self.menusaveas.tk_popup(event.x_root, event.y_root) 
        except Exception as ex:
            None
        finally:
            self.menusaveas.grab_release()
                
    def menuPopup(self, event):
        if(self.areaselectionActive or self.selectionActive):
            self.menu = tkinter.Menu(root, tearoff=0)
            self.menu.add_command(label="Copiar", command=self.copiar)
            self.menu.add_separator()
            menus = []
            listaquads = self.docInnerCanvas.find_withtag("link")
            ehLink = False
            for quadelement in listaquads:
                bbox = self.docInnerCanvas.bbox(quadelement)
                if(self.docInnerCanvas.canvasx(event.x) >= bbox[0] and self.docInnerCanvas.canvasy(event.y) >= bbox[1] \
                   and self.docInnerCanvas.canvasx(event.x) <= bbox[2] and self.docInnerCanvas.canvasy(event.y) <= bbox[3]):
                    ehLink = True
                    self.menu.add_command(label='Excluir link', image=self.delcat, compound='left', command=partial(self.dellink,quadelement))
            if(not ehLink):
                getleafs =  self.treeviewObs.tag_has('obsitem')
                cats = {}
                for leaf in getleafs:                    
                    parent = self.treeviewObs.parent(leaf)
                    if(parent==''):
                        None
                    else:
                        while(True):
                            if(self.treeviewObs.parent(parent)==''):
                                break
                            parent = self.treeviewObs.parent(parent)
                            
                    if(not parent in cats):
                        cats[parent] = []
                    cats[parent].append(leaf)
                menucats = tkinter.Menu(self.menu, tearoff=0)                
                for obscat in cats:
                    menuitens = tkinter.Menu(menucats, tearoff=0)
                    for obsitens in cats[obscat]:                        
                        item = self.treeviewObs.item(obsitens, 'text')
                        menuitens.add_command(label=item, image=self.itemimage, compound='left', command=partial(self.addlink,obsitens))
                    cat = self.treeviewObs.item(obscat, 'text')
                    menucats.add_cascade(label=cat, menu=menuitens, image=self.catimage, compound='left')
                self.menu.add_cascade(label='Adicionar link', menu=menucats, image=self.linkimage, compound='left')
            getobscatas =  self.treeviewObs.get_children('')
            self.menucats = tkinter.Menu(self.menu, tearoff=0)
            for obscat in getobscatas:
                cat = self.treeviewObs.item(obscat, 'text')
                self.menucats.add_command(label=cat, image=self.catimage, compound='left', command=partial(self.addmarker,cat))
            self.menu.add_cascade(label='Adicionar marcador', menu=self.menucats, image=self.itemimage, compound='left')
            try:
                if(len(self.docInnerCanvas.find_withtag('quad')) == 0):
                    self.menu.entryconfig(0, state='disabled')
                    if(not ehLink):
                        self.menu.entryconfig(2, state='disabled')
                else:
                    self.menu.entryconfig(0, state='normal')
                    self.menu.entryconfig(2, state='normal')
                self.menu.tk_popup(event.x_root, event.y_root)         
            except Exception as ex:
                printlogexception(ex=ex)
            finally:
                self.menu.grab_release()
        else:
            self.rightClickOnOpenableFile(event)
                
    def scrollzoom(self, event=None):
        try:
            if (event.delta>0):
                 self.zoomx(tipozoom='plus')
            else:
                 self.zoomx(tipozoom='minus')
        except Exception as ex:
            printlogexception(ex=ex)
    def focusSimpleSearch(self, event):
        self.simplesearch.focus()
        self.simplesearch.selection_range(0, 'end')

    
    def drawCanvas(self):
        global minMaxLabels, divididoEm, pathpdfatual, infoLaudo, zoom, margemesq, margemdir
        try:
            self.f12 = False
            linkimageb = b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAqklEQVRIie2UsQ2FMAxETxkiQ9AyHIz4aX7DCGEDBoDiGwl9sM+BUCA4KU3iu+c4UoAnqwMwKWu8GjCVAKwVAfQMEAC0AAajq46EryEbtUawBvgPjxZg6bzaO3R0HmVfBeQ8jhZeBGCFA78x7r2VC8DCTTHAqXAGODwWL+BrhDOvq+gjEG0spwFFvC+Aepe/qM4Mr8SXWKHnN7VWwwBBilJmcBJf8Fz3fpoBnR6QQ589hA8AAAAASUVORK5CYII='
            self.linkimage = tkinter.PhotoImage(data=linkimageb)
            self.docFrame = CustomFrame(self.docOuterFrame, bg=self.bg, highlightthickness=0)
            self.docFrame.grid(column=0, row=1, sticky='nsew',padx=0, pady=0,)  
            self.docFrame.rowconfigure(0, weight=1)
            self.docFrame.columnconfigure(0, weight=1)
            
            self.docInnerCanvas = CustomCanvas(self.docFrame, bg='white', highlightthickness=0, relief="raised")    
            self.docInnerCanvas.grid(row=0, column=0, padx=0, pady=0, sticky='ns')
            self.docInnerCanvas.rowconfigure(0, weight=1)
            self.docInnerCanvas.columnconfigure(0, weight=1)
    
            self.vscrollbar = tkinter.Scrollbar(self.docFrame, orient='vertical', cursor="left_ptr")
            self.vscrollbar.grid(row=0, column=1, sticky='nse')
            self.vscrollbar.config( command = self.docInnerCanvas.yview )
            self.labeldocname = tkinter.Label(self.docFrame, text="")
            self.labeldocname.grid(row=2, column=0, sticky='ew')
            self.docInnerCanvas.bind("<MouseWheel>", self._on_mousewheel)
            self.docInnerCanvas.bind("<Button-4>", self._on_mousewheel)
            self.docInnerCanvas.bind("<Button-5>", self._on_mousewheel)
            self.docFrame.bind("<MouseWheel>", self._on_mousewheel)
            self.docFrame.bind("<Button-4>", self._on_mousewheel)
            self.docFrame.bind("<Button-5>", self._on_mousewheel)
            self.docFrame.bind_all("<1>", lambda event: self.clearSelectedTextByCLick("press", event))
            self.docInnerCanvas.bind("<B1-Motion>", self._selectingText)
            self.docFrame.bind_all('<Double-Button-1>', self.doubleClickSelection)
            
            root.bind('<Control-c>', self.copiar)
    
            self.docFrame.bind_all("<ButtonRelease-1>", lambda event: self.clearSelectedTextByCLick("release", event))
            self.docInnerCanvas.bind("<Button-3>", self.menuPopup)
            self.hscrollbar = tkinter.Scrollbar(self.docFrame, orient='horizontal', cursor="left_ptr")
            self.hscrollbar.grid(row=1, column=0, sticky='ew')
            self.hscrollbar.config( command = self.docInnerCanvas.xview )
            
           
            
            
            self.docInnerCanvas.bind('<Right>', lambda event: self.docInnerCanvas.xview_scroll(1, "units"))
            self.docInnerCanvas.bind('<Left>', lambda event: self.docInnerCanvas.xview_scroll(-1, "units"))
            self.docInnerCanvas.bind('<Up>', lambda event: self.docInnerCanvas.yview_scroll(-1, "units"))
            self.docInnerCanvas.bind('<Down>', lambda event: self.docInnerCanvas.yview_scroll(1, "units"))
            self.docInnerCanvas.bind('<Prior>', lambda event: self.manipulatePagesByClick('prev', event))
            self.docInnerCanvas.bind('<Next>', lambda event: self.manipulatePagesByClick('next', event))
            self.docInnerCanvas.bind('<Home>', lambda event: self.manipulatePagesByClick('first', event))
            self.docInnerCanvas.bind('<End>', lambda event: self.manipulatePagesByClick('last', event))
            root.bind('<Alt_L>', self.altPressed)
            root.bind('<Control-Alt-F12>', f12Pressed)
            self.docInnerCanvas.bind("<Control-MouseWheel>", self.scrollzoom)
            self.docInnerCanvas.bind("<Control-4>", lambda event: self.zoomx(event, tipozoom='plus'))
            self.docInnerCanvas.bind("<Control-5>", lambda event: self.zoomx(event, tipozoom='minus'))
            self.docFrame.bind("<Control-MouseWheel>", self.scrollzoom)
            self.docFrame.bind("<Control-4>", lambda event: self.zoomx(event, tipozoom='plus'))
            self.docFrame.bind("<Control-5>", lambda event: self.zoomx(event, tipozoom='minus'))
            root.bind('<KeyRelease-Alt_L>', self.altRelease)
            #root.bind('<KeyRelease-F12>', self.f12Release)
            self.docInnerCanvas.bind("<Motion>", self.checkLink)
            self.docFrame.bind_all("<Control-f>", self.focusSimpleSearch)
            self.docFrame.bind_all("<Control-F>", self.focusSimpleSearch)
            self.docFrame.bind_all("<Control-Down>", lambda event: self.dosearchsimple('next'))
            self.docFrame.bind_all("<Control-Up>", lambda event: self.dosearchsimple('prev'))
            root.update_idletasks()
            self.zoom_x =round((self.hscrollbar.winfo_rooty()-self.docFrame.winfo_rooty()-35)/infoLaudo[pathpdfatual].pixorgh, 16)#  zoom
            self.canvash = self.docInnerCanvas.winfo_height()-self.hscrollbar.winfo_height()-self.labeldocname.winfo_height()
            self.canvasw = self.docFrame.winfo_width()
            margemesq = 0
            margemdir = infoLaudo[pathpdfatual].pixorgw
            self.maiorw = self.canvasw
            if(infoLaudo[pathpdfatual].pixorgw*self.zoom_x*zoom>self.maiorw):
                self.maiorw = infoLaudo[pathpdfatual].pixorgw*self.zoom_x *zoom
    
            self.docInnerCanvas.config(width=infoLaudo[pathpdfatual].pixorgw*self.zoom_x*zoom)    
            sobraEspaco = self.docInnerCanvas.winfo_x()    
            self.mat = fitz.Matrix(self.zoom_x*zoom, self.zoom_x*zoom)
            self.scrolly = round((infoLaudo[pathpdfatual].pixorgh*self.zoom_x*zoom), 16)*infoLaudo[pathpdfatual].len  - 35
            self.docInnerCanvas.config(scrollregion=(sobraEspaco, 0, sobraEspaco+ (infoLaudo[pathpdfatual].pixorgw*zoom*self.zoom_x), self.scrolly))
            self.docInnerCanvas.configure(xscrollcommand=self.hscrollbar.set)
            self.docInnerCanvas.configure(yscrollcommand=self.vscrollbar.set)
            self.docInnerCanvas.configure(yscrollincrement=str(round((infoLaudo[pathpdfatual].pixorgh*self.zoom_x)/self.totalMov, 8)))
            self.altpressed=False
            self.ctrlpressed=False            
            anc_h = 'nw'
            pos_h =  (self.docFrame.winfo_width() - infoLaudo[pathpdfatual].pixorgw*self.zoom_x*zoom) / 2            
            self.create_fakeimage()
            init = self.docInnerCanvas.winfo_width()/2
            for k in range(minMaxLabels):
                for d in range(divididoEm):
                    indice = (k*divididoEm) + d
                    altura = (k*infoLaudo[pathpdfatual].pixorgh*self.zoom_x*zoom) + ((d/divididoEm)*infoLaudo[pathpdfatual].pixorgh*self.zoom_x*zoom)
                    self.ininCanvasesid[indice] = self.docInnerCanvas.create_image((pos_h,altura), \
                                                                                   anchor=anc_h, tag="canvas")
                self.fakePages[k] = self.docInnerCanvas.create_image((pos_h,(k*infoLaudo[pathpdfatual].pixorgh*self.zoom_x*zoom)), anchor=anc_h, image=self.fakeImage)
                self.docInnerCanvas.tag_lower(self.fakePages[k])
            self.docInnerCanvas.program = self            
            self.topLine = self.docInnerCanvas.create_line(0,0, max(self.docFrame.winfo_width(), infoLaudo[pathpdfatual].pixorgw*self.zoom_x*zoom), 0, width=10, fill=self.bg)            
            self.fakeLines[0] = self.docInnerCanvas.create_line(0,0, max(self.docFrame.winfo_width(), infoLaudo[pathpdfatual].pixorgw*self.zoom_x*zoom), 0, width=5, fill=self.bg)
            self.fakeLines[1] = self.docInnerCanvas.create_line(0,infoLaudo[pathpdfatual].pixorgh * self.zoom_x * zoom, max(self.docFrame.winfo_width(), \
                                                                infoLaudo[pathpdfatual].pixorgh*self.zoom_x*zoom), \
                                                                infoLaudo[pathpdfatual].pixorgh * self.zoom_x * zoom, width=5, fill=self.bg)
            self.docInnerCanvas.tag_raise(self.topLine)
            root.bind('<Alt-Left>', self.altleft)
            root.bind('<Alt-Right>', self.altright)
            
            
        except Exception as ex:
            printlogexception(ex=ex)
     
    def altright(self, event):
        global pathpdfatual
        try:
            temp = self.indiceposition+1
            if(self.indiceposition==9):
                temp = 0
            if(self.positions[temp]!=None):
                newpath = self.positions[temp][0]
                novoscroll = self.positions[temp][1]
                self.positions[self.indiceposition] = (pathpdfatual, self.vscrollbar.get()[0])
                if(pathpdfatual!=newpath):
                    #infoLaudo[pathpdfatual].ultimaPosicao=(self.vscrollbar.get()[0])
                    for i in range(minMaxLabels):
                        processed_pages[i] = -1    
                    sobraEspaco = 0
                    if(self.docFrame.winfo_width() > infoLaudo[pathpdfatual].pixorgw * self.zoom_x * zoom):
                        sobraEspaco = self.docInnerCanvas.winfo_x()
                    self.maiorw = self.docFrame.winfo_width()
                    if(infoLaudo[newpath].pixorgw*self.zoom_x*zoom>self.maiorw):
                        self.maiorw = infoLaudo[newpath].pixorgw*self.zoom_x *zoom           
                    self.scrolly = round((infoLaudo[pathpdfatual].pixorgh*self.zoom_x*zoom), 16)*infoLaudo[pathpdfatual].len  - 35
                    self.docInnerCanvas.config(scrollregion=(sobraEspaco, 0, sobraEspaco+ (infoLaudo[newpath].pixorgw*zoom*self.zoom_x), self.scrolly))
                    pagina = round(novoscroll*infoLaudo[newpath].len)
                    if(str(pagina+1)!=self.pagVar.get()):
                        self.pagVar.set(str(pagina+1) )
                    root.update_idletasks()
                    self.docInnerCanvas.yview_moveto(novoscroll)
                    self.docInnerCanvas.delete("quad")
                    self.docInnerCanvas.delete("simplesearch")
                    self.docInnerCanvas.delete("obsitem")
                    self.docInnerCanvas.delete("link")
                    self.clearSomeImages(["quad", "simplesearch", "obsitem", "link"])
                    pathpdfatual =newpath  
                    self.labeldocname.config(text=os.path.basename(pathpdfatual))
                    
                    self.totalPgg.config(text="/ "+str(infoLaudo[pathpdfatual].len))
                    for pdf in infoLaudo:
                        infoLaudo[pdf].retangulosDesenhados = {}
                else:
                    novoscroll = self.positions[temp][1]
                    self.docInnerCanvas.yview_moveto(novoscroll)
                    pagina = round(novoscroll*infoLaudo[newpath].len)
                    if(str(pagina+1)!=self.pagVar.get()):
                        self.pagVar.set(str(pagina+1))
                    self.totalPgg.config(text="/ "+str(infoLaudo[pathpdfatual].len))
                self.indiceposition += 1
        except Exception as ex:
            None
        
    def altleft(self, event):
        global pathpdfatual
        try:
            temp = self.indiceposition-1
            if(self.indiceposition==0):
                temp = 9
            if(self.positions[temp]!=None):
                newpath = self.positions[temp][0]
                novoscroll = self.positions[temp][1]
                self.positions[self.indiceposition] = (pathpdfatual, self.vscrollbar.get()[0])
                if(pathpdfatual!=newpath):
                    #infoLaudo[pathpdfatual].ultimaPosicao=(self.vscrollbar.get()[0])
                    for i in range(minMaxLabels):
                        processed_pages[i] = -1    
                    sobraEspaco = 0
                    if(self.docFrame.winfo_width() > infoLaudo[pathpdfatual].pixorgw * self.zoom_x * zoom):
                        sobraEspaco = self.docInnerCanvas.winfo_x()
                    self.maiorw = self.docFrame.winfo_width()
                    if(infoLaudo[newpath].pixorgw*self.zoom_x*zoom>self.maiorw):
                        self.maiorw = infoLaudo[newpath].pixorgw*self.zoom_x *zoom           
                    self.scrolly = round((infoLaudo[pathpdfatual].pixorgh*self.zoom_x*zoom), 16)*infoLaudo[pathpdfatual].len  - 35
                    self.docInnerCanvas.config(scrollregion=(sobraEspaco, 0, sobraEspaco+ (infoLaudo[newpath].pixorgw*zoom*self.zoom_x), self.scrolly))
                    pagina = round(novoscroll*infoLaudo[newpath].len)
                    root.update_idletasks()
                    self.docInnerCanvas.yview_moveto(novoscroll)
                    if(str(pagina+1)!=self.pagVar.get()):
                        self.pagVar.set(str(pagina+1))
                    pathpdfatual =newpath      
                    self.labeldocname.config(text=os.path.basename(pathpdfatual))
                    pathpdf2 = pathpdfatual
                    if plt == "Linux":
                        pathpdf2 = pathpdf2.replace("\\","/")
                    elif plt=="Windows":
                        pathpdf2 = pathpdf2.replace("/","\\")
                    
                    
                    self.totalPgg.config(text="/ "+str(infoLaudo[pathpdfatual].len))
                    for pdf in infoLaudo:
                        infoLaudo[pdf].retangulosDesenhados = {}                    
                    self.docInnerCanvas.delete("quad")
                    self.docInnerCanvas.delete("simplesearch")
                    self.docInnerCanvas.delete("obsitem")
                    self.docInnerCanvas.delete("link")
                    self.clearSomeImages(["quad", "simplesearch", "obsitem", "link"])            
                else:
                    novoscroll = self.positions[temp][1]
                    pagina = round(novoscroll*infoLaudo[newpath].len)
                    self.docInnerCanvas.yview_moveto(novoscroll)
                    if(str(pagina+1)!=self.pagVar.get()):
                        self.pagVar.set(str(pagina+1))
                    
                    self.totalPgg.config(text="/ "+str(infoLaudo[pathpdfatual].len))
                self.indiceposition -= 1  
        except Exception as ex:
            None
    
          
    
    
   
    
    def altRelease(self, event):
        self.altpressed=False
    
    def altPressed(self, event):
        #if(self.selectionActive):
        self.altpressed=True
        #else:
        #    self.altpressed=False
    def ctrlPressed(self, event):
        if(not self.selectionActive and not self.areaselectionActive and not self.areaselectionActiveCustom):
            self.ctrlpressed=True
        else:
            self.ctrlpressed=False            
                   
    def create_fakeimage(self):
        global infoLaudo, pathpdfatual
        altura = math.ceil(infoLaudo[pathpdfatual].pixorgh * self.zoom_x*zoom)
        largura = math.ceil(infoLaudo[pathpdfatual].pixorgw * self.zoom_x*zoom)
        image = Image.new('RGBA', (largura, altura), (255, 255, 255, 255))       
        self.fakeImage = ImageTk.PhotoImage(image)

def f12Pressed(event):
    None
class SearchResult():
    def __init__(self, pai, texto):
        self.pai = pai
        self.texto = texto
        
#def startThreads(request_queue, request_queuexml, response_queue, queuesair, infoLaudo, erros):
#        try:
#            render_thread = thr.Thread(target=backgroundRenderer, args=(1,request_queue, request_queuexml, response_queue, queuesair, infoLaudo, erros,), daemon=True)
#            render_thread.start()
#            render_thread2 = thr.Thread(target=backgroundRenderer, args=(2, request_queue, request_queuexml, response_queue, queuesair, infoLaudo, erros,), daemon=True)
#            render_thread2.start() ##
#
#            render_thread.join()
#            render_thread2.join()
#        except Exception as ex:
#            None
            
def deleteSearchProcess(result_queue, pathdb, idtermos, erros, queuesair):
    sqliteconn = None
    cursor = None
    notok = True
    
    while(notok):
                
        try:
            sqliteconn =  connectDB(str(pathdb), 5)
            cursor = sqliteconn.cursor()
            #cursor.execute("PRAGMA journal_mode=WAL")
            sqliteconn.execute("PRAGMA foreign_keys = ON")
            termostr = ','.join(('?') for t in idtermos)
            cursor.execute("DELETE FROM Anexo_Eletronico_SearchTerms WHERE id_termo IN ({})".format(termostr), idtermos)
            sqliteconn.commit()
            cursor.close()
            notok = False
            #return None
        except sqlite3.OperationalError as ex:
            printlogexception(ex=ex)
            time.sleep(2)
        except Exception as ex:
            printlogexception(ex=ex)       
        finally:
                 
            if(sqliteconn):
                sqliteconn.close()   
            
def execute(string, param=None):
    sqliteconn =  connectDB(str(pathdb), 5)
    cursor = sqliteconn.cursor()
    #cursor.execute("PRAGMA journal_mode=WAL")
    try:
        if(param!=None):
            cursor.execute(string,param)
        else:
            cursor.execute(string)
    except Exception as ex:
         printlogexception(ex=ex)        
    finally:
        cursor.close()        
        if(sqliteconn):
            sqliteconn.close()
            
            
def searchsqlite(advanced, termo, pathpdf, pathdb, idpdf, simplesearch = False, queuesair = None, \
                 idtermo = None, idtermopdf = None, update_queue = None, erros = None, fixo = None, result_queue = None,\
                     jarecords=None, sqliteconnx=None, infoLaudo=None, historicoDeParsing=None):
    lowerCodeNoDiff = [ 
        #00-0F #0
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
         #00-0F #16
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
         #10-1F #32
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
         #20-2F #48
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
         #30-3F #64
         0,  32,  32,  32,  32,  32,  32,  32,  32,  32,  32,  32,  32,  32,  32,  32,\
         #40-4F #80
        32,  32,  32,  32,  32,  32,  32,  32,  32,  32,  32,   0,   0,   0,   0,   0,\
        #50-5F #96
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
         #60-6F #112
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
         #70-7F #128
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
         #80-8F #144
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
         #90-9F #160
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
         #A0-AF #176
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
         #B0-BF #192
         -95, -96, -97, -98, -99,-100,  32,-100, -99,-100,-101,-102, -99,-100,-101,-102,\
       #C0-CF #208
        32, -99, -99,-100,-101,-102,-103,   0,   0,-100,-101,-102,-103,-100,  32,   0,\
        #D0-DF #224
        -127,-128,-129,-130,-131,-132,   0,-132,-131,-132,-133,-134,-131,-132,-133,-134,\
      #E0-EF #240
         0,-131,-131,-132,-133,-134,-135,   0,   0,-132,-133,-134,-135,-132,   0,-134 \
         #F0-FF #256
         ]
    '''
    novotermo = ""
    for char in termo:
        codePoint = ord(char)
        if(codePoint<256):
            codePoint += lowerCodeNoDiff[codePoint]
        novotermo += chr(codePoint) 
    termo = novotermo.lower()
    #sqliteconn = None
    #cursor = None
    #    pathpdf = str(pathpdf).replace("/","\\")
    if plt == "Linux":                           
        pathdocespecial1 = str(pathpdf).replace("\\","/")
    elif plt=="Windows":                 
        pathdocespecial1 = str(pathpdf).replace("/","\\")
    '''
    pathdocespecial1 = pathpdf
    doc = fitz.open(pathdocespecial1)
    destepdf = 0
    try:       
        
        if(advanced):            
            notok = True
            while(notok):
                #sqliteconn = None
                #cursor = None
                try:
                    if(sqliteconnx==None):
                        sqliteconn = connectDB(str(pathdb), 5)
                    else:
                        sqliteconn=sqliteconnx
                    cursor = sqliteconn.cursor()     
                    #cursor.execute("PRAGMA journal_mode=WAL")
                    novabusca =  'SELECT  C.pagina, C.texto, offsets(Anexo_Eletronico_Conteudo_id_pdf_'+str(idpdf)+') FROM Anexo_Eletronico_Conteudo_id_pdf_'+str(idpdf)+' C where texto MATCH :termo ORDER BY 1'
                    cursor.execute(novabusca, {'termo': termo.upper()})                   
                    records2 = cursor.fetchall()
                    notok = False
                except sqlite3.OperationalError:
                    printlogexception(ex=ex)
                    
                    time.sleep(2)
                except Exception as ex:
                    printlogexception(ex=ex)
                finally:
                    try:
                        try:
                            cursor.close() 
                        except Exception as ex:
                            None
                        try:
                            sqliteconn.close()
                        except Exception as ex:
                            None
                    except Exception as ex:
                        None
            rectspagina = {}
            results = []
            countpagina = 0
            counter = 0
            parar = False
            resultadosx = []
            for pages in records2:
                #resultporsecao = 0
                if(parar):
                    inserts = []
                    break                
                offsets = str(pages[2]).split(' ')
                qualcharinit = None
                qualcharfim = None
                contchar = 0
                contagem = 0
                textoembytes = pages[1].encode('utf-8')
                for offset in range(0, len(offsets),4):
                    
                    
                    init = int(offsets[offset+2])
                    fim = int(init+int(offsets[offset+3]))                    
                    slicebytesinit = textoembytes[:init]
                    slicebytesdif =  textoembytes[init:fim]
                    devoltainit = slicebytesinit.decode('utf-8')
                    devoltadif = slicebytesdif.decode('utf-8')
                    if(infoLaudo!=None):
                        toc = locateToc(pages[0], pathpdf, None, len(devoltainit), infoLaudo)
                    else:
                        toc = None
                    counter += 1
                    resultsearch = ResultSearch()
                    resultsearch.toc = toc
                    resultsearch.idtermopdf = idtermopdf
                    resultsearch.init = len(devoltainit)
                    resultsearch.fim = resultsearch.init + len(devoltadif)
                    resultsearch.pagina = pages[0]
                    resultsearch.pathpdf = pathpdf
                    resultsearch.idpdf = str(idpdf)
                    resultsearch.termo = termo.upper()
                    resultsearch.advanced = advanced
                    resultsearch.idtermo = idtermo
                    snippet = ''.join(char if len(char.encode('utf-8')) < 3 else '�' for char in pages[1])
                    snippetantes = ""
                    snippetdepois = ""
                    espacos = 0
                    for k in range(len(devoltainit)-1, -1, -1):
                        if(snippet[k]== ' '):
                            espacos+=1
                        snippetantes = snippet[k] + snippetantes
                        if(espacos>=7):
                            break
                    espacos = 0
                    for k in range(len(devoltainit)+1, len(snippet)):
                        if(snippet[k]==' '):
                            espacos+=1
                        snippetdepois += snippet[k] 
                        if(espacos>=7):
                            break    
                    resultsearch.snippet =  (snippetantes, snippet[len(devoltainit):len(devoltainit)+len(devoltadif)], snippetdepois)                    
                    resultsearch.fixo = fixo
                    resultsearch.counter = counter
                    if(queuesair != None and not queuesair.empty()):
                        x = queuesair.get()    
                        if(x[0]=='pararbusca' and str(x[1])==str(idtermo)):                             
                            parar = True
                            resultadosx = []
                        elif(x[0]=='sairtudo'):
                            if(cursor):
                                cursor.close()              
                            if(sqliteconn):
                                sqliteconn.close()
                            parar = True
                            queuesair.put(x)
                            return
                        else:
                            queuesair.put(x)
                    if(not simplesearch):
                        if(parar):
                            resultadosx = []
                            break
                        resultadosx.append((1, resultsearch))
                        
                    else:
                        results.append((resultsearch))
                    contchar += 1
                countpagina += 1
                if(not simplesearch and countpagina%50==0 and not parar):
                    update_queue.put(('updatecontpdf', idtermopdf, pathpdf, countpagina, len(records2), idtermo))   
            for resu in resultadosx:
                result_queue.put(resu)
            return results
        else:
            notok = True
            while(notok):
                sqliteconn = None
                cursor = None
                try:
                    #termo = termo.replace("%", "\\%")
                    #termo = termo.replace("\\", "\\\\")
                    sqliteconn = connectDB(str(pathdb), 5)
                    cursor = sqliteconn.cursor()
                    #cursor.execute("PRAGMA journal_mode=WAL")
                    if(not simplesearch):
                        
                        novabusca =  'SELECT  C.pagina, C.texto FROM Anexo_Eletronico_Conteudo_id_pdf_'+str(idpdf)+''' C where texto like :termo ESCAPE :escape ORDER BY 1'''
                                                       
                        cursor.execute(novabusca, {'termo':'%'+termo+'%', 'escape': '\\'})
                        records2 = cursor.fetchall()
                    else:
                        records2 = jarecords
                        #cursor.execute(query, {'termo':'%'+termo+'%', 'pag':paginaquery, 'escape': '\\'})
                    
                    notok = False
                except sqlite3.OperationalError as ex:
                    printlogexception(ex=ex)
                    time.sleep(2)
                except Exception as ex:
                    printlogexception(ex=ex)
                    if(printorlog=='log'):
                        logging.exception('!')
                    elif(printorlog=='print'):
                        traceback.print_exc()
                    else:
                        None
                finally:
                    try:
                        try:
                            cursor.close() 
                        except Exception as ex:
                            None
                        try:
                            sqliteconn.close()
                        except Exception as ex:
                            None
                    except Exception as ex:
                        None
            results = []
            countpagina = 0
            counter = 0
            inserts = []
            parar = False
            resultadosx = []   
            resultporsecao = {}
            for pagina in records2:
                
                if(parar):
                    break
                jaachados = set()
                qualcharinit = None
                qualcharfim = None
                init = 0
                resultfind = pagina[1].find(termo, init, len(pagina[1]))
                while resultfind!=-1:
                    if(infoLaudo!=None):
                        toc = locateToc(pagina[0], pathpdf, None, resultfind, infoLaudo)
                        if(toc not in resultporsecao):
                            resultporsecao[toc]=0
                        if(resultporsecao[toc]>=1000):
                            break  
                        resultporsecao[toc]+=1
                    else:
                        toc = None
                    
                    if(str(qualcharinit)+'-'+str(qualcharfim) in jaachados):
                        init = resultfind+len(termo)-1
                        resultfind = pagina[1].find(termo, init, len(pagina[1]))
                    else:
                        jaachados.add(str(qualcharinit)+'-'+str(qualcharfim))
                        counter += 1
                        qualcharinit = resultfind
                        qualcharfim = qualcharinit + len(termo)
                        resultsearch = ResultSearch()
                        resultsearch.idtermopdf = idtermopdf                        
                        resultsearch.init = qualcharinit
                        resultsearch.fim = qualcharfim
                        resultsearch.pagina = pagina[0]

                        pathpdf = os.path.normpath(pathpdf)
                        resultsearch.pathpdf = pathpdf
                        resultsearch.idpdf = str(idpdf)
                        resultsearch.termo = termo.upper()
                        resultsearch.advanced = advanced
                        resultsearch.idtermo = idtermo
                        snippetantes = ""
                        snippetdepois = ""
                        espacos = 0
                        for k in range(resultfind-1, -1, -1):
                            char = pagina[1][k]
                            if(char== ' '):
                                espacos+=1                            
                            if(len(char.encode('utf-8')) < 3):
                                snippetantes = char + snippetantes
                            else:
                                snippetantes = '�' + snippetantes
                            if(espacos>=4):
                                break
                        espacos = 0
                        for k in range(resultfind+(len(termo)), len(pagina[1])):
                            char = pagina[1][k]
                            if(char== ' '):
                                espacos+=1 
                            if(len(char.encode('utf-8')) < 3):
                                snippetdepois += char 
                            else:
                                snippetdepois += '�'
                            #snippetdepois += snippet[k] 
                            if(espacos>=4):
                                break    
                        #snippetantes = ''.join(char if len(char.encode('utf-8')) < 3 else '�' for char in snippetantes)
                        termo = ''.join(char if len(char.encode('utf-8')) < 3 else '�' for char in termo)
                        #snippetantes = ''.join(char if len(char.encode('utf-8')) < 3 else '�' for char in snippetantes[1])
                        resultsearch.snippet =  (snippetantes, termo, snippetdepois)
                        resultsearch.fixo = fixo
                        resultsearch.counter = counter   
                        resultsearch.toc = toc
                        init = resultfind+len(termo)-1
                        resultfind = pagina[1].find(termo, init, len(pagina[1]))
                    if(queuesair != None and not queuesair.empty()):
                        x = queuesair.get()    
                        if(x[0]=='pararbusca' and str(x[1])==str(idtermo)): 
                            parar = True
                            resultadosx = []
                        elif(x[0]=='sairtudo'):                            
                            parar = True
                            queuesair.put(x)
                            return False
                        else:
                            queuesair.put(x)
                    if(not simplesearch):
                        if(parar):
                            resultadosx = []
                            break
                        resultadosx.append((1, resultsearch))
                    else:
                        results.append((resultsearch))
                countpagina += 1
                if(not simplesearch and countpagina%50==0 and not parar):
                    update_queue.put(('updatecontpdf', idtermopdf, pathpdf, countpagina, len(records2), idtermo))
            for resu in resultadosx:
                result_queue.put(resu)    
            return results    
    except sqlite3.Error:
        exc_type, exc_value, exc_tb = sys.exc_info()
        erros.put(('errosqlbusca', traceback.format_exception(exc_type, exc_value, exc_tb)))
                    
    except Exception as ex:
        printlogexception(ex=ex)
    finally:        
        doc.close()
            
def searchProcess(result_queue, pathdb, erros, queuesair, searchqueue, update_queue, infoLaudo, listaRELS, listaTERMOS, estavel=False):
    lowerCodeNoDiff = [ 
        #00-0F #0
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
         #00-0F #16
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
         #10-1F #32
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
         #20-2F #48
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
         #30-3F #64
         0,  32,  32,  32,  32,  32,  32,  32,  32,  32,  32,  32,  32,  32,  32,  32,\
         #40-4F #80
        32,  32,  32,  32,  32,  32,  32,  32,  32,  32,  32,   0,   0,   0,   0,   0,\
        #50-5F #96
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
         #60-6F #112
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
         #70-7F #128
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
         #80-8F #144
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
         #90-9F #160
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
         #A0-AF #176
         0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,\
         #B0-BF #192
         -95, -96, -97, -98, -99,-100,  32,-100, -99,-100,-101,-102, -99,-100,-101,-102,\
       #C0-CF #208
        32, -99, -99,-100,-101,-102,-103,   0,   0,-100,-101,-102,-103,-100,  32,   0,\
        #D0-DF #224
        -127,-128,-129,-130,-131,-132,   0,-132,-131,-132,-133,-134,-131,-132,-133,-134,\
      #E0-EF #240
         0,-131,-131,-132,-133,-134,-135,   0,   0,-132,-133,-134,-135,-132,   0,-134 \
         #F0-FF #256
         ]
    historicoDeParsing = {}
    while(True): 
        if(len(searchqueue)>0):           
            notok = True
            while(notok):
                sqliteconn = None
                cursor = None
                try:                    
                    notok = False
                    pedidos = []
                    adv = []
                    notadv = []
                    while len(searchqueue)>0:
                        try:
                            pedidosearch = searchqueue.pop(0)       
                        except Exception as ex:
                            continue
                        sqliteconn = connectDB(str(pathdb), 5)
                        cursor = sqliteconn.cursor()
                        #cursor.execute("PRAGMA journal_mode=WAL")
                        termo = pedidosearch[0]
                        termoorg = termo                        
                        novotermo = ""
                        for char in termo:
                            codePoint = ord(char)
                            if(codePoint<256):
                                codePoint += lowerCodeNoDiff[codePoint]
                            novotermo += chr(codePoint) 
                        termo = novotermo.lower()
                        advancedsearch = pedidosearch[1]
                        
                        
                        
                        if((termo,advancedsearch) in listaTERMOS):
                            idtermo = listaTERMOS[(termo,advancedsearch)]
                        else:
                            if(expertmode):
                                fixo = 1    
                            sql_insert_searchterm = "INSERT INTO Anexo_Eletronico_SearchTerms (termo, advancedsearch, fixo) VALUES (?,?,?)" 
                            cursor.execute(sql_insert_searchterm, (termo,advancedsearch, fixo,))
                            idtermo = cursor.lastrowid
                            listaTERMOS[(termo,advancedsearch)] = idtermo
                            sqliteconn.commit()
                        '''
                        check_previous_search_termo =  \
                            SELECT ST.id_termo, ST.termo, ST.advancedsearch, ST.fixo FROM Anexo_Eletronico_SearchTerms ST where termo = ? AND advancedsearch = ?   
                        cursor.execute(check_previous_search_termo,(termo,advancedsearch,))
                        jaexistermo = cursor.fetchone()  
                        #jaexistermo = None
                        fixo = 0
                        if(expertmode):
                            fixo = 1                            
                        if(jaexistermo == None or len(jaexistermo)==0):
                            sql_insert_searchterm = "INSERT INTO Anexo_Eletronico_SearchTerms (termo, advancedsearch, fixo) VALUES (?,?,?)" 
                            cursor.execute(sql_insert_searchterm, (termo,advancedsearch, fixo,))
                            idtermo = cursor.lastrowid
                            sqliteconn.commit()
                        else:
                            idtermo = jaexistermo[0]
                        '''
                        if(expertmode):
                            fixo = 1    
                        if(len(pedidosearch)==4):
                            pedidos.insert(0, (termo, advancedsearch, idtermo))
                        else:
                            pedidos.append((termo, advancedsearch, idtermo))
                        
                        if(advancedsearch==0):
                            notadv.append(termo)
                        else:
                            adv.append(termo)
                         
                        
                        try:
                            cursor.close() 
                        except Exception as ex:
                            None
                        try:
                            sqliteconn.close()
                        except Exception as ex:
                            None
                        
                        resultsearch = ResultSearch()
                        resultsearch.termo = termo.upper()
                        resultsearch.advanced = advancedsearch
                        resultsearch.idtermo = idtermo
                        resultsearch.fixo = fixo
                        result_queue.put((0,  resultsearch)) 
                        time.sleep(0.1)
                    '''
                    sqliteconn = connectDB(str(pathdb), 5)
                    cursor = sqliteconn.cursor()
                    cursor.execute(SELECT P.rel_path_pdf, P.id_pdf FROM Anexo_Eletronico_Pdfs P  WHERE P.tipo = 'relatorio' ORDER BY 1)
                    records = cursor.fetchall()  
                    try:
                        cursor.close() 
                    except Exception as ex:
                        None
                    try:
                        sqliteconn.close()
                    except Exception as ex:
                        None
                        '''
                    
                    while len(pedidos)>0:
                        while len(searchqueue)>0:
                            pedidosearch = searchqueue.pop(0)                    
                            sqliteconn = connectDB(str(pathdb), 5)
                            cursor = sqliteconn.cursor()
                            #cursor.execute("PRAGMA journal_mode=WAL")
                            termo = pedidosearch[0]
                            termoorg = termo                        
                            novotermo = ""
                            for char in termo:
                                codePoint = ord(char)
                                if(codePoint<256):
                                    codePoint += lowerCodeNoDiff[codePoint]
                                novotermo += chr(codePoint) 
                            termo = novotermo.lower()
                            advancedsearch = pedidosearch[1]
                            
                            
                            
                            if((termo,advancedsearch) in listaTERMOS):
                                idtermo = listaTERMOS[(termo,advancedsearch)]
                            else:
                                if(expertmode):
                                    fixo = 1    
                                sql_insert_searchterm = "INSERT INTO Anexo_Eletronico_SearchTerms (termo, advancedsearch, fixo) VALUES (?,?,?)" 
                                cursor.execute(sql_insert_searchterm, (termo,advancedsearch, fixo,))
                                idtermo = cursor.lastrowid
                                listaTERMOS[(termo,advancedsearch)] = idtermo
                                sqliteconn.commit()
                            '''
                            check_previous_search_termo =  \
                                SELECT ST.id_termo, ST.termo, ST.advancedsearch, ST.fixo FROM Anexo_Eletronico_SearchTerms ST where termo = ? AND advancedsearch = ?   
                            cursor.execute(check_previous_search_termo,(termo,advancedsearch,))
                            jaexistermo = cursor.fetchone()  
                            #jaexistermo = None
                            fixo = 0
                            if(expertmode):
                                fixo = 1                            
                            if(jaexistermo == None or len(jaexistermo)==0):
                                sql_insert_searchterm = "INSERT INTO Anexo_Eletronico_SearchTerms (termo, advancedsearch, fixo) VALUES (?,?,?)" 
                                cursor.execute(sql_insert_searchterm, (termo,advancedsearch, fixo,))
                                idtermo = cursor.lastrowid
                                sqliteconn.commit()
                            else:
                                idtermo = jaexistermo[0]
                            '''
                            if(expertmode):
                                fixo = 1    
                            if(len(pedidosearch)==4):
                                pedidos.insert(0, (termo, advancedsearch, idtermo))
                            else:
                                pedidos.append((termo, advancedsearch, idtermo))
                            
                            if(advancedsearch==0):
                                notadv.append(termo)
                            else:
                                adv.append(termo)
                             
                            
                            try:
                                cursor.close() 
                            except Exception as ex:
                                None
                            try:
                                sqliteconn.close()
                            except Exception as ex:
                                None
                            
                            resultsearch = ResultSearch()
                            resultsearch.termo = termo.upper()
                            resultsearch.advanced = advancedsearch
                            resultsearch.idtermo = idtermo
                            resultsearch.fixo = fixo
                            result_queue.put((0,  resultsearch)) 
                            time.sleep(0.1)
                        
                        pedidosearch = pedidos.pop(0)
                        
                        termo = pedidosearch[0]
                        
                        '''
                        novotermo = ""
                        for char in termo:
                            codePoint = ord(char)
                            if(codePoint<256):
                                codePoint += lowerCodeNoDiff[codePoint]
                            novotermo += chr(codePoint) 
                        termo = novotermo.lower()
                        '''
                        advancedsearch = pedidosearch[1]
                        idtermo = pedidosearch[2]
                        records = listaRELS
                        for r in records:
                            pp = os.path.normpath(os.path.join(pathdb.parent, r[0]))
                            if plt == "Linux":
                                pp = pp.replace("\\","/")
                            elif plt=="Windows":
                                pp = pp.replace("/","\\")
                            idtermopdf = str(r[1])+'-'+str(idtermo)
                            searchsqlite(advancedsearch, termo, pp, pathdb, r[1], queuesair=queuesair, idtermo=str(idtermo), idtermopdf=str(idtermopdf), \
                                                         update_queue=update_queue, erros = erros, fixo = fixo, result_queue = result_queue, \
                                                             sqliteconnx=None, infoLaudo=infoLaudo, historicoDeParsing=historicoDeParsing)
                        result_queue.put((2,  idtermo, advancedsearch, termo.upper())) 
                    
                except sqlite3.Error:
                    exc_type, exc_value, exc_tb = sys.exc_info()
                    erros.put(('errosqlbusca', traceback.format_exception(exc_type, exc_value, exc_tb)))
             
                except sqlite3.OperationalError:
                    printlogexception(ex=ex)
                    time.sleep(2)
                except Exception as ex:
                    printlogexception(ex=ex) 
                finally:
                    try:
                        cursor.close() 
                    except Exception as ex:
                        None
                    try:
                        sqliteconn.close()
                    except Exception as ex:
                        None
        else:
            if(not estavel):
                break
            else:
                historicoDeParsing = {}
                time.sleep(1)
            
def backgroundRendererXML(request_queuexml, response_queuexml, queuesair, infoLaudo, erros, listadeobs): 
    docs = {}
    doc = None
    pathatual = None
    lastpos = 0
    qtdeCache = 1
    docs = [None]*qtdeCache    
    while True:
        try:
            pedidoPagina = None
            if(not request_queuexml.empty()):             
                 pedidoPagina = request_queuexml.get(0)
            else:
                time.sleep(0.1)
            if(pedidoPagina!=None): 
                if(pedidoPagina.qualPdf!=pathatual):
                    pathatual = pedidoPagina.qualPdf
                    if plt == "Linux":
                        pathatual = pathatual.replace("\\","/")
                    elif plt=="Windows":
                        pathatual = pathatual.replace("/","\\")
                    doc = None
                    for aberto in docs:
                        if(aberto==None):
                            continue
                        if(aberto[0]==pathatual):
                            doc = aberto[1]
                            break
                    if(doc==None):
                        doc = fitz.open(pathatual)
                        try:
                            docs[lastpos%qtdeCache][1].close()
                        except Exception as ex:
                            None
                        docs[lastpos%qtdeCache] = (pathatual, doc)
                        
                        lastpos+=1
                        if(lastpos==qtdeCache):
                            lastpos=0
                mt = pedidoPagina.mt
                mb = pedidoPagina.mb
                me = pedidoPagina.me
                md = pedidoPagina.md
                if pedidoPagina.qualPagina >= len(doc):
                    continue
                loadedPage = doc[pedidoPagina.qualPagina]                
                mmtopxtop = math.floor(mt/25.4*72)
                mmtopxbottom = math.ceil(pedidoPagina.pixheight-(mb/25.4*72))
                mmtopxleft = math.floor(me/25.4*72)
                mmtopxright = math.ceil(pedidoPagina.pixwidth-(md/25.4*72))                
                respostaPagina = RespostaDePaginaXML()
                respostaPagina.qualPdf = pedidoPagina.qualPdf
                respostaPagina.links = loadedPage.getLinks()
                respostaPagina.qualPagina = pedidoPagina.qualPagina
                wids = loadedPage.widgets()
                respostaPagina.widgets = []
                for wid in wids:
                    tup = (wid.field_label, wid.rect)
                    respostaPagina.widgets.append(tup)
                respostaPagina.mapeamento = {}
                respostaPagina.quadspagina = []
                dictx = loadedPage.getText("rawdict")
                novotexto = ""
                for block in dictx['blocks']:
                    if(block['type']==0):
                        pontosBlock = block['bbox']
                        bloco = (math.floor(float(pontosBlock[0])), math.floor(float(pontosBlock[1])), \
                                 math.ceil(float(pontosBlock[2])), math.floor(float(pontosBlock[3])))
                        respostaPagina.mapeamento[bloco] = {}
                        for line in block['lines']:
                            pontosLine = line['bbox']
                            linha = (math.floor(float(pontosLine[0])), math.ceil(float(pontosLine[1])), \
                                 math.ceil(float(pontosLine[2])), math.floor(float(pontosLine[3])))
                            respostaPagina.mapeamento[bloco][linha] = []
                            for span in line['spans']:
                                #a = span["ascender"]
                                #d = span["descender"]
                                r = fitz.Rect(span["bbox"])
                                #o = fitz.Point(span["origin"])
                                r.y1 = r.y1 -1
                                r.y0 = r.y0 +1
                                x0 = y0 = x1 = y1 = None
                                for char in span['chars']:
                                    bboxchar = char['bbox']
                                    bboxxmedio = (bboxchar[0]+bboxchar[2])/2
                                    bboxymedio = (bboxchar[1]+bboxchar[3])/2
                                    temchar = True
                                    
                                    att = char['bbox']
                                    x0 = math.floor(float(att[0]))
                                    y0 = math.floor(r.y0)
                                    x1 = math.ceil(float(att[len(att)-2]))
                                    y1 = math.floor(r.y1)
                                    c = char['c']
                                    respostaPagina.mapeamento[bloco][linha].append((x0, y0, x1, y1, c))
                                    if(bboxxmedio >= mmtopxleft and bboxxmedio <= mmtopxright and bboxymedio >= mmtopxtop and bboxymedio <= mmtopxbottom):
                                        respostaPagina.quadspagina.append((x0, y0, x1, y1))
                                        novotexto += c
                            if(len(novotexto) > 0 and novotexto[-1]!=' '):
                                novotexto += ' '
                                respostaPagina.quadspagina.append((x0, y0, x1, y1))
                        if(len(novotexto) > 0 and novotexto[-1]!=' '):
                            novotexto += ' '
                            respostaPagina.quadspagina.append((x0, y0, x1, y1))
                response_queuexml.put(respostaPagina) 
        except Exception as ex:
            printlogexception(ex=ex)
        finally:
            for abs_path_pdf in infoLaudo:
                try:
                    docs[abs_path_pdf].close()
                except Exception as ex:
                    None

def connectDB(dbpath, timeout):
    hasconn = False
    
    while(not hasconn):
        try:
            sqliteconn = sqlite3.connect(str(dbpath), timeout=timeout)
            hasconn = True
            return sqliteconn
        except Exception as ex:
            None
def backgroundRendererImage(processed_pages, request_queue, response_queue, queuesair, infoLaudo, erros):    
    docs = {}
    doc = None
    pathatual = None
    lastpos = 0
    qtdeCache = 1
    docs = [None]*qtdeCache    
    while True:
        try:
            pedidoPagina = None

            if(not request_queue.empty()):             
                 pedidoPagina = request_queue.get(0)
            else:
                time.sleep(0.1)
      
            if(pedidoPagina!=None): 
                if(pedidoPagina.qualPdf!=pathatual):
                    pathatual = pedidoPagina.qualPdf
                    if plt == "Linux":
                        pathatual = pathatual.replace("\\","/")
                    elif plt=="Windows":
                        pathatual = pathatual.replace("/","\\")
                    doc = None
                    for aberto in docs:
                        if(aberto==None):
                            continue
                        if(aberto[0]==pathatual):
                            doc = aberto[1]
                            break
                    if(doc==None):
                        
                        doc = fitz.open(pathatual)
                        try:
                            docs[lastpos%qtdeCache][1].close()
                        except Exception as ex:
                            None
                        docs[lastpos%qtdeCache] = (pathatual, doc)
                        
                        lastpos+=1
                        if(lastpos==qtdeCache):
                            lastpos=0
                if(not pedidoPagina.qualPagina in processed_pages):
                    continue
                if pedidoPagina.qualPagina >= len(doc):
                    continue
                loadedPage = doc[pedidoPagina.qualPagina]
                if(not pedidoPagina.qualPagina in processed_pages):
                    continue
                pix = loadedPage.getPixmap(alpha=False, matrix=pedidoPagina.matriz)                
                imgdata = pix.getImageData("ppm")
                respostaPagina = RespostaDePagina()
                respostaPagina.links = loadedPage.getLinks()
                wids = loadedPage.widgets()
                respostaPagina.widgets = []
                if(not pedidoPagina.qualPagina in processed_pages):
                    continue
                for wid in wids:
                    tup = (wid.field_label, wid.rect)
                    respostaPagina.widgets.append(tup)
                respostaPagina.mapeamento = {}
                i = 0
                respostaPagina.qualPagina = pedidoPagina.qualPagina
                respostaPagina.qualGrid = i     
                respostaPagina.imgdata = imgdata
                respostaPagina.qualLabel = pedidoPagina.qualLabel
                respostaPagina.qualPdf = pedidoPagina.qualPdf
                respostaPagina.zoom = pedidoPagina.zoom
                pix = None
                response_queue.put(respostaPagina)               
            else:
                time.sleep(0)
                
        except Exception as ex:
            printlogexception(ex=ex)
        finally:
            for abs_path_pdf in infoLaudo:
                try:
                    docs[abs_path_pdf].close()
                except Exception as ex:
                    None
def processBatchInsertObs(listadeitenscompleto, allitens):
        doc = None
        pathpdfatual = None
        paginaatual = None
        quadspagina = []
        try:
            for item in allitens:
                resultsearch = item[0]
                mt = item[1]
                mb = item[2]
                me = item[3]
                md =  item[4]
                mmtopxtop = math.floor(mt/25.4*72)
                mmtopxbottom = math.ceil(item[6]-(mb/25.4*72))
                mmtopxleft = math.floor(me/25.4*72)
                mmtopxright = math.ceil(item[5]-(md/25.4*72))
                pathpdf = resultsearch.pathpdf
                if(pathpdfatual!=pathpdf):
                    if(doc!=None):
                        doc.close()
                    pathpdfatual=pathpdf
                    if plt == "Linux":                           
                        pathdocespecial1 = str(pathpdfatual).replace("\\","/")
                    elif plt=="Windows":                 
                        pathdocespecial1 = str(pathpdfatual).replace("/","\\")
                    doc = fitz.open(pathdocespecial1)
                pagina = int(resultsearch.pagina)
                
                
                
                if(pagina !=paginaatual):
                    quadspagina = []
                    paginaatual = pagina
                    loadedPage = doc[paginaatual]
                    dictx = loadedPage.getText("rawdict")
                    novotexto = ""
                    for block in dictx['blocks']:
                        if(block['type']==0):
                            pontosBlock = block['bbox']
                            bloco = (math.floor(float(pontosBlock[0])), math.floor(float(pontosBlock[1])), \
                                     math.ceil(float(pontosBlock[2])), math.floor(float(pontosBlock[3])))
                            for line in block['lines']:
                                pontosLine = line['bbox']
                                linha = (math.floor(float(pontosLine[0])), math.ceil(float(pontosLine[1])), \
                                     math.ceil(float(pontosLine[2])), math.floor(float(pontosLine[3])))
                                for span in line['spans']:
    
                                    r = fitz.Rect(span["bbox"])
                                    #o = fitz.Point(span["origin"])
                                    r.y1 = r.y1 -1
                                    r.y0 = r.y0 +1
                                    x0 = y0 = x1 = y1 = None
                                    for char in span['chars']:
                                        bboxchar = char['bbox']
                                        bboxxmedio = (bboxchar[0]+bboxchar[2])/2
                                        bboxymedio = (bboxchar[1]+bboxchar[3])/2
                                        temchar = True
                                        
                                        att = char['bbox']
                                        x0 = math.floor(float(att[0]))
                                        y0 = math.floor(r.y0)
                                        x1 = math.ceil(float(att[len(att)-2]))
                                        y1 = math.floor(r.y1)
                                        c = char['c']
                                        if(bboxxmedio >= mmtopxleft and bboxxmedio <= mmtopxright and bboxymedio >= mmtopxtop and bboxymedio <= mmtopxbottom):
                                            quadspagina.append((x0, y0, x1, y1))
                                            novotexto += c
                                if(len(novotexto) > 0 and novotexto[-1]!=' '):
                                    novotexto += ' '
                                    quadspagina.append((x0, y0, x1, y1))
                            if(len(novotexto) > 0 and novotexto[-1]!=' '):
                                novotexto += ' '
                                quadspagina.append((x0, y0, x1, y1))
            
                posicoes = quadspagina
                init = posicoes[resultsearch.init]
                fim = posicoes[resultsearch.fim-1]
                p0x = round(init[0])
                p0y = round((init[1]+init[3])/2)
                p1x = round(fim[2])
                p1y = round((fim[1]+fim[3])/2)
                listadeitenscompleto.append((p0x, p0y, p1x, p1y, pagina, pathpdfatual))
        except Exception as ex:
            printlogexception(ex=ex)
        finally:
            if(doc!=None):
                doc.close()       

def on_quit():
    global exitFlag, renderprocess, queuesair, initsearchprocess, processes, uniquesearchprocess, posicaoZoom, root, mw
    exitFlag = True
    try:
        queuesair.put(('sairtudo')) 
    except Exception as ex:
        None
    try:
        uniquesearchprocess.terminate()
    except Exception as ex:
        None
    try:
        searchprocess.terminate()
    except Exception as ex:
        None
    try:
        renderprocess.terminate()
    except Exception as ex:
        None
    try:
        initsearchprocess.terminate()
    except Exception as ex:
        None
    for p in processes:
        try:
            p.terminate()
        except Exception as ex:
            None
    sqliteconn = connectDB(pathdb, 5)
    cursor = sqliteconn.cursor()
    try:
        selectpdf = ("SELECT P.id_pdf, P.rel_path_pdf FROM Anexo_Eletronico_Pdfs P")
        cursor.execute(selectpdf)
        allpdfs = cursor.fetchall()
        selectconfigzoom = "SELECT * FROM FERA_CONFIG WHERE config = ?"
        cursor.execute(selectconfigzoom, ('zoom',))
        configzoom = cursor.fetchone()
       
        for pdf in allpdfs:
            pathpdf = os.path.normpath(os.path.join(pathdb.parent, pdf[1]))
            if plt == "Linux":                           
                pathpdf = str(pathpdf).replace("\\","/")
            elif plt=="Windows":                 
                pathpdf = str(pathpdf).replace("/","\\")
            #pdfx = (str(Path(pathpdf)))
            
            cursor.execute("UPDATE Anexo_Eletronico_Pdfs set lastpos = ? WHERE id_pdf = ?", (infoLaudo[pathpdf].ultimaPosicao, pdf[0],))
        
        
        if(configzoom==None or configzoom==''):
            insertzoom = "INSERT INTO FERA_CONFIG (config, param) values (?,?)"
            cursor.execute(insertzoom, ('zoom', posicaoZoom,))
        else:
            cursor.execute("UPDATE FERA_CONFIG set param = ? WHERE config = ?", (posicaoZoom, 'zoom',))
        obscats = mw.treeviewObs.get_children('')
        
        for obscat in obscats:
            updateinto2 = "UPDATE Anexo_Eletronico_Obscat set ordem = ? WHERE id_obscat = ?"
            id_obscat = mw.treeviewObs.item(obscat, 'values')[1]
            cursor.execute(updateinto2, (mw.treeviewObs.index(obscat), id_obscat,))            
        sqliteconn.commit()
    except Exception as ex:
        printlogexception(ex=ex)
    finally:
        cursor.close()
        if(sqliteconn):
            sqliteconn.close() 
        try:
            for child in mw.treeviewSearches.get_children(''):
                mw.treeviewSearches.delete(child)
            mw.treeviewSearches.grid_forget()
           
            mw.treeviewSearches.destroy()

        except Exception as ex:
            printlogexception(ex=ex)
        try:
            root.destroy()
        except Exception as ex:
            None
        sys.exit(0)
        
def popupcomandook(sair, window):
    if(sair):
        window.destroy()
        on_quit()
    else:
        window.destroy()
        

        
def popup_window(texto, sair, imagepcp=None):
    global warningimage, windowpopup
    try:
        windowpopup.destroy()
        windowpopup = None
    except Exception as ex:
        None
    windowpopup = tkinter.Toplevel()
    windowpopup.focus_set()
    #w = 300 # width for the Tk root
    #h = 200 # height for the Tk root
    if(imagepcp!=None):
        label = tkinter.Label(windowpopup, text=texto, image=imagepcp, compound='top')
    else:
        label = tkinter.Label(windowpopup, text=texto, image=warningimage, compound='top')
    label.pack(fill='x', padx=5, pady=5)
    # get screen width and height
    ws = root.winfo_screenwidth() # width of the screen
    hs = root.winfo_screenheight() # height of the screen
    
    # calculate x and y coordinates for the Tk root window
    #x = (ws/2) - (w/2)
    #y = (hs/2) - (h/2)
    #window.geometry('%dx%d+%d+%d' % (w, h, x, y))

    button_close = tkinter.Button(windowpopup, text="OK", command= lambda : popupcomandook(sair, windowpopup))
    button_close.pack(fill='y', pady=20) 
    windowpopup.bind('<Return>',  lambda e: popupcomandook(sair, windowpopup))
    windowpopup.bind('<Escape>',  lambda e: popupcomandook(sair, windowpopup))
    
 
def get_size(obj, seen=None):
    """Recursively finds size of objects"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size

def iterateXREF_Names(doc, xref, abs_path_pdf, pismm, aprocurar, rereference, rename_dest, regex):
    chaves = doc.xref_get_keys(xref)
    #regex = "\([A-Za-z0-9\.]+\)[0-9]+\s[0-9]\sR"
    if("Names" in chaves):
        named_kids = doc.xref_get_key(xref, "Names")[1]
        found = regex.findall(named_kids)
        for f in found:
            name_dest, reference = f
       
            if(name_dest==aprocurar):
                destination_final = doc.xref_object(int(reference)).split(" ")

                dest_page = infoLaudo[abs_path_pdf].ref_to_page[int(destination_final[1])]
                cropbox = doc.page_cropbox(dest_page)
                return (name_dest, dest_page, math.floor(float(destination_final[5])), math.floor((cropbox.y1-float(destination_final[6]))))
        return None

    elif("Kids" in chaves):
        destinations_kids = doc.xref_get_key(xref, "Kids")
        destinations_limits = doc.xref_get_key(xref, "Limits")
        retorno = None
        if(len(destinations_limits)>1):
            
            quaislimites = pismm.findall(destinations_limits[1]) 
            if('null'==destinations_limits[0]):
                splitted = destinations_kids[1].split(" ")
                grauavore = int(len(splitted)/3)
                for i in range(grauavore):
                    indice = i * 3
                    novoxref = int(splitted[indice].replace("[", "").replace("]", ""))
                    retorno = iterateXREF_Names(doc, novoxref, abs_path_pdf, pismm, aprocurar, rereference, rename_dest, regex)
                    if(retorno != None):
                        break
            elif(len(quaislimites)>1):
                if(aprocurar >= quaislimites[0] and aprocurar <= quaislimites[1]):
                    splitted = destinations_kids[1].split(" ")
                    grauavore = int(len(splitted)/3)
                    for i in range(grauavore):
                        indice = i * 3
                        novoxref = int(splitted[indice].replace("[", "").replace("]", ""))
                        retorno = iterateXREF_Names(doc, novoxref, abs_path_pdf, pismm, aprocurar, rereference, rename_dest, regex)
                        if(retorno != None):
                            break
            elif(len(quaislimites)>0):
                if(aprocurar >= quaislimites[0]):
                    splitted = destinations_kids[1].split(" ")
                    grauavore = int(len(splitted)/3)
                    for i in range(grauavore):
                        indice = i * 3
                        novoxref = int(splitted[indice].replace("[", "").replace("]", ""))
                        retorno = iterateXREF_Names(doc, novoxref, abs_path_pdf, pismm, aprocurar, rereference, rename_dest, regex)
                        if(retorno != None):
                            break
        return retorno
    
def iteratetreepages(abs_path_doc, doc, numberregex, xref, count):
    objrootpages = doc.xref_get_key(int(xref), "Type")[1]
    if(objrootpages=="/Pages"):
        objrootkids = doc.xref_get_key(int(xref), "Kids")[1]
        for indobj, gen in numberregex.findall(objrootkids):
           count = iteratetreepages(abs_path_doc, doc, numberregex, indobj, count)  
        #return count
    elif(objrootpages=="/Page"):
        infoLaudo[abs_path_doc].ref_to_page[int(xref)] = count
        count += 1
    return count
        
    
def loadPages(abs_path_pdf, doc, numberregex):
    rootpdf  = doc.pdf_catalog()
    objpagesr = numberregex.findall(doc.xref_get_key(rootpdf, "Pages")[1])[0][0]
    objrootpages = doc.xref_get_key(int(objpagesr), "Type")[1]
    if(objrootpages=="/Pages"):
       objrootkids = doc.xref_get_key(int(objpagesr), "Kids")[1]
       count = 0
       for indobj, gen in numberregex.findall(objrootkids):
           count = iteratetreepages(abs_path_pdf, doc, numberregex, indobj, count)
    else:
        None
    
            
def processDocXREF(abs_path_pdf, doc, aprocurar):
    regex = "\(([A-Za-z0-9\.]+)\)([0-9]+)"
    
    if(len(infoLaudo[abs_path_pdf].ref_to_page)==0):
        numbercompile = re.compile(r"([0-9]+)\s([0-9]+)")
        loadPages(abs_path_pdf, doc, numbercompile)
        #sys.exit(0)
    #    for i in range(len(doc)):
    #        pageref = doc.page_xref(i)
    #        infoLaudo[abs_path_pdf].ref_to_page[pageref] = i
    rootpdf  = doc.pdf_catalog()
    tupla_names1 = doc.xref_get_key(rootpdf, "Names")
    
    regexismm = r"\(([mm]+\.[a-zA-Z0-9_\.\-]+)\)"
    pismm = re.compile(regexismm)
    tupla_dests = doc.xref_get_key(int(tupla_names1[1].split(" ")[0]), "Dests")
    destinations = doc.xref_get_keys(int(tupla_dests[1].split(" ")[0]))
    if("Kids" in destinations):
        rereference = re.compile("[0-9]+\s")
        rename_dest = re.compile("\([A-Za-z0-9\.]+\)")
        regex = re.compile("\(([A-Za-z0-9\.]+)\)([0-9]+)")
        retorno = iterateXREF_Names(doc, int(tupla_dests[1].split(" ")[0]), abs_path_pdf, pismm, aprocurar, rereference, rename_dest, regex)
        return retorno
    else:
        regex = re.compile("\(([A-Za-z0-9\.]+)\)([0-9]+)")
        named_kids = doc.xref_get_key(int(tupla_dests[1].split(" ")[0]), "Names")[1]
        found = regex.findall(named_kids)
        
        for f in found:
            name_dest, reference = f
            
            if(name_dest==aprocurar):
                
                destination_final = doc.xref_object(int(reference)).split(" ")

                dest_page = infoLaudo[abs_path_pdf].ref_to_page[int(destination_final[1])]
                cropbox = doc.page_cropbox(dest_page)
                return (name_dest, dest_page, math.floor(float(destination_final[5])), math.floor((cropbox.y1-float(destination_final[6]))))
    return None 

def validarPath():
    global infoLaudo, pathdb, expertmode, root, version, totalpaginas, docatual, listaRELS, listaTERMOS, clientmode
    ok = True
    infoLaudo = {}
    totalpaginas = 0
    clientmode = False
    try:
        if(len(sys.argv) == 2): 
            clientmode = True
        elif(expertmode):
            root = showInfo(None, expertmode, version)
        if(clientmode):
            pathdb = Path(sys.argv[1])
        else:
            pathdb = indexador_fera.pathdb
        doc=None
        progress = None
        if(clientmode or indexador_fera.ok):
            localp = str(pathdb)        
            sqliteconn = connectDB(str(pathdb), 5)
            cursor = sqliteconn.cursor()
            #cursor.execute("PRAGMA journal_mode=WAL")
            try:
                try:
                    root.destroy()
                except Exception as ex:
                    None
                root = tkinter.Tk()
                
                icon = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAsCSURBVFhHnZcJVJV1GsZ/390vFy7LBVkEQWQNBJdQUdGJRlMzs6YpK2tOnWnx1NRMaeuU0+nUTLadaiaNo9VYqUVWWpZa7ijuCyqIggIKiHDZ7gZ3nfcCmUzndKZ5zvkOR797/8/zf5fnfa8SEPBf6Olxc8OsmUwoLCQnN4e8vHyysrNQqVQDn/hl2LptVFZVcqLiOAf278fr9bL8g/cH3g7GzwS0tnVQXDRG3oQLoa/vyx6PB4/bQwAtkRGxGEPCMRp1hIZqUBTo7PTidPbS3dWGzd6GXi+f1Gr7Ho1GK+88ZGcnse6bTQMsP2GQgOamJkblT2bNW608/dZw1IqpT0BvryIkfoqKFO68O4xx40OJijTKN4QdZ9/j9XexeZON0tVadu0KxWTyixA/KrWWzLRWRg5r5euyq9lR9kOQ6jIux7SqspK8UQW8MW8k1+QnsXffm8TFxdPYiBC6qW3Q89Gq4Rw+pBbybIYlVPHFWiMPLXCze3ck82/TSXQsfLCyk6/W1VF8jZ3zF2D06Hz+veolFs5KoXion4JxEwcY+3E5AlMmTcbabmNkGjw4twl/sp9bbk5j3YYWubmF+XcYSBkeRc0ZO/n5QxmeGkN4uBFXjwu9ziEiGrjU0kF6BhL2Dh5f2MzhMhPXXj+MTRtrMNar+MMrKVjbWnniyUU89PDDgwW4XC4yRqSTmhJHY6uWgCfA3r01RMeZJNDpfPiBjhkzcyUqopBUKisbqKtrhYCLoYmKiFLj9tbyycpaFPVF7r6zDZXHR09XgNyJOQTUkBDlQq2PYPvO7UHKPgyqgeee/StffvEVdoeZ/WXVWCRkvd54DPp09uwyER6RyksvVrBtSzUGowa1Wk4VeX5/8AIwcbKFRc8aCHgbmFTYiKMdQhQpUBExsjgPxd/C6k9XSUrH9xMKBgk4deoUheNv5OPlDq6fa8fl1aAzJvH2q07szjAhctHSYusrPZ1OjUEem8NAj9ShXyI2NNLB6CQPzc0RxBQ4uXV+O84WEaH1sHObkTseHcGFC/v7yQYwSEAQUwsT2VFuxdVhwK3SUrIslLqGMYzImkFcbIxEQ4/V2kZN7VlaGk+x5I7PIFwj0YHasxquShU1bSm8tSqS2FGd3HZbC+7OAPpwJ/c/NIaSjw8NMPVjkLOs//oALz4pBdgeDC+crVELmYHUzJlkpScSY9ajpxeL2UhmRqr0diJDRvkYMlrF6rIEFpeMgFg50lTPrVO81Bw1SY3IwRKyQKeOBbcclk76Kf9BDBKwacO/mHJNAHeP/MMXIDHeQ2urAcVnZUiURQxIxKSnotdqMBlDiJC2I2gHuhnsPziW+gshOL2hYPZT0drJ0nVhNDXq0Kj9iI8xugDKt77Rx/UjBgkwekuhVysJlTMNPpYutbBta4BoS5O0TyfxCfGsXfsl5eXlfQLsdhsYoKMrm1BTrvS8liMnwyQCQlRpxGAI8PayIagNYkhyJm6IUjbQK2J+xGUBFScamZAv+ZMPKcGy1vn44quIvkMuXWrDZDZTXVnNnNnX91Vxq9UqhShi5SsR4VsomFDNxKIeqX4rdIkom1pE+vhqY6Sw+ORSkgs5e+oYP4eO1AywXiGgpqae7BTJlahTSwi6GzR0dKvFVBSxYhf1Yokur5/TtQ20dnTT3t3JxZZL0B3M7xHMhh+I0p2HFulHu67vZJXk3u1V0VKrR6uICBGQnQzV1bUDrFcIaO/oIlKiF/AEw+Wnw6pCUo3PpxI5Tk6cOCrdUCvDqk5u30RDfY08dVLxEoXzHjKMDsYO6SDQJDmxp6HTBIeXuKI6IENKaKTZAqLBIiXS3t7ZTyoQin5oNBq8UnyKFB8+v7zwyR+FiGiFWel1jM3eKLGGA0e1FEyTMAXPkFZdU3uGCINNwq3rm5qnvTrccvP46Pki3iciNDJDJaXegKRWg7vXiyZ4swFcjsCItFS5XX/+/b1iKrEunC4V48a5ULnsSP9Ji4Xw0eZ0vt0+Br/FjEMfQpS+myiTjfqachpq97J5/QosIU6GJudLFNz0iprEaCkUj6jy62ix6klLH95PKpD4euH4InKUVyirjOn7z4B4OBof+VmOPuVDoqTaZfYfOBJGbFwxzz1lQaWdRsCkYNTrOHH8uIh1Sk1clAFlRivJ14elMSzKR0qCC4056JSSGnTsPhXNaPdaaZPXJdJe1M9nr/4bnmOEqBu42iL5N7lRCXmwvfQSwLIjEaQnOUjJkltlhnP2bCoFBQVExZwh3NhMxck5kqouAnLBxGFJTC6ahFoXzund77J6q5sn72okL7MHxSsHunXkaWWKKnKxi2dhV2m/FfeWXCPbzwW6FSsRuX42HjBSuiOSD0uqyC6cwI3XWblxahvJuQHufeQqOtrVZOXY+eCVBsqqynC76khMTsQUFinbj589Xz4jE+8gB+rMVG46yFvvDMegVfHAbCftB8Iwq80iOgL9w5sk5QdfCGD9RDYwPfWmd1lbMofbZ2hZVBLHQzefJ2u4g+S5E5hbbKVoTCc5o91MnCa9Z5f8NpjYbd0vKVJkWLlprvqEk+Wl7Kk2sfe0mWPLq6SVDXy3T4ZTqILa28rVN31GTttr0r5SiKm/RxVo2CBJ1+JzNMsNJ3PGt4D4WDvDhnjYvC9WthwV5SUVfCdbz9+XJ7OsJIaXF8ax9fMw9L0xtNl9HN3yHOuXTeO999ezcmc0h86a+X7JOZIy/KzYEINeuO69toudbbeRM/43srU2C6fk7HSZdN0PtwcUqQFFK+Yw8aD4cS53zsrg/cdcPLI8krHpPdx/Uws2m8LvFssiUmdEowqQN8LJTZNUshHZWfGdge6eEDEdhdR4N18sFtNyaVjyuYUe6YI37+rlT8t6Kfn6LCrrPtgm25B3qMyM8ZKCqvcCyrl/cEFCmJgh5TqykpM17ax9MY2bi6Oxunz8c304s8Z3c88fL3FsexirtoWz/ZiJLruKbqdCSqyXybk9zJtqZ0yRg5fejKXinJ4Z+R7ume7n1Q8vUfTnw2L1ibDjWnbv70Xl0FA47+mBfWBzPE+tsXBD4TkmTU+F5OOUHepi05t5PD3PyPOlRh6caef1dSYW395JXJQYkZCKV/X7rVrBXa/ldKOe9zeH8ts8L+XVWp6ZE+C1z7sYe18Zs4oS8JVdy7rNLbTZzEyMN5L7xJYBAY5qOjZmMX9pDgvn1RIZ1cOomffT1DGbRQte4+3bbVQ0KmyskJF9TMPKR21sP6khWmzV6lBYs0PPxGyv+IiWJ27wEarTMC1XxT0rFJ564X4yk7fRsOkTvtmXJkNKz925HpIW7ASt5YqNyHeJwIGrONNs5URzKOdaZOlItTOl0I+MByzaEKl8mfcXzbTJs++c/GiREOhlWB2u1TA9R0Ncgo2MAitd8kNFF9NBXa0Wk8/Jjv1RVNREcot00bjMkSjTvxPLDRqT/Lks4Ed0fypES9j1w2HsMhtKv0/glceaiImHBS+k8/Ad58lJ8dNZncaWPRICMdM5xV1oc05JKgI89WIq0eEuFt7XzOI3LBSPshInS0vmyNkw9HGZJ9IFV+DnAq5EzzdSrbupP3qQ5LDtlG700tBmJj9TCjjMRvTwB/C6rRh6SnninSzee+wUh6ugcKxJbHo8xoTJ4qjyQ8Rw3cCBP8cvC/gZJBeXXubM1udY+m0K469yUFkfwtUZdkYmWUmZIuvWkL8MfPZ/w68UcAVOFnN0z2GpAb+071TCJn098OLX4f8XEETNEikBWUhSf92tfwL8B8MhvFTZhRwkAAAAAElFTkSuQmCC'
                #root.tk.call('wm', 'iconphoto', root._w, tkinter.PhotoImage(data=icon))
                root.title("FERA "+version+" - Forensics Evidence Report Analyzer -- Polícia Científica do Paraná")
                root.geometry("400x100")
                root.rowconfigure(0, weight=1)
                root.columnconfigure(0, weight=1)
                progress = ttk.Progressbar(root, mode='indeterminate')
                progress.grid(row=0, column=0, sticky='nsew', pady=20)
                sqliteconn.execute("PRAGMA foreign_keys = ON")
                cursor.execute("begin")
                select_all_pdfs = '''SELECT  P.id_pdf, P.rel_path_pdf, P.lastpos, P.tipo, P.margemsup, P.margeminf, P.margemesq, P.margemdir FROM 
                Anexo_Eletronico_Pdfs P ORDER BY 4,2
                '''
                cursor.execute(select_all_pdfs)
                relats = cursor.fetchall()
                progress['mode'] = 'determinate'
                progress['maximum'] = len(relats)
                qtos = 0
                verificados = {}            
                cont = 0
                docatual = ""
                abs_path_pdf = None
                pathpd = None
                for r in relats:
                    if(r[3]=='relatorio'):
                        listaRELS.append((r[1], r[0]))
                    progress['value'] = qtos
                    #root.update_idletasks()
                    progress.update()
                    qtos+=1
                    if(doc!=None):
                        doc.close()
                    beforereplace = os.path.normpath(os.path.join(os.sep, pathdb.parent, r[1]))
                    afterreplace = ""
                    if plt == "Linux":                   
                        abs_path_pdf = str(beforereplace).replace("\\","/")
                    elif plt=="Windows":     
                        abs_path_pdf = str(beforereplace).replace("/","\\")
                    #abs_path_pdf = os.path.normpath(abs_path_pdf)
                    pathpd = os.path.relpath(Path(abs_path_pdf).parent, pathdb.parent)
                    novorelatorio = Relatorio()
                    filename, file_extension = os.path.splitext(abs_path_pdf)
                    if(file_extension.lower()==".pdf"):
                        doc = fitz.open(abs_path_pdf)   
                        pdf = os.path.basename(abs_path_pdf)
                        idpdf= r[0]
                        novorelatorio.mt = r[4]
                        novorelatorio.mb = r[5]
                        novorelatorio.me = r[6]
                        novorelatorio.md = r[7]
                        novorelatorio.id = idpdf
                        novorelatorio.len = len(doc)
                        totalpaginas += novorelatorio.len
                        pageorg = doc[0]
                        pixorg = pageorg.getPixmap()
                        novorelatorio.pixorgw = pixorg.width
                        novorelatorio.pixorgh = pixorg.height
                        select_tocs = '''SELECT  T.toc_unit, T.pagina, T.deslocy, T.init FROM 
                        Anexo_Eletronico_Tocs T WHERE T.id_pdf = ? ORDER BY 2,3
                        '''              
                        cursor.execute(select_tocs, (r[0],))
                        tocs = cursor.fetchall()
                        for toc in tocs:
                            novorelatorio.toc.append((toc[0], toc[1], toc[2], toc[3]))
                        infoLaudo[abs_path_pdf] = novorelatorio
                        infoLaudo[abs_path_pdf].ultimaPosicao=float(r[2])
                        infoLaudo[abs_path_pdf].tipo = r[3]
                        infoLaudo[abs_path_pdf].idpdf = r[0] 
                        #try:
                        #    processDocXREF(abs_path_pdf, doc)
                        #except Exception as ex:
                        #    printlogexception()
                        teste = 'SELECT 1 FROM Anexo_Eletronico_Conteudo_id_pdf_' + str(idpdf) + ' LIMIT 1'
                        verificados[str(idpdf)] = "OK"
                        cursor.execute(teste)                    
                        cont+=1
                      
            except Exception as ex:
                printlogexception(ex=ex)
                return False
                #sys.exit(1)
            finally:
                if(doc!=None):
                    doc.close()
                cursor.close()
                sqliteconn.close()
                if(progress!=None):
                    progress.grid_forget()
            if(clientmode):
                return True
            return indexador_fera.ok
    except Exception as ex:
        printlogexception(ex=ex)
        return False
        #sys.exit(1)


def locateToc(pagina, pdf, p0y=None, init=None, infoLaudo=None):
        pdfx = (str(Path(pdf)))
        t = 0
        napagina = False
        naoachou = True
        if(init!=None):
            for t in range(len(infoLaudo[pdfx].toc)-1):
                if(pagina >= infoLaudo[pdfx].toc[t][1] and pagina < infoLaudo[pdfx].toc[t+1][1]):
                    naoachou = False
                    break   
                elif(pagina >= infoLaudo[pdfx].toc[t][1] and pagina <= infoLaudo[pdfx].toc[t+1][1]):
                    napagina = True
                    
                if(napagina and infoLaudo[pdfx].toc[t+1][3] > init  ):  
                    naoachou = False
                    break
            
            if(naoachou):
                if(pagina==0):
                    t=0
                else:
                    t=len(infoLaudo[pdfx].toc)-1
                    
        elif(p0y!=None):
             for t in range(len(infoLaudo[pdfx].toc)-1):
                if(pagina >= infoLaudo[pdfx].toc[t][1] and pagina < infoLaudo[pdfx].toc[t+1][1]):
                    naoachou = False
                    break   
                elif(pagina >= infoLaudo[pdfx].toc[t][1] and pagina <= infoLaudo[pdfx].toc[t+1][1]):
                    napagina = True
                    
                if(napagina and infoLaudo[pdfx].toc[t+1][2] > p0y  ):  
                    naoachou = False
                    break
            
             if(naoachou):
                if(pagina==0):
                    t=0
                else:
                    t=len(infoLaudo[pdfx].toc)-1
        
        #t-=2
        t = min(t, len(infoLaudo[pdfx].toc)-1)
        t = max(0, t)
        if(len(infoLaudo[pdfx].toc)>0):
            return infoLaudo[pdfx].toc[t][0]
        else:
            return ""
        



def go():
    global request_queue, response_queue, response_queuexml, processed_pages, minMaxLabels, divididoEm, \
            zoom, listaZooms, posicaoZoom, exitFlag, comandos_queue, request_queuexml, infoLaudo, \
            pathdb, renderprocess, erros, queuesair, result_queue, realce, root, searchqueue, warningimage, version, update_queue,\
            searchResultsDict, mw, manager, render_process, render_processxml, listadeobs, processed_requests, listaTERMOS, listaRELS
    minMaxLabels = 5
    
    exitFlag = False
   
    continuar = True    
    divididoEm = 1
    
    realce = None    
    posicaoZoom = 0
    try:
        '''
        if(len(sys.argv)==1):
            root = tkinter.Tk()
            if getattr(sys, 'frozen', False):
                application_path = sys._MEIPASS
            elif __file__:
                application_path = os.path.dirname(__file__)
            #iconFile = 'logoMini.ico'
    
            #root.iconbitmap(default=os.path.join(application_path, iconFile))
            #root.bind('<Control-Alt-F12>', f12Pressed)
           
            icon = b'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'
            root.tk.call('wm', 'iconphoto', root._w, tkinter.PhotoImage(data=icon))
            root.title("FERA "+version+" - Forensics Evidence Report Analyzer -- Polícia Científica do Paraná")
            root.geometry("400x200")
        
            root.rowconfigure(0, weight=1)
            root.columnconfigure(0, weight=1)
        '''
        manager = mp.Manager()
        listaRELS = manager.list()
        if(not validarPath()):
            on_quit()
        else:
            if plt == "Linux":
                try:
                    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
                    root.geometry("%dx%d+0+0" % (w, h-50))
                    
                except Exception as ex:
                    root.state("zoomed")
                    #printlogexception(ex=ex)
                    
            elif plt=="Windows":
                try:
                    root.state("zoomed")
                    #monitor_info = GetMonitorInfo(MonitorFromPoint((0,0)))
                    #work_area = monitor_info.get("Work")
                    #root.geometry("{}x{}+0+0".format(work_area[2], work_area[3]))
                except Exception as ex:
                    #printlogexception(ex=ex)
                    try:
                        root.attributes('-zoomed', True)
                    except Exception as ex:
                        None
            root.resizable(False, False) 
            
            root.title("FERA "+version+" - Forensics Evidence Report Analyzer -- Polícia Científica do Paraná")   
            iconFile = 'logoMini.ico'
    
            #root.iconbitmap(default=os.path.join(application_path, iconFile))
            #root.bind('<Control-Alt-F12>', f12Pressed)
           
            icon = b'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'
            root.tk.call('wm', 'iconphoto', root._w, tkinter.PhotoImage(data=icon))
            queuesair = mp.Queue()
            request_queue = mp.Queue()
            request_queuexml = mp.Queue()
            response_queue = mp.Queue()
            response_queuexml = mp.Queue()
            
            erros = mp.Queue()
            searchqueue = manager.list()
            result_queue = mp.Queue()
            update_queue = mp.Queue()
            comandos_queue = queue.Queue()
            LOG_FILENAME = os.path.join(pathdb.parent, 'fera.log')
            logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)
            root.columnconfigure(0, weight=1)
            root.rowconfigure(0, weight=1)
            loadingimageb = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAABbElEQVRYhe2XwU7CUBBFz++4YaEL48If0Ci1Loou/FkSNyWaQKSEhcQVLf4BauqirXmOQ53XFk0IN3kr3sw9pcncKTTXFZABK6Dfok9jZUBenuw/AHJxdgfgEBgBCRB0ABABcyAGehaAkdP0vWzQFOAO+HDu3FsAEtF4E0Tq3EkN5jkwtgAEpamEkK+jDyxL8wvx20AxXwNnFgCAGwUisRYDL6L2jWJueOlWQMQetVNhHvqaV7oGZqX5kUfdCfBI8a9dNjXf689UpZocLCndpFwIvCr9v1JUM6/OsgMAzfxbiq5qLmgTzle/9u+z+RXICddE2+6/13Y1AJ6BCXDsUXdKMcIXtMgBmecPHrUzp65uqTGb58CTR/1C1HpBRIr5GjgX96oJp30XhNiWGlVzxVxbJtwJp30XRArExAIQG8zh52DRJCGGFoAexfY6pn6Hs67lAcWTD4EDC4BVu/tlZJWbcl2kpreqlGuVap8XFOOeE7/ywAAAAABJRU5ErkJggg=='
            loadingimage = tkinter.PhotoImage(data=loadingimageb)
            #window = tkinter.Toplevel()
            
            #label = tkinter.Label(window, text="Carregando arquivos", image=loadingimage, compound='top')
            #label.image = loadingimage
            #label.pack(fill='x', padx=50, pady=20)
            #root.update_idletasks()
            #root.attributes("-alpha", 0)
            try:
                
               
                listaTERMOS = manager.dict()
                
                processed_pages = manager.list([None] * minMaxLabels)
                processed_requests = [None] * minMaxLabels
                listadeobs = manager.list()
                render_process = mp.Process(target=backgroundRendererImage, args=(processed_pages, request_queue, response_queue, queuesair, infoLaudo, erros,), daemon=True)
                render_process.start()
                render_processxml = mp.Process(target=backgroundRendererXML, args=(request_queuexml, response_queuexml, queuesair, infoLaudo, erros, listadeobs,), daemon=True)
                render_processxml.start() 
                 
                #renderprocess = mp.Process(target=startThreads, args=(request_queue, request_queuexml, response_queue, queuesair, infoLaudo, erros,), daemon=True)
                #renderprocess.start()
                #processes.append(render_process)
                #processes.append(render_processxml)
                processes['Renderização de PDF'] = render_process
                processes['Extração de XML'] = render_processxml
                sqliteconn = connectDB(str(pathdb), 5)
                cursor = sqliteconn.cursor()
                #cursor.execute("PRAGMA journal_mode=WAL")
                pos = 0
                try:
                    teste = 'SELECT id_conf, config, param FROM FERA_CONFIG'
                    cursor.execute(teste)
                    configs = cursor.fetchall()
                    for config in configs:
                        if(config[1]=='zoom'):
                            pos = int(config[2])
                except Exception as ex:
                    printlogexception(ex=ex)                   
                finally:
                    cursor.close()
                    if(sqliteconn):
                        sqliteconn.close()
                
                posicaoZoom = pos
                listaZooms = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0]
                searchResultsDict = {}
                zoom = listaZooms[posicaoZoom]
                warningb = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAChklEQVRYR8XXt44UQRDG8d/hibEiIsC7iICHgAjvrQAhEjwhBAhPBhLeexIkXoMA762EgATxABygknpOc6PdnZm9W5hope2p+tf3VVdPd/nPT1cf8w9K7/9qN067AANxGqvRjVPYgT91QdoFOIkt+J2SBtB+7PsXADPxKCWegx94goCYiM91INpR4B7m4w4Wp2QnsC3ZsrmTAPnqZ+FZSjYGHxBNOaGOCnUVuIsFuI0lhUqPYzvOYFNVFeoAzMDj5H0o8byQJFR4j8GpFz5VgagDEJ4vbFJ9litT4Sw29ifA9NTpsc9DiRdNgo9OvRAqTMLHMoiqCoTni3ALS3NBs8GTj3MsDaXz2NAfAFF9eB9PsfpGAJkKQ5IKsTuaPlUUyKq/iWWFSI0AYslR7MQFrO8LwLTkfcQIJV5WBBiV/A8VJqfd0ZCjTIHwPKbdDSxvEKGZArH0CHbhItY1U6EVQL76+P2qJkCoEP4PxRS8awTRCiA8j2nXrPqI10qBvAqXsLYOwFQ8TQnC+0bVVwEoVaGZAln117GiRReXKRCvHsZuXMaaYqxGAFWrL5sx2f8j044Ylnrhbf7FRgDheUy7a1hZNUvJukPYgyvpM65neREgujXO+JA2Ov91i8BzcS79HyP3QYu1oULsiOEIhd9ka4sA4XlMu6tYVVLVN8QRHM93jC1ZfxB7i7HzADGx4oyP6ntRNglcF2BE6oVQoUfdPEDM7dirVaoPpjoWZDVkKvT0Qh7gC8alE6zHo35qwixMqBDK/UTMCHmAr8nH2XjYz4mzcPNwPwfQnQfIDo8O5e4VNi42W4sKDMCBNP/Hd4giLi1xr4jJGFe6XhZ0KGfrsGXfAx2H+gthzokhxc9aDgAAAABJRU5ErkJggg=='
                warningimage = tkinter.PhotoImage(data=warningb)
                #window.destroy()
                mw = MainWindow() 
                #root.attributes("-alpha",255)
                
            except Exception as ex:
                printlogexception(ex=ex)
            root.protocol("WM_DELETE_WINDOW", on_quit)
            root.mainloop()
            
    except Exception as ex:
        printlogexception(ex=ex)
        on_quit()

if __name__ == '__main__':
    try:
        mp.freeze_support()
        go()
    except Exception as ex:
        sys.exit(1)