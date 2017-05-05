#!/usr/bin/python3

from tkinter import *
from PIL import Image, ImageTk
import sqlite3

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



class ConfigSlidesFile(object):
    """
       Classant permettant de se connecter au fichier de configuration des diapositives

       entrée:
           < filename > = Nom et chemain du fichier 'string'
    """
    def __init__(self, filename):
        self.__filename = filename

    def read(self):
        """Retourner les valeurs contenues dans le fichier

           Sortie:
               < delays >: Délais de chaque diapositives [list]
               < links > : Liens pointant vers l'adresse de l'image [list]
        """
        delays = []
        links = []
        with open(self.__filename) as configFile:
            for line in configFile.readlines():
                if '#' in line:
                    continue
                vd, vl = line.split()
                delays.append(vd)
                links.append(vl)
        return delays, links

    def write(self, content):
        with open(self.__filename) as configFile:
            configFile.write(content)



class Slideshow(Frame):
    """
       Classe dérivée de Frame pour faire l'affichage du diaporama

       Entrée:
           < master >: Fenêtre principale (Défaut: None) 'string'
           < dbfile >: Fichier de connexion à la base de donnée Sqlite3 (Défaut: ./slides/slides.db) 'string'
    """
    def __init__(self, master = None, dbfile = './slides/slides.db'):
        Frame.__init__(self, master)

        self.__dbfile = dbfile

        self.bind_all('<Escape>', self.keyQuit)
        self.bind_all('<space>', self.keyPlayPause)
        self.bind_all('<F11>', self.keyFullscreenToggle)
        self.bind_all('<o>', self.keyOptionsMenu)
        self.bind_all('<u>', self.keyUpdate)

        #self.dbStart()
        self.fileConfig()
        self.fileRead()

        self.__slides = []                  # Initialisation de la liste contenant les diapositives
        self.loadSlides()

        self.label = Label(self)            # Création du Label pour afficher les diapositives
        self.label.pack()

        self.__play_loop = False            # Initialisation de la variable contrôlant la boucle de lecture
        self.__i_slide = 0                  # Initialisation du pointeur de la diapositive

        self.__win_opt_open = False          # Initialisation de la variable contrôlant l'activation de la fenêtre des options

        self.fullscreenOn()
        self.play()

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
        self.__delays, self.__links = self.db.sortedDelayLink()

    def dbUpdate(self):
        """Mise à jour de la base de donnée"""
        self.dbStart()


    #######
    ### Configuration File

    def fileConfig(self):
        self.__filename = './slides/slides.txt'
        self._openfile = ConfigSlidesFile(self.__filename)

    def fileRead(self):
        self.__delays, self.__links = self._openfile.read()

    def fileWrite(self, content):
        self._openfile.write(content)


    #######
    ### Managements modules

    def loadSlides(self):
        """Charger les diapositives dans la variable __slides"""
        for link  in self.__links:
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
        self.optMenu = OptionWin(self)

    def optionsMenuQuit(self):
        """Ferme la fenêtre du menu d'options"""
        self.optMenu.winQuit()


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
            self.__win_opt_open = False
            self.optionsMenuQuit()
        else:
            self.__win_opt_open = True
            self.optionsMenu()

    def keyUpdate(self, event):
        self.dbUpdate()



class OptionWin(Toplevel):
    def __init__(self, master = None):
        Toplevel.__init__(self, master)
        optSql = OptionsSql(self)
        optSql.pack()

    def winQuit(self):
        self.destroy()



class OptionsSql(Frame):
    def __init__(self, master = None):
        Frame.__init__(self, master)
        global dbfile
        fichier = dbfile
        self.sql = Sql(fichier)

        Label(self, text = 'Options Slite3 {}'.format(fichier)).pack()

        self.table()

    def table(self):
        tableau = self.sql.fetchAll()
        line = []
        for i in range(len(tableau)):
            varline[i] = StringVar()
            varline[i].set(tableau[i])
            line[i] = Entry(self, textvariable = varline[i])



def OptionsFile(Frame):
    def __init__(self, master = None):
        Frame.__init__(self, master)
        Label(self, text = "Fichier d'options")



if __name__ == '__main__':
    dbfile = './slides/slides.db'

    Slideshow(dbfile = dbfile).mainloop()


# vim: ft=python ts=8 et sw=4 sts=4
