import sys
import re
import os
import resources

from datetime import datetime
from collections import Counter
import PyPDF2
from PyPDF2.pdf import PdfFileReader, PdfFileWriter, PageObject

from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow, QLabel,
                             QPushButton, QFileDialog, QMessageBox,
                             QLineEdit, QVBoxLayout, QButtonGroup,
                             QRadioButton, QFormLayout, QMenu, QHBoxLayout)
from PyQt5.QtGui import QIcon

from typing import List, Union

# pyinstaller --onefile --windowed --icon=favicon.ico main.py


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# aurora_icon_path = resource_path("icons\\aurora.ico")
# information_icon_path = resource_path("icons\\information_large.png")
aurora_icon_path = ":aurora.ico"
information_icon_path = ":information.png"


class PDFApp(QMainWindow):

    def __init__(self):
        super(PDFApp, self).__init__()

        self.setWindowTitle('PDF Tool')
        self.setWindowIcon(QIcon(aurora_icon_path))
        self.resize(450, 50)
        self.create_menu_bar()

        self.dir: str = ""
        self.name: str = ""

        self.button_group: QButtonGroup = None
        self.init_ui()

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        help_menu = menu_bar.addMenu(QIcon(information_icon_path), "&Help")
        help_menu.triggered.connect(self.show_help)
        help_menu.addAction('Contenido')

    @staticmethod
    def show_help():
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Ayuda")

        msg.setText("Pasos a seguir: ")
        msg.setInformativeText(
            '1. Coloca los pdfs a unir dentro de la misma carpeta. \n'
            '2. Nombra el archivo. \n'
            '3. Selecciona una opción para ordenar los archivos:\n'
            '   - Automáticamente si el estado de cuenta es BBVA o Santander.'
            ' \n'
            '   - Manualmente si nombraste los archivos de manera alfabetica'
        )
        # msg.setDetailedText("The details are as follows:")
        msg.setStandardButtons(QMessageBox.Ok)
        _ = msg.exec_()

    def add_file_name_form_layout(self, outer_layout: QVBoxLayout) -> None:
        """File Name for the new pdf will be create"""
        form_layout = QFormLayout()
        form_layout.addRow("Nombre del archivo: ", QLineEdit("combined_file"))
        self.name = form_layout.itemAt(0, 1).widget().text()
        outer_layout.addLayout(form_layout)

    def add_sorting_button(self, outer_layout: QVBoxLayout) -> None:
        """Options of processing, first option its a automatic process
        and second its a manually process"""
        radio_buttons = [QRadioButton("Automático"), QRadioButton("Manual")]
        radio_buttons[0].setChecked(True)

        options_layout = QVBoxLayout()
        options_layout.addWidget(QLabel('Orden de los archivos: '))
        self.button_group = QButtonGroup()

        for n, button in enumerate(radio_buttons):
            options_layout.addWidget(button)
            self.button_group.addButton(button, n)

        outer_layout.addLayout(options_layout)

    def add_search_folder_button(self, outer_layout: QVBoxLayout) -> None:
        # Search folder button
        button = QPushButton("Buscar Folder")
        button.clicked.connect(self.select_type_sorting_process)
        outer_layout.addWidget(button)

    def init_ui(self):
        outer_layout = QVBoxLayout()
        self.add_file_name_form_layout(outer_layout)
        self.add_sorting_button(outer_layout)
        self.add_search_folder_button(outer_layout)

        widget = QWidget()
        widget.setLayout(outer_layout)
        self.setCentralWidget(widget)

    @staticmethod
    def show_dialog(text=""):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        msg.setText(text)
        msg.setWindowTitle("Información de la acción")
        msg.setStandardButtons(QMessageBox.Ok)
        _ = msg.exec_()

    def select_type_sorting_process(self):
        if self.button_group.checkedId() == 0:  # Automatically
            return self.process_pdf_automatically()
        elif self.button_group.checkedId() == 1:  # Manually
            return self.process_pdf_manually()
        
    def process_pdf_automatically(self):
        self.statusBar().showMessage('Procesando...')
        # print("File Name:", self.name)
        if self.name != "":
            self.dir = QFileDialog.getExistingDirectory()
            ls = []
            files = [x for x in os.listdir(self.dir + '/') if
                     x.endswith('.pdf') and x != "join.pdf"]
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
                fecha = \
                re.findall("(corte.*[0-9]{1,2}[/][0-9]{1,2}[/][0-9]{2,4})",
                           text.lower())[0]
                fecha = \
                re.findall("([0-9]{1,2}[/][0-9]{1,2}[/][0-9]{2,4})", fecha)[0]
                ls.append({'page': page,
                           'bank': Counter(banco).most_common()[0][0].upper(),
                           'date': fecha})

            fecha = []
            for i in ls:
                fecha.append(i['date'])
            fecha.sort(key=lambda date: datetime.strptime(date, '%d/%m/%Y'))

            for i in fecha:
                for x in ls:
                    if (x['date'] == i):
                        outfile.addPage(x['page'])

            self.statusBar().showMessage('Creando PDF...')

            save_in = self.dir + '/' + self.name + '.pdf'

            with open(save_in, 'wb') as f:
                outfile.write(f)

            self.statusBar().showMessage('Creación del PDF Exitosa')
            self.show_dialog("Acción realizada con éxito")
        else:
            self.show_dialog("No fue posible crear el archivo PDF")
            self.statusBar().showMessage('')

    def process_pdf_manually(self):
        self.statusBar().showMessage('Procesando...')
        self.dir = QFileDialog.getExistingDirectory()
        pdf_files_list = get_pdf_files_list(self.dir)
        readers_list = read_pdf_files_from_path_list(pdf_files_list)
        first_pages_list = get_first_page_from_list_files(readers_list)
        join_pdf = join_pdf_files(first_pages_list)
        save_pdf(join_pdf, path=self.dir + '/' + self.name + '.pdf')
        self.statusBar().showMessage('Creación del PDF Exitosa')
        self.show_dialog("Acción realizada con éxito")

        # self.show_dialog("No fue posible crear el archivo PDF")
        # self.statusBar().showMessage('')


def sort_paths(path_list: List) -> List:
    path_list.sort(key=str.lower)
    return path_list


def get_pdf_files_list(path: str) -> List:
    pdf_files = []
    for dir_path, sub_dirs, files in os.walk(path):
        for item in files:
            if is_pdf_extension(item):
                pdf_files.append(os.path.abspath(os.path.join(dir_path, item)))

        break

    # pdf_files = [path for path in os.listdir(self.dir + '/') if
        #             path.endswith('.pdf')]

    return sort_paths(pdf_files)


def is_pdf_extension(file: str) -> bool:
    """Returns True if is a valid pdf and false if don't"""
    return bool(file.lower().endswith(".pdf"))


def read_pdf_file(file: str) -> PdfFileReader:
    """Read a pdf file"""
    if is_pdf_extension(file):
        try:
            return PyPDF2.PdfFileReader(open(file, 'rb'))
        except Exception as e:
            print(e)
    else:
        raise Exception('No es un archivo válido')


def read_pdf_files_from_path_list(pdf_path: List[str]) -> List[PdfFileReader]:
    """Returns a list with """
    print('reading list', pdf_path)
    return [read_pdf_file(path) for path in pdf_path]


def get_page(pdf_reader: PdfFileReader,
             number_page: int = 0) -> PageObject:
    """Returns the selected page from pdf file"""
    return pdf_reader.getPage(number_page)


def get_first_page_from_list_files(readers_list: List[PdfFileReader])\
        -> List[PageObject]:
    return [get_page(pdf_file) for pdf_file in readers_list]


def join_pdf_files(pdf_files: List[Union[PdfFileReader, PageObject]])\
        -> PdfFileWriter:
    """Returns a combined pdf file from a given list of paths of pdf files"""
    pdf_writer = PyPDF2.PdfFileWriter()

    for pdf_file in pdf_files:
        pdf_writer.addPage(pdf_file)

    return pdf_writer


def save_pdf(file: PdfFileWriter, path: str):
    """Save a file in a given """
    with open(path, "wb") as output:
        file.write(output)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    pdf_app = PDFApp()
    pdf_app.show()
    sys.exit(app.exec_())
