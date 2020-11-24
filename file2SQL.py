from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlQueryModel, QSqlTableModel
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal, Qt
import time, json, os, random, subprocess
from vert_diag import VertTextDiag
from mangatable import PotTableRightClick
from datetime import datetime as dtinthehouse
import hashlib

def md5(fname, size = 4096):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(size), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def filesize(fname):
    return os.path.getsize(fname)

class Count_Query(QSqlQuery):
    
    def counts(self):
        a = self.at()
        self.last()
        r = self.at() + 1
        self.seek(a)
        return r

    def printf(self):
        r = []
        for i in range(self.record().count()):
            r.append(self.value(i))
        return r

def make_potplayer_playlist(list, play = None):
    f = open("playlist.dpl", mode = "w", encoding = 'UTF-8')
    f.write("DAUMPLAYLIST\n")
    if play:
        f.write('playname={}\n'.format(play))
        f.write('playtime=0\n')
    i = 1
    f.write('topindex=0\n')
    for j in list:
        f.write('{}*file*{}\n'.format(i, j))
        f.write('{}*played*0\n'.format(i))
        i += 1
    f.close()
    #subprocess.call([r'C:\Program Files\DAUM\PotPlayer\potplayermini64.exe', r'{}\playlist.dpl'.format(os.getcwd())], shell = True)
    #os.system(r'"C:\Program Files\DAUM\PotPlayer\potplayermini64.exe" {}\playlist.dpl'.format(os.getcwd()))

class File2SQLThread(QThread):
    
    progressbar_update = pyqtSignal(int)
    tableview_refresh  = pyqtSignal()
    log_update  = pyqtSignal(str)
    
    MEDIA_PATH_SQL_COL = [
        ['name', 'varchar'],
        ['path', 'varchar NOT NULL UNIQUE'],
        ['size', 'INT'],
        ['ctime', 'datetime']
    ]

    DEDUP_SQL_COL = [
        ['path', 'TEXT'],
        ['size', 'INT'],
        ['key1', 'TEXT'],
        ['key2', 'TEXT'],
    ]
#self.query.exec('CREATE TABLE "dedup" ("path" TEXT, "size" INTEGER, "key1" TEXT, "key2" TEXT) ')
    CREATE_DEDUP_SQL_QUERY = 'CREATE TABLE "dedup" ('
    for i in DEDUP_SQL_COL:
        CREATE_DEDUP_SQL_QUERY += '"{}" {}, '.format(i[0], i[1])
    CREATE_DEDUP_SQL_QUERY += 'PRIMARY KEY("path"));'

    SELECT_MEDIA_PATH_SQL = 'SELECT * FROM media_path '#INNER JOIN visible ON visible.
    MEDIA_PATH_SQL_COL_NUM = {}

    j = 0
    for i in MEDIA_PATH_SQL_COL:
        MEDIA_PATH_SQL_COL_NUM[i[0]] = j
        j += 1
        
    MEDIA_PATH_INSERT = 'INSERT INTO media_path(name, path, size, ctime) VALUES ("{}", "{}", {}, datetime("{}")) '

    ACCEPTED_EXT = [
        #'.',
        '.mp3',
        '.mkv',
        '.mp4',
        '.wav',
        '.webm',
    ]

    def __init__(self, param):
        QThread.__init__(self)
        self.start_db()
        self.query = Count_Query(self.database())
        self.create_db()
        self.param = param
        self.runType = None

    def start_db(self):
        QSqlDatabase.addDatabase('QSQLITE', 'media').setDatabaseName('chungus.db')
        if not QSqlDatabase.database('media').open():
            QSqlDatabase.addDatabase('QSQLITE', 'media').setDatabaseName(':memory:')
            QSqlDatabase.database('media').open()

    def database(self):
        return QSqlDatabase.database('media')

    def create_db(self):
        self.query.exec(self.CREATE_DEDUP_SQL_QUERY)
        self.query.exec('CREATE TABLE "path_tags" (path VARCAHR, class VARCHAR, value VARCHAR);')
        s = 'CREATE TABLE "media_path" ('
        for i in self.MEDIA_PATH_SQL_COL:
           s += ' "{}" {},'.format(i[0], i[1])
        self.query.exec(s + ' PRIMARY KEY("path"));')

    def scan_db(self):
        self.query.exec('BEGIN;')
        orgpath = os.getcwd()
        self.clean_db()
        for path in self.param['gallery_path']:  
            self.scan_directory(path)
        self.query.exec('COMMIT;')
        os.chdir(orgpath)
        self.tableview_refresh.emit()

    def clean_db(self):
        self.query.exec(self.SELECT_MEDIA_PATH_SQL)
        self.query.first()
        tot = self.query.counts()
        prog = 0
        r = []
        while self.query.isValid():
            prog += 1
            self.progressbar_update.emit(int(prog * 100 / tot))
            a = self.query.value(self.MEDIA_PATH_SQL_COL_NUM['path'])
            try:
                os.path.isfile(a)
                for path in self.param['gallery_path']:
                    if not a.find(path) == -1:
                        continue
                raise Exception('you done messed up', "A-A-RON")
            except:
                r.append(a)
            self.query.next()
        for i in r:
            self.query.exec('DELETE FROM media_path WHERE path = "{}";'.format(i))
            self.query.exec('DELETE FROM dedup WHERE path = "{}";'.format(i))

    def scan_directory(self, path):
        os.chdir(path)
        r = os.listdir()#list all files
        current_dir = os.getcwd()
        prog = 0
        for i in r:
            prog += 1
            self.progressbar_update.emit(int(prog * 100 / len(r)))
            if os.path.isfile(current_dir + '\\' + i):
                for j in self.ACCEPTED_EXT:
                    if i[len(i) - len(j):] == j:
                        self.insert_sql_entry(name = i, path = current_dir)
            if self.param['sub_folder']:
                self.scan_current_directory(current_dir + '\\' + i)

    def gen_uniq_id(self, path, type = 1, md5_size = 4096):
        if type == 1:
            return filesize(path)
        elif type == 2:
            return str(filesize(path)) + str(md5(path, md5_size))
        return str(filesize(path))# + str(md5(path, md5_size))

    def insert_sql_entry(self, name, path, play = 0):
        path = path + '\\' + name
        ctime = os.path.getctime(path)
        ctime = dtinthehouse.fromtimestamp(ctime).strftime('%Y-%m-%d %H:%M:%S')
        if not self.query.exec(self.MEDIA_PATH_INSERT.format(name, path, filesize(path), ctime)):
            self.log_update.emit('insert error on ' + path)
        self.insert_dedup_query(path, 1)


    def insert_dedup_query(self, path, type = 1):
        key = self.gen_uniq_id(path, type)
        if isinstance(key, str):
            key = '"{}"'.format(key)
        if not self.query.exec('INSERT INTO dedup(path, {}) VALUES ("{}", {});'.format(self.DEDUP_SQL_COL[type][0], path, key)):
            self.query.exec('SELECT size, {} FROM dedup WHERE path = "{}";'.format(self.DEDUP_SQL_COL[type][0], path))
            self.query.first()
            if filesize(path) != self.query.value(0) or self.query.value(1) == '':
                self.query.exec('UPDATE dedup SET size = {}, {} = {} WHERE path = "{}"'.format(filesize(path),self.DEDUP_SQL_COL[type][0], key, path))

    def run(self):
        if self.runType:
            return
        self.runType = True
        self.scan_db()
        self.runType = False
    

class FileToSQL(QMainWindow):

    def __init__(self):
        super(FileToSQL, self).__init__()
        uic.loadUi('pot.ui', self)

        self.setWindowTitle('Hugh Chungus')

        self.load_param()
        self.thread = File2SQLThread(self.param)

        self.progress_bar = self.findChild(QProgressBar, 'progressBar')
        self.sql_table = self.findChild(PotTableRightClick, 'sql_table')
        self.sql_table.open_location_signal.connect(self.open_in_explorer)
        self.sql_table.doubleClicked.connect(self.playlist)
        self.sql_table.clicked.connect(self.launched_notif)
        self.sql_table.setSelectionBehavior(QTableView.SelectRows)
        self.queryModel = QSqlQueryModel()
        self.sql_table.setModel(self.queryModel)
        self.log_textedit = self.findChild(QTextEdit, 'log_textedit')

        self.random_check = self.findChild(QCheckBox, 'random_check')
        self.sql_line = QLineEdit(self)

        self.query_button = self.findChild(QPushButton, 'query_button')
        self.query_button.clicked.connect(self.query)
        self.playlist_button = self.findChild(QPushButton, 'playlist_button')
        self.playlist_button.clicked.connect(self.playlist)

        self.tasksMenu = self.menuBar().addMenu('&Tasks')
        self.ins_menu_action('Set Path', self.set_path, self.tasksMenu)
        self.ins_menu_action('Scan Path', self.scan_db, self.tasksMenu)

        self.combobox = self.findChild(QComboBox, 'comboBox')
        self.combobox.addItems([
            '', 
            'ORDER BY ctime DESC',
#            'SELECT DISTINCT a.path AS path1, b.path AS path2, a.size FROM dedup AS a, dedup as b WHERE a.size == b.size AND a.path != b.path;',
            'SELECT DISTINCT a.path AS path1, b.path AS path2, a.size FROM dedup AS a JOIN dedup as b ON a.size == b.size AND a.path != b.path',
            ])
        self.combobox.setLineEdit(self.sql_line)
        self.column_combobox = self.findChild(QComboBox, 'column_combobox')
        self.tablename_combobox = self.findChild(QComboBox, 'tablename_comboBox')
        self.final_query_lineedit = self.findChild(QLineEdit, 'final_query_lineEdit')
        self.tablename_combobox.addItems([
            'media_path',
            'dedup',
            'path_tags',
        ])
        self.tablename_combobox.setCurrentIndex(0)
        #textChanged(str)
        self.tablename_combobox.editTextChanged.connect(self.guess_query)
        self.column_combobox.editTextChanged.connect(self.guess_query)
        self.tablename_combobox.currentIndexChanged.connect(self.update_column_selection)
        self.sql_line.textChanged.connect(self.guess_query)

        self.show()
        self.refresh_view()
        self.thread.tableview_refresh.connect(self.refresh_view)
        self.thread.progressbar_update.connect(self.progress_bar_update)
        self.thread.log_update.connect(self.log_update)

        self.update_column_selection()
        self.guess_query()

    def update_column_selection(self, index = 0):
        self.column_combobox.clear()
        table = self.tablename_combobox.currentText()
        if table == 'media_path':
            self.column_combobox.addItems([
                'name, path',
                'name',
                'path',
                'ctime',
            ])
        elif table == 'dedup':
            self.column_combobox.addItems([
                'path',
                'size',
                'key1',
                'key2',
            ])
        elif table == 'path_tags':
            self.column_combobox.addItems([
                'path',
                'class',
                'value',
            ])
        self.guess_query()


    def log_update(self, text):
        self.log_textedit.insertPlainText(text + '\n')

    def open_in_explorer(self, index):
        #print(r'explorer /select,"{}"'.format(self.get_data(index, 1)))
        subprocess.Popen(r'explorer /select,"{}"'.format(self.get_data(index, 1)))

    def launched_notif(self):
        self.progress_bar_update(0)

    def refresh_view(self, query = None):
        if query:
            self.set_query(query)
        else:
            self.set_query(self.thread.SELECT_MEDIA_PATH_SQL)
        self.resize_column()

    def progress_bar_update(self, i):
        self.progress_bar.setValue(int(i))

    def resize_column(self):
        self.sql_table.setColumnWidth(self.thread.MEDIA_PATH_SQL_COL_NUM['name'], self.sql_table.width())

    def resizeEvent(self, event):
        self.resize_column()

    def set_query(self, query):
        self.queryModel.setQuery(query, self.thread.database())

    def ins_menu_action(self, name, func, menu):
        action = QAction(name, self)
        action.triggered.connect(func)
        menu.addAction(action)

    def set_path(self):
        self.gc_placeholder = VertTextDiag(self.param)

    def scan_db(self):
        self.thread.start()

    def query(self):
        self.refresh_view(self.guess_query())

    def guess_query(self,  *args):#self.final_query_lineedit
        string = ''
        after_where = self.sql_line.text()
        b4_where = self.tablename_combobox.currentText()
        columns = self.column_combobox.currentText()
        if columns == '':
            columns = '*'
        #logic of guess query: if b4where == '', if after where doesnt start by SELECT then return nothing; else retunr after where
        #if len(b4_where) == 0:
        if after_where.find("SELECT") == 0:
            string = after_where
        elif len(b4_where) > 0:#then string starts with SELECT * FROM b4_where
            string = "SELECT {} FROM {}".format(columns, b4_where)
            if len(after_where) > 0:
                if after_where.find('ORDER BY') != -1 or after_where.find('WHERE') != -1:
                    string += ' ' + after_where
                else:
                    string += ' WHERE name LIKE "%{}%";'.format(after_where)

        if string[-1] != ';':
            string += ';'
        self.final_query_lineedit.setText(string)
        return string

        if len(string) == 0:
            return string
        if not string.find('ORDER BY') == -1:
            return 'SELECT * FROM media_path ' + string
        elif string.find("SELECT") == -1:
            return 'SELECT * FROM media_path WHERE name LIKE "%{}%"'.format(string)
        return string

    def keyPressEvent(self, e):
        if (e.key() == QtCore.Qt.Key_Return or e.key() == QtCore.Qt.Key_Enter):
            self.query()

    def playlist(self):
        play = None
        if self.get_current_row() > -1:
            play = self.get_current_data(self.thread.MEDIA_PATH_SQL_COL_NUM['path'])
        make_potplayer_playlist(self.tableview_to_list(), play)
        subprocess.Popen([r'C:\Program Files\DAUM\PotPlayer\potplayermini64.exe', r'{}\playlist.dpl'.format(os.getcwd())])
        self.progress_bar_update(100)

    def get_current_data(self, col = 0):
        return self.get_data(self.get_current_row(), col)
        #return self.queryModel.data(self.mk_querymodel_index(self.get_current_row(), col))
    
    def get_data(self, row, col = 0):
        return self.queryModel.data(self.mk_querymodel_index(row, col))

    def mk_querymodel_index(self, row, col):
        return self.queryModel.createIndex(row, col)

    def get_current_row(self):
        return self.sql_table.selectionModel().currentIndex().row()

    def tableview_to_list(self):
        a = self.queryModel.query()
        a.first()
        r = []
        while a.isValid():
            r.append(a.value(self.thread.MEDIA_PATH_SQL_COL_NUM['path']))
            if not a.next():
                break
        if self.random_check.checkState() == Qt.Checked:
            random.shuffle(r)
        return r
    def load_param(self):
        self.param = {
            'gallery_path' : [],
            'sub_folder' : False,
        }
        if os.path.exists('settings.json'):
            try:
                with open('settings.json') as json_file:
                    paramR = json.load(json_file)
                    for i in paramR.keys():
                        self.param[i] = paramR[i]
            except:
                'okay'

    def save_param(self):
        with open('settings.json', 'w') as outfile:
            json.dump(self.param, outfile)

    def closeEvent(self, event):
        self.save_param()
        try:
            self.gc_placeholder.close()
        except:
            'okay'

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    ui = FileToSQL()
    sys.exit(app.exec_())
