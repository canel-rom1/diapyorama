#!/usr/bin/python3
# -*- coding: Utf8 -*-

from tkinter import *
from tkinter.ttk import Notebook
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import askokcancel
from shutil import copy2
from os import listdir
from os.path import basename
from sq3 import Sql
from configuration import Settings


class ConfigWin(Toplevel):
    def __init__(self, master = None):
        Toplevel.__init__(self, master)
        self.title('Options')

        tabs_bar = Notebook(self)
        tabs_bar.pack(side = 'top', expand = 'yes')

        tab1 = SlidesFrame(self)
        tab2 = SettingsFrame(self)
        tab3 = SqlQueryFrame(self)

        tabs_bar.add(tab1, text = 'Slides')
        tabs_bar.add(tab2, text = 'Settings')
        tabs_bar.add(tab3, text = 'SQL Query')

    def winQuit(self):
        self.master.optionsMenuQuit()


class SlidesFrame(Frame):
    def __init__(self, master = None):
        Frame.__init__(self, master)

        self.path_slides = Settings.slides_path
        self.MasterFrame = None                                     # if not None destroy the frame

        self.Sql = Sql(Settings.sqlite3_file)

        self.id_slide_select = None

        self.posVarTk = StringVar()
        self.imageVarTk = StringVar()
        self.delayVarTk = StringVar()

        self.displayFrame()

    def displayFrame(self):
        if self.MasterFrame:                                        # Refresh window
            self.MasterFrame.destroy()
        self.MasterFrame = Frame(self)
        Label(self.MasterFrame, text = 'Options slides').pack(side = 'top')
        #self.pathSlides(self.MasterFrame, 'top')
        self.listSlides(self.MasterFrame, 'top')
        #Button(self.MasterFrame, text = 'Add a slide', command = self.addSlides).pack(side = 'bottom')
        self.MasterFrame.pack()

    def listSlides(self, master = None, side = 'top'):
        listSlidesFrame = Frame(master)
        nb_slides = 0
        for i, header in enumerate(self.Sql.fetchSlideHeaders()[1:4]):
            Label(listSlidesFrame, text = header).grid(row = 1, column = i)
        for i, slide in enumerate(self.Sql.fetchSlides()):
            for column in range(1, 4):
                Label(listSlidesFrame, text = slide[column]).grid(row = i + 2, column = column-1)
            Button(listSlidesFrame, text = 'Modify', command = lambda arg = slide[0]: self.modifySlide(arg)) \
            .grid(row = i + 2, column = 3)
            Button(listSlidesFrame, text = 'Delete', command = lambda arg = slide[0]: self.deleteSlide(arg)) \
            .grid(row = i + 2, column = 4)
            nb_slides += 1

        # Entry zone for modify a slide
        self.posEntry = Entry(listSlidesFrame)
        self.posEntry.grid(row = nb_slides + 2, column = 0)
        self.imageEntry = Entry(listSlidesFrame)
        self.imageEntry.grid(row = nb_slides + 2, column = 1)
        self.delayEntry = Entry(listSlidesFrame)
        self.delayEntry.grid(row = nb_slides + 2, column = 2)
        Button(listSlidesFrame, text = 'Save', command = self.saveSlide) \
        .grid(row = nb_slides + 2, column = 3, columnspan = 2)
        # Add a slide
        Button(listSlidesFrame, text = 'Add', command = self.addSlide) \
        .grid(row = 1, column = 3, columnspan = 2)

        listSlidesFrame.pack(side = side)

    def deleteSlide(self, id_slide):
        opts = {}
        opts['title'] = 'Delete'
        opts['message'] = ' Do you want delete this slide: %s' % id_slide
        sel = askokcancel(**opts)
        if sel == True:
            self.Sql.deleteSlide(id_slide)
            self.Sql.commitData()
            self.displayFrame()

    def modifySlide(self, id_slide):
        list_slide = self.Sql.fetchSlide(id_slide)
        self.id_slide_select = id_slide
        self.posEntry.delete(0, 'end')
        self.posEntry.insert('end', str(list_slide[1]))
        self.imageEntry.delete(0, 'end')
        self.imageEntry.insert('end', str(list_slide[2]))
        self.delayEntry.delete(0, 'end')
        self.delayEntry.insert('end', str(list_slide[3]))

    def saveSlide(self):
        self.Sql.updateSlide(self.id_slide_select,
                             self.posEntry.get(),
                             self.imageEntry.get(),
                             self.delayEntry.get())
        self.displayFrame()

    def addSlide(self):
        opts = {}
        opts['title'] = 'Add a slide'
        opts['filetypes'] = [('Supported types', ('.jpg', '.jpeg', '.JPG', '.JPEG', 'png')),
                             ('Image JPG', ('.jpg', '.jpeg', '.JPG', '.JPEG')),
                             ('Image PNG', '.png'),
                             ('All files', '.*')]
        openSlides = askopenfilename(**opts)
        copy2(openSlides, self.path_slides)
        self.Sql.addSlide(int(self.Sql.nbSlides()) + 1, basename(openSlides), 1000)
        self.displayFrame()


class SettingsFrame(Frame):
    def __init__(self, master = None):
        Frame.__init__(self, master)
        Label(self, text = 'Options Sqlite3')

        self.__slides_path  = StringVar()
        self.__sqlite3_file = StringVar()

        self.readConfig()
        self.pathSlides()
        self.sqlite3File()
        self.buttons()

    def readConfig(self):
        self.__slides_path.set(Settings.slides_path)
        self.__sqlite3_file.set(Settings.sqlite3_file)

    def writeConfig(self):
        Settings.slides_path  = self.__slides_path.get()
        Settings.sqlite3_file = self.__sqlite3_file.get()

    def pathSlides(self, master = None, side = 'top'):
        pathSlidesFrame = Frame(self)
        Label(pathSlidesFrame, text = 'Slides path').pack(side = 'left')
        Entry(pathSlidesFrame, textvariable = self.__slides_path, width = 50).pack(side = 'right')
        pathSlidesFrame.pack(side = side)

    def sqlite3File(self, master = None, side = 'top'):
        sqlite3FileFrame = Frame(self)
        Label(sqlite3FileFrame, text = 'Sqlite3 file').pack(side = 'left')
        Entry(sqlite3FileFrame, textvariable = self.__sqlite3_file, width = 50).pack(side = 'right')
        sqlite3FileFrame.pack(side = side)

    def buttons(self, side = 'bottom'):
        buttonsFrame = Frame(self)
        Button(buttonsFrame, text = 'save', command = self.writeConfig).pack(side = 'right')
        buttonsFrame.pack(side = side)


class SqlQueryFrame(Frame):
    def __init__(self, master = None):
        Frame.__init__(self, master)

        self.__query = StringVar()
        self.__data = ''

        self.printData()
        self.queryFrame(self, 'bottom', width = 40)

    def queryFrame(self, master, side, width = 30):
        queryFrame = Frame(master)
        Entry(queryFrame, textvariable = self.__query, width = width).pack(side = 'left')
        Button(queryFrame, text = 'Exec', command = self.execSqlQuery).pack(side = 'right')
        queryFrame.pack(side = side)

    def execSqlQuery(self):
        self.__data = self.__query.get()
        self.printData()

    def printData(self):
        Label(self, text = self.__data).pack(side = 'top')


if __name__ == '__main__':
#    dbfile = './slideshow.sq3'
#    config_file = './slides.txt'
#
#    openfile = File(config_file)
#
#    slides_delays, slides_names = openfile.readDelaysNames()
#
#    Slideshow(names = slides_names, delays = slides_delays).mainloop()
    win = ConfigWin()
    win.mainloop()


# vim: ft=python ts=8 et sw=4 sts=4
