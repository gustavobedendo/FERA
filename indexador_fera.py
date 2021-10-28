# -*- coding: utf-8 -*-
"""
Created on Fri Oct 30 10:41:59 2020

@author: gustavo.bedendo
"""
from tkinter.filedialog import askopenfilename, asksaveasfilename, askopenfilenames
import tkinter 
from tkinter import ttk
from pathlib import Path
import os
import fitz
import sqlite3
import traceback
import sys
import multiprocessing as mp
import threading as thr
import time
import math
import hashlib
import logging, re
from functools import partial
import platform 
#from fera import f12Pressed
from PIL import Image, ImageTk

plt = platform.system()

#mp.set_start_method('forkserver', force=True)
#mp.freeze_support()
global dbversion, clear_searches, root
dbversion = "1.22-30032021"
printorlog = 'none'
def printlogexception(printorlog='print', ex=None):
        if(printorlog=='log'):
            None
        elif(printorlog=='print'):
            print(ex)
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_tb)
        else:
            None 
class Processar():
    def __init__(self, idpdf, rel_path_pdf, pdf, init, fim, mt, mb, me, md):
        self.rel_path_pdf = rel_path_pdf
        self.pdf = pdf
        self.idpdf = idpdf
        self.paginit = init
        self.pagfim = fim
        self.me = me
        self.mt = mt
        self.mb = mb
        self.md = md


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

def sairpdfdif(varok, valor, window):
        varok.set(valor)
        window.destroy()

def popup(window, varok, texto = 'Os arquivos não possuem HASH compatível.\n\nDeseja prosseguir?'):
        #global warningimage
        warningb = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAChklEQVRYR8XXt44UQRDG8d/hibEiIsC7iICHgAjvrQAhEjwhBAhPBhLeexIkXoMA762EgATxABygknpOc6PdnZm9W5hope2p+tf3VVdPd/nPT1cf8w9K7/9qN067AANxGqvRjVPYgT91QdoFOIkt+J2SBtB+7PsXADPxKCWegx94goCYiM91INpR4B7m4w4Wp2QnsC3ZsrmTAPnqZ+FZSjYGHxBNOaGOCnUVuIsFuI0lhUqPYzvOYFNVFeoAzMDj5H0o8byQJFR4j8GpFz5VgagDEJ4vbFJ9litT4Sw29ifA9NTpsc9DiRdNgo9OvRAqTMLHMoiqCoTni3ALS3NBs8GTj3MsDaXz2NAfAFF9eB9PsfpGAJkKQ5IKsTuaPlUUyKq/iWWFSI0AYslR7MQFrO8LwLTkfcQIJV5WBBiV/A8VJqfd0ZCjTIHwPKbdDSxvEKGZArH0CHbhItY1U6EVQL76+P2qJkCoEP4PxRS8awTRCiA8j2nXrPqI10qBvAqXsLYOwFQ8TQnC+0bVVwEoVaGZAln117GiRReXKRCvHsZuXMaaYqxGAFWrL5sx2f8j044Ylnrhbf7FRgDheUy7a1hZNUvJukPYgyvpM65neREgujXO+JA2Ov91i8BzcS79HyP3QYu1oULsiOEIhd9ka4sA4XlMu6tYVVLVN8QRHM93jC1ZfxB7i7HzADGx4oyP6ntRNglcF2BE6oVQoUfdPEDM7dirVaoPpjoWZDVkKvT0Qh7gC8alE6zHo35qwixMqBDK/UTMCHmAr8nH2XjYz4mzcPNwPwfQnQfIDo8O5e4VNi42W4sKDMCBNP/Hd4giLi1xr4jJGFe6XhZ0KGfrsGXfAx2H+gthzokhxc9aDgAAAABJRU5ErkJggg=='
        warningimage = tkinter.PhotoImage(data=warningb)
        window.rowconfigure((0,1), weight=1)
        window.columnconfigure((0,1), weight=1)
        w = 400 # width for the Tk root
        h = 200 # height for the Tk root
    
        label = tkinter.Label(window, text=texto, image=warningimage, compound='top')
    
        label.grid(row=0, column=0, sticky='ew', pady=20, columnspan=2)
        
        
        # get screen width and height
        ws = root.winfo_screenwidth() # width of the screen
        hs = root.winfo_screenheight() # height of the screen
        
        # calculate x and y coordinates for the Tk root window
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        window.geometry('%dx%d+%d+%d' % (w, h, x, y))
        
        button_ok = tkinter.Button(window, text="Prosseguir", command= lambda : sairpdfdif(varok, True, window))
        button_ok.grid(row=1, column=1, pady=20) 
        button_cancel = tkinter.Button(window, text="Cancelar", command= lambda : sairpdfdif(varok, False, window))
        button_cancel.grid(row=1, column=0, pady=20) 
    

global root, listapdfs, nthreads, threads, threadp, threadcontinuar, stopwords
import psutil 
nthreads = math.floor(psutil.cpu_count(logical = False)*0.8)
threads = [None] * nthreads


class App():
    global pathdb, indexando, qlchild
    def __init__(self):
        global indexando, finalizados, paginasindexadas, threads, clientmode
        try:
            if(clientmode):
                self.abrir()
            indexando = 0
            
            finalizados = 0
            paginasindexadas = 0
            self.globalFrame = tkinter.Frame(root)
            self.globalFrame.grid(row=0, column=0, sticky="nsew")
            self.globalFrame.rowconfigure(0, weight=1)
            self.globalFrame.columnconfigure(0, weight=1)
            
            self.dir = None
            self.file = None
            
            #self.topFrame = tkinter.Frame(self.globalFrame)
            #self.topFrame.grid(row=0, column=0, sticky="nsew")
            #self.topFrame.rowconfigure((0,1), weight=1)
            #self.topFrame.columnconfigure(0, weight=1)
            #fileimageb = b'iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAABqUlEQVRoge3YPWsVQRQG4Cf+EYnGBP+CSkCxMUZNo1iIdQoxggumESyDBhRtLCwETWcKUbENCILaCZY2NjZ+IEhIo7GYlVw3dzWLZycK88Iplj33zD4w93J3KCkpKfkfMoKzuB1QS3iEHTkB0/iIq1j4y1rGOl7nRFT1whGZkQBZERUeBM06YQOQDREJOO5XQBZEJOCYzYDeEZGAacMBvSIiAUe1A3pDRAKm/B7QCyIScNifAeu4GbQeYgEj2IlR7MJujGEPxjGBFcwFrYdYwFbyGOciBxZAxxRAMwXQMQXQTAF0TAE0UwAdUwDNFEDH9A44IP1fvxBUc9iXC3AQ323trapLfcP+HIBLLQ/wQnqTelkD39bXz/C10bOCD0NmXMwBmG8BjOE8JnG5/swRzGIvVgd65vFmyIxquwHPcUU6ya5wp743g6d1zy3cbZmx7YDT0hfyXQNwCg/rnkXpmP2fBAzu6wpncE06efg8pCcr4OfxehtgGWsD16+krbKE9y09bYAn0YApfMJ13LfxSxJd9+o1vuBQJIC0v29kqpPRD19SUlLST34A2hs/U9aSDHMAAAAASUVORK5CYII='
            #self.fileimage = tkinter.PhotoImage(data=fileimageb)
            #self.labelLaudo = tkinter.Button(self.topFrame, image=self.fileimage, command=self.loadLaudo)
            #self.labelLaudo.grid(row=0, column=0, sticky="ns")
            
            
            
            #self.labelLaudo2 = tkinter.Label(self.topFrame, text="")
            #self.labelLaudo2.grid(row=1, column=0, sticky='ew')
            
            
            #self.bottomFrame = tkinter.PanedWindow(self.globalFrame)
            #self.bottomFrame.grid(row=0, column=0, sticky="nsew")
            
            self.directoriesFrame = tkinter.Frame(self.globalFrame, borderwidth=1, relief='groove')
            self.directoriesFrame.grid(row=0, column=0, sticky="nsew")
            self.directoriesFrame.rowconfigure(0, weight=1)
            self.directoriesFrame.columnconfigure(0, weight=1)
            if(expertmode):
                self.dirs = ttk.Treeview(self.directoriesFrame, selectmode='extended', columns=('ID', '% Indexado', 'Tempo Decorrido (s)', 'Tempo Restante (s)', 'Paginas / Segundo', 'N Threads', 'Tipo'))
                self.dirs['column']=("zero","one", "two", "three", "four", "five", "six")
            #root.update()
           
                self.dirs.heading("#0", text="Relatorio", anchor="n")
                self.dirs.heading("zero", text="ID", anchor="n")
                self.dirs.heading("one", text="% Indexado", anchor="n")
                self.dirs.heading("two", text="Tempo Decorrido", anchor="n")
                self.dirs.heading("three", text="Tempo Restante", anchor="n")
                self.dirs.heading("four", text="Paginas / Segundo", anchor="n")
                self.dirs.heading("five", text="N Threads", anchor="n")
                self.dirs.heading("six", text="Tipo", anchor="n")
                #self.dirs.column("one", minwidth=150, width=150, stretch=True)
                #self.dirs.column("zero", minwidth=50, width=50, stretch=True)
                #self.dirs.column("#0", minwidth=200, width=200, stretch=True)
            else:
                self.dirs = ttk.Treeview(self.directoriesFrame, selectmode='browse', columns=('Status', 'Tipo'))
                self.dirs['column']=("zero", "one")
                self.dirs.heading("zero", text="Status", anchor="n")
                self.dirs.heading("one", text="Tipo", anchor="n")
            
            self.hscroll = tkinter.Scrollbar(self.directoriesFrame, orient="horizontal")
            self.hscroll.config( command = self.dirs.xview )
            self.dirs.configure(xscrollcommand=self.hscroll.set)
            self.hscroll.grid(row=1, column=0, sticky='ew')
            
            self.vscroll = tkinter.Scrollbar(self.directoriesFrame, orient="vertical")
            self.vscroll.config( command = self.dirs.yview )
            self.dirs.configure(yscrollcommand=self.vscroll.set)
            self.vscroll.grid(row=0, column=1, sticky='ns')
            
            #self.dirs.bind('<<ListboxSelect>>', self.onselect)
    
            self.dirs.grid(row=0, column=0, sticky="nsew")
            self.dirs.bind("<<TreeviewSelect>>", lambda e: self.treeview_selection(e))
            
            #self.bottomFrame.add(self.directoriesFrame)
            
            root.update()
            imfecharb = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAhElEQVRYhe2WsQ3AIAwEbwr2H4eKJkXGSRojpUiigIEv4pco/fcSYBtCodCzMlCA5PBI5pF7igtwAFtniGS1h3m5DFpDeGrdRsPgPYbD4S3G0+BfANPhb6Bl8LsQu51l8GuICq5BlsHlAaRXIH2E0m8obUTSViwdRvJxLF9I5CtZKPQPnYIqZ80MhoLJAAAAAElFTkSuQmCC'
            self.imfechar = tkinter.PhotoImage(data=imfecharb)
            imopenb = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAABkElEQVRYhe3VwUtUURTH8Q9ECPoPtPIfEKKVf0C0FcyiRYxoqdRiaqFSq6BFqxZDLUSDVvoHSAutVbgQg5RBhIJW7VsZWhElr8W90uPpDL4382ZczA8O53Deu7wvv3vuffR0jjWGN7iU6r3Gbs64hoEiAB+Q4F6qtxF7eWIyrssNUcE8rrQBICkCsYkfTjqwhWqDWD4FYCX1fCQPwCimMJQByOtAOt7lAdiJi6oZgE3cLxAfzwowiyV8awBQugNLMTdyoNkMNIvtdgH0HCjdgYVuA/S3AHDYDoBjnRXgFx5jAnMxP8HvTgD8wU18yvR3cQtHZQPUhFOxj2nh6p7BAd5jsWyAiZgf4Wusv+BprCfLBqic8qEj4e5PcLtsgCn8xJowiHU8FOz/LvzKCwNcxR0MNgGoCxOfYA+v/B/IeXxuBeCGMFz9qV4WIME67gp7/zcCjAsutHQMLwjDldZb4bLJxiie4wFe4HqD91bzAOTRtJPD2VEdA9SEbegKwMtYP+sGwDD6Yn0RlzsN0FNh/QMhUGALjgWQ1AAAAABJRU5ErkJggg=='
            self.imopen = tkinter.PhotoImage(data=imopenb)
            imupdateb = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAACFklEQVRYhdXXTYjNURjH8c/cmWksjJDXkCy8ZCg0KZESGzZsiMJKxE5KUZItNt5JysJC0WQKE7FAKI1SxCgiUfJSxshLGtfiHLlN9/+f+597b5dfnc25v+d5vp1zzznPn39cTWiuVfEGfEA3ZhfM5zAO87AKy9GK4ZUGWIR8HI8xF3vxumC+cPzCLWzFkEoAHEwp9ADtOIpTuNwH7B22oH6gxevwqkjx0xifEjMrgv+I/g4MHQhAa5HieXwU9r8/TcT1GNOFMVkBziUA5HGjxByNOB5j7ggnqmTtSwF4miFPDm0x7nAWAJiGhViCZViBlRibMc9gvEQvWrJCVErrhVW4UCuAerzBTwxLM+7AVWHvKq0TwiqsSzM9i6aK3GR9tDrmPpJkyOE7eoRLpdJaEAHakgyjouFJFYoTTlUet5MMzdHwvEoA82P+9jRTN76qzhasiQCH0kyd0TSligCb00y7o2lbFQBywh+xMc00MwI8UsZbXq4uRoi1tQKYITwcbzEhQ1yDcMZf4CHu467QPV2Lv5esncIqdCr9VmyR/ITnhZe0ZNXhjL8N6eQSYy4lFO81gNasEcdigi/Yo//VGIn3RQA6shYv1CZ8iol6cB4bsBjTMUf4NtiOe0WK57GxHAAYgQP4nFCgcHQJfWPh3OhyAf6oCUuxH2dxE1dwEruEbroOg4RH7ZtwKmqiScKqTa0VwP+h3y5rsNtpU0mxAAAAAElFTkSuQmCC'
            self.imupdate = tkinter.PhotoImage(data=imupdateb)
            imaddb = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAS0lEQVRYhWNgoAzMhOIBA2egeNQBow4YdcCoA0YdMOqAoe2AmUgGkYq/QjG5+mcOCgdQAoZHGhh1wKgDRh0w6oBRB4w6gBJAcfccAKlCYd1gjUu5AAAAAElFTkSuQmCC'
            imremoveb = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAA4klEQVRYhe2XIQ7CQBBFXwKCpAZRUcNVCIpwjapeoqKiB0DiOEAFpqpcAIHgDpBUcwIQHZJm2TZtGdy85Jvm78xLtmbBzwwIO7IHXh059pybd+zyUvQsmZrzGIENkCtnN0ZgCaTAQSmpzBzMP66gGCNwByqaH0cjlcwczAMonW8LT++zwMXtljJzskACPIHA6Z0kbQLpJpoCOc09Rk7vKmkTSTc3ARMwARMwARMwARMwAU2BTIaGTu8iaRNKN9MUWAGxp7eWuMRyRk3gV0YL3IAavadZLTMHsxVjrWfZQ2Z+8QZsqyF6+vcXyAAAAABJRU5ErkJggg=='
            imbrowseb = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAiElEQVRYhe3SOwqAMBCE4R/sPZkHsbDyGLYWXiRH8gJqqRCbBIQYH2CyhTswkG4+woIGOmAF7EU3oE8FuBs/IpLkybhvIQ1oUiDeAL5ocE+5AcE9SQBsDFAhkFOVNMCQ9vt9TQyQ9RYUoAAFKEABClCAOGBxj8mNlxnHZ4AWGIHajQ8Zx1t+nx2V3cDT6bQk5wAAAABJRU5ErkJggg=='
            self.imadd = tkinter.PhotoImage(data=imaddb)
            self.imremove = tkinter.PhotoImage(data=imremoveb)
            self.imbrowse = tkinter.PhotoImage(data=imbrowseb)
            self.continueFrame = tkinter.Frame(self.globalFrame, borderwidth=4, relief='flat', pady=5)
            self.continueFrame.grid(row=2, column=0, sticky="nsew")
            if(expertmode):
                self.continueFrame.rowconfigure((0,1,2,3,4,5,6), weight=1)
                self.continueFrame.columnconfigure((0,1,2), weight=1)          
                self.blocate = tkinter.Button(self.continueFrame, text="Localizar relatorio(s)", command=self.locarel, state='disabled', image=self.imbrowse, compound="right")
                self.blocate.grid(row=0, column=0, sticky="n")           
                self.badd = tkinter.Button(self.continueFrame, text="Adicionar relatorio(s)", command=self.addrelsPopup, image=self.imadd, compound="right")
                self.badd.grid(row=0, column=1, sticky="n")          
                self.brem = tkinter.Button(self.continueFrame, text="Remover relatorio", command=self.remrels, image=self.imremove, compound="right", state="disabled")
                self.brem.grid(row=0, column=2, sticky="n")          
                self.fakelabel = tkinter.Label(self.continueFrame, text="")
                self.fakelabel.grid(row=1, column=0, sticky="ns", rowspan=2)
                self.bopenviewer = tkinter.Button(self.continueFrame, text="Abrir no visualizador", command=self.abrir, image=self.imopen, compound="right")
                self.bopenviewer.grid(row=3, column=2, sticky="w")           
                self.bupdate = tkinter.Button(self.continueFrame, text="Atualizar informações", command=self.updateInfo, image=self.imupdate, compound="right")
                self.bupdate.grid(row=3, column=0, sticky="e")        
                
                self.largura = self.directoriesFrame.winfo_width()
                self.dirs.column("#0", width=math.floor(10*(self.largura/20)))
                self.dirs.column("zero", width=math.floor(1*(self.largura/20)))
                self.dirs.column("one", width=math.floor(3*(self.largura/20)))
                self.dirs.column("two", width=math.floor(1*(self.largura/20)))
                self.dirs.column("three", width=math.floor(1*(self.largura/20)))
                self.dirs.column("four", width=math.floor(1*(self.largura/20)))
                self.dirs.column("five", width=math.floor(1*(self.largura/20)))
                self.dirs.column("six", width=math.floor(2*(self.largura/20)))
                    
                self.fakelabe2l = tkinter.Label(self.continueFrame, text="")
                self.fakelabe2l.grid(row=4, column=0, sticky="ns", rowspan=2)            
                self.bfechar = tkinter.Button(self.continueFrame, text="Fechar", command=on_quit, image=self.imfechar, compound="right")
                self.bfechar.grid(row=6, column=1, sticky="s")  
                self.populateEqs()
                
                #None
                root.after(1000, self.checkIfneedIndexing)
            else:
                self.continueFrame.rowconfigure(0, weight=1)
                self.continueFrame.columnconfigure((0,1), weight=1)  
                self.bopenviewer = tkinter.Button(self.continueFrame, text="Abrir Visualizador", command=self.abrir, image=self.imopen, compound="right")
                self.bopenviewer.grid(row=0, column=1, sticky="ns", pady=20)  
                self.bfechar = tkinter.Button(self.continueFrame, text="Fechar", command=on_quit, image=self.imfechar, compound="right")
                self.bfechar.grid(row=0, column=0, sticky="ns", pady=20)   
                self.largura = self.directoriesFrame.winfo_width()
                self.dirs.column("#0", width=math.floor((self.largura*0.6)))
                self.dirs.column("zero", width=math.floor(1*(self.largura*0.2)))
                self.dirs.column("one", width=math.floor(1*(self.largura*0.2)))
                self.populateEqs()
                #self.bopenviewer.config(state='normal')
            
            
            
        except Exception as ex:
            None
            printlogexception(ex=ex)
        finally:
            None
            #self.abrir()
            
    def searchSqlite(self):
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
        sqliteconn = connectDB(pathdb, 5)
        try:
            cursor = sqliteconn.cursor()
            selectpdf = ("SELECT P.id_pdf, P.rel_path_pdf FROM Anexo_Eletronico_Pdfs P")
            cursor.execute(selectpdf)
            allpdfs = cursor.fetchall()
            selectconfigzoom = "SELECT * FROM FERA_CONFIG WHERE config = ?"
            cursor.execute(selectconfigzoom, ('zoom',))
            configzoom = cursor.fetchone()
            check_previous_search =  "SELECT DISTINCT C.termo, C.advancedsearch, C.id_termo, C.fixo, C.pesquisado  FROM Anexo_Eletronico_SearchTerms C ORDER by 3"
            #cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute(check_previous_search)
            termos = cursor.fetchall()
            tocs = {}
            cursor.close()
            resultador_por_termo = []
            self.progresssearch['maximum'] = len(termos)
            self.progresssearch['mode'] = 'determinate'
            qtermos = 0
            self.progresssearch['value'] = qtermos
            hastocommit = False
            for termox in termos:
                qtermos += 1
                #print(termox)
                pesquisados = []
                pesquisadoadd = termox[4]
                if(pesquisadoadd==None):
                    pesquisadoadd = ""
                if(termox[4]!=None):
                    pesquisados = termox[4].split("-")
                advanced = False
                tipobusca = 0
                
                termo = termox[0].strip().upper()
                idtermo = termox[2]
                if(termox[1]==1):
                    tipobusca = 1
                    advanced=True
                listaresults = []
                
                for pdf in allpdfs:
                    if(pdf[0] not in tocs):
                        tocs[pdf[0]] = []
                        select_tocs = '''SELECT  T.toc_unit, T.pagina, T.deslocy, T.init FROM 
                        Anexo_Eletronico_Tocs T WHERE T.id_pdf = ? ORDER BY 2,3
                        '''    
                        cursor = sqliteconn.cursor()
                        cursor.execute(select_tocs, (pdf[0],))
                        tocsx = cursor.fetchall()
                        cursor.close()
                        for toc in tocsx:
                            tocs[pdf[0]].append((toc[0], toc[1], toc[2], toc[3]))
                    
                    
                    pathpdf = os.path.normpath(os.path.join(pathdb.parent, pdf[1]))
                    if plt == "Linux":                           
                        pathpdf = str(pathpdf).replace("\\","/")
                    elif plt=="Windows":                 
                        pathpdf = str(pathpdf).replace("/","\\")
                      
                    if(str(pdf[0]) in pesquisados):
                        cursor = sqliteconn.cursor()
                        get_search_results =  "SELECT id_termo, id_pdf, pagina, init, fim, toc, snippetantes, snippetdepois, termo "+\
                            "FROM Anexo_Eletronico_SearchResults  where id_termo = ? AND id_pdf = ? ORDER by 1,2,3,4"
                        cursor.execute(get_search_results, (idtermo, pdf[0],))
                        search_results = cursor.fetchall()
                        listaresults.append(search_results)
                        
                    else:
                        #searchLogic(pathpdf, advanced, pathdb, idpdf, tocs, idtermo, termo)
                        search_results = searchLogic(pathpdf, advanced, pathdb, pdf[0], tocs[pdf[0]], idtermo, termo)
                        pesquisadoadd += "-{}".format(pdf[0])
                        
                        
                        hastocommit = True
                        cursor = sqliteconn.cursor()
                        sql_insert_searchresukt = "INSERT INTO Anexo_Eletronico_SearchResults (id_termo, id_pdf, pagina, init, fim, toc, snippetantes, snippetdepois, termo) VALUES (?,?,?,?,?,?,?,?,?)"
                        cursor.executemany(sql_insert_searchresukt, search_results)
                        updateinto2 = "UPDATE Anexo_Eletronico_SearchTerms set pesquisado = ? WHERE id_termo = ?"                   
                        cursor.execute(updateinto2, (pesquisadoadd,idtermo,))
                        listaresults.append(search_results)
                resultador_por_termo.append((termox, listaresults))
                self.progresssearch['value'] = qtermos
                root.update_idletasks()
                self.progresssearch.update()
            if(hastocommit):
                sqliteconn.commit()
            return resultador_por_termo
        except Exception as ex:
            printlogexception(ex=ex)
        finally:
             try:
                 cursor.close()
             except:
                 None
             try:
                 sqliteconn.close()
             except:
                 None
            
    def abrir(self):
        global exitFlag, nthreads, threads, threadp, root, continuar, ok, g_search_results

        for i in range(nthreads):
            try:
                continuar.put("parar")
                threads[i].terminate()
            except Exception as ex:
                None
        #self.windSearchResults()
        #g_search_results = self.searchSqlite()  
        #root.destroy()
        ok = True
        on_quit(False)
        print("OK3")
        
    def windSearchResults(self):

        syncb = b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAABYUlEQVRIie3Vv0scQRTA8U/8baMSQ9BCsDQ2HughGEgh0bQawUJIIGIlaGUnikVIFRCx078gIQqKRfqAlbFQOIuAgqDGFIE0sVBIilm5Uw5v9+7K+8LCMDv7fY+ZeW+pUAb6sIxDXOEGp/iCcdQUK27DZ5xgAWm0owE9eIfvOMLzpPIuHON9JHyIMfzGm7jyZvzAZIKEUvgad/EaVhPIE9GJX2gppzSFqmg8J2Rfi3XUlSPAFj5G422MYB47Rfo+oDF3ogkHmMEeRnGJjiLks/iHlfsvOnEmXM19TBchH8bP6LkU6uYOaVwjI3smcemKpEP4K9RERp4amsoXuQB1Qt28xSvsRvMbwnmUzCO8iMabstv7FIvlCHDLS+EMC7UW8ETYz7g8wwUG437QEWWzgvoCa0eFmzORICHQKrTrcyyhH4+FZtgtNMNvQg0NJJXn0iv7w/kjXMMMPuE1qkuRV/Af+O4/TI0aLSkAAAAASUVORK5CYII='
        self.sync= tkinter.PhotoImage(data=syncb)
        window = tkinter.Toplevel()
        window.overrideredirect(True)
        window.columnconfigure(0, weight=1)
        window.rowconfigure((0,1), weight=1)
        label = tkinter.Label(window, text='Sincronizando buscas!', image=self.sync, compound='top')
        label.grid(row=0, column=0, sticky='ew', padx=50, pady=10)
        self.progresssearch = ttk.Progressbar(window, mode='indeterminate')
        self.progresssearch.grid(row=1, column=0, sticky='ew', padx=50, pady=10)

       
    def sairpdfdif(self, varok, valor, window):
        varok.set(valor)
        window.destroy()
    
    
    def popup_pdfdif(self, window, varok, texto = 'Os arquivos não possuem HASH compatível.\n\nDeseja prosseguir?'):
        #global warningimage
        warningb = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAChklEQVRYR8XXt44UQRDG8d/hibEiIsC7iICHgAjvrQAhEjwhBAhPBhLeexIkXoMA762EgATxABygknpOc6PdnZm9W5hope2p+tf3VVdPd/nPT1cf8w9K7/9qN067AANxGqvRjVPYgT91QdoFOIkt+J2SBtB+7PsXADPxKCWegx94goCYiM91INpR4B7m4w4Wp2QnsC3ZsrmTAPnqZ+FZSjYGHxBNOaGOCnUVuIsFuI0lhUqPYzvOYFNVFeoAzMDj5H0o8byQJFR4j8GpFz5VgagDEJ4vbFJ9litT4Sw29ifA9NTpsc9DiRdNgo9OvRAqTMLHMoiqCoTni3ALS3NBs8GTj3MsDaXz2NAfAFF9eB9PsfpGAJkKQ5IKsTuaPlUUyKq/iWWFSI0AYslR7MQFrO8LwLTkfcQIJV5WBBiV/A8VJqfd0ZCjTIHwPKbdDSxvEKGZArH0CHbhItY1U6EVQL76+P2qJkCoEP4PxRS8awTRCiA8j2nXrPqI10qBvAqXsLYOwFQ8TQnC+0bVVwEoVaGZAln117GiRReXKRCvHsZuXMaaYqxGAFWrL5sx2f8j044Ylnrhbf7FRgDheUy7a1hZNUvJukPYgyvpM65neREgujXO+JA2Ov91i8BzcS79HyP3QYu1oULsiOEIhd9ka4sA4XlMu6tYVVLVN8QRHM93jC1ZfxB7i7HzADGx4oyP6ntRNglcF2BE6oVQoUfdPEDM7dirVaoPpjoWZDVkKvT0Qh7gC8alE6zHo35qwixMqBDK/UTMCHmAr8nH2XjYz4mzcPNwPwfQnQfIDo8O5e4VNi42W4sKDMCBNP/Hd4giLi1xr4jJGFe6XhZ0KGfrsGXfAx2H+gthzokhxc9aDgAAAABJRU5ErkJggg=='
        warningimage = tkinter.PhotoImage(data=warningb)
        window.rowconfigure((0,1), weight=1)
        window.columnconfigure((0,1), weight=1)
        w = 300 # width for the Tk root
        h = 200 # height for the Tk root
    
        label = tkinter.Label(window, text=texto, image=warningimage, compound='top')
    
        label.grid(row=0, column=0, sticky='ew', pady=20, columnspan=2)
        
        
        # get screen width and height
        ws = root.winfo_screenwidth() # width of the screen
        hs = root.winfo_screenheight() # height of the screen
        
        # calculate x and y coordinates for the Tk root window
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        window.geometry('%dx%d+%d+%d' % (w, h, x, y))
        
        button_ok = tkinter.Button(window, text="Prosseguir", command= lambda : self.sairpdfdif(varok, True, window))
        button_ok.grid(row=1, column=1, pady=20) 
        button_cancel = tkinter.Button(window, text="Cancelar", command= lambda : self.sairpdfdif(varok, False, window))
        button_cancel.grid(row=1, column=0, pady=20) 
        
            
    
    def updateInfo(self):
        global nthreads, threads
        self.dirs.delete(*self.dirs.get_children())
        for i in range(nthreads):
            try:
                continuar.put("parar")
                threads[i].terminate()
            except Exception as ex:
                None
        self.populateEqs()
        
        

    
    def locarel(self):
        global pathdb, mt, mb, md, me, marginsok
        try:
            tipos = [('Arquivo PDF', '*.pdf')]
            path = (askopenfilename(filetypes=tipos, defaultextension=tipos))
            if(path!=None and path!=''):
                selecao = self.dirs.focus()
                values = self.dirs.item(selecao, 'values')
                hashpdf = str(md5(path))
                
                sqliteconn = sqlite3.connect(str(pathdb))
                cursor = sqliteconn.cursor()
                try:
                    sqliteconn.execute("PRAGMA foreign_keys = ON")
                    cursor.execute('''SELECT P.rel_path_pdf, P.indexado, P.id_pdf, P.hash FROM Anexo_Eletronico_Pdfs P WHERE P.id_pdf = ? ''', (values[0],))
                    record = cursor.fetchone()
                    #hashpdf = record[3]
                    #
                    if(record[3]==hashpdf):
                        relpathpdf = os.path.relpath(path, pathdb.parent)
                        name = os.path.basename(relpathpdf)
                        #
                        cursor.execute("UPDATE Anexo_Eletronico_Pdfs set rel_path_pdf = ? WHERE id_pdf = ?", (relpathpdf, record[2],))
                        parentpath = Path(path).parent
                        
                        try:
                            if(not self.dirs.exists(str(parentpath))):
                                self.dirs.insert('', index='end', iid=str(parentpath), text=str(parentpath), values=("","","","","","","",""))
                        except Exception as ex:
                            None
                            printlogexception(ex=ex)
                            None
                        try:
                            relative_path = os.path.relpath(path, parentpath)
                            self.dirs.insert(str(parentpath), index='end', iid=relpathpdf, text=str(relative_path), values=(values[0],"100%","-","-","-","-", "-", path))
                            self.dirs.see(relpathpdf)
                            self.dirs.delete(selecao)
                            #self.dirs.item(selecao,values=(record[2],"100%","-","-","-","-"))
                        except Exception as ex:
                            None
                        sqliteconn.commit()
                    else:
                        varok = tkinter.BooleanVar()
                        varok.set(False)
                        window = tkinter.Toplevel()
                        self.popup_pdfdif(window, varok)
                        root.wait_window(window)
                        if(varok.get()):
                            window = tkinter.Toplevel()
                            marginsok = False
                            pathpdf2 = str(path)
                            if plt == "Linux":
                                pathpdf2 = pathpdf2.replace("\\","/")
                            elif plt=="Windows":
                                pathpdf2 = pathpdf2.replace("/","\\")
                            doc = fitz.open(pathpdf2)
                            try:
                                marginsok = False
                                setMargin(window, doc)                                
                                root.wait_window(window)
                                #
                                if(not marginsok):
                                    return
                                
                                relpathpdf = os.path.relpath(path, pathdb.parent)
                                name = os.path.basename(relpathpdf)
                                cursor.execute("UPDATE Anexo_Eletronico_Pdfs set indexado = 0 WHERE id_pdf = ?", (record[2],))
                                #
                                cursor.execute("DELETE FROM Anexo_Eletronico_Tocs WHERE id_pdf = ?", (record[2],))
                                cursor.execute("UPDATE Anexo_Eletronico_Pdfs set rel_path_pdf = ?, hash = ? WHERE id_pdf = ?", (relpathpdf, hashpdf, record[2],))
                                
                                cursor.execute("UPDATE Anexo_Eletronico_Obsitens set status = 'alterado' WHERE id_pdf = ?", (record[2],))
                                parentpath = Path(path).parent
                                relp = Path(os.path.normpath(os.path.join(pathdb.parent, str(relpathpdf))))
                                relpdir = relp.parent
                                
                                
                                
                                
                                pixorg = doc[0].getPixmap()
                                
                                
                                
                               
                                mmtopxtop = math.floor(mt/25.4*72)
                                mmtopxbottom = math.ceil(pixorg.height-(mb/25.4*72))
                                mmtopxleft = math.floor(me/25.4*72)
                                mmtopxright = math.ceil(pixorg.width-(md/25.4*72))
                                try:
                                    nameddests = grabNamedDestinations(doc)
                                    #
                                except Exception as ex:
                                    nameddests = []
                                toc = doc.getToC(simple=False)
                            
                                for entrada in toc:
                                    #
                                    novotexto = ""
                                    init = 0
                                    tocunit = entrada[1]
                                    #idpdf = None
                                    pagina = None
                                    deslocy = None
                                    init = 0
                                    if('page' in entrada[3]):
                                        #dictx = doc[entrada[3]['page']].getText("rawdict")
                                        pagina = entrada[3]['page'] 
                                        deslocy = entrada[3]['to'].y
                                    elif('file' in entrada[3]):
                                        arquivocomdest = entrada[3]['file'].split("#")
                                        arquivo = arquivocomdest[0]
                                        dest = arquivocomdest[1]
                                        if(os.path.basename(pathpdf2)==arquivo):
                                            for sec in nameddests:
                                                if(dest==sec[0]):
                                                    pagina = int(sec[1])
                                                    deslocy = pixorg.height-round(float(sec[3]))
                                                    break
                                    if(pagina==None):
                                        
                                        continue
                                    dictx = doc[pagina].getText("rawdict")
                                    parar = False
                                    for block in dictx['blocks']:
                                        bboxb = block['bbox']
                                        if(bboxb[1]>deslocy or parar):
                                            break  
                                        if('lines' in block):
                                            for line in block['lines']:
                                                bboxl = line['bbox']
                                                #if(bboxl[2]>deslocy or parar):
                                                #    parar = True
                                                #    break
                                                for span in line['spans']:
                                                    for char in span['chars']:
                                                        bboxchar = char['bbox']
                                                        bboxxmedio = (bboxchar[0]+bboxchar[2])/2
                                                        bboxymedio = (bboxchar[1]+bboxchar[3])/2
                                                        if(bboxxmedio < mmtopxleft or bboxxmedio > mmtopxright or bboxymedio < mmtopxtop or bboxymedio > mmtopxbottom):
                                                            continue
                                                        char = char['c']
                                                        #codePoint = ord(char)
                                                        #if(codePoint<256):
                                                        #    codePoint += lowerCodeNoDiff[codePoint]
                                                        novotexto += char
                                                        init += 1
                                                    #if(len(novotexto) > 0 and novotexto[-1]!=' '):
                                                    #    novotexto += ' '
                                                if(len(novotexto) > 0 and novotexto[-1]!=' '):
                                                    novotexto += ' '
                                                    init += 1
                                            if(len(novotexto) > 0 and novotexto[-1]!=' '):
                                                novotexto += ' '
                                                init += 1
                                    
                                                    
                                                    
                                                    
                                         
                                    insert_query_toc = """INSERT INTO Anexo_Eletronico_Tocs
                                            (toc_unit, id_pdf , pagina, deslocy, init) VALUES
                                            (?,?,?,?,?)
                                    """
                                    
                                    cursor.execute(insert_query_toc, (entrada[1], record[2], pagina, deslocy, init,))
                                    
                            except Exception as ex:
                                printlogexception(ex=ex)
                            finally:
                                doc.close()
                            
                            try:
                                if(not self.dirs.exists(str(parentpath))):
                                    self.dirs.insert('', index='end', iid=str(parentpath), text=str(parentpath), values=("","","","","","","",""))
                            except Exception as ex:
                                None
                                printlogexception(ex=ex)
                                None
                            try:
                                relative_path = os.path.relpath(path, parentpath)
                                self.dirs.insert(str(parentpath), index='end', iid=relpathpdf, text=str(relative_path), values=(values[0],"0%","-","-","-","-", "-", path))
                                #self.dirs.insert(relpdir, index='end', iid=str(relp), text=str(relp), values=(idpdf,"0%","-","-","-", "-", tipo, pathpdf2))
                                #indexando = 0
                                self.dirs.delete(selecao)
                                self.dirs.see(relpathpdf)
                                #self.dirs.item(selecao,values=(record[2],"100%","-","-","-","-"))
                            except Exception as ex:
                                None
                                
                                
                            cursor.execute("DELETE FROM Anexo_Eletronico_SearchResults where id_pdf = ?", (record[2],))
                
                            check_previous_search =  "SELECT DISTINCT C.termo, C.advancedsearch, C.id_termo, C.fixo, C.pesquisado  FROM Anexo_Eletronico_SearchTerms C ORDER by 3"
                            cursor.execute(check_previous_search)
                            termosbuscados = cursor.fetchall()
                            for termo in termosbuscados:
                                id_termo = termo[2]
                                pesquisados = termo[4].replace("-{}-".format(record[2]),'-').replace("--", '-')
                                updateinto2 = "UPDATE Anexo_Eletronico_SearchTerms set pesquisado = ? WHERE id_termo = ?"
                                cursor.execute(updateinto2, (pesquisados, id_termo))
                            sqliteconn.commit()
                            
                except Exception as ex:
                    None
                    printlogexception(ex=ex)
                finally:
                    cursor.close()
                    
                    if(sqliteconn):
                        sqliteconn.close()
        except Exception as ex:
            None
            printlogexception(ex=ex)
    
    def treeview_selection(self, event=None):
        try:
            selecao = self.dirs.focus()
            #
            selecaoiid = self.dirs.selection()[0]
            #
            #
            if(len(self.dirs.get_children(selecao))==0 and len(self.dirs.selection())==1):
                values = self.dirs.item(selecao, 'values')
                #
                if(values[1]=='PDF não encontrado' or values[1]=='Hash incompatível'):
                    self.blocate.config(state='normal')
                else:
                    self.blocate.config(state='disabled')
            else:
                self.blocate.config(state='disabled')
            mesmopai = self.dirs.parent(selecaoiid)
            podehabilitar=True
            for selec in self.dirs.selection():
                if(self.dirs.parent(selec)!=mesmopai):
                    podehabilitar = False
                    break
            if(podehabilitar):
                self.brem.config(state='normal')
            else:
                self.brem.config(state='disabled')
        except Exception as ex:
            self.blocate.config(state='disabled')
            
   
        
    
    def checkIfneedIndexing(self):
        global indexando, qlchild, finalizados, paginasindexadas, totalPaginas, start_time, nthreads,erros
        tempo = 1000
        try:
            for chi in self.dirs.get_children():
                if(len(self.dirs.get_children(chi))==0):
                    self.dirs.delete(chi)
            if(not erros.empty()):
                None
            habilitar = True
            #None
            if(indexando==0):
                childrenroot = self.dirs.get_children()
                for childroot in childrenroot:
                    childs = self.dirs.get_children(childroot)
                    for child in childs:
                        
                        values = self.dirs.item(child, 'values')
                        #None
                        if(values[0]=='OK'):
                            qlchild = None
                            None
                        if(values[1]!='100%'):
                            habilitar = False
                        if(values[1]=='0%' and indexando == 0):
                            #None
                            #self.bopenviewer.config(state='disabled')
                            indexando = 1
                            qlchild = child
                            caminho = self.dirs.item(child, 'text')
                            start_time = time.time()
                            #None
                            idpdf = self.dirs.item(qlchild,'values')[0]
                            self.septhread = thr.Thread(target=separateThread, args=([idpdf],))
                            self.septhread.start()
                            #select_all_pdfs = '''SELECT P.id_pdf, P.rel_path_pdf, P.pdf  FROM Anexo_Eletronico_Pdfs P where P.indexado = 0 AND P.id_pdf'''
                if(qlchild == None and habilitar):
                    self.bopenviewer.config(state='normal')
                            #None
            elif(indexando==1):
                #self.bopenviewer.config(state='disabled')
                tempo= 10
                if(not processados.empty()):
                    proc = processados.get(0)
                    if(proc[0]=='update'):
                        idpdf = self.dirs.item(qlchild, 'values')[0]
                        paginasindexadas += 100
                        #None
                        porcent = round(paginasindexadas / totalPaginas * 100)
                        ateagora = round(time.time() - start_time)       
                        eta = str(math.floor(totalPaginas*ateagora/paginasindexadas)-math.floor(ateagora))
                        ps = str(round(paginasindexadas/ateagora))
                        values = self.dirs.item(qlchild, 'values')
                        self.dirs.item(qlchild, values=(idpdf, str(porcent)+'%', str(ateagora)+' (s)', str(eta)+' (s)', str(ps), str(nthreads-finalizados), values[6], values[7]))
                    elif(proc[0]=='ok'):
                        finalizados += 1
                        idpdf = self.dirs.item(qlchild, 'values')[0]
                        paginasindexadas += proc[2]
                        porcent = round(paginasindexadas / totalPaginas * 100)
                        ateagora = round(time.time() - start_time)       
                        eta = str(math.floor(totalPaginas*ateagora/paginasindexadas+1)-math.floor(ateagora))
                        ps = str(round(paginasindexadas/ateagora+1))
                        values = self.dirs.item(qlchild, 'values')
                        self.dirs.item(qlchild, values=(idpdf, str(porcent)+'%', str(ateagora)+' (s)', str(eta)+' (s)', str(ps), str(nthreads-finalizados), values[6], values[7]))
                        if(finalizados==nthreads):
                            
                            self.dirs.item(qlchild, values=(idpdf,"100%","-","-","-","-"))
                            #self.bopenviewer.config(state='enabled')
                            indexando = 0
                            qlchild = None
                            finalizados = 0
                            paginasindexadas = 0
                    #root.update_idletasks()   
                           
        except Exception as ex:
            printlogexception(ex=ex)
            None
        finally:
            root.after(tempo, self.checkIfneedIndexing)
    
        
    
            
 
    
    def populateEqs(self):
        global pathdb
        #None
        #self.dirs.delete(0, 'end')
        sqliteconn = sqlite3.connect(str(pathdb))
        cursor = sqliteconn.cursor()
        ok = False
        try:
            #@self.bfechar = tkinter.Button(self.continueFrame, text="Fechar", command=on_quit, image=self.imfechar, compound="right")
            self.progressinit = ttk.Progressbar(self.continueFrame, mode='indeterminate')
            self.bopenviewer.config(state='disabled')
            self.progressinit.grid(row=6, column=1, sticky='nsew', pady=10)
            #self.bfechar.grid(row=6, column=1, sticky="s")  
            sqliteconn.execute("PRAGMA foreign_keys = ON")
            #cursor.execute('''SELECT P.rel_path_pdf FROM Anexo_Eletronico_Pdfs P WHERE P.tipo == 'laudo' ''')
            #lau = cursor.fetchone()
            #if(lau!=None):
            #    self.labelLaudo2.config(text=str(lau[0]))
            
            cursor.execute('''SELECT P.rel_path_pdf, P.indexado, P.id_pdf, P.hash, P.tipo FROM Anexo_Eletronico_Pdfs P ORDER BY 4,1''')
            records = cursor.fetchall()
            relpathsdir = set()

            qtos = 0
            self.progressinit['maximum'] = len(records)
            self.progressinit['mode'] = 'determinate'
            ok = True
            for r in records:
                self.progressinit['value'] = qtos
                qtos += 1
                root.update_idletasks()
                self.progressinit.update()
                
                pp = os.path.normpath(os.path.join(pathdb.parent, r[0]))
                if plt == "Linux":
                    pp = pp.replace("\\","/")
                elif plt=="Windows":
                    pp = pp.replace("/","\\")
                relp = Path(pp)
                relpdir = relp.parent
                if(expertmode):
                    try:
                        self.dirs.insert('', index='end', iid=relpdir, text=str(relpdir), values=("","","","","","","",""))
                    except Exception as ex:
                        None
                        #printlogexception(ex=ex)
                    try:
                        relative_path = os.path.relpath(pp, relpdir)
                        if(not os.path.exists(relp)):
                            ok = False
                            self.dirs.insert(relpdir, index='end', iid=str(relp), text=str(relative_path), values=(r[2],"PDF não encontrado","-","-","-","-", r[4], pp))
                            self.bopenviewer.config(state='disabled')
                            
                        else:
                            if(r[1]==0):
                                
                                self.dirs.insert(relpdir, index='end', iid=str(relp), text=str(relative_path), values=(r[2],"0%","-","-","-","-", r[4], pp))
                                 
                            else:
                                hashpdf = str(md5(str(relp)))
                                if(hashpdf!=r[3]):
                                    ok = False
                                    self.dirs.insert(relpdir, index='end', iid=str(relp), text=str(relative_path), values=(r[2],"Hash incompatível","-","-","-","-", r[4], pp))
                                    self.bopenviewer.config(state='disabled')
                                else:
                                    self.dirs.insert(relpdir, index='end', iid=str(relp), text=str(relative_path), values=(r[2],"100%","-","-","-","-", r[4], pp))
                        
                        self.dirs.see(str(relp))
                    except Exception as ex:
                        None
                        #printlogexception(ex=ex)
                        #None
                else:
                    
                    relative_path = os.path.relpath(pp, relpdir)
                    try:
                        self.dirs.insert('', index='end', iid=relpdir, text=str(relpdir), values=(""))
                    except Exception as ex:
                        None
                        #printlogexception(ex=ex)
                        #None
                    try:
                        if(not os.path.exists(relp)):
                            ok = False
                            self.dirs.insert(relpdir, index='end', iid=str(relp), text=str(relative_path), values=("PDF não encontrado", r[4]), tag='problema')
                            self.bopenviewer.config(state='disabled')
                        else:
                            if(r[1]==0):
                                ok=False
                                self.dirs.insert(relpdir, index='end', iid=str(relp), text=str(relative_path), values=("NÃO INDEXADO", r[4]),  tag='problema')
                                self.bopenviewer.config(state='disabled')
                            else:
                                hashpdf = str(md5(str(relp)))
                                if(hashpdf!=r[3]):
                                    ok = False
                                    self.dirs.insert(relpdir, index='end', iid=str(relp), text=str(relative_path), values=("Hash imcompatível", r[4]), tag='problema')
                                    self.bopenviewer.config(state='disabled')
                                else:
                                    self.dirs.insert(relpdir, index='end', iid=str(relp), text=str(relative_path), values=("OK", r[4]), tag='ok')
                        self.dirs.see(str(relp))
                        self.dirs.tag_configure('ok', background='#1dcf4d')
                        self.dirs.tag_configure('problema', background='#db342e')
                        
                    except Exception as ex:
                        printlogexception(ex=ex)
                        #printlogexception(ex=ex)
                        #None
            self.bopenviewer.config(state='normal')
        except Exception as ex:
            printlogexception(ex=ex)
            #printlogexception(ex=ex)
            #None
        finally:
            if(ok):
                self.bopenviewer.config(state='normal')
            cursor.close()
            if(sqliteconn):
                sqliteconn.close()
            self.progressinit.grid_forget()
    
    
    def create_rectanglex(self, x1, y1, x2, y2, color, **kwargs):
        
        image = Image.new('RGBA', (x2-x1, y2-y1), color)   
        return ImageTk.PhotoImage(image)
       

        
        
        
    
        
        
        
        # get screen width and height
        
    
        
        #button_close.pack(fill='y', pady=20) 
   
    def addrelsPopup(self):   
        global pathdb
        try:
            self.opcao = tkinter.Menu(root, tearoff=0)
            self.opcao.add_command(label='Laudo', command=partial(addrels,'laudo', self))
            self.opcao.add_command(label='Relatorio', command=partial(addrels,'relatorio',  self))
            self.opcao.add_command(label='Outros', command=partial(addrels,'outros', self))
            
            
            self.opcao.tk_popup(self.badd.winfo_rootx(),self.badd.winfo_rooty())         
        except Exception as ex:
            printlogexception(ex=ex)
            None
        finally:
            self.opcao.grab_release() 

   
        
        
    
            
        
    def remrels(self):
        global qlchild, continuar, indexando, finalizados, paginasindexadas, threads, nthreads, processar, processados
        sqliteconn = sqlite3.connect(str(pathdb))
        cursor = sqliteconn.cursor()
        try:
            for selection in self.dirs.selection():
           # selection=self.dirs.focus()
            #parentid = self.dirs.parent(self.dirs.selection()[0])
                #if(len(self.dirs.get_children(selection))==0):
                if(selection==qlchild):
                    while (not processados.empty()):
                        processados.get()
                    while (not processar.empty):
                        processar.get()
                    for i in range(nthreads):
                        try:
                            
                            threads[i].terminate()
                            indexando = 0
                            qlchild = None
                            finalizados = 0
                            paginasindexadas = 0
                            
                        except Exception as ex:
                            printlogexception(ex=ex)
                            None
                texto = self.dirs.item(selection, 'text')
                value = self.dirs.item(selection, 'values')[0]
                sqliteconn.execute("PRAGMA foreign_keys = ON")
                cursor.execute("SELECT P.id_pdf, P.rel_path_pdf, P.indexado FROM Anexo_Eletronico_Pdfs P where :pdf = P.id_pdf ",{'pdf': value})
                record = cursor.fetchone()
                
                
                #if(record[2]==1):
                cursor.execute("DROP TABLE IF EXISTS Anexo_Eletronico_Conteudo_id_pdf_"+str(record[0]))
                cursor.execute("DROP TABLE IF EXISTS Anexo_Eletronico_Conteudo_id_pdf_"+str(record[0]))
                cursor.execute("DROP TABLE IF EXISTS Anexo_Eletronico_Conteudo_id_pdf_"+str(record[0])+"_config")
                cursor.execute("DROP TABLE IF EXISTS Anexo_Eletronico_Conteudo_id_pdf_"+str(record[0])+"_content")
                cursor.execute("DROP TABLE IF EXISTS Anexo_Eletronico_Conteudo_id_pdf_"+str(record[0])+"_data")
                cursor.execute("DROP TABLE IF EXISTS Anexo_Eletronico_Conteudo_id_pdf_"+str(record[0])+"_docsize")
                cursor.execute("DROP TABLE IF EXISTS Anexo_Eletronico_Conteudo_id_pdf_"+str(record[0])+"_idx")
                cursor.execute("DELETE FROM Anexo_Eletronico_Pdfs where id_pdf = ?", (record[0],))
                cursor.execute("DELETE FROM Anexo_Eletronico_SearchResults where id_pdf = ?", (record[0],))
                
                check_previous_search =  "SELECT DISTINCT C.termo, C.advancedsearch, C.id_termo, C.fixo, C.pesquisado  FROM Anexo_Eletronico_SearchTerms C ORDER by 3"
                cursor.execute(check_previous_search)
                termosbuscados = cursor.fetchall()
                for termo in termosbuscados:
                    id_termo = termo[2]
                    pesquisados = termo[4].replace("-{}-".format(record[0]),'').replace("--", '-')
                    updateinto2 = "UPDATE Anexo_Eletronico_SearchTerms set pesquisado = ? WHERE id_termo = ?"
                    cursor.execute(updateinto2, (pesquisados, id_termo))
                
            for selection in self.dirs.selection():
                self.dirs.delete(selection)
            sqliteconn.commit()

        except Exception as ex:
            printlogexception(ex=ex)
        finally:
            cursor.close()
           # None
            if(sqliteconn):
                sqliteconn.close()
          
def insertThread(processar, processadosfromviewer, lock, lockp, processados, pathdb, continuar):
        #mng = mp.Manager()
        #Global = mng.Namespace()
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
        divisao = 1024 * 1024
        
        inserts = []
        #cursor.execute("begin")
        soma = 0
        
        #None
        while not processar.empty():
            #lockp.acquire()
            proc = None

            proc = processar.get()
            ppaginas = 0
            #None
            mt = proc.mt
            mb = proc.mb
            me = proc.me
            md = proc.md
            abs_path_pdf = os.path.normpath(os.path.join(pathdb.parent, proc.rel_path_pdf))
            if plt == "Linux":
                abs_path_pdf = abs_path_pdf.replace("\\","/")
            elif plt=="Windows":
                abs_path_pdf = abs_path_pdf.replace("/","\\")
            doc2 = fitz.open(abs_path_pdf)
            pixorg = doc2[0].getPixmap()
            mmtopxtop = math.floor(mt/25.4*72)
            mmtopxbottom = math.ceil(pixorg.height-(mb/25.4*72))
            mmtopxleft = math.floor(me/25.4*72)
            mmtopxright = math.ceil(pixorg.width-(md/25.4*72))
            #None
            try:
                for p in range(proc.paginit, proc.pagfim):
                    if(continuar != None and not continuar.empty()):
                        return
                    if(p==len(doc2)):
                        continue
                    novotexto = ""
                    dictx = doc2[p].getText("rawdict")
                    for block in dictx['blocks']:
                        if('lines' in block):
                            for line in block['lines']:
                                for span in line['spans']:
                                    for char in span['chars']:
                                        bboxchar = char['bbox']
                                        bboxxmedio = (bboxchar[0]+bboxchar[2])/2
                                        bboxymedio = (bboxchar[1]+bboxchar[3])/2
                                        if(bboxxmedio < mmtopxleft or bboxxmedio > mmtopxright or bboxymedio < mmtopxtop or bboxymedio > mmtopxbottom):
                                            continue
                                        char = char['c']
                                        codePoint = ord(char)
                                        if(codePoint<256):
                                            codePoint += lowerCodeNoDiff[codePoint]
                                        novotexto += chr(codePoint)
                                    #if(len(novotexto) > 0 and novotexto[-1]!=' '):
                                    #    novotexto += ' '
                                if(len(novotexto) > 0 and novotexto[-1]!=' '):
                                    novotexto += ' '
                            if(len(novotexto) > 0 and novotexto[-1]!=' '):
                                novotexto += ' '
                    

                    tupla = (novotexto, p)
                    inserts.append(tupla)
                    ppaginas += 1
                    if(ppaginas%100==0):
                        if(processadosfromviewer!=None):
                            processadosfromviewer[0] += 100
                        if(processados!=None):
                            processados.put(('update', 1))
                    #
                
                lock.acquire(block=True)
                
                    
                    
                sqliteconn = sqlite3.connect(str(pathdb))
                sqliteconn.execute("PRAGMA foreign_keys = ON")
                cursor = sqliteconn.cursor()
                #cursor.execute("begin")
                total = len(inserts)
                qtos = 0
                sql_insert_content = "INSERT INTO Anexo_Eletronico_Conteudo_id_pdf_" + str(proc.idpdf) +\
                                    " (texto, pagina) VALUES (?,?)"
                #for t in inserts:               
                cursor.executemany(sql_insert_content, inserts)
                    
                cursor.close()
                sqliteconn.commit()
                sqliteconn.close()
                inserts = []
                if(processadosfromviewer!=None):
                    processadosfromviewer[0] += ppaginas%100
                if(processados!=None):
                    processados.put(('ok', 1, ppaginas%100))
            except Exception as ex:
                #Global.erroaddviewer = 1
                printlogexception(ex=ex)
                return
            finally:
                doc2.close()
                lock.release()
                if(sqliteconn):
                    sqliteconn.close()
            


def on_quit2():
    pass

def on_quit(sair=True):
    global exitFlag, nthreads, threads, threadp, continuar

    for i in range(nthreads):
        try:
            continuar.put("parar")
            threads[i].terminate()
            #threads[i].join()
        except Exception as ex:
            None
    try:
        root.destroy()
        print("OK2")
        return True
    except Exception as ex:
        None
    if(sair):
        try:
            os.remove(str(pathdb)+'.lock')
        except:
            None
        sys.exit(0)
    #return False
    
def createNewDbFile(view = True):
    global pathdb
    if(pathdb !=None):
        if(os.path.exists(str(pathdb))):
            os.remove(str(pathdb))
        sqliteconn = sqlite3.connect(str(pathdb))
        cursor = sqliteconn.cursor()
        try:
            sqliteconn.execute("PRAGMA foreign_keys = ON")
            cursor.execute(''' DROP TABLE IF EXISTS Anexo_Eletronico_Equips''')
            cursor.execute(''' DROP TABLE IF EXISTS Anexo_Eletronico_Pdfs''')
            cursor.execute(''' DROP TABLE IF EXISTS Anexo_Eletronico_Tocs''')
            cursor.execute(''' DROP TABLE IF EXISTS Anexo_Eletronico_Conteudo''')
    
            create_table_pdfs = '''CREATE TABLE Anexo_Eletronico_Pdfs (
            id_pdf INTEGER PRIMARY KEY AUTOINCREMENT,
            rel_path_pdf TEXT NOT NULL,
            indexado INTEGER NOT NULL,
            hash TEXT,
            tipo TEXT NOT NULL,
            lastpos TEXT NOT NULL,
            margemsup INTEGER NOT NULL,
            margeminf INTEGER NOT NULL,
            margemesq INTEGER NOT NULL,
            margemdir INTEGER NOT NULL)
            '''
    
            create_table_tocs = '''CREATE TABLE Anexo_Eletronico_Tocs (
            id_toc INTEGER PRIMARY KEY AUTOINCREMENT,
            toc_unit TEXT NOT NULL,
            id_pdf TEXT NOT NULL,
            pagina INTEGER NOT NULL,
            deslocy INTEGER NOT NULL,
            init INTEGER NOT NULL,
            external_pdf TEXT,
            CONSTRAINT fk_pdf
                FOREIGN KEY (id_pdf)
                    REFERENCES Anexo_Eletronico_Pdfs (id_pdf)
                    ON DELETE CASCADE
            )'''
    
            create_table_pdflinks = '''CREATE TABLE Anexo_Eletronico_Links(
            id_link INTEGER PRIMARY KEY AUTOINCREMENT,
            paginainit INTEGER NOT NULL,
            p0x INTEGER NOT NULL,
            p0y INTEGER NOT NULL,
            paginafim INTEGER NOT NULL,
            p1x INTEGER NOT NULL,
            p1y INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            id_obs INTEGER NOT NULL,
            id_pdf INTEGER NOT NULL,
            fixo INTEGER NOT NULL,
            CONSTRAINT fk_obs
                FOREIGN KEY (id_obs)
                    REFERENCES Anexo_Eletronico_Obsitens (id_obs)
                    ON DELETE CASCADE
            CONSTRAINT fk_pdf
                FOREIGN KEY (id_pdf)
                    REFERENCES Anexo_Eletronico_Pdfs (id_pdf)
                    ON DELETE CASCADE
            )
            '''
    
            create_table_searchterms = '''CREATE TABLE Anexo_Eletronico_SearchTerms (
            id_termo INTEGER PRIMARY KEY AUTOINCREMENT,
            termo TEXT NOT NULL,
            advancedsearch INTEGER NOT NULL, 
            fixo INTEGER NOT NULL,
            pesquisado TEXT)  
            '''
    
            create_table_searchpdfs = '''CREATE TABLE Anexo_Eletronico_SearchPdfs (
            id_termo_pdf INTEGER PRIMARY KEY AUTOINCREMENT,
            id_pdf INTEGER NOT NULL,
            id_termo INTEGER NOT NULL,
            CONSTRAINT fk_pdf
                FOREIGN KEY (id_pdf)
                    REFERENCES Anexo_Eletronico_Pdfs (id_pdf)
                    ON DELETE CASCADE,
            CONSTRAINT fk_id_termo
                FOREIGN KEY (id_termo)
                    REFERENCES Anexo_Eletronico_SearchTerms (id_termo)
                    ON DELETE CASCADE
            )  
            '''
            
            create_table_searchesresults = '''CREATE TABLE Anexo_Eletronico_SearchResults (
            id_termo INTEGER NOT NULL,
            id_pdf INTEGER NOT NULL,
            pagina INTEGER NOT NULL,
            init INTEGER NOT NULL,
            fim INTEGER NOT NULL,
            toc TEXT,
            snippetantes TEXT,
            snippetdepois TEXT,
            termo TEXT,
            CONSTRAINT fk_termo
                FOREIGN KEY (id_termo)
                    REFERENCES Anexo_Eletronico_SearchTerms (id_termo)
                    ON DELETE CASCADE,
            CONSTRAINT fk_pdf
            FOREIGN KEY (id_pdf)
                REFERENCES Anexo_Eletronico_Pdfs (id_pdf)
                ON DELETE CASCADE
            )
            '''
            
            create_table_obscat = '''CREATE TABLE Anexo_Eletronico_Obscat (
            id_obscat INTEGER PRIMARY KEY AUTOINCREMENT,
            obscat TEXT NOT NULL,
            fixo INTEGER NOT NULL,
            ordem INTEGER NOT NULL
            )
            '''
            
            create_table_obsitens = '''CREATE TABLE Anexo_Eletronico_Obsitens (
            id_obs INTEGER PRIMARY KEY AUTOINCREMENT,
            id_obscat INTEGER NOT NULL,
            id_pdf INTEGER NOT NULL,
            paginainit INTEGER NOT NULL,
            p0x INTEGER NOT NULL,
            p0y INTEGER NOT NULL,
            paginafim INTEGER NOT NULL,
            p1x INTEGER NOT NULL,
            p1y INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            fixo INTEGER NOT NULL,
            status TEXT NOT NULl DEFAULT 'ok',
            CONSTRAINT fk_obs
                FOREIGN KEY (id_obscat)
                    REFERENCES Anexo_Eletronico_Obscat (id_obscat)
                    ON DELETE CASCADE,
            CONSTRAINT fk_pdf                    
                FOREIGN KEY (id_pdf)
                    REFERENCES Anexo_Eletronico_Pdfs (id_pdf)
                    ON DELETE CASCADE
            )
            '''
            
            create_table_config = '''CREATE TABLE FERA_CONFIG (
            id_conf INTEGER PRIMARY KEY AUTOINCREMENT,
            config TEXT NOT NULL,
            param TEXT NOT NULL
            )'''
            
            
            None
            #cursor.execute(create_table_equip)
            #None
            cursor.execute(create_table_pdfs)
            None
            cursor.execute(create_table_tocs)
            None
            cursor.execute(create_table_searchterms)
            None
            #cursor.execute(create_table_searchpdfs)
            #None
            cursor.execute(create_table_searchesresults)
            None
            cursor.execute(create_table_obscat)
            None
            cursor.execute(create_table_obsitens)
            None
            cursor.execute(create_table_pdflinks)
            None
            cursor.execute(create_table_config)
            None
            insert_query_pdf = """INSERT INTO FERA_CONFIG
            (config , param) VALUES (?,?)   """
            cursor.execute(insert_query_pdf, ('dbversion', str(dbversion),))
            sqliteconn.commit()
            '''
            try:
                recenttxt = os.path.join(os.getcwd(),"recents.txt")
                count = 0
                add = []
                try:
                    with open(recenttxt, 'r') as f:
                       
                       for line in f:
                           if(line.strip() ==str(pathdb).strip()):
                               count =1                           
                           else:
                               if(os.path.isfile(pathdb)):
                                  add.append((str(pathdb)+'\n'))
                except Exception as ex:
                    None
                with open(recenttxt, 'w') as f:
                    for linha in add:
                        f.write(linha)
                    if(count==0):
                        f.write(str(pathdb))
            except IOError:
                printlogexception(ex=ex)
            except Exception as ex:
                printlogexception(ex=ex)
                '''
            
            loaddb(view = view)
        except Exception as ex:
            printlogexception(ex=ex)
            pathdb = None
        finally:
            cursor.close()
            
            sqliteconn.close()
    
def solicitarDiretorio(pathdbx = None, addrel = None):
    global nrep, anorep, pathdb, numerorep, anorep, root
    tipos = [('SQLite DB', '*.db')]
    if(pathdbx==None):
        path = (asksaveasfilename(filetypes=tipos, defaultextension=tipos))
    else:
        path = pathdbx
    if(path!=None):
        pathdb = Path(path)
        createNewDbFile()
        #root.destroy()
        #root = tkinter.Tk()
        #icon = b'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'
        #root.tk.call('wm', 'iconphoto', root._w, tkinter.PhotoImage(data=icon))
        #root.geometry("1200x500")
        #root.columnconfigure(0, weight=1)
        #root.rowconfigure(0, weight=1)
        #root.title("FERA "+ version+" - Forensics Evidence Report Analyzer -- Polícia Científica do Paraná")
        #None
        
        #frameinitial.grid_forget()
        #frameinitial.destroy()
        #mw = App(addrel)
       #if(addrel!=None):
            
        #None
        #root.mainloop()
        #sqliteconn = sqlite3.connect(pathdb)
 
def popupcomandook1(sair, window):
    if(sair):
        window.destroy()
        on_quit()
    else:
        window.destroy()
    
def popup_window(texto, sair):
    global warningimage
    warningb = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAChklEQVRYR8XXt44UQRDG8d/hibEiIsC7iICHgAjvrQAhEjwhBAhPBhLeexIkXoMA762EgATxABygknpOc6PdnZm9W5hope2p+tf3VVdPd/nPT1cf8w9K7/9qN067AANxGqvRjVPYgT91QdoFOIkt+J2SBtB+7PsXADPxKCWegx94goCYiM91INpR4B7m4w4Wp2QnsC3ZsrmTAPnqZ+FZSjYGHxBNOaGOCnUVuIsFuI0lhUqPYzvOYFNVFeoAzMDj5H0o8byQJFR4j8GpFz5VgagDEJ4vbFJ9litT4Sw29ifA9NTpsc9DiRdNgo9OvRAqTMLHMoiqCoTni3ALS3NBs8GTj3MsDaXz2NAfAFF9eB9PsfpGAJkKQ5IKsTuaPlUUyKq/iWWFSI0AYslR7MQFrO8LwLTkfcQIJV5WBBiV/A8VJqfd0ZCjTIHwPKbdDSxvEKGZArH0CHbhItY1U6EVQL76+P2qJkCoEP4PxRS8awTRCiA8j2nXrPqI10qBvAqXsLYOwFQ8TQnC+0bVVwEoVaGZAln117GiRReXKRCvHsZuXMaaYqxGAFWrL5sx2f8j044Ylnrhbf7FRgDheUy7a1hZNUvJukPYgyvpM65neREgujXO+JA2Ov91i8BzcS79HyP3QYu1oULsiOEIhd9ka4sA4XlMu6tYVVLVN8QRHM93jC1ZfxB7i7HzADGx4oyP6ntRNglcF2BE6oVQoUfdPEDM7dirVaoPpjoWZDVkKvT0Qh7gC8alE6zHo35qwixMqBDK/UTMCHmAr8nH2XjYz4mzcPNwPwfQnQfIDo8O5e4VNi42W4sKDMCBNP/Hd4giLi1xr4jJGFe6XhZ0KGfrsGXfAx2H+gthzokhxc9aDgAAAABJRU5ErkJggg=='
    warningimage = tkinter.PhotoImage(data=warningb)
    window = tkinter.Toplevel()

    label = tkinter.Label(window, text=texto, image=warningimage, compound='top')

    label.pack(fill='x', padx=50, pady=20)

    button_close = tkinter.Button(window, text="OK", command= lambda : popupcomandook1(sair, window))
    button_close.pack(fill='y', pady=20)   
    return window
    
    
def loaddb(event=None, lb1=None, addrel = None, pathdecided = False, view=True, rootx=None):
    global listapdfs, frameinitial, labelopcao, pathdb, continuar, root, recenttxt, version
    #frameinitial.grid_forget()
    #None
    ok = True
    #None
    if(pathdecided):
        None
    elif(rootx!=None):
        pathdb = Path(rootx[0])
        #root = rootx[1]
    elif(event!=None):
        widget = event.widget
        selection=widget.curselection()
        value = widget.get(selection[0]).strip()
        pp =value
        
        pathdb = Path(pp)
        #None
    elif(lb1!=None and lb1.curselection()!=()):
        selection=lb1.curselection()
        value = lb1.get(selection[0]).strip()
        pp =value
        
        pathdb = Path(pp)
        
    elif(pathdb==None):
        pathdb = Path(askopenfilename(filetypes=(("SQLite", "*.db"), ("Todos os arquivos", "*"))))
        if(pathdb!=None and pathdb!="."):
           
            None
        else:
            
            pathdb = None
            
    if(pathdb != None and pathdb != "." and os.path.isfile(pathdb)):
        if(os.path.exists(str(pathdb)+'.lock')):
            #window = tkinter.Toplevel()
            root.withdraw()
            window = popup_window(sair=True, texto = "O banco de dados aparentemente está aberto em outra execução!\nO programa irá encerrar para evitar inconsistências.\n"+\
                         "Para corrigir esse problema:\nVerifique outras execuções utilizando o mesmo banco de dados\n ou \nApague o arquivo <{}>".format(str(pathdb)+'.lock'))
            root.wait_window(window)
            #sys.exit(0)
        else:
            with open(str(pathdb)+'.lock', 'w') as fp:
                pass
        try:
            count = 0
            add = []
            add.append(str(pathdb)+"\n")
            recenttxt = os.path.join(os.getcwd(),"recents.txt")
            try:
                with open(recenttxt, 'r') as f:                   
                   for line in f:              
                       if(os.path.isfile(line.strip()) and  line not in add):
                           add.append(line)
            except Exception as ex:
                printlogexception(ex=ex)
            with open(recenttxt, 'w') as f:    
                None
                for linha in add:                    
                    f.write(linha)
        except IOError as ex:
            printlogexception(ex=ex)
        except Exception as ex:
            printlogexception(ex=ex)
            pathdb = None
            None
        try:
            pathdb = Path(pathdb)
            LOG_FILENAME = os.path.join(pathdb.parent, 'fera.log')
            logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)
            sqliteconn = None
            #None
            sqliteconn = sqlite3.connect(str(pathdb))
            cursor = sqliteconn.cursor()
            #None
            resulttable = '''SELECT name FROM sqlite_master WHERE type="table" AND name="Anexo_Eletronico_SearchResults"'''
            cursor.execute(resulttable)
            tableresultcount = cursor.fetchone()
            if(tableresultcount==None):
                create_table_searchesresults = '''CREATE TABLE Anexo_Eletronico_SearchResults (
                id_termo INTEGER NOT NULL,
                id_pdf INTEGER NOT NULL,
                pagina INTEGER NOT NULL,
                init INTEGER NOT NULL,
                fim INTEGER NOT NULL,
                toc TEXT,
                snippetantes TEXT,
                snippetdepois TEXT,
                termo TEXT,
                CONSTRAINT fk_termo
                    FOREIGN KEY (id_termo)
                        REFERENCES Anexo_Eletronico_SearchTerms (id_termo)
                        ON DELETE CASCADE,
                CONSTRAINT fk_pdf
                FOREIGN KEY (id_pdf)
                    REFERENCES Anexo_Eletronico_Pdfs (id_pdf)
                    ON DELETE CASCADE
                )
                '''
                cursor.execute(create_table_searchesresults)
                
                try:
                   cursor.execute('ALTER TABLE Anexo_Eletronico_SearchTerms ADD COLUMN pesquisado')
                except Exception as ex:
                    printlogexception(ex=ex)
                sqliteconn.commit()
            select_query = """SELECT config, param FROM FERA_CONFIG """
            cursor.execute(select_query)
            records = cursor.fetchall()
            nodbversion = True
            for conf in records:
                if(conf[0]=='dbversion'):
                    nodbversion = False
                    if(conf[1]!=str(dbversion)):
                        varok = tkinter.BooleanVar()
                        varok.set(False)
                        #{dbatual})".format
                        texto = 'A versão do seu banco de dados {dbantigo} é diferente da versão mais atual {dbatual}.\nDeseja prosseguir?'.format(dbantigo=conf[1], dbatual=dbversion)
                        window = tkinter.Toplevel()
                        popup(window, varok, texto = texto)
                        root.wait_window(window)
                        if(varok.get()):
                            try:
                                addcolumn = "ALTER TABLE Anexo_Eletronico_Obscat ADD COLUMN ordem INTEGER NOT NULL DEFAULT 0"
                                addcolumn2 = "ALTER TABLE Anexo_Eletronico_Obsitens ADD COLUMN status TEXT NOT NULL DEFAULT 'ok'"
                                #addcolumn3 = "ALTER TABLE Anexo_Eletronico_Obsitens ADD COLUMN status TEXT NOT NULL DEFAULT 'ok'"
                                obscats = "SELECT id_obscat FROM Anexo_Eletronico_Obscat"
                                cursor.execute(addcolumn)
                                cursor.execute(obscats)
                                obscats = cursor.fetchall()
                                ordem = 0
                                for obscat in obscats:
                                    updateinto2 = "UPDATE Anexo_Eletronico_Obscat set ordem = ? WHERE id_obscat = ?"
                                    cursor.execute(updateinto2, (ordem, obscat[0],))
                                    ordem += 1
                                
                                
                                
                            except Exception as ex:
                                #pathdb = None
                                try:
                                    cursor.execute(addcolumn2)
                                except Exception as ex:
                                    None
                            finally:
                                sqliteconn.commit()
                        else:
                            pathdb = None
                            return
            if(view):
                if(nodbversion):
                    varok = tkinter.BooleanVar()
                    varok.set(False)
                    #{dbatual})".format
                    texto = 'Não foi possível identificar a versão do seu banco de dados.\nDeseja prosseguir?'
                    window = tkinter.Toplevel()
                    popup(window, varok, texto = texto)
                    root.wait_window(window)
                    if(varok.get()):
                        try:
                            addcolumn = "ALTER TABLE Anexo_Eletronico_Obscat ADD COLUMN ordem INTEGER NOT NULL  DEFAULT 0"
                            addcolumn2 = "ALTER TABLE Anexo_Eletronico_Obsitens ADD COLUMN status TEXT NOT NULL DEFAULT 'ok'"
                            obscats = "SELECT id_obscat FROM Anexo_Eletronico_Obscat"
                            cursor.execute(addcolumn)
                            cursor.execute(obscats)
                            obscats = cursor.fetchall()
                            ordem = 0
                            for obscat in obscats:
                                updateinto2 = "UPDATE Anexo_Eletronico_Obscat set ordem = ? WHERE id_obscat = ?"
                                cursor.execute(updateinto2, (ordem, obscat[0],))
                                ordem += 1
                            
                        except Exception as ex:
                            #pathdb = None
                            try:
                                cursor.execute(addcolumn2)
                            except Exception as ex:
                                None
                        finally:
                            sqliteconn.commit()
                        #root.destroy()
                        #root = tkinter.Tk()
                        icon = b'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'
                        root.tk.call('wm', 'iconphoto', root._w, tkinter.PhotoImage(data=icon))
                        root.geometry("1200x500")
                        root.columnconfigure(0, weight=1)
                        root.rowconfigure(0, weight=1)
                        root.title("FERA "+ version+" - Forensics Evidence Report Analyzer -- Polícia Científica do Paraná")
                        sqliteconn.close()
                        
                        #frameinitial.grid_forget()
                        #frameinitial.destroy()
                        root.bind('<Control-Alt-F12>', f12Pressed)
                        mw = App()
                        #None
                        
                        #root.mainloop()
                else:
                    #pathdb = None
                    #root.destroy()
                    #root = tkinter.Tk()
                    icon = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAsCSURBVFhHnZcJVJV1GsZ/390vFy7LBVkEQWQNBJdQUdGJRlMzs6YpK2tOnWnx1NRMaeuU0+nUTLadaiaNo9VYqUVWWpZa7ijuCyqIggIKiHDZ7gZ3nfcCmUzndKZ5zvkOR797/8/zf5fnfa8SEPBf6Olxc8OsmUwoLCQnN4e8vHyysrNQqVQDn/hl2LptVFZVcqLiOAf278fr9bL8g/cH3g7GzwS0tnVQXDRG3oQLoa/vyx6PB4/bQwAtkRGxGEPCMRp1hIZqUBTo7PTidPbS3dWGzd6GXi+f1Gr7Ho1GK+88ZGcnse6bTQMsP2GQgOamJkblT2bNW608/dZw1IqpT0BvryIkfoqKFO68O4xx40OJijTKN4QdZ9/j9XexeZON0tVadu0KxWTyixA/KrWWzLRWRg5r5euyq9lR9kOQ6jIux7SqspK8UQW8MW8k1+QnsXffm8TFxdPYiBC6qW3Q89Gq4Rw+pBbybIYlVPHFWiMPLXCze3ck82/TSXQsfLCyk6/W1VF8jZ3zF2D06Hz+veolFs5KoXion4JxEwcY+3E5AlMmTcbabmNkGjw4twl/sp9bbk5j3YYWubmF+XcYSBkeRc0ZO/n5QxmeGkN4uBFXjwu9ziEiGrjU0kF6BhL2Dh5f2MzhMhPXXj+MTRtrMNar+MMrKVjbWnniyUU89PDDgwW4XC4yRqSTmhJHY6uWgCfA3r01RMeZJNDpfPiBjhkzcyUqopBUKisbqKtrhYCLoYmKiFLj9tbyycpaFPVF7r6zDZXHR09XgNyJOQTUkBDlQq2PYPvO7UHKPgyqgeee/StffvEVdoeZ/WXVWCRkvd54DPp09uwyER6RyksvVrBtSzUGowa1Wk4VeX5/8AIwcbKFRc8aCHgbmFTYiKMdQhQpUBExsjgPxd/C6k9XSUrH9xMKBgk4deoUheNv5OPlDq6fa8fl1aAzJvH2q07szjAhctHSYusrPZ1OjUEem8NAj9ShXyI2NNLB6CQPzc0RxBQ4uXV+O84WEaH1sHObkTseHcGFC/v7yQYwSEAQUwsT2VFuxdVhwK3SUrIslLqGMYzImkFcbIxEQ4/V2kZN7VlaGk+x5I7PIFwj0YHasxquShU1bSm8tSqS2FGd3HZbC+7OAPpwJ/c/NIaSjw8NMPVjkLOs//oALz4pBdgeDC+crVELmYHUzJlkpScSY9ajpxeL2UhmRqr0diJDRvkYMlrF6rIEFpeMgFg50lTPrVO81Bw1SY3IwRKyQKeOBbcclk76Kf9BDBKwacO/mHJNAHeP/MMXIDHeQ2urAcVnZUiURQxIxKSnotdqMBlDiJC2I2gHuhnsPziW+gshOL2hYPZT0drJ0nVhNDXq0Kj9iI8xugDKt77Rx/UjBgkwekuhVysJlTMNPpYutbBta4BoS5O0TyfxCfGsXfsl5eXlfQLsdhsYoKMrm1BTrvS8liMnwyQCQlRpxGAI8PayIagNYkhyJm6IUjbQK2J+xGUBFScamZAv+ZMPKcGy1vn44quIvkMuXWrDZDZTXVnNnNnX91Vxq9UqhShi5SsR4VsomFDNxKIeqX4rdIkom1pE+vhqY6Sw+ORSkgs5e+oYP4eO1AywXiGgpqae7BTJlahTSwi6GzR0dKvFVBSxYhf1Yokur5/TtQ20dnTT3t3JxZZL0B3M7xHMhh+I0p2HFulHu67vZJXk3u1V0VKrR6uICBGQnQzV1bUDrFcIaO/oIlKiF/AEw+Wnw6pCUo3PpxI5Tk6cOCrdUCvDqk5u30RDfY08dVLxEoXzHjKMDsYO6SDQJDmxp6HTBIeXuKI6IENKaKTZAqLBIiXS3t7ZTyoQin5oNBq8UnyKFB8+v7zwyR+FiGiFWel1jM3eKLGGA0e1FEyTMAXPkFZdU3uGCINNwq3rm5qnvTrccvP46Pki3iciNDJDJaXegKRWg7vXiyZ4swFcjsCItFS5XX/+/b1iKrEunC4V48a5ULnsSP9Ji4Xw0eZ0vt0+Br/FjEMfQpS+myiTjfqachpq97J5/QosIU6GJudLFNz0iprEaCkUj6jy62ix6klLH95PKpD4euH4InKUVyirjOn7z4B4OBof+VmOPuVDoqTaZfYfOBJGbFwxzz1lQaWdRsCkYNTrOHH8uIh1Sk1clAFlRivJ14elMSzKR0qCC4056JSSGnTsPhXNaPdaaZPXJdJe1M9nr/4bnmOEqBu42iL5N7lRCXmwvfQSwLIjEaQnOUjJkltlhnP2bCoFBQVExZwh3NhMxck5kqouAnLBxGFJTC6ahFoXzund77J6q5sn72okL7MHxSsHunXkaWWKKnKxi2dhV2m/FfeWXCPbzwW6FSsRuX42HjBSuiOSD0uqyC6cwI3XWblxahvJuQHufeQqOtrVZOXY+eCVBsqqynC76khMTsQUFinbj589Xz4jE+8gB+rMVG46yFvvDMegVfHAbCftB8Iwq80iOgL9w5sk5QdfCGD9RDYwPfWmd1lbMofbZ2hZVBLHQzefJ2u4g+S5E5hbbKVoTCc5o91MnCa9Z5f8NpjYbd0vKVJkWLlprvqEk+Wl7Kk2sfe0mWPLq6SVDXy3T4ZTqILa28rVN31GTttr0r5SiKm/RxVo2CBJ1+JzNMsNJ3PGt4D4WDvDhnjYvC9WthwV5SUVfCdbz9+XJ7OsJIaXF8ax9fMw9L0xtNl9HN3yHOuXTeO999ezcmc0h86a+X7JOZIy/KzYEINeuO69toudbbeRM/43srU2C6fk7HSZdN0PtwcUqQFFK+Yw8aD4cS53zsrg/cdcPLI8krHpPdx/Uws2m8LvFssiUmdEowqQN8LJTZNUshHZWfGdge6eEDEdhdR4N18sFtNyaVjyuYUe6YI37+rlT8t6Kfn6LCrrPtgm25B3qMyM8ZKCqvcCyrl/cEFCmJgh5TqykpM17ax9MY2bi6Oxunz8c304s8Z3c88fL3FsexirtoWz/ZiJLruKbqdCSqyXybk9zJtqZ0yRg5fejKXinJ4Z+R7ume7n1Q8vUfTnw2L1ibDjWnbv70Xl0FA47+mBfWBzPE+tsXBD4TkmTU+F5OOUHepi05t5PD3PyPOlRh6caef1dSYW395JXJQYkZCKV/X7rVrBXa/ldKOe9zeH8ts8L+XVWp6ZE+C1z7sYe18Zs4oS8JVdy7rNLbTZzEyMN5L7xJYBAY5qOjZmMX9pDgvn1RIZ1cOomffT1DGbRQte4+3bbVQ0KmyskJF9TMPKR21sP6khWmzV6lBYs0PPxGyv+IiWJ27wEarTMC1XxT0rFJ564X4yk7fRsOkTvtmXJkNKz925HpIW7ASt5YqNyHeJwIGrONNs5URzKOdaZOlItTOl0I+MByzaEKl8mfcXzbTJs++c/GiREOhlWB2u1TA9R0Ncgo2MAitd8kNFF9NBXa0Wk8/Jjv1RVNREcot00bjMkSjTvxPLDRqT/Lks4Ed0fypES9j1w2HsMhtKv0/glceaiImHBS+k8/Ad58lJ8dNZncaWPRICMdM5xV1oc05JKgI89WIq0eEuFt7XzOI3LBSPshInS0vmyNkw9HGZJ9IFV+DnAq5EzzdSrbupP3qQ5LDtlG700tBmJj9TCjjMRvTwB/C6rRh6SnninSzee+wUh6ugcKxJbHo8xoTJ4qjyQ8Rw3cCBP8cvC/gZJBeXXubM1udY+m0K469yUFkfwtUZdkYmWUmZIuvWkL8MfPZ/w68UcAVOFnN0z2GpAb+071TCJn098OLX4f8XEETNEikBWUhSf92tfwL8B8MhvFTZhRwkAAAAAElFTkSuQmCC'
                    root.tk.call('wm', 'iconphoto', root._w, tkinter.PhotoImage(data=icon))
                    root.geometry("1200x500")
                    root.columnconfigure(0, weight=1)
                    root.rowconfigure(0, weight=1)
                    root.title("FERA "+ version+" - Forensics Evidence Report Analyzer -- Polícia Científica do Paraná")
                    sqliteconn.close()
                    
                    #frameinitial.grid_forget()
                    #frameinitial.destroy()
                    root.bind('<Control-Alt-F12>', f12Pressed)
                    mw = App()
                    #None
                    
                    #root.mainloop()
            
            
        except Exception as ex:
            popup_window("Erro na abertura do Banco de Dados", False)
            #None
            printlogexception(ex=ex)
            pathdb=None
        finally:
            None
    else:
        pathdb = None

def check_clicklistbox(event=None, lb1=None):
    if (event.y < lb1.bbox(0)[1]) or (event.y > lb1.bbox("end")[1]+lb1.bbox("end")[3]): # if not between it
        
        lb1.select_clear(0, 'end')



def go():
    global listapdfs, path, processar, somaq, lock, exitFlag, inserts, lockp, processados, root, importarDB, frameinitial, labelopcao, newdb, \
        olddb, continuar,qlchild,primeiraexec,pathdb, ok, expertmode, erros, warningimage, recenttxt, heightimage, widthimage, pathpdfinput, g_search_results
    exitFlag = False
    inserts = []

    qlchild = None
    continuar = False
    primeiraexec = True
    ok = False
    warningb = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAChklEQVRYR8XXt44UQRDG8d/hibEiIsC7iICHgAjvrQAhEjwhBAhPBhLeexIkXoMA762EgATxABygknpOc6PdnZm9W5hope2p+tf3VVdPd/nPT1cf8w9K7/9qN067AANxGqvRjVPYgT91QdoFOIkt+J2SBtB+7PsXADPxKCWegx94goCYiM91INpR4B7m4w4Wp2QnsC3ZsrmTAPnqZ+FZSjYGHxBNOaGOCnUVuIsFuI0lhUqPYzvOYFNVFeoAzMDj5H0o8byQJFR4j8GpFz5VgagDEJ4vbFJ9litT4Sw29ifA9NTpsc9DiRdNgo9OvRAqTMLHMoiqCoTni3ALS3NBs8GTj3MsDaXz2NAfAFF9eB9PsfpGAJkKQ5IKsTuaPlUUyKq/iWWFSI0AYslR7MQFrO8LwLTkfcQIJV5WBBiV/A8VJqfd0ZCjTIHwPKbdDSxvEKGZArH0CHbhItY1U6EVQL76+P2qJkCoEP4PxRS8awTRCiA8j2nXrPqI10qBvAqXsLYOwFQ8TQnC+0bVVwEoVaGZAln117GiRReXKRCvHsZuXMaaYqxGAFWrL5sx2f8j044Ylnrhbf7FRgDheUy7a1hZNUvJukPYgyvpM65neREgujXO+JA2Ov91i8BzcS79HyP3QYu1oULsiOEIhd9ka4sA4XlMu6tYVVLVN8QRHM93jC1ZfxB7i7HzADGx4oyP6ntRNglcF2BE6oVQoUfdPEDM7dirVaoPpjoWZDVkKvT0Qh7gC8alE6zHo35qwixMqBDK/UTMCHmAr8nH2XjYz4mzcPNwPwfQnQfIDo8O5e4VNi42W4sKDMCBNP/Hd4giLi1xr4jJGFe6XhZ0KGfrsGXfAx2H+gthzokhxc9aDgAAAABJRU5ErkJggg=='
    warningimage = tkinter.PhotoImage(data=warningb)
    try:
        if(primeiraexec):
            #stopwords = ["que", "com", "dos", "das", "mas", "foi", "tem", "por"]
            if(expertmode):
                importarDB = None
                lockp = mp.Lock()
                lock = mp.Lock()
                processados = mp.Queue()
                processar = mp.Queue()
                continuar = mp.Queue()
                erros = mp.Queue()
                somaq = mp.Queue()
                #root = tkinter.Tk()
                if(pathpdfinput!=None):
                    basename = os.path.basename(pathpdfinput)
                    file_name = os.path.splitext(basename)[0]
                    pathdbfrompdf = os.path.join(Path(pathpdfinput).parent, file_name+".db")
                    if(os.path.isfile(pathdbfrompdf)):
                        
                        pathdb = Path(pathdbfrompdf)
                        loaddb(pathdecided=True)
                    else:
                        solicitarDiretorio(pathdbx = pathdbfrompdf, addrel = pathpdfinput)
                        #loaddb()
                elif(pathdb!=None):
                    loaddb()
                else:
                    root.protocol("WM_DELETE_WINDOW", on_quit)
        
                    root.geometry("600x600")
                    root.title("FERA "+version+" - Forensics Evidence Report Analyzer v1.0 -- Polícia Científica do Paraná")
                    root.columnconfigure(0, weight=1)
                    root.rowconfigure(0, weight=1)
                    
                    frameinitial = tkinter.Frame(root, highlightbackground="green", highlightcolor="green", highlightthickness=1, bd=0)
                    frameinitial.grid(row=0, column=0, sticky='nsew')
                    frameinitial.columnconfigure((0,1), weight=1)
                    frameinitial.rowconfigure((0,1), weight=1)
                    frameinitial.rowconfigure(2, weight=10)
                    labelopcao = tkinter.Label(frameinitial, text="Clique na opção desejada")
                    labelopcao.grid(row=0, column=0, columnspan=2, sticky='nsew')
                    
                    newdb = tkinter.Button(frameinitial, text="Criar caso", command=solicitarDiretorio)
                    newdb.grid(row=1, column=0, sticky='n')
                    recenttxt = os.path.join(os.getcwd(),"recents.txt")
                    Lb1 = tkinter.Listbox(frameinitial)
                    olddb = tkinter.Button(frameinitial, text="Importar caso", command= lambda lb=Lb1: loaddb(None, lb))
                    olddb.grid(row=1, column=1, sticky='n')
                    
                    Lb1.bindtags(('.Lb1', 'Listbox', 'post-listbox-bind-search','.','all'))
                    Lb1.grid(row=2, column=0, columnspan=2, sticky='nsew')
                    Lbhs = tkinter.Scrollbar(frameinitial, orient="horizontal")
                    Lbhs.config( command = Lb1.xview )
                    Lbhs.grid(row=3, column=0, columnspan=2, sticky='ew')
                    Lb1.configure(xscrollcommand=Lbhs.set)
                    
                    
                    Lbvs = tkinter.Scrollbar(frameinitial, orient="vertical")
                    Lbvs.config( command = Lb1.yview )
                    Lbvs.grid(row=2, column=2, rowspan=2, sticky='ns')
                    Lb1.configure(yscrollcommand=Lbvs.set)
                    try:
                        
                        with open(recenttxt, 'r') as f:
                            count = 1
                            for line in f:
                                #None
                                if(os.path.isfile(line.strip())):
                                    Lb1.insert(count, line)
                                    count += 1
                                    
                                   
                    except Exception as ex:
                        None
                        printlogexception(ex=ex)
                    Lb1.bind_class('post-listbox-bind-search', '<Double-1>', lambda e, lb=Lb1: loaddb(e, lb))
                    Lb1.bind_class('post-listbox-bind-search','<1>',  lambda e,  lb=Lb1: check_clicklistbox(e, lb))
            else:
                #None
                loaddb()
                primeiraexec = False
            #root.bind('<Control-Alt-F12>', f12Pressed)
            
            #root.mainloop()
        
    except Exception as ex:
        #None
        printlogexception(ex=ex)
        pathdb = None
        #None
        on_quit()
        
'''       
def addrelfromfiewer(tipo, toplevelfromviewer):
     
   
    global pathdb, marginsok, mt, mb, me, md, threads
    processar = mp.Queue()
    mng = mp.Manager()
    processedpages = mng.list()
    processedpages.append(0)
    #Global = mng.Namespace()
    #Global.erroaddviewer = 0
    #Global.ppaginas = 0
    patpdf = askopenfilename(filetypes=(("PDF", "*.pdf"), ("Todos os arquivos", "*")))
    ok = False
    idpdfretorno = None
    try:
        if(patpdf!=None):
            ok = True
            pathpdf = Path(patpdf)
            doc = fitz.open(pathpdf)    
            pdfs = []
            try:
                pixorg= doc[0].getPixmap()                
                window = tkinter.Toplevel()
                marginsok = False
                try:
                    setMargin(window, doc)
                except Exception as ex:
                    printlogexception(ex=ex)
                finally:
                   None# doc.close()
                toplevelfromviewer.wait_window(window)
                if(not marginsok):
                    None
                    ok = False
                else:
                    pdfs.append((patpdf, mt, mb, me, md, pixorg))
                    sqliteconn = sqlite3.connect(str(pathdb))
                    cursor = sqliteconn.cursor()
                    try:
                        for pdf in pdfs:
                            #None
                            patpdf = pdf[0]
                            pathpdf = Path(patpdf)
                            mt = pdf[1]
                            mb = pdf[2]
                            me = pdf[3]
                            md = pdf[4]
                            pixorg = pdf[5]
                            pathpdfbase = os.path.basename(pathpdf)
                            relpathpdf = os.path.relpath(pathpdf, pathdb.parent)
                            filename, file_extension = os.path.splitext(patpdf)
                            #None
                            if(file_extension==".pdf"):
                                sqliteconn.execute("PRAGMA foreign_keys = ON")
                                cursor.execute("SELECT P.id_pdf FROM Anexo_Eletronico_Pdfs P where :pdf = P.rel_path_pdf ",{'pdf': str(relpathpdf)})
                                r = cursor.fetchone()
                                if(r!=None):
                                    None
                                else:
                                    erro = False
                                    insert_query_pdf = """INSERT INTO Anexo_Eletronico_Pdfs
                                                (rel_path_pdf , indexado, tipo, lastpos, margemsup, margeminf, margemesq, margemdir) VALUES
                                                (?,?,?, '0.0', ?,?,?,?)
                                    """
                                    cursor.execute(insert_query_pdf, (relpathpdf, 0,tipo, mt, mb, me, md,))
                                    mmtopxtop = math.floor(mt/25.4*72)
                                    mmtopxbottom = math.ceil(pixorg.height-(mb/25.4*72))
                                    mmtopxleft = math.floor(me/25.4*72)
                                    mmtopxright = math.ceil(pixorg.width-(md/25.4*72))
                                    idpdf = cursor.lastrowid
                                    sqliteconn.commit()
                                    relp = Path(os.path.normpath(os.path.join(pathdb.parent, str(relpathpdf))))
                                    relpdir = relp.parent
                                    pathpdf2 = str(pathpdf)
                                    if plt == "Linux":
                                        pathpdf2 = pathpdf2.replace("\\","/")
                                    elif plt=="Windows":
                                        pathpdf2 = pathpdf2.replace("/","\\")
                                    
                                    doc = fitz.open(pathpdf2)
                                    
                                    try:
                                        
                                        toc = doc.getToC(simple=False)
                                        for entrada in toc:
                                            None
                                            novotexto = ""
                                            init = 0
                                            dictx = doc[entrada[3]['page']].getText("rawdict")
                                            deslocy = entrada[3]['to'].y
                                            parar = False
                                            for block in dictx['blocks']:
                                                bboxb = block['bbox']
                                                if(bboxb[1]>deslocy or parar):
                                                    break  
                                                if('lines' in block):
                                                    for line in block['lines']:
                                                        bboxl = line['bbox']
                                                        #if(bboxl[2]>deslocy or parar):
                                                        #    parar = True
                                                        #    break
                                                        for span in line['spans']:
                                                            for char in span['chars']:
                                                                bboxchar = char['bbox']
                                                                bboxxmedio = (bboxchar[0]+bboxchar[2])/2
                                                                bboxymedio = (bboxchar[1]+bboxchar[3])/2
                                                                if(bboxxmedio < mmtopxleft or bboxxmedio > mmtopxright or bboxymedio < mmtopxtop or bboxymedio > mmtopxbottom):
                                                                    continue
                                                                char = char['c']
                                                                #codePoint = ord(char)
                                                                #if(codePoint<256):
                                                                #    codePoint += lowerCodeNoDiff[codePoint]
                                                                novotexto += char
                                                                init += 1
                                                            #if(len(novotexto) > 0 and novotexto[-1]!=' '):
                                                            #    novotexto += ' '
                                                        if(len(novotexto) > 0 and novotexto[-1]!=' '):
                                                            novotexto += ' '
                                                            init += 1
                                                    if(len(novotexto) > 0 and novotexto[-1]!=' '):
                                                        novotexto += ' '
                                                        init += 1
                                                 
                                            insert_query_toc = """INSERT INTO Anexo_Eletronico_Tocs
                                                    (toc_unit, id_pdf , pagina, deslocy, init) VALUES
                                                    (?,?,?,?,?)
                                            """
                                            
                                            cursor.execute(insert_query_toc, (entrada[1], idpdf, entrada[3]['page'], deslocy, init,))
                                       
                                        totalPaginas = len(doc)
                                        cursor.execute("DROP TABLE IF EXISTS Anexo_Eletronico_Conteudo_id_pdf_"+str(idpdf))
                                        cursor.execute("DROP TABLE IF EXISTS Anexo_Eletronico_Conteudo_id_pdf_"+str(idpdf)+"_config")
                                        cursor.execute("DROP TABLE IF EXISTS Anexo_Eletronico_Conteudo_id_pdf_"+str(idpdf)+"_content")
                                        cursor.execute("DROP TABLE IF EXISTS Anexo_Eletronico_Conteudo_id_pdf_"+str(idpdf)+"_data")
                                        cursor.execute("DROP TABLE IF EXISTS Anexo_Eletronico_Conteudo_id_pdf_"+str(idpdf)+"_docsize")
                                        cursor.execute("DROP TABLE IF EXISTS Anexo_Eletronico_Conteudo_id_pdf_"+str(idpdf)+"_idx")
                                        create_table_content = 'CREATE VIRTUAL TABLE Anexo_Eletronico_Conteudo_id_pdf_' + str(idpdf) + \
                                        ' USING fts4(texto, pdf_id UNINDEXED, pagina' ')'
                                        cursor.execute(create_table_content) 
                                        sqliteconn.commit()
                                        tamanhodoc = len(doc)
                                        
                                        fim = 0
                                        threads = [None] * nthreads
                                        #Global.processados = 0
                                        for i in range(nthreads):
                                            #None
                                            init = fim
                                            fim = math.ceil((i+1) * (len(doc)/nthreads))
                                            if(i==nthreads-1):
                                                fim = len(doc)
                                            #None
                                            proc = Processar(idpdf, relpathpdf, pathpdfbase, init, min(fim, len(doc)), mt, mb, me, md)     
                                            processar.put(proc)
                                        doc.close()    
                                        for i in range(nthreads):
                                            
                                            threads[i] = mp.Process(target=insertThread, args=(processar, processedpages, lock, lockp, None, pathdb,None,))
                                            threads[i].start()   
                                        if(not erro):
                                            tl1 = tkinter.Toplevel()
                                            #icon = b'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'
                                            #root.tk.call('wm', 'iconphoto', root._w, tkinter.PhotoImage(data=icon))
                                            #root.title("FERA "+version+" - Forensics Evidence Report Analyzer -- Polícia Científica do Paraná")
                                            tl1.geometry("400x100")
                                            tl1.rowconfigure(0, weight=1)
                                            tl1.columnconfigure(0, weight=1)
                                            progress = ttk.Progressbar(tl1, mode='indeterminate')
                                            progress.grid(row=0, column=0, sticky='nsew', pady=20)
                                            progress['mode'] = 'determinate'
                                            progress['maximum'] = tamanhodoc
                                            tl1.update()
                            
                                            while(True):
                                                algumvivo = False
                                                for i in range(nthreads):
                                                    if(threads[i].is_alive()):
                                                        algumvivo = True
                                                        break
                                                if(not algumvivo):
                                                    break
                                                else:
                                                    #None
                                                    progress['value'] =processedpages[0]
                                                    #tl1.update_idletasks()
                                                    tl1.update()
                                                    time.sleep(0.5)
                                            sqliteconn.execute("PRAGMA foreign_keys = ON")
                                            try:
                                                hashpdf = str(md5(str(pathpdf2)))
                                                cursor.execute("UPDATE Anexo_Eletronico_Pdfs set indexado = 1, hash = ? WHERE id_pdf = ?", (hashpdf, idpdf,))
                                                sqliteconn.commit()
                                                
                                            except Exception as ex:
                                                printlogexception(ex=ex)
                                                None
                                            
                                            #if(Global.erroaddviewer==1):
                                            #    ok = False
                                            #None
                                            tl1.destroy()
                                            idpdfretorno = idpdf
                                            
                                    except Exception as ex:
                                        ok = False
                                        erro = True
                                        printlogexception(ex=ex)
                                        None
                                    finally:
                                        try:
                                            doc.close()
                                        except Exception as ex:
                                            None
            
                    except Exception as ex:
                        ok = False
                        printlogexception(ex=ex)
                    finally:
                        cursor.close()
                        if(sqliteconn):
                            sqliteconn.close()
            except Exception as ex:
                printlogexception(ex=ex)
            finally:
                try:
                    doc.close()
                except Exception as ex:
                    None
                try:
                    None
                except Exception as ex:
                    None
                    
    except Exception as ex:
        printlogexception(ex=ex)
    finally:
        return (ok, idpdfretorno, patpdf, mt, mb, me, md)
'''


def separateThread(idpdfs, view=True):
    global indexando, qtos, cont, totalPaginas, threads, continuar, qlchild, clear_searches 
    clear_searches = False
    for idpdf in idpdfs:
        print(idpdf)
        sqliteconn = sqlite3.connect(str(pathdb))
        cursor = sqliteconn.cursor()
        try:
            sqliteconn.execute("PRAGMA foreign_keys = ON")
            select_all_pdfs = '''SELECT P.id_pdf, P.rel_path_pdf, P.margemsup, P.margeminf, P.margemesq, P.margemdir  FROM Anexo_Eletronico_Pdfs P where p.id_pdf = ?'''
            cursor.execute(select_all_pdfs, (idpdf,))
            records = cursor.fetchall()
            #lock = {}
            soma = 0.0
            divisao = 1024 * 1024
            totalPaginas = 0
            qtos = len(records)
            cont = 0
            abs_path_pdf = None
            for r in records:
                
                idpdf = r[0]
                rel_path_pdf = r[1]
                abs_path_pdf = os.path.normpath(os.path.join(pathdb.parent, rel_path_pdf))
                if plt == "Linux":
                    abs_path_pdf = abs_path_pdf.replace("\\","/")
                elif plt=="Windows":
                    abs_path_pdf = abs_path_pdf.replace("/","\\")
                try:
                    doc = fitz.open(abs_path_pdf)
                    pdf = os.path.basename(abs_path_pdf)
                    fim = 0
                    
                    totalPaginas += len(doc)
                    cursor.execute("DROP TABLE IF EXISTS Anexo_Eletronico_Conteudo_id_pdf_"+str(idpdf))
                    cursor.execute("DROP TABLE IF EXISTS Anexo_Eletronico_Conteudo_id_pdf_"+str(idpdf)+"_config")
                    cursor.execute("DROP TABLE IF EXISTS Anexo_Eletronico_Conteudo_id_pdf_"+str(idpdf)+"_content")
                    cursor.execute("DROP TABLE IF EXISTS Anexo_Eletronico_Conteudo_id_pdf_"+str(idpdf)+"_data")
                    cursor.execute("DROP TABLE IF EXISTS Anexo_Eletronico_Conteudo_id_pdf_"+str(idpdf)+"_docsize")
                    cursor.execute("DROP TABLE IF EXISTS Anexo_Eletronico_Conteudo_id_pdf_"+str(idpdf)+"_idx")
                    create_table_content = 'CREATE VIRTUAL TABLE Anexo_Eletronico_Conteudo_id_pdf_' + str(idpdf) + \
                    ' USING fts4(texto, pdf_id UNINDEXED, pagina' ')'
                    cursor.execute(create_table_content)
                    
                    cont+=1
                    for i in range(nthreads):
                        
                        init = fim
                        fim = math.ceil((i+1) * (len(doc)/nthreads))
                        if(i==nthreads-1):
                            fim = len(doc)
                        
                        proc = Processar(idpdf, rel_path_pdf, pdf, init, min(fim, len(doc)), r[2], r[3], r[4], r[5])
                        
                        
                        processar.put(proc)
                except Exception as ex:
                    printlogexception(ex=ex)
                finally:
                    doc.close()
            
            for i in range(nthreads):
                
                threads[i] = mp.Process(target=insertThread, args=(processar, None, lock, lockp, processados, pathdb,continuar,), daemon=True)
                threads[i].start()
            indexando = 1
            for i in range(nthreads):
                threads[i].join()
            if(continuar != None and continuar.empty()):
                
                hashpdf = str(md5(abs_path_pdf))
                #None
                #None
                sqliteconn.execute("PRAGMA foreign_keys = ON")
               
                cursor.execute("UPDATE Anexo_Eletronico_Pdfs set indexado = 1, hash = ? WHERE id_pdf = ?", (hashpdf, idpdf,))
                sqliteconn.commit()
                

            
    
            
        except Exception as ex:
            printlogexception(ex=ex)
        finally:
            cursor.close()
            sqliteconn.commit()
            sqliteconn.close()
    processados.put(('clear_searches', True))
'''
def setMargin(window, pdf):
        global docimg, margemimg
        
        #pathpdf = Path(pdf)
        window.geometry("800x640")
        window.rowconfigure(1, weight=1)
        window.columnconfigure(0, weight=1)
        prop = 1.5
        loadedpage = pdf[math.floor(len(pdf)/prop)]
        pixorg = loadedpage.getPixmap()
        
        #72pixels = 1 inch = 25,4mm
        inch = 2.54
        
        ajustar = tkinter.Frame(window, borderwidth=2, bg='white', relief='ridge')
        ajustar.grid(row=0, column=0, sticky='nsew')
        ajustar.rowconfigure(0, weight=1)
        ajustar.columnconfigure((0,1,2,3,4,5,6,7), weight=1)
        datatop = tkinter.IntVar()
        databottom = tkinter.IntVar()
        dataleft = tkinter.IntVar()
        dataright = tkinter.IntVar()
        
        datatop.set(math.floor(115/72 * 25.4))     
        databottom.set(math.floor(max(0, ((pixorg.height-813)/72) * 25.4)))
        
        #None
        dataleft.set(30)       
        dataright.set(10)
        
        

        
        top = tkinter.Label(ajustar, text='Superior (mm): ')
        top.grid(row=0, column=0, sticky='e')
        entrytop = tkinter.Entry(ajustar, textvariable=datatop)
        entrytop.grid(row=0, column=1, sticky='nsw')
        bottom = tkinter.Label(ajustar, text='Inferior (mm): ')
        bottom.grid(row=0, column=2, sticky='e')
        entrybottom = tkinter.Entry(ajustar, textvariable=databottom)
        entrybottom.grid(row=0, column=3, sticky='nsw')
        left = tkinter.Label(ajustar, text='Esquerda (mm): ')
        left.grid(row=0, column=4, sticky='e')
        entryleft = tkinter.Entry(ajustar, textvariable=dataleft)
        entryleft.grid(row=0, column=5, sticky='nsw')
        right = tkinter.Label(ajustar, text='Direita (mm): ')
        right.grid(row=0, column=6, sticky='e')
        entryright = tkinter.Entry(ajustar, textvariable=dataright)
        entryright.grid(row=0, column=7, sticky='nsw')
        
        fotodoc = tkinter.Frame(window, borderwidth=2, relief='ridge')
        fotodoc.grid(row=1, column=0, sticky='nsew')
        fotodoc.rowconfigure(0, weight=1)
        fotodoc.columnconfigure(0, weight=1)
        fotocanvas = tkinter.Canvas(fotodoc, bg='gray', highlightthickness=0, relief="raised")
        fotocanvas.grid(row=0, column=0, sticky='nsew')
        mat = fitz.Matrix(1/prop, 1/prop)
        pix = loadedpage.getPixmap(alpha=False, matrix=mat) 
        imgdata = pix.getImageData("ppm")
        docimg = tkinter.PhotoImage(data = imgdata)
        
        docvanvas = fotocanvas.create_image((0,0), anchor='nw', image=docimg)
        #docvanvas.image = docimg
        
        bottomframe = tkinter.Frame(window, borderwidth=2, relief='ridge')
        bottomframe.grid(row=2, column=0, sticky='nsew')
        bottomframe.rowconfigure(0, weight=1)
        bottomframe.columnconfigure((0,1), weight=1)
        button_ok = tkinter.Button(bottomframe, text="OK", command= lambda : popupcomandook(window, datatop, databottom, dataleft, dataright))
        button_ok.grid(row=0, column=0, sticky='ns', pady=5)
        button_cancel = tkinter.Button(bottomframe, text="Cancelar", command= lambda : popupcomandocancel(window))
        button_cancel.grid(row=0, column=1, sticky='ns', pady=5)
        
        dataleft.trace_add("write", lambda *args: checkmargin(fotocanvas, prop, datatop, databottom, dataleft, dataright, button_ok, pixorg))
        databottom.trace_add("write", lambda *args : checkmargin(fotocanvas, prop, datatop, databottom, dataleft, dataright, button_ok, pixorg))
        datatop.trace_add("write", lambda *args : checkmargin(fotocanvas, prop, datatop, databottom, dataleft, dataright, button_ok, pixorg))
        dataright.trace_add("write", lambda *args : checkmargin(fotocanvas, prop, datatop, databottom, dataleft, dataright, button_ok, pixorg))
        mmtopxtop = math.floor(datatop.get()/25.4*72)
        mmtopxbottom = math.ceil(max(0, pixorg.height-(databottom.get()/25.4*72)))
        mmtopxleft = math.floor(dataleft.get()/25.4*72)
        mmtopxright = math.ceil(pixorg.width-(dataright.get()/25.4*72))
        x0k = math.floor(mmtopxleft/prop)
        y0k = math.floor(mmtopxtop/prop)
        x1k = math.ceil(mmtopxright/prop)
        y1k =  math.ceil(mmtopxbottom/prop)
        margemimg = create_rectanglex(x0k, y0k, x1k, y1k, (21, 71, 150, 85))
        margempreimage = fotocanvas.create_image(x0k, y0k, image=margemimg, anchor='nw', tags=("margem"))
        #margempreimage.image = margemimg
'''

def iterateXREF_NamedDests(doc, xref, p1, p2, p3, p4, pnotmm, xreftopage):
    chaves = doc.xref_get_keys(xref)
    
    listax = []
    #regex= r"\(mm\.[a-zA-Z0-9_\.-]+)\)([0-9]+)(\s[0-9]+\s)([A-Z])"
    if("Names" in chaves):
        
       
        #objeto = p1.findall(pobjetoxref)
        #limits = doc.xref_get_key(xref, "Limits")
        names = doc.xref_get_key(xref, "Names")[1]
        
        namesdest = p3.findall(names)
        
        for namedd, xr, num, letra  in namesdest:

            #keys = doc.xref_get_keys(int(xr))
            folhas = p4.findall(doc.xref_object(int(xr)))
            
            for pageref, x, y in folhas:
                
                listax.append((namedd, xreftopage[int(pageref)], x, y))

    elif("Kids" in chaves):
        
        destinations_kids = doc.xref_get_key(xref, "Kids")
        destinations_limits = doc.xref_get_key(xref, "Limits")
        if(len(destinations_limits)>1):
            
            quaislimites = pnotmm.findall(destinations_limits[1])
            if(len(quaislimites)>0 or 'null'==destinations_limits[0]):
                splitted = destinations_kids[1].split(" ")
                grauavore = int(len(splitted)/3)
                for i in range(grauavore):
                    indice = i * 3
                    novoxref = int(splitted[indice].replace("[", "").replace("]", ""))
                    listax.extend(iterateXREF_NamedDests(doc, novoxref, p1, p2, p3, p4, pnotmm, xreftopage))
    return listax

def iteratetreepages( xreftopage, doc, numberregex, xref, count):
    objrootpages = doc.xref_get_key(int(xref), "Type")[1]
    if(objrootpages=="/Pages"):
        objrootkids = doc.xref_get_key(int(xref), "Kids")[1]
        for indobj, gen in numberregex.findall(objrootkids):
           count = iteratetreepages(xreftopage, doc, numberregex, indobj, count)  
        #return count
    elif(objrootpages=="/Page"):
        xreftopage[int(xref)] = count
        count += 1
    
    return count

def loadPages(xreftopage, doc, numberregex):
    rootpdf  = doc.pdf_catalog()
    objpagesr = numberregex.findall(doc.xref_get_key(rootpdf, "Pages")[1])[0][0]
    objrootpages = doc.xref_get_key(int(objpagesr), "Type")[1]
    if(objrootpages=="/Pages"):
       objrootkids = doc.xref_get_key(int(objpagesr), "Kids")[1] 
       count = 0
       for indobj, gen in numberregex.findall(objrootkids):
           count = iteratetreepages(xreftopage, doc, numberregex, indobj, count)

def grabNamedDestinations(doc):
    #global xreftopage
    xreftopage = {}
    numbercompile = re.compile(r"([0-9]+)\s([0-9]+)")
    loadPages(xreftopage, doc, numbercompile)
    #
    listnameddestinations = []
    #for p in range(len(doc)):
    #    xref = doc.page_xref(p)
    #    xreftopage[xref] = p
    regex2= r"\/F\([-_\.a-zA-Z0-9]+\)"
    regex1= r"([0-9]+)(\s[0-9]+\s)([A-Z])"
    regex3= r"\(([subsection|subsubsection|section]+\.[a-zA-Z0-9_\.\-]+)\)([0-9]+)(\s[0-9]+\s)([A-Z])"
    regexnotmm = r"\(([subsection|subsubsection|section]+\.[a-zA-Z0-9_\.\-]+)\)"
    regex4 = r"\[\s+([0-9]+)\s+0\s+R\s+/XYZ\s+([0-9\.]+)\s+([0-9\.]+)"
    p1 = re.compile(regex1)
    p2 = re.compile(regex2)
    p3 = re.compile(regex3)
    p4 = re.compile(regex4)
    pnotmm = re.compile(regexnotmm)
    pagexref = doc.page_xref(1)
    
    
    key = doc.xref_get_key(doc.pdf_catalog(), "Names")
    lista = []
    try:
        dests = doc.xref_get_key(int(key[1].split(" ")[0]), "Dests")
        if("xref" in key[0]):
        
            lista.extend(iterateXREF_NamedDests(doc, int(dests[1].split(" ")[0]),p1,p2, p3, p4, pnotmm, xreftopage))
        
        else:
            
            None
    except Exception as ex:
        printlogexception(ex=ex)
        #
        None
        #printlogexception(ex=ex)
    
    
        #sys.exit(0)
    return lista
        
def popupcomandook(window, datatop, databottom, dataleft, dataright):
        global marginsok, mt, mb, me, md

        marginsok = True
        mt = datatop.get()
        mb = databottom.get()
        me = dataleft.get()
        md = dataright.get()
        window.destroy()
def md5(path_pdf):
    hash_md5 = hashlib.md5()
    with open(path_pdf, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
       
def popupcomandocancel(window):
    global marginsok

    marginsok = False

    window.destroy()

def locateToc(pagina, pdf, p0y=None, init=None, toc=None):
    pdfx = (str(Path(pdf)))
    t = 0
    napagina = False
    naoachou = True
    if(init!=None):
        for t in range(len(toc)-1):
            if(pagina >=toc[t][1] and pagina < toc[t+1][1]):
                naoachou = False
                break   
            elif(pagina >= toc[t][1] and pagina <= toc[t+1][1]):
                napagina = True
                
            if(napagina and toc[t+1][3] > init  ):  
                naoachou = False
                break
        
        if(naoachou):
            if(pagina==0):
                t=0
            else:
                t=len(toc)-1
                
    elif(p0y!=None):
         for t in range(len(toc)-1):
            if(pagina >= toc[t][1] and pagina < toc[t+1][1]):
                naoachou = False
                break   
            elif(pagina >= toc[t][1] and pagina <= toc[t+1][1]):
                napagina = True
                
            if(napagina and toc[t+1][2] > p0y  ):  
                naoachou = False
                break
        
         if(naoachou):
            if(pagina==0):
                t=0
            else:
                t=len(toc)-1
    
    #t-=2
    t = min(t, len(toc)-1)
    t = max(0, t)
    if(len(toc)>0):
        return toc[t][0]
    else:
        return ""
    

def searchLogic(pathpdf, advanced, pathdb, idpdf, tocs, idtermo, termo):
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

    termo = novotermo.strip().upper()
    '''
    termo = termo.lower()
    idtermopdf = str(idpdf)+'-'+str(idtermo)
    
    pathdocespecial1 = pathpdf
    doc = fitz.open(pathdocespecial1)
    destepdf = 0
    resultados_para_banco = []
    try:       
        
        if(advanced):            
            notok = True
            while(notok):
                #sqliteconn = None
                #cursor = None
                try:
                    sqliteconn = connectDB(str(pathdb), 5, maxrepeat=-1)

                    cursor = sqliteconn.cursor()   
                    cursor.execute("PRAGMA journal_mode=WAL")
                    #cursor.execute("PRAGMA synchronous = normal")
                    #cursor.execute("PRAGMA temp_store = memory")
                    #cursor.execute("PRAGMA mmap_size = 30000000000")
                    #cursor.execute("PRAGMA journal_mode=WAL")
                    novabusca =  'SELECT  C.pagina, C.texto, offsets(Anexo_Eletronico_Conteudo_id_pdf_'+str(idpdf)+') FROM Anexo_Eletronico_Conteudo_id_pdf_'+str(idpdf)+' C where texto MATCH :termo ORDER BY 1'
                    cursor.execute(novabusca, {'termo': termo.upper()})                   
                    records2 = cursor.fetchall()
                    notok = False
                except sqlite3.OperationalError as ex:
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
            resultporsecao = {}
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
                    
                    toc = locateToc(pages[0], pathpdf, None, len(devoltainit), tocs)
                    if(toc not in resultporsecao):
                        resultporsecao[toc]=0
                    if(resultporsecao[toc]>=1000):
                        break  
                    resultporsecao[toc]+=1
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
                    for k in range(len(devoltainit)+len(devoltadif)+1, len(snippet)):
                        if(snippet[k]==' '):
                            espacos+=1
                        snippetdepois += snippet[k] 
                        if(espacos>=7):
                            break    
                    resultsearch.snippet =  (snippetantes, snippet[len(devoltainit):len(devoltainit)+len(devoltadif)], snippetdepois)                    
                    resultsearch.fixo = 0
                    resultsearch.counter = counter
                    resultados_para_banco.append((resultsearch.idtermo, resultsearch.idpdf, \
                                                 resultsearch.pagina, resultsearch.init, resultsearch.fim, str(resultsearch.toc), resultsearch.snippet[0], \
                                                     resultsearch.snippet[2], resultsearch.snippet[1],))
                    
                
            return resultados_para_banco
        else:
            notok = True
            records2 = []
            while(notok):
                sqliteconn = None
                cursor = None
                try:
                    #termo = termo.replace("%", "\\%")
                    #termo = termo.replace("\\", "\\\\")
                    sqliteconn = connectDB(str(pathdb), 5, maxrepeat=-1)
                    cursor = sqliteconn.cursor()
                    cursor.execute("PRAGMA journal_mode=WAL")
                    #cursor.execute("PRAGMA synchronous = normal")
                    #cursor.execute("PRAGMA temp_store = memory")
                    #cursor.execute("PRAGMA mmap_size = 30000000000")
                    #cursor.execute("PRAGMA journal_mode=WAL")
                    novabusca =  'SELECT  C.pagina, C.texto FROM Anexo_Eletronico_Conteudo_id_pdf_'+str(idpdf)+''' C where texto like :termo ESCAPE :escape ORDER BY 1'''
                    cursor.execute(novabusca, {'termo':'%'+termo+'%', 'escape': '\\'})
                    records2 = cursor.fetchall()
                    #cursor.execute(query, {'termo':'%'+termo+'%', 'pag':paginaquery, 'escape': '\\'})
                    
                    notok = False
                except sqlite3.OperationalError as ex:
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
                    toc = locateToc(pagina[0], pathpdf, None, resultfind, tocs)
                    
                    if(toc not in resultporsecao):
                        resultporsecao[toc]=0
                    if(resultporsecao[toc]>=1000):
                        break  
                    resultporsecao[toc]+=1
                    
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
                        resultsearch.fixo = 0
                        resultsearch.counter = counter   
                        resultsearch.toc = toc
                        resultados_para_banco.append((resultsearch.idtermo, resultsearch.idpdf, \
                                                 resultsearch.pagina, resultsearch.init, resultsearch.fim, str(resultsearch.toc), resultsearch.snippet[0], \
                                                     resultsearch.snippet[2], resultsearch.snippet[1],))
                        init = resultfind+len(termo)-1
                        resultfind = pagina[1].find(termo, init, len(pagina[1]))
                
            return resultados_para_banco
    except sqlite3.Error as ex:
        
        printlogexception(ex=ex)
                    
    except Exception as ex:
        printlogexception(ex=ex)
    
    finally:        
        doc.close()

def addrels(tipo, view=None, pathpdfinput = None, pathdbext=None, rootx=None):
    #None
    global marginsok, mt, mb, me, md, pathdb, root
    idpdfs = []
    if(pathpdfinput==None):
        pathpdfs = askopenfilenames(filetypes=(("PDF", "*.pdf"), ("Todos os arquivos", "*")))
    else:
        pathpdfs = pathpdfinput
        pathdb = Path(pathdbext)
        
        
    if(pathpdfs!=None and pathpdfs!=''):
        pdfs = []
        window = tkinter.Toplevel()
        window.rowconfigure((0,1), weight=1)
        window.columnconfigure((0,1), weight=1)
        labelask = tkinter.Label(window, text="Deseja definir a(s) margens do(s) documento(s)?")
        labelask.grid(row=0, column=0, columnspan=2, sticky='ns', pady=5)
        definirmargens = [True]
        #answer = False
        answeryes = tkinter.Button(window, text="SIM", command=  partial(defineMargins,window, definirmargens, True))
        answerno = tkinter.Button(window, text="NÃO", command=  partial(defineMargins,window, definirmargens, False))
        
        answeryes.grid(row=1, column=0, sticky='ns', pady=5)
        answerno.grid(row=1, column=1, sticky='ns', pady=5)
        root.wait_window(window)
        
        for patpdf in pathpdfs:   
            if(definirmargens[0]):
                window = tkinter.Toplevel()
                marginsok = False
                
                pathpdf = Path(patpdf)
                doc = fitz.open(pathpdf)
                pixorg= doc[0].getPixmap()
                try:
                    #if('mobilemerger' in doc.metadata[producer].lower):
                    setMargin(window, doc)
                except Exception as ex:
                    printlogexception(ex=ex)
                finally:
                    doc.close()
                root.wait_window(window)
                if(not marginsok):
                    continue
                else:
                    pdfs.append((patpdf, mt, mb, me, md, pixorg))
            else:
                pathpdf = Path(patpdf)
                #None
                doc = fitz.open(pathpdf)
                try:
                    pathpdf = Path(patpdf)                    
                    pixorg= doc[0].getPixmap()
                    pdfs.append((patpdf, 0, 0, 0, 0, pixorg))
                except Exception as ex:
                    printlogexception(ex=ex)
                finally:
                    doc.close()
        #sys.exit(0)
        sqliteconn = sqlite3.connect(str(pathdb))
        cursor = sqliteconn.cursor()
        try:
            for pdf in pdfs:
                #None
                patpdf = pdf[0]
                pathpdf = Path(patpdf)
                mt = pdf[1]
                mb = pdf[2]
                me = pdf[3]
                md = pdf[4]
                pixorg = pdf[5]
                relpathpdf = os.path.relpath(pathpdf, pathdb.parent)
                filename, file_extension = os.path.splitext(patpdf)
                #None
                if(file_extension.lower()==".pdf"):
                    sqliteconn.execute("PRAGMA foreign_keys = ON")
                    cursor.execute("SELECT P.id_pdf FROM Anexo_Eletronico_Pdfs P where :pdf = P.rel_path_pdf ",{'pdf': str(relpathpdf)})
                    r = cursor.fetchone()
                    if(r!=None):
                        pathpdf = os.path.join(pathdb.parent, str(relpathpdf))
                        pathpdf2 = str(pathpdf)
                        if plt == "Linux":
                            pathpdf2 = pathpdf2.replace("\\","/")
                        elif plt=="Windows":
                            pathpdf2 = pathpdf2.replace("/","\\")
                        
                        doc = fitz.open(pathpdf2)
                        try:                            
                            idpdfs.append((r[0], len(doc)))
                        except Exception as ex:
                            printlogexception(ex=ex)
                        finally:
                            doc.close()
                        None
                    else:
                        insert_query_pdf = """INSERT INTO Anexo_Eletronico_Pdfs
                                    (rel_path_pdf , indexado, tipo, lastpos, margemsup, margeminf, margemesq, margemdir) VALUES
                                    (?,?,?, '0.0', ?,?,?,?)
                        """
                        cursor.execute(insert_query_pdf, (relpathpdf, 0,tipo, mt, mb, me, md,))
                        mmtopxtop = math.floor(mt/25.4*72)
                        mmtopxbottom = math.ceil(pixorg.height-(mb/25.4*72))
                        mmtopxleft = math.floor(me/25.4*72)
                        mmtopxright = math.ceil(pixorg.width-(md/25.4*72))
                        idpdf = cursor.lastrowid
                        
                        #sqliteconn.commit()
                        relp = Path(os.path.normpath(os.path.join(pathdb.parent, str(relpathpdf))))
                        relpdir = relp.parent
                        pathpdf2 = str(pathpdf)
                        if plt == "Linux":
                            pathpdf2 = pathpdf2.replace("\\","/")
                        elif plt=="Windows":
                            pathpdf2 = pathpdf2.replace("/","\\")
                        
                        doc = fitz.open(pathpdf2)
                        idpdfs.append((idpdf, len(doc)))
                        try:
                            
                            try:
                                nameddests = grabNamedDestinations(doc)
                            except Exception as ex:
                                printlogexception(ex=ex)
                                nameddests = []
                            toc = doc.getToC(simple=False)
                            None
                            for entrada in toc:
                                #None
                                novotexto = ""
                                init = 0
                                tocunit = entrada[1]
                                #idpdf = None
                                pagina = None
                                deslocy = None
                                init = 0
                                if('page' in entrada[3]):
                                    #dictx = doc[entrada[3]['page']].getText("rawdict")
                                    pagina = entrada[3]['page'] 
                                    deslocy = entrada[3]['to'].y
                                elif('file' in entrada[3]):
                                    arquivocomdest = entrada[3]['file'].split("#")
                                    arquivo = arquivocomdest[0]
                                    dest = arquivocomdest[1]
                                    if(os.path.basename(pathpdf2)==arquivo):
                                        for sec in nameddests:
                                            if(dest==sec[0]):
                                                pagina = int(sec[1])
                                                deslocy = pixorg.height-round(float(sec[3]))
                                                break
                                if(pagina==None):
                                    None
                                    continue
                                #None
                                #None
                                dictx = doc[pagina].getText("rawdict")
                                parar = False
                                for block in dictx['blocks']:
                                    bboxb = block['bbox']
                                    if(bboxb[1]>deslocy or parar):
                                        break  
                                    if('lines' in block):
                                        for line in block['lines']:
                                            bboxl = line['bbox']
                                            #if(bboxl[2]>deslocy or parar):
                                            #    parar = True
                                            #    break
                                            for span in line['spans']:
                                                for char in span['chars']:
                                                    bboxchar = char['bbox']
                                                    bboxxmedio = (bboxchar[0]+bboxchar[2])/2
                                                    bboxymedio = (bboxchar[1]+bboxchar[3])/2
                                                    if(bboxxmedio < mmtopxleft or bboxxmedio > mmtopxright or bboxymedio < mmtopxtop or bboxymedio > mmtopxbottom):
                                                        continue
                                                    char = char['c']
                                                    #codePoint = ord(char)
                                                    #if(codePoint<256):
                                                    #    codePoint += lowerCodeNoDiff[codePoint]
                                                    novotexto += char
                                                    init += 1
                                                #if(len(novotexto) > 0 and novotexto[-1]!=' '):
                                                #    novotexto += ' '
                                            if(len(novotexto) > 0 and novotexto[-1]!=' '):
                                                novotexto += ' '
                                                init += 1
                                        if(len(novotexto) > 0 and novotexto[-1]!=' '):
                                            novotexto += ' '
                                            init += 1
                                
                                                
                                                
                                                
                                None
                                insert_query_toc = """INSERT INTO Anexo_Eletronico_Tocs
                                        (toc_unit, id_pdf , pagina, deslocy, init) VALUES
                                        (?,?,?,?,?)
                                """
                                
                                cursor.execute(insert_query_toc, (entrada[1], idpdf, pagina, deslocy, init,))
                                
                                
                                
                        except Exception as ex:
                            printlogexception(ex=ex)
                            None
                            sys.exit(1)
                        finally:
                            None
                            #doc.close()
                        
                        
                        
                        if(view!=None):
                            try:
                                if(not view.dirs.exists(str(relpdir))):
                                    view.dirs.insert('', index='end', iid=str(relpdir), text=str(relpdir), values=("","","","","","","",""))
                            except Exception as ex:
                                None
                                printlogexception(ex=ex)
                                None
                            try:
                                relative_path = os.path.relpath(pathpdf2, relpdir)
                                view.dirs.insert(relpdir, index='end', iid=str(relp), text=str(relp), values=(idpdf,"0%","-","-","-", "-", tipo, pathpdf2))
                                view.dirs.see(str(relp))
                            except Exception as ex:
                                None
                                printlogexception(ex=ex)  
                                None
            sqliteconn.commit()

        except Exception as ex:
            printlogexception(ex=ex)
        finally:
            cursor.close()
            if(sqliteconn):
                sqliteconn.close()
    return idpdfs

def connectDB(dbpath, timeout, maxrepeat=5):
    hasconn = False
    repeat = 0
    while(repeat < maxrepeat or maxrepeat==-1):
        try:
            sqliteconn = sqlite3.connect(str(dbpath), timeout=timeout)
            hasconn = True
            return sqliteconn
        except Exception as ex:
            printlogexception(ex=ex)
            repeat += 1
            None
    return None    


def popupcomandocancel(window):
    global marginsok

    marginsok = False

    window.destroy()
    
def popupcomandook(window, datatop, databottom, dataleft, dataright):
    global marginsok, mt, mb, me, md

    marginsok = True
    mt = datatop.get()
    mb = databottom.get()
    me = dataleft.get()
    md = dataright.get()
    window.destroy()

def defineMargins(window, definirmargens, boolean):
    definirmargens[0] = boolean
    window.destroy()
        
def checkmargin(fotocanvas, prop, datatop, databottom, dataleft, dataright, button_ok, pixorg, margemimg, margempreimage):
    try:
        mmtopxtop = math.floor(datatop.get()/25.4*72)
        mmtopxbottom = math.ceil(pixorg.height-(databottom.get()/25.4*72))
        mmtopxleft = math.floor(dataleft.get()/25.4*72)
        mmtopxright = math.ceil(pixorg.width-(dataright.get()/25.4*72))
        if(mmtopxbottom>=0 and mmtopxbottom> mmtopxtop and
            mmtopxright>=0 and mmtopxright > mmtopxleft):
            fotocanvas.delete("margem")
            x0k = math.floor(mmtopxleft/prop)
            y0k = math.floor(mmtopxtop/prop)
            x1k = math.ceil(mmtopxright/prop)
            y1k =  math.ceil(mmtopxbottom/prop)
            margemimg[0] = create_rectanglex(x0k, y0k, x1k, y1k, (21, 71, 150, 85))
            margempreimage[0] = fotocanvas.create_image(x0k, y0k, image=margemimg[0], anchor='nw', tags=("margem"))
            button_ok.config(relief='raised', state='active')
        else:
            #None
            button_ok.config(relief='sunken', state='disabled')
    except Exception as ex:
        button_ok.config(relief='sunken', state='disabled')
    
def setMargin(window, pdf):
    global docimg
    
    #pathpdf = Path(pdf)
    window.geometry("800x640")
    window.rowconfigure(1, weight=1)
    window.columnconfigure(0, weight=1)
    prop = 1.5
    loadedpage = pdf[math.floor(len(pdf)/prop)]
    pixorg = loadedpage.getPixmap()
    
    #72pixels = 1 inch = 25,4mm
    inch = 2.54
    
    ajustar = tkinter.Frame(window, borderwidth=2, bg='white', relief='ridge')
    ajustar.grid(row=0, column=0, sticky='nsew')
    ajustar.rowconfigure(0, weight=1)
    ajustar.columnconfigure((0,1,2,3,4,5,6,7), weight=1)
    datatop = tkinter.IntVar()
    databottom = tkinter.IntVar()
    dataleft = tkinter.IntVar()
    dataright = tkinter.IntVar()
    
    datatop.set(math.floor(115/72 * 25.4))     
    databottom.set(max(0, math.floor((pixorg.height-813)/72 * 25.4)))
    dataleft.set(30)       
    dataright.set(10)
    
    

    
    top = tkinter.Label(ajustar, text='Superior (mm): ')
    top.grid(row=0, column=0, sticky='e')
    entrytop = tkinter.Entry(ajustar, textvariable=datatop)
    entrytop.grid(row=0, column=1, sticky='nsw')
    bottom = tkinter.Label(ajustar, text='Inferior (mm): ')
    bottom.grid(row=0, column=2, sticky='e')
    entrybottom = tkinter.Entry(ajustar, textvariable=databottom)
    entrybottom.grid(row=0, column=3, sticky='nsw')
    left = tkinter.Label(ajustar, text='Esquerda (mm): ')
    left.grid(row=0, column=4, sticky='e')
    entryleft = tkinter.Entry(ajustar, textvariable=dataleft)
    entryleft.grid(row=0, column=5, sticky='nsw')
    right = tkinter.Label(ajustar, text='Direita (mm): ')
    right.grid(row=0, column=6, sticky='e')
    entryright = tkinter.Entry(ajustar, textvariable=dataright)
    entryright.grid(row=0, column=7, sticky='nsw')
    
    fotodoc = tkinter.Frame(window, borderwidth=2, relief='ridge')
    fotodoc.grid(row=1, column=0, sticky='nsew')
    fotodoc.rowconfigure(0, weight=1)
    fotodoc.columnconfigure(0, weight=1)
    fotocanvas = tkinter.Canvas(fotodoc, bg='gray', highlightthickness=0, relief="raised")
    fotocanvas.grid(row=0, column=0, sticky='nsew')
    mat = fitz.Matrix(1/prop, 1/prop)
    pix = loadedpage.getPixmap(alpha=False, matrix=mat) 
    imgdata = pix.getImageData("ppm")
    docimg = tkinter.PhotoImage(data = imgdata)
    
    docvanvas = fotocanvas.create_image((0,0), anchor='nw', image=docimg)
    
    
    bottomframe = tkinter.Frame(window, borderwidth=2, relief='ridge')
    bottomframe.grid(row=2, column=0, sticky='nsew')
    bottomframe.rowconfigure(0, weight=1)
    bottomframe.columnconfigure((0,1), weight=1)
    button_ok = tkinter.Button(bottomframe, text="OK", command= lambda : popupcomandook(window, datatop, databottom, dataleft, dataright))
    button_ok.grid(row=0, column=0, sticky='ns', pady=5)
    button_cancel = tkinter.Button(bottomframe, text="Cancelar", command= lambda : popupcomandocancel(window))
    button_cancel.grid(row=0, column=1, sticky='ns', pady=5)
    
    
    mmtopxtop = math.floor(datatop.get()/25.4*72)
    mmtopxbottom = math.ceil(max(0, pixorg.height-(databottom.get()/25.4*72)))
    mmtopxleft = math.floor(dataleft.get()/25.4*72)
    mmtopxright = math.ceil(pixorg.width-(dataright.get()/25.4*72))
    x0k = math.floor(mmtopxleft/prop)
    y0k = math.floor(mmtopxtop/prop)
    x1k = math.ceil(mmtopxright/prop)
    y1k =  math.ceil(mmtopxbottom/prop)
    margemimg = [create_rectanglex(x0k, y0k, x1k, y1k, (21, 71, 150, 85))]
    margempreimage = [fotocanvas.create_image(x0k, y0k, image=margemimg[0], anchor='nw', tags=("margem"))]
    dataleft.trace_add("write", lambda *args: checkmargin(fotocanvas, prop, datatop, databottom, dataleft, dataright, button_ok, pixorg, margemimg, margempreimage))
    databottom.trace_add("write", lambda *args : checkmargin(fotocanvas, prop, datatop, databottom, dataleft, dataright, button_ok, pixorg, margemimg, margempreimage))
    datatop.trace_add("write", lambda *args : checkmargin(fotocanvas, prop, datatop, databottom, dataleft, dataright, button_ok, pixorg, margemimg, margempreimage))
    dataright.trace_add("write", lambda *args : checkmargin(fotocanvas, prop, datatop, databottom, dataleft, dataright, button_ok, pixorg, margemimg, margempreimage))

'''            
def checkmargin(fotocanvas, prop, datatop, databottom, dataleft, dataright, button_ok, pixorg):
    global margemimg
    try:
        mmtopxtop = math.floor(datatop.get()/25.4*72)
        mmtopxbottom = math.ceil(pixorg.height-(databottom.get()/25.4*72))
        mmtopxleft = math.floor(dataleft.get()/25.4*72)
        mmtopxright = math.ceil(pixorg.width-(dataright.get()/25.4*72))
        if(mmtopxbottom>=0 and mmtopxbottom> mmtopxtop and
            mmtopxright>=0 and mmtopxright > mmtopxleft):
            fotocanvas.delete("margem")
            x0k = math.floor(mmtopxleft/prop)
            y0k = math.floor(mmtopxtop/prop)
            x1k = math.ceil(mmtopxright/prop)
            y1k =  math.ceil(mmtopxbottom/prop)
            margemimg = create_rectanglex(x0k, y0k, x1k, y1k, (21, 71, 150, 85))
            margempreimage = fotocanvas.create_image(x0k, y0k, image=margemimg, anchor='nw', tags=("margem"))
            #margempreimage.image = margemimg
            button_ok.config(relief='raised', state='active')
        else:
            #None
            button_ok.config(relief='sunken', state='disabled')
    except Exception as ex:
        button_ok.config(relief='sunken', state='disabled')                        
'''                
def create_rectanglex(x1, y1, x2, y2, color, **kwargs):
        
        image = Image.new('RGBA', (x2-x1, y2-y1), color)   
        return ImageTk.PhotoImage(image)

def showInfo(rootx, expertmodex, versionx, filein=None, f12Pressedx=None, pathdbext=None):
    global root, expertmode, pathdb, version, f12Pressed, pathpdfinput, clientmode, ok
    try:
        version = versionx
        pathdb = None
        if(pathdbext!=None):
            pathdb = Path(pathdbext)
        f12Pressed = f12Pressedx
        clientmode = False
        #pathpdfinput = pathpdfx
        pathpdfinput = None
        if(filein!=None):
            clientmode = True
            basename = os.path.basename(filein)
            file_name = os.path.splitext(basename)[0]
            fileinext = os.path.splitext(basename)[1]
            if(fileinext==".db"):
                pathdb = Path(filein)
            elif(fileinext==".pdf"):
                pathpdfinput = filein
        #if(pathpdf!=None):
           
        expertmode = expertmodex
        #if(rootx==None):
        #    rootx=tkinter.Tk()
        #root = rootx
        mp.freeze_support()
        
        go()
        
            
        #return root
    except Exception as ex:
        printlogexception(ex=ex)
        #return None
'''
if __name__ == '__main__':  
    mp.freeze_support()
    go()
  '''  