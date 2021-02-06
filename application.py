import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QFileDialog, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
import re
import os
from datetime import datetime
from collections import Counter
from PyPDF2 import PdfFileReader, PdfFileWriter


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'PDF Tool'
        self.left = 400
        self.top = 100
        self.width = 300
        self.height = 100
        self.dir = None
        self.name = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        button = QPushButton('Buscar Folder', self)
        button.setToolTip('This is an example button')
        button.move(10, 30)
        button.clicked.connect(self.pdf_)
        self.show()

    def showdialog(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        msg.setText("Action Successesful")
        msg.setWindowTitle("MessageBox demo")
        msg.setStandardButtons(QMessageBox.Ok)
        retval = msg.exec_()

    def pdf_(self):
        self.statusBar().showMessage('Processing...')
        self.dir = QFileDialog.getExistingDirectory()  # .getOpenFileName(self, 'Open file', 'c:\\', "Image files (*.pdf)")
        ls = []
        files = [x for x in os.listdir(self.dir + '/') if x.endswith('.pdf') and x != "join.pdf"]
        outfile = PdfFileWriter()

        bancos = ['bbva', 'santander']
        for i in files:
            pdf = PdfFileReader(open(self.dir + '/' + str(i), 'rb'))
            page = pdf.getPage(0)
            pages = pdf.getNumPages()
            last = pdf.getPage(pages - 1)
            text = last.extractText()
            banco = re.findall("(bbva|santander)", text.lower())
            text = page.extractText()
            fecha = re.findall("(corte.*[0-9]{1,2}[/][0-9]{1,2}[/][0-9]{2,4})", text.lower())[0]
            fecha = re.findall("([0-9]{1,2}[/][0-9]{1,2}[/][0-9]{2,4})", fecha)[0]
            ls.append({'page': page, 'bank': Counter(banco).most_common()[0][0].upper(), 'date': fecha})

        fecha = []
        for i in ls:
            fecha.append(i['date'])
        fecha.sort(key=lambda date: datetime.strptime(date, '%d/%m/%Y'))

        for i in fecha:
            for x in ls:
                if (x['date'] == i):
                    outfile.addPage(x['page'])

        self.statusBar().showMessage('Creating PDF...')

        with open('test.pdf', 'wb') as f:
            outfile.write(f)
        self.statusBar().showMessage('successful pdf creation')
        self.showdialog()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())