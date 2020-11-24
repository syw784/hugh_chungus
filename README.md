# hugh_chungus
a hugh SQLite chungus for all your chunguses.

requuires:
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlQueryModel, QSqlTableModel
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal, Qt
import time, json, os, random, subprocess
from vert_diag import VertTextDiag
from mangatable import PotTableRightClick
from datetime import datetime as dtinthehouse
import hashlib

Q:why am I using this?

great question. Think of it as a redundant potplayer playlist app where updating it is a tiny bit easier. Why? well someone's gotta take care of all the linux distros;)

how does it work:

this is the main app page:

![Chungus](https://github.com/syw784/hugh_chungus/raw/main/chuguus/chungus1.PNG)

you can click on task to add paths to be scanned to the chungus database, or start to scan:

![Chungus](https://github.com/syw784/hugh_chungus/raw/main/chuguus/chungus2.PNG)

by add, you can click add to add more entries, or empty them to ignore

![Chungus](https://github.com/syw784/hugh_chungus/blob/main/chuguus/chungus3.PNG)


once scanned, you'll see something like this in the main app page.

![Chungus](https://github.com/syw784/hugh_chungus/raw/main/chuguus/chungus1.PNG)

just double-click on an entry to open potplayer with that file in play; a playlist with all the queried items will be created. toggle "random" to randomize the playlist.

you can type something to search the db in the field left to the "query" button; two built in queries are shown, one to list by time, one to show duplicates by size

![Chungus](https://github.com/syw784/hugh_chungus/raw/main/chuguus/chugus4.PNG)
