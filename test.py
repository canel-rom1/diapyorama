#!/usr/bin/python3

from tkinter import *
from tkinter.ttk import Notebook
from tkinter.filedialog import askopenfilename
from PIL import Image, ImageTk
import sqlite3
from shutil import copy2
from os import listdir


class Sql(object):
    """
       Classe créant la connexion à la base de données Sqlite 3

       Entrée:
          < dbfile >: Fichier de connexion à la base de donnée 'string'
    """
    def __init__(self, dbfile):
        """Initialisation et connexion à la base de données"""

        self.table = 'slides'

        conn_db = sqlite3.connect(dbfile)
        with conn_db:
            self.cursor = conn_db.cursor()

    def sortedDelayLink(self):
        """
           Retourne les données des temps et les liens des diapositives. Ordre de la seq

           Sortie:
               < delays >: Délais de chaque diapositive
               < links > : Lien pointant vers l'adresse de l'image
        """
        self.cursor.execute('SELECT req, delay, link FROM slides')
        tab = self.cursor.fetchall()
        delay = [0]*len(tab)
        link = [0]*len(tab)
        for s, d, l in tab:
            delay[s-1] = d
            link[s-1] = l
        return delay, link

    def fetchDelayLink(self):
        """
           Retourne les données des temps et les liens des diapositives. Ordre de l'id

           Sortie:
               < delays >: Délais de chaque diapositives [list]
               < links > : Liens pointant vers l'adresse de l'image [list]
        """
        delays = []
        links = []
        self.cursor.execute('SELECT delay, link FROM slides')
        for slide in self.cursor.fetchall():
            delays.append(slide[1])
            links.append(slide[2])
        return delays, links

    def fetchAll(self):
        self.cursor.execute('SELECT * FROM slides')
        return self.cursor.fetchall()



class File(object):
    """
       Classant permettant de se connecter au fichier de configuration des diapositives

       entrée:
           < filename > = Nom du fichier [string]
    """
    def __init__(self, filename):
        self.__filename = filename

    def readRelaysNames(self):
        """Retourner les valeurs contenues dans le fichier

           Sortie:
               < delays >: Délais de chaque diapositives [list]
               < links > : Liens pointant vers l'adresse de l'image [list]
        """
        delays = []
        links = []
        with open(self.__filename, 'r') as f:
            for line in f.readlines():
                if line[0] == '#' or line[0] == '\n' or line[0] == ' ':
                    continue
                vd, vl = line.split()
                delays.append(vd)
                links.append(vl)
        return delays, links

    def readAll(self):
        with open(self.__filename, 'r') as f:
            return f.read()

    def write(self, content):
        with open(self.__filename, 'w') as f:
            f.write(content)



class Slideshow(Frame):
    """
       Classe dérivée de Frame pour faire l'affichage du diaporama

       Entrée:
           < master >: Fenêtre principale (Défaut: None) 'string'
           < dbfile >: Fichier de connexion à la base de donnée Sqlite3 (Défaut: ./slides/slides.db) 'string'
    """
    def __init__(self, master = None, dbfile = './slides.db'):
        Frame.__init__(self, master)
        self.master.title('Slideshow')

        self.__dbfile = dbfile
        self.__path_slides = './slides/'

        self.bind_all('<Escape>', self.keyQuit)
        self.bind_all('<space>', self.keyPlayPause)
        self.bind_all('<F11>', self.keyFullscreenToggle)
        self.bind_all('<o>', self.keyOptionsMenu)
        self.bind_all('<u>', self.keyBegin)

        self.label = Label(self)            # Création du Label pour afficher les diapositives
        self.label.pack()
        self.__play_loop = False            # Initialisation de la variable contrôlant la boucle de lecture
        self.__i_slide = 0                  # Initialisation du pointeur de la diapositive
        self.__win_opt_open = False          # Initialisation de la variable contrôlant l'activation de la fenêtre des options
        self.fullscreenOn()

        self.begin()
        #self.sortDelayLink()

        self.pack()


    def sortDelayLink(self):
        self.db = Sql(self.__dbfile)
        print(self.db.fetchData())
        #return delays, links


    #######
    ### SQL

    def dbStart(self):
        """Connexion à la base de donnée"""
        self.db = Sql(self.__dbfile)
        self.__delays, self.__names = self.db.sortedDelayLink()

    def dbUpdate(self):
        """Mise à jour de la base de donnée"""
        self.dbStart()


    #######
    ### Configuration File

    def fileConfig(self):
        filename = 'slides.txt'
        self._openfile = File(filename)

    def fileRead(self):
        self.__delays, self.__names = self._openfile.readRelaysNames()

    def fileWrite(self, content):
        self._openfile.write(content)


    #######
    ### Managements modules

    def loadSlides(self):
        """Charger les diapositives dans la variable __slides"""
        for name  in self.__names:
            link = self.__path_slides + name
            image = Image.open(link)
            slide = ImageTk.PhotoImage(image)
            self.__slides.append(slide)

    def loop(self):
        """Boucle de lecture du diaporama"""
        if self.__play_loop:
            if self.__i_slide >= len(self.__slides):
                self.__i_slide = 0
            self.label.config(image = self.__slides[self.__i_slide])
            self.after(self.__delays[self.__i_slide], self.loop)
            self.__i_slide += 1


    #######
    ### Slideshow actions

    def begin(self):
        """Charges les données du diaporama puis les jouer"""
        self.fileConfig()
        self.fileRead()

        self.__slides = []                  # Initialisation de la liste contenant les diapositives
        self.loadSlides()

        self.play()

    def play(self):
        """Jouer le diaporama"""
        if not self.__play_loop:
            self.__play_loop = True
            self.loop()

    def pause(self):
        """Mettre en pause le diaporama"""
        #if self.__play_loop:
        self.__play_loop = False


    def fullscreen(self):
        """Commande du mode pleine écran"""
        self.master.attributes("-fullscreen", self.__fullscreen_state)

    def fullscreenOn(self):
        """Active le mode pleine écran"""
        self.__fullscreen_state = True
        self.fullscreen()

    def fullscreenOff(self):
        """Désactive le mode pleine écran"""
        self.__fullscreen_state = False
        self.fullscreen()

    def fullscreenToggle(self):
        """Inverse le mode pleine écran"""
        if self.__fullscreen_state:
            self.fullscreenOff()
            self.__fullscreen_state = False
        else:
            self.fullscreenOn()
            self.__fullscreen_state = True


    #######
    ### Options

    def optionsMenu(self):
        """Instancie la fenêtre du menu d'options"""
        self.__win_opt_open = True
        self.optMenu = OptionsWin(self)

    def optionsMenuQuit(self):
        """Ferme la fenêtre du menu d'options et charger les nouvelles données"""
        self.__win_opt_open = False
        self.optMenu.destroy()
        self.fileRead()


    #######
    ### Keys actions

    def keyQuit(self,event):
        """Touche clavier pour quitter"""
        self.master.destroy()

    def keyFullscreenToggle(self, event):
        """Touche clavier pour inverser le mode pleine écran"""
        self.fullscreenToggle()

    def keyPlayPause(self, event):
        """Touche Play/Pause"""
        if self.__play_loop:
            self.pause()
        else:
            self.play()

    def keyOptionsMenu(self, event):
        """Touche pour activer la fenêtre d'option"""
        if self.__win_opt_open:
            self.optionsMenuQuit()
        else:
            self.optionsMenu()

    def keyUpdate(self, event):
        self.dbUpdate()
        self.__command(index)

    def keyBegin(self, event):
        self.begin()



class OptionsWin(Toplevel):
    def __init__(self, master = None):
        Toplevel.__init__(self, master)
        self.title('Options')

        tabs_bar = Notebook(self)
        tabs_bar.pack(side = 'top', expand = 'yes')

        tab1 = SlidesFrame(self)
        tab2 = FileFrame(self)
        tab3 = SqlFrame(self)

        tabs_bar.add(tab1, text = 'Slides')
        tabs_bar.add(tab2, text = 'File')
        #tabs_bar.add(tab3, text = 'SQL')

    def winQuit(self):
        self.master.optionsMenuQuit()



class SqlFrame(Frame):
    def __init__(self, master = None):
        Frame.__init__(self, master)
        global db_file
        f = db_file
        self.sql = Sql(f)

        Label(self, text = 'Options Sqlite3 {}'.format(f)).pack()

        #self.table()

    def table(self):
        tableau = self.sql.fetchAll()
        line = []
        for i in range(len(tableau)):
            varline[i] = StringVar()
            varline[i].set(tableau[i])
            line[i] = Entry(self, textvariable = varline[i])



class FileFrame(Frame):
    def __init__(self, master = None):
        Frame.__init__(self, master)

        global config_file
        f = config_file

        self.cf = File(f)

        Label(self, text = 'Options File').pack(side = 'top')
        self.txtArea = Text(self, height = 10, width = 60)
        self.txtArea.pack(side = 'top')
        Button(self, text = 'Enregistrer', command = self.save).pack(side = 'left')
        Button(self, text = 'Quitter', command = self.master.winQuit).pack(side = 'right')
        self.read()

    def read(self):
        self.txtArea.insert(0.0, self.cf.readAll())
        return

    def save(self):
        self.cf.write(self.txtArea.get(0.0, 'end'))



class SlidesFrame(Frame):
    def __init__(self, master = None):
        Frame.__init__(self, master)

        self.path_slides = './slides/'
        self.MasterFrame = None

        self.displayFrame()

    def displayFrame(self):
        if self.MasterFrame:
            print('destroy')
            self.MasterFrame.destroy()
        self.MasterFrame = Frame(self)
        Label(self.MasterFrame, text = 'Options slides').pack(side = 'top')
        self.pathSlides(self.MasterFrame, 'top')
        self.listSlides(self.MasterFrame, 'top')
        Button(self.MasterFrame, text = 'Add a slide', command = self.addSlides).pack(side = 'bottom')
        self.MasterFrame.pack()

    def pathSlides(self, master, side):
        pathSlidesFrame = Frame(master)
        Label(pathSlidesFrame, text = 'Slides path').pack(side = 'top')
        self.pathSlidesEntry = Entry(pathSlidesFrame, text = 'PATH')
        self.pathSlidesEntry.pack(side = 'left')
        self.pathSlidesButton = Button(pathSlidesFrame, text = 'Save path')
        self.pathSlidesButton.pack(side = 'right')
        pathSlidesFrame.pack(side = side)

    def addSlides(self):
        opts = {}
        opts['title'] = 'Add a slide'
        opts['filetypes'] = [('Supported types', ('.jpg', '.jpeg', '.JPG', '.JPEG', 'png')),
                             ('Image JPG', ('.jpg', '.jpeg', '.JPG', '.JPEG')),
                             ('Image PNG', '.png'),
                             ('All files', '.*')]
        openSlides = askopenfilename(**opts)
        copy2(openSlides, self.path_slides)
        self.displayFrame()

    def listSlides(self, master, side):
        list_slides = listdir(self.path_slides)
        list_slides.sort()
        listSlidesFrame = Frame(master)
        for slide in list_slides:
            Label(listSlidesFrame, text = slide).pack(side = 'top')
        listSlidesFrame.pack(side = side)


if __name__ == '__main__':
    db_file = './slides.db'
    config_file = './slides.txt'

    Slideshow(dbfile = db_file).mainloop()


# vim: ft=python ts=8 et sw=4 sts=4