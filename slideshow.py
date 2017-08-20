#!/usr/bin/python3
# -*- coding: Utf8 -*-

from tkinter import *
from PIL import Image, ImageTk
from winconf import ConfigWin
from configuration import Settings

class Slideshow(Frame):
    """
       Classe dérivée de Frame pour faire l'affichage du diaporama

       Entrée:
           < master >: Fenêtre principale (Défaut: None) 'string'
           < dbfile >: Fichier de connexion à la base de donnée Sqlite3 (Défaut: ./slides/slides.db) 'string'
    """
    def __init__(self, master = None, images = [], delays = []):
        Frame.__init__(self, master)
        self.master.title('Slideshow')

        self.__images, self.__delays = images, delays

        self.bind_all('<Escape>', self.keyQuit)
        self.bind_all('<space>', self.keyPlayPause)
        self.bind_all('<F11>', self.keyFullscreenToggle)
        self.bind_all('<o>', self.keyConfigMenu)

        self.label = Label(self)                                    # Création du Label pour afficher les diapositives
        self.label.pack()

        self.__play_loop = False                                    # Initialisation de la variable contrôlant la boucle de lecture
        self.__i_slide = 0                                          # Initialisation du pointeur de la diapositive
        self.__config_menu_open = False                             # Initialisation de la variable contrôlant l'activation de 
                                                                    #  la fenêtre de configuration
        self.fullscreenOn()

        if self.__images != []:
            self.loadSlides()
        else:
            self.label.config(text = 'No slides loaded',\
                              font = 'Helvetica 30 bold')

        self.play()

        self.pack()


    #######
    ### Managements modules

    def loadSlides(self):
        """Charger les diapositives dans la variable __slides"""
        self.__slides = []                                          # Initialisation de la liste contenant les diapositives
        for link  in self.__images:
            link = Settings.slides_path + '/' + link
            try:
                image = Image.open(link)
                slide = ImageTk.PhotoImage(image)
                self.__slides.append(slide)
            except FileNotFoundError as err:
                print("Impossible to load: %s" % err)

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
        if not self.__play_loop and self.__images != []:
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

    def configMenu(self):
        """Instancie la fenêtre du menu d'options"""
        self.__config_menu_open = True
        self.__play_loop = False
        self.configWin = ConfigWin(self)

    def configMenuQuit(self):
        """Ferme la fenêtre du menu d'options et charger les nouvelles données"""
        self.__config_menu_open = False
        self.configWin.destroy()
        self.loadSlides()
        if not self.__play_loop:
            self.play()


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

    def keyConfigMenu(self, event):
        """Touche pour activer la fenêtre d'option"""
        if self.__config_menu_open:
            self.configMenuQuit()
        else:
            self.configMenu()


# vim: ft=python ts=8 et sw=4 sts=4
