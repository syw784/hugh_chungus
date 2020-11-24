from PyQt5.QtWidgets import *#QTableView, QDialog
from PyQt5.QtCore import QModelIndex, pyqtSignal, Qt

class VertTextDiag(QDialog):

    def __init__(self, param = {'gallery_path':[]}):
        super(VertTextDiag, self).__init__()
        self.setWindowTitle("add a Chungus path")
        self.verticalLayout = QVBoxLayout(self)
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.verticalLayout.addWidget(self.scrollArea)
        
        self.scrollAreaWidgetContents = QWidget()
        self.scrollVLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        self.verticalLayout.addWidget(self.buttonBox)
        self.buttonBox.accepted.connect(self.accepted_kk)
        self.buttonBox.rejected.connect(self.close_plz)


        self.add_line_button = QPushButton('Add', self)
        self.add_line_button.clicked.connect(self.add_lineEdit_spaghetti)
        self.buttonBox.addButton(self.add_line_button, QDialogButtonBox.ActionRole)

        self.param = param
        self.r = []
        for i in range(len(param['gallery_path'])):
            self.add_lineEdit(self.param['gallery_path'][i])
        self.add_lineEdit()
        self.show()

    def add_lineEdit_spaghetti(self):
        self.add_lineEdit()

    def add_lineEdit(self, text = ''):
        j = QLineEdit((self.scrollAreaWidgetContents))
        j.setText(text)
        self.scrollVLayout.addWidget(j)
        self.r.append(j)

    def accepted_kk(self):
        self.param['gallery_path'] = []
        for i in self.r:
            if not i.text() == "":
                self.param['gallery_path'].append(i.text()) 
        self.close()

    def close_plz(self):
        self.close()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    a = VertTextDiag()
    sys.exit(app.exec_())
