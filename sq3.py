#!/usr/bin/python3
# -*- coding: Utf8 -*-

import sqlite3
from configuration import Database as Config
from configuration import Settings


class Sql(object):
    """
       Classe créant la connexion à la base de données Sqlite 3

       Entrée:
          < dbfile >: Fichier de connexion à la base de donnée [str]
    """
    def __init__(self, dbfile):
        """
        Constructeur: initialisation et connexion à la base de données
        """
        # Charge les paramètres de la base de données contenu dans le fichier db.py
        self.config = Config()
        # Charge le nom de la table des slides
        self.table_slides = self.config.table_slides

        # Connection à la base de données Sqlite3
        self.connection = sqlite3.connect(dbfile)
        self.cursor = self.connection.cursor()

        # Contrôle si la table est paramétrée
        if self.checkTablesExists() == False:
            self.createTables()

    def __del__(self):
        """
           Destructeur: Ferme le curseur et déconnecte la base de données
        """
        self.cursor.close()
        self.connection.close()

    def checkTablesExists(self):
        """
           Teste si la table est créee.

           Output:
               True or False: Si la table existe ou pas [Bool]
        """
        req = "SELECT name FROM sqlite_master WHERE type='table' AND name='%s'" % self.table_slides
        self.executeData(req)
        if self.cursor.fetchall() == []:
            return False
        return True

    def createTables(self):
        """
           Créer la table pour le diaporama.
        """
        dicoTables = self.config.tables
        for table in list(dicoTables.keys()):
            req = 'CREATE TABLE %s (' % table
            for fields in dicoTables[table]:
                name_field = fields[0]
                type_field = fields[1]
                if type_field == 'k':
                    typeF = 'integer primary key'
                elif type_field == 'i':
                    typeF = 'INTEGER'
                else:
                    typeF = 'VARCHAR(%s)' % type_field
                req += '%s %s, ' % (name_field, typeF)              # Meilleur solution?? (Faille de sécurité à corriger)
            req = req[:-2] + ');'
            self.executeData(req)
        self.commitData()

    def deleteTables(self):
        """
           Supprimer les tables
        """
        for table in list(self.config.tables.keys()):
            req = 'DROP TABLE %s' % table
            self.cursor.execute(req)
        self.connection.commit()

    def addData(self, tup_data):
        """
           Ajouter un slide

           Input:
               < données > :  [tuple]
        """
        table = self.table_slides
        table_slides = self.config.tables[table]

        req = 'INSERT INTO %s(' % (table)
        for fields in table_slides:
            name_field = fields[0]
            type_field = fields[1]
            if not type_field == 'k':
                req += '%s, ' % name_field
        req = req[:-2] + ') '
        req += 'VALUES(?, ?, ?);'
        self.executeData(req, tup_data)
        self.commitData()

    def deleteData(self, id_slide):
        """
           Supprimer un slide
           Input:
               < id > : Identifant du slide [int]
        """
        req  = 'DELETE FROM %s ' % self.table_slides
        req += "WHERE %s=%s;" % ('id', id_slide)

        self.executeData(req)

    def updateData(self, id_slide, tup_data):
        """
           Mettre à jour une entrée de la tables Slide en fonction de l'id reçu.

           Input:
               < id_slide >  ; Clé du slides
               < list_data > : Champs modifié [tuple]
                                    |->  <pos>
                                    |->  <name>
                                    `->  <delay>
        """
        table = self.table_slides
        table_slides = self.config.tables[table]
        key = self.config.tables[table][0][0]

        req = 'UPDATE %s SET ' % table
        for i in range(1, len(table_slides)):
            req += '%s=?, ' % table_slides[i][0]
        req = req[:-2] + "WHERE %s='%s'" % (key, id_slide)

        self.executeData(req, tup_data)
        self.commitData()

    def fetchSlideHeaders(self):
        """
           Récupérer les en-tête des données contenuent dans la table slides

           Ouput:
               < headers > : Liste des en-têtes [list]
        """
        headers = []
        for header in self.config.tables[self.table_slides]:
            headers.append(header[2])
        return headers

    def fetchSlides(self):
        """
           Récupérer les données des slides

           Output:
               < fetchall > : Contenu de toute la table slides [list]
        """
        table = self.table_slides
        field_sort = self.config.tables[table][1][0]

        req = 'SELECT * FROM %s ORDER BY %s;' % (table, field_sort)
        self.executeData(req)

        return self.cursor.fetchall()

    def fetchSlide(self, id_slide):
        """
        """
        req = 'SELECT * FROM %s ' % self.table_slides
        req += 'WHERE id=%s' % id_slide

        self.executeData(req)

        return self.cursor.fetchone()

    def fetchDelaysImages(self):
        """
           Retourne les données des temps et les liens des diapositives. Order
           par position.
           )
           Sortie:
               < delays >: Délais entre chaque diapositives [list]
               < images > : Noms des images des diapositive [list]
        """
        table = self.table_slides
        delay = self.config.tables[table][3][0]
        name = self.config.tables[table][2][0]
        field_sort = self.config.tables[table][1][0]

        req  = 'SELECT %s, %s ' % (delay, name)
        req += 'FROM %s ' % table
        req += 'ORDER BY %s;' % field_sort

        self.executeData(req, error = 'No silde(s) in the table')

        delays = []
        images = []
        for slide in self.cursor.fetchall():
            delays.append(slide[0])
            images.append(slide[1])

        return delays, images

    def sortSlides(self, start, end = None, orient = 'up'):
        table = self.table_slides
        field_sort = self.config.tables[table][1][0]
        # Si il n'y a pas de borne limite finale prendre la valeur max dans la table 
        if end == None:
            req = 'SELECT MAX(%s) FROM %s' % (field_sort, table)
            self.executeData(req)
            end = self.cursor.fetchone()[0]
        # Modifie les champs les un après les autres.
        req = 'UPDATE %s ' % table
        req += 'SET %s=? ' % field_sort
        req += 'WHERE %s=?;' % field_sort
        if orient == 'up':
            for i in reversed(range(int(start), int(end) + 1)):
                self.executeData(req, (i + 1, i))
        elif orient == 'down':
            for i in range(int(start), int(end) + 1):
                self.executeData(req, (i - 1, i))
        else:
            print('Orient error')
            return
        self.commitData()

    def addSlide(self, position, image, delay):
        """
           Ajouter un slide dans la base de données et mettre à jour la séquence des slides
        """
        self.sortSlides(position, orient = 'up')
        self.addData((position, image, delay))                           # Il faut passer les donnée via un tuple

    def deleteSlide(self, id_slide):
        self.deleteData(id_slide)
        self.sortSlides(id_slide + 1, orient = 'down')

    def updateSlide(self, id_slide, position, image, delay):
        table = self.table_slides
        field_id = self.config.tables[table][0][0]
        field_pos = self.config.tables[table][1][0]
        # Récupérer la position initiale du slide
        req = "SELECT %s FROM %s WHERE %s=%s;" % (field_pos, table, field_id, id_slide)
        self.executeData(req)
        pos_id_slide = self.cursor.fetchone()[0]
        # Si la position ne change pas, il faut garder les slides sans l'ordre
        if pos_id_slide == position:
            self.updateData(id_slide, (position, image, delay))
        # Si la nouvelle position est différent, il faut réorganiser l'ordres de positions
        else:
            self.updateData(id_slide, (0, image, delay))
            self.sortSlides(pos_id_slide + 1, orient = 'down')
            self.sortSlides(position, orient = 'up')
            self.updateData(id_slide, (position, image, delay))

    def nbSlides(self):
        """
           Retourne le nombre de slides dans la base de donnée.
        """
        req = "SELECT COUNT(*) FROM %s" % self.table_slides
        self.executeData(req)
        return self.cursor.fetchone()[0]


    def executeData(self, req, tup_arg = None, error = None):
        """
        """
        try:
            if tup_arg == None:
                self.cursor.execute(req)
            else:
                self.cursor.execute(req, tup_arg)
        except Exception as e:
            print('SQL error:\n%s' % e)
            if error != None:
                print('Script error: %s' % error)

    def commitData(self):
        """
        """
        self.connection.commit()




if __name__ == '__main__':
    database = Sql(Settings.sqlite3_file)
    print(Settings.sqlite3_file)
    print(database.fetchDelaysImages())
    #database.deleteTables()
    #database.createTables()
    #database.addData(('6', 'img10.png', '2000'))
    #database.addSlide('6', 'img15.png', '1500')
    #database.addSlide('3', 'img20.png', '1000')
    #database.addSlide('4', 'img25.png', '1500')
    #database.addSlide('5', 'img35.png', '2000')
    #database.addSlide('5', 'img35.png', '2000')
    #database.addSlide('5', 'img35.png', '2000')
    #print(database.fetchSlides())
    #database.updateSlide(['6', '8', 'img100.png', '3000'])
    #print(database.fetchSlides())
    #print(database.fetchSlide(3))
    #database.deleteSlide(5)
    #database.sortSlides(3, orient = 'up')
    print(database.fetchSlides())
    #database.updateData(1, (1, 'img11.png', 1000))
    #database.updateData(2, (2, 'img12.png', 2000))
    #database.updateData(3, (3, 'img13.png', 3000))
    #database.updateData(4, (4, 'img14.png', 4000))
    #database.updateData(5, (5, 'img15.png', 5000))
    #database.updateData(6, (6, 'img16.png', 6000))
    #database.updateData(7, (7, 'img17.png', 7000))
    #database.updateData(7, (7, 'img17.png', 7000))
    #print(database.fetchSlides())
    #database.updateSlide(2, 5, 'img55.png', 1600)
    #print(database.fetchSlides())
    print(database.nbSlides())


# vim: ft=python ts=8 et sw=4 sts=4
