import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QFileDialog, QMessageBox, QLineEdit, QLabel
from PyQt5.QtGui import QIcon, QFont
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
        self.width = 450
        self.height = 150
        self.dir = None
        self.name = None
        self.e1 = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        button = QPushButton('Buscar Folder', self)
        button.setGeometry(130,60,180,40)
        #button.setToolTip('This is an example button')
        #button.move(130, 60)
        button.clicked.connect(self.pdf_)
        label = QLabel("Nombre Archivo:", self)
        label.setGeometry(20,20,130,20)
        # label.move(20,20)
        self.name = QLineEdit("", self)
        self.name.setGeometry(150, 20, 180, 20)
        #self.name.move(140,20)
        self.name.setMaxLength(200)
        #self.setAlignment(Qt.AlignLeft)
        self.setFont(QFont("Arial", 12))
        self.show()

    def showdialog(self, texto=""):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        msg.setText(texto)
        msg.setWindowTitle("Información de la acción")
        msg.setStandardButtons(QMessageBox.Ok)
        retval = msg.exec_()

    def pdf_(self):
        self.statusBar().showMessage('Procesando...')
        print("x:",self.name.text())
        if(self.name.text()!=""):
            self.dir = QFileDialog.getExistingDirectory()
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

            self.statusBar().showMessage('Creando PDF...')

            with open(f'{self.name.text()}', 'wb') as f:
                outfile.write(f)
            self.statusBar().showMessage('Creación del PDF Exitosa')
            self.showdialog("Acción realizada con éxito")
        else:
            self.showdialog("Agrega el nombre del archivo")
            self.statusBar().showMessage('')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())