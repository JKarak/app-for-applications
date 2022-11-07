import sys
import traceback
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PIL import Image
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QPushButton, QApplication,
                             QSizePolicy, QWidget,
                             QMainWindow, QWidgetItem,
                             QFileDialog, QLabel,
                             QDialog, QInputDialog,
                             QMessageBox, QLineEdit,
                             QTableWidgetItem)
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QIcon


def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("error catched!:")
    print("error message:\n", tb)
    QApplication.quit()


sys.excepthook = excepthook


class RegWin(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('teacher_entrance.ui', self)
        self.pushButton.clicked.connect(self.clickBtn1)
        self.pushButton_2.clicked.connect(self.clickBtn2)
        self.a = None

    def clickBtn1(self):
        print(1)
        self.openTeacherEntrance()

    def clickBtn2(self):
        print(1)
        self.openTeacherCheckin()

    def openTeacherEntrance(self):
        self.hide()
        self.a = TeacherEntrance()

    def openTeacherCheckin(self):
        self.hide()
        self.a = TeacherCheckin()


class TeacherCheckin(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('teacher_register.ui', self)
        self.show()
        self.pushButton.clicked.connect(self.clickBtn)

    def clickBtn(self):
        print(1)
        self.teacherAddPupil()

    def teacherAddPupil(self):
        self.hide()
        self.a = TeacherAddPupil()


class TeacherAddPupil(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('teacher_add_class.ui', self)
        self.show()
        self.pushButton.clicked.connect(self.clickBtn)
        self.pushButton_2.clicked.connect(self.openFile)

    def clickBtn(self):
        print(1)
        self.openTeacherEntrance()

    def openTeacherEntrance(self):
        self.hide()
        self.a = TeacherEntrance()

    def openFile(self):
        self.fname = QFileDialog.getOpenFileName(self, 'Open file')[0]
        if self.fname:
            f = open(self.fname, 'r', encoding='utf-8')
            with f:
                data = [i.rstrip() for i in f.readlines()]

                self.tableWidget.setRowCount(len(data))
                self.tableWidget.setColumnCount(4)
                self.titles = data[0].split(';')
                for i, elem in enumerate(data):
                    for j, val in enumerate(elem.split(';')):
                        self.tableWidget.setItem(i, j, QTableWidgetItem(val))


class TeacherEntrance(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('teacher_main.ui', self)
        self.pushButton_12.clicked.connect(self.clickBtn3)
        self.pushButton_9.clicked.connect(self.clickBtn9)
        self.show()

    def clickBtn9(self):
        print(3)
        self.changeAvatar()

    def clickBtn3(self):
        print(1)
        self.checkInquary()

    def checkInquary(self):
        self.hide()
        self.a = TeacherCheckInquary()

    def changeAvatar(self):
        self.a = Avatar()


class Avatar(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('all_avatar.ui', self)
        self.pushButton_9.clicked.connect(self.clickBtn9)
        self.show()

    def clickBtn9(self):
        print('no')
        self.hide()


class TeacherCheckInquary(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('teacher_application.ui', self)
        self.show()
        self.pushButton_3.clicked.connect(self.clickBtn3)
        self.pushButton_4.clicked.connect(self.clickBtn4)

        self.le = QLineEdit(self)
        self.le.move(130, 22)

    def clickBtn3(self):
        print(1)
        self.approveInquary()

    def approveInquary(self):
        self.hide()
        self.a = TeacherEntrance()

    def clickBtn4(self):
        print(1)
        self.approveInquary2()

    def approveInquary2(self):
        self.hide()
        self.a = TeacherEntrance()
        text, ok = QInputDialog.getText(self, 'Отклонить', 'Введите причину отказа:')

        if ok:
            print(text)
            self.le.setText(str(text))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = RegWin()
    win.show()
    app.exec_()
