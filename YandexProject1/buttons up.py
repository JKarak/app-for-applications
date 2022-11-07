import sys
import traceback
import sqlite3

from PIL import Image
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtWidgets import QTableView, QComboBox, QTableWidgetItem
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QPushButton, QApplication, QSizePolicy, QWidget, QMainWindow, QWidgetItem, QFileDialog, \
    QLabel, QDialog, \
    QInputDialog, QMessageBox, QLineEdit
from PyQt5 import uic, QtCore


def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("error catched!:")
    print("error message:\n", tb)
    QApplication.quit()
    # or QtWidgets.QApplication.exit(0)


sys.excepthook = excepthook


class RoleWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('entrance1.ui', self)
        self.pushButton.clicked.connect(self.clickBtn1)
        self.a = None
        self.users = sqlite3.connect("users.sqlite")
        self.cur1 = self.users.cursor()
        self.cur1.execute("""CREATE TABLE IF NOT EXISTS users(
           pupillogin TEXT,
           pupilpassword TEXT,
           pupilname TEXT,
           pupilsurname TEXT,
           teacherlogin TEXT);
        """)
        self.users.commit()
        self.teachers = sqlite3.connect("teachers.sqlite")
        self.cur2 = self.teachers.cursor()
        self.cur2.execute("""CREATE TABLE IF NOT EXISTS teachers(
                   teachersurname TEXT,
                   teachername TEXT,
                   teachername2 TEXT,
                   teacherlogin TEXT,
                   teacherpassword TEXT,
                   email TEXT);
                """)
        self.teachers.commit()
        self.link = sqlite3.connect("link.sqlite")
        self.cur3 = self.link.cursor()
        self.cur3.execute("""CREATE TABLE IF NOT EXISTS link(
                   teacherlogin TEXT,
                   pupillogin TEXT);
                """)
        self.link.commit()


    def clickBtn1(self):
        print(1)
        if self.comboBox.currentText() == 'Учитель':
            self.openTeacherEntrance()
        else:
            self.openPupilEntrance()

    def openTeacherEntrance(self):
        self.hide()
        self.b = RegWin()

    def openPupilEntrance(self):
        self.hide()
        self.a = PupilEntrance()


class PupilEntrance(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('pupil_entrance1.ui', self)
        self.pushButton.clicked.connect(self.clickBtn1)
        self.pushButton_2.clicked.connect(self.clickBtn2)
        self.show()

    def clickBtn1(self):
        users = sqlite3.connect("users.sqlite")
        cur1 = users.cursor()
        login = cur1.execute(f"SELECT * from users where pupillogin='{self.lineEdit.text()}'").fetchone()
        print(login)
        if login is None:
            self.openEntranceError()
            """msg = QMessageBox(QMessageBox.Information, '', 'Логин не найден. \nПопробуйте ещё раз или \nобратитесь к своему учителю', parent=self)
            msg.show()"""
        elif login[1] == self.lineEdit_2.text():
            self.openMainPupil()

    def clickBtn2(self):
        self.openEntranceError()

    def openMainPupil(self):
        self.hide()
        self.a = PupilMain()

    def openEntranceError(self):
        self.b = EntranceError()


class EntranceError(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('error_entrance_pupil.ui', self)
        self.pushButton.clicked.connect(self.clickBtn1)
        self.pushButton_2.clicked.connect(self.clickBtn2)
        self.show()

    def clickBtn1(self):
        self.hide()

    def clickBtn2(self):
        # отправить письмо со слёзной просьбой восстановить логин и пароль
        self.hide()
        self.a = AppForRecovery()


class AppForRecovery(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('app_for_recovery.ui', self)
        self.pushButton.clicked.connect(self.clickBtn1)
        self.show()

    def clickBtn1(self):
        self.hide()


class PupilMain(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main_pupil.ui', self)
        self.pushButton.clicked.connect(self.clickBtn1)
        self.pushButton_2.clicked.connect(self.clickBtn2)
        self.pushButton_3.clicked.connect(self.clickBtn3)
        self.show()

    def clickBtn1(self):
        print(3)
        self.changeAvatar()

    def clickBtn2(self):
        print('fuckshit')
        sys.exit()

    def clickBtn3(self):
        print(3)
        self.hide()
        self.application()

    def changeAvatar(self):
        self.a = Avatar()

    def application(self):
        self.b = PupilApplication()


class Avatar(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('avatar_change_universal.ui', self)
        self.pushButton_9.clicked.connect(self.clickBtn9)
        self.show()

    def clickBtn9(self):
        print('no')
        self.hide()


class PupilApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('application_pupil.ui', self)
        self.pushButton.clicked.connect(self.clickBtn1)
        self.pushButton_2.clicked.connect(self.clickBtn2)
        self.pushButton_3.clicked.connect(self.clickBtn3)
        self.show()

    def clickBtn1(self):
        print('application')
        self.changeAvatar()

    def clickBtn2(self):
        print('fuckshit')
        sys.exit()

    def clickBtn3(self):
        print('application')
        self.hide()
        self.openMainPupil()

    def changeAvatar(self):
        self.a = Avatar()

    def openMainPupil(self):
        self.hide()
        self.b = PupilMain()


class RegWin(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('teacher_entrance1.ui', self)
        self.pushButton.clicked.connect(self.clickBtn1)
        self.pushButton_2.clicked.connect(self.clickBtn2)
        self.a = None
        self.show()

    def clickBtn1(self):
        teachers = sqlite3.connect("teachers.sqlite")
        cur1 = teachers.cursor()
        login = cur1.execute(f"SELECT * from teachers where teacherlogin='{self.lineEdit.text()}'").fetchone()
        print(login)
        if login is None:
            msg = QMessageBox(QMessageBox.Information, '', 'Логин не найден. \nПопробуйте ещё раз или \nсоздайте новый аккаунт', parent=self)
            msg.show()
        elif login[1] == self.lineEdit_2.text():
            self.openTeacherEntrance()
        print(1)


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
        uic.loadUi('register_teacher1.ui', self)
        self.show()
        self.pushButton.clicked.connect(self.clickBtn)

    def clickBtn(self):
        print(1)
        teachers = sqlite3.connect("teachers.sqlite")
        cur1 = teachers.cursor()
        input = (self.lineEdit.text(), self.lineEdit_2.text(), self.lineEdit_3.text(), self.lineEdit_4.text(), self.lineEdit_5.text(), self.lineEdit_6.text())
        print(input)
        cur1.execute(f"INSERT INTO teachers (teachersurname, teachername, teachername2, teacherlogin, teacherpassword, email) VALUES{input}")
        teachers.commit()
        self.teacherAddPupil()

    def teacherAddPupil(self):
        self.hide()
        self.a = TeacherAddPupil(self.lineEdit_4)


class TeacherAddPupil(QMainWindow):
    def __init__(self, user):
        super().__init__()
        uic.loadUi('pupil_add.ui', self)
        self.show()
        self.user = user
        self.pushButton.clicked.connect(self.clickBtn)
        self.pushButton_2.clicked.connect(self.openFile)
        self.users = sqlite3.connect("users.sqlite")
        self.cur1 = self.users.cursor()
        """cur1.execute(
            f"INSERT INTO teachers (teachersurname, teachername, teachername2, teacherlogin, teacherpassword, email) VALUES{input}")"""

    def clickBtn(self):
        print(1)
        self.openTeacherEntrance()

    def openTeacherEntrance(self):
        self.hide()
        self.a = TeacherEntrance()

    def openFile(self):
        self.fname = QFileDialog.getOpenFileName(self, 'Open file')[0]
        if self.fname:
            with open(self.fname, 'r', encoding='utf-8') as f:
                data = [i.rstrip() for i in f.readlines()]

                self.tableWidget.setRowCount(len(data))
                self.tableWidget.setColumnCount(4)
                self.titles = data[0].split(';')
                for i, elem in enumerate(data):
                    for j, val in enumerate(elem.split(';')):
                        self.tableWidget.setItem(i, j, QTableWidgetItem(val))
                    if i != 0:
                        b = list(elem.split(';')) + [self.user]
                        a = tuple(b)
                        print(a)
                        if self.cur1.execute(f"SELECT * from users where pupillogin='{a[0]}'") is not None:
                            self.cur1.execute(f"INSERT INTO users (pupillogin, pupilpassword, pupilname, pupilsurname, teacherlogin) VALUES{a}")
                            self.users.commit()



class TeacherEntrance(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main_teacher.ui', self)
        self.show()
        self.pushButton_3.clicked.connect(self.clickBtn3)

    def clickBtn3(self):
        print(1)
        self.checkInquary()

    def checkInquary(self):
        self.hide()
        self.a = TeacherCheckInquary()


class TeacherCheckInquary(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('application_teacher.ui', self)
        self.show()
        self.pushButton_3.clicked.connect(self.clickBtn3)
        self.pushButton_4.clicked.connect(self.clickBtn4)

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = RoleWindow()
    win.show()
    app.exec_()

