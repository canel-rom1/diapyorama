class Settings(object):
    """
    """
    slides_path  = "/home/diapy/slides"
    sqlite3_file = "/home/diapy/slideshow.sq3"

class Database(object):
    """
       Paramètre de la base de donnée.

       Output:
           < name >   : Nom de la base de données [str]
           < user >   : Utilisateur pour la connexion au serveur de la base de donnée [str]
           < passwd > : Mot de passe du server [str]
           < host >   : Adresse du serveur [str]
           < port >   : Port du serveur [int]


           < table_slides > : Nom de la table contenant les slides [str]
           < tables >       : Définition des tables [dic]
    """
    name   = 'slideshow'
    user   = 'slideshow'
    passwd = '1234'
    host   = '127.0.0.1'
    port   = 5432

    table_slides = 'slides'
    tables = {table_slides:[('id', 'k', 'Clé primaire'),            # Essayer de tous mettre dans un dictionnaire! A la json
                            ('pos', 'i', 'Position'),
                            ('img', 30, 'Nom du fichier'),
                            ('delay', 'i', 'Délai')]}

# vim: ft=python ts=8 et sw=4 sts=4
