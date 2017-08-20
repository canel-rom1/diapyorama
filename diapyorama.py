#!/usr/bin/python3
# -*- encoding:Utf-8 -*-

from slideshow import Slideshow
from sq3 import Sql
import configuration

import sys
from tkinter import Tk

if __name__ == '__main__':
    dbfile = configuration.Settings.sqlite3_file
    root = Tk()

    dbsql = Sql(dbfile = dbfile)
    delays, images = dbsql.fetchDelaysImages()

    slideshow = Slideshow(master = root, images = images, delays = delays)
    slideshow.mainloop()



# vim: ft=python ts=8 et sw=4 sts=4
