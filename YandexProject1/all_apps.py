import sys
import traceback
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.header    import Header
import string
import random


from PIL import Image
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtWidgets import QTableView, QComboBox, QTableWidgetItem, QTableWidget
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QPushButton, QApplication,
                             QSizePolicy, QWidget,
                             QMainWindow, QWidgetItem,
                             QFileDialog, QLabel,
                             QDialog, QInputDialog,
                             QMessageBox, QLineEdit)
from PyQt5 import uic, QtCore, QtWidgets


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
        uic.loadUi('all_entrance.ui', self)
        self.pushButton.clicked.connect(self.clickBtn1)
        self.a = None
        self.users = sqlite3.connect("users.sqlite")
        self.cur1 = self.users.cursor()
        self.cur1.execute("""CREATE TABLE IF NOT EXISTS users(
           pupillogin TEXT,
           pupilpassword TEXT,
           pupilname TEXT,
           pupilsurname TEXT,
           pupilemail TEXT,
           teacherlogin TEXT,
           avatarfile TEXT);
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
                   email TEXT,
                   avatarfile TEXT);
                """)
        self.teachers.commit()
        self.apps = sqlite3.connect("apps.sqlite")
        self.cur4 = self.apps.cursor()
        self.cur4.execute("""CREATE TABLE IF NOT EXISTS apps(
                    teacherlogin TEXT,
                    pupillogin TEXT,
                    reason TEXT,
                    time TEXT,
                    date TEXT,
                    reaction TEXT,
                    teacherreason TEXT,
                    status TEXT);
                """)
        self.apps.commit()


    def clickBtn1(self):
        print(1)
        if self.comboBox.currentText() == 'Учитель':
            self.openTeacherEntrance()
        elif self.comboBox.currentText() == 'Выбрать роль':
            msg = QMessageBox(QMessageBox.Information, '', 'Выберите роль!', parent=self)
            msg.show()
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
        uic.loadUi('pupil_entrance.ui', self)
        self.pushButton.clicked.connect(self.clickBtn1)
        self.pushButton_2.clicked.connect(self.clickBtn2)
        self.user = None
        self.teacher = None
        self.show()

    def clickBtn1(self):
        users = sqlite3.connect("users.sqlite")
        cur1 = users.cursor()
        login = cur1.execute(f"SELECT * from users where pupillogin='{self.lineEdit_4.text()}'").fetchone()
        print(login)
        if login is None:
            self.openEntranceError()
        elif login[1] == self.lineEdit_7.text():
            self.user = self.lineEdit_4.text()
            self.teacher = login[4]
            self.openMainPupil()

    def clickBtn2(self):
        self.openEntranceError()

    def openMainPupil(self):
        self.hide()
        self.a = PupilMain(self.user, self.teacher)

    def openEntranceError(self):
        self.b = EntranceError()


class EntranceError(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('pupil_error_entrance.ui', self)
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
        uic.loadUi('pupil_password_recovery.ui', self)
        self.pushButton.clicked.connect(self.clickBtn1)
        self.new_login = 'login'
        self.new_password = 'password'
        self.users = sqlite3.connect("users.sqlite")
        self.cur1 = self.users.cursor()
        self.show()

    def clickBtn1(self):
        flag = True
        string = self.lineEdit.text().strip()
        if '@' not in string:
            flag = False
        elif '.' not in string:
            flag = False
        if not flag:
            msg = QMessageBox(QMessageBox.Information, '',
                              'Некорректный адрес электронной почты. \nПопробуйте ещё раз.', parent=self)
            msg.show()
        else:
            if self.send_new_password(string) == 'ok':
                msg = QMessageBox(QMessageBox.Information, '',
                                  'Письмо с новым логином и паролем \n отправлены на Вашу почту\n Если письмо не пришло, \nпроверьте папку "Спам"', parent=self)
                self.cur1.execute("DELETE FROM ")
                msg.show()
                self.hide()
            else:
                msg = QMessageBox(QMessageBox.Information, '',
                                  'Некорректный адрес электронной почты. \nПопробуйте ещё раз.', parent=self)
                msg.show()

    def generate_random_login(self):
        characters = list(string.ascii_letters + string.digits)
        Length = 8
        random.shuffle(characters)
        login = []
        for i in range(Length):
            login.append(random.choice(characters))
        random.shuffle(login)
        self.new_login = "".join(login)

    def generate_random_password(self):
        characters = list(string.ascii_letters + string.digits + "!@#$%^&*()")
        Length = 8
        random.shuffle(characters)
        password = []
        for i in range(Length):
            password.append(random.choice(characters))
        random.shuffle(password)
        self.new_password = "".join(password)

    def send_new_password(self, user_mail):
        smtpObj = smtplib.SMTP('smtp.mail.ru', 587)
        smtpObj.starttls()
        smtpObj.login("aqwertyamkr@mail.ru", "8vEyhKXqTQMkb8SiJ9VT")
        #m = 'pamparam'
        m = f"""Ваш новый логин: {self.new_login}\nПароль: {self.new_password}\n\nНе сообщайте никому эти данные в целях безопасности!"""
        subject = 'Новый логин и пароль'
        msg = MIMEText(m, 'plain', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        print(msg)
        smtpObj.sendmail("aqwertyamkr@mail.ru", user_mail, msg.as_string())
        smtpObj.quit()
        return 'ok'


class PupilMain(QMainWindow):
    def __init__(self, user, teacher):
        super().__init__()
        uic.loadUi('pupil_main_smt.ui', self)
        self.users = sqlite3.connect('users.sqlite')
        self.cur1 = self.users.cursor()
        self.inf = self.cur1.execute(f"SELECT * from users where pupillogin='{user}'").fetchone()
        self.name, self.surname = self.inf[2], self.inf[3]
        self.label.setText(str(self.name + ' ' + self.surname))
        self.pushButton_5.clicked.connect(self.clickBtn1)
        self.pushButton_2.clicked.connect(self.clickBtn2)
        self.pushButton_3.clicked.connect(self.clickBtn3)
        self.table = QTableWidget()
        self.btn = QPushButton(self.table)
        self.table.setCellWidget(0, 2, self.btn)
        """self.table = QTableWidget()
        self.btn = QPushButton("Some button")
        self.table.setCellWidget(1, 3, self.btn)"""
        self.user = user
        self.teacher = teacher
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
        self.a = Avatar(self.user)

    def application(self):
        self.b = PupilApplication(self.user, self.teacher)


class Avatar(QWidget):
    def __init__(self, user):
        super().__init__()
        uic.loadUi('all_avatar.ui', self)
        self.user = user
        self.users = sqlite3.connect('users.sqlite')
        self.cur1 = self.users.cursor()
        self.pushButton_9.clicked.connect(self.clickBtn9)
        self.show()


    def clickBtn9(self):
        print('no')
        self.hide()

    """def clickBtn2(self):
        self.cur1.execute("INSERT INTO users WHERE pupillogin=? VALUES(?)")"""


class PupilApplication(QMainWindow):
    def __init__(self, user, teacher):
        super().__init__()
        uic.loadUi('pupil_application.ui', self)
        self.pushButton_5.clicked.connect(self.clickBtn1)
        self.pushButton_4.clicked.connect(self.clickBtn2)
        self.pushButton_3.clicked.connect(self.clickBtn3)
        self.pushButton.clicked.connect(self.clickBtn)
        self.calendarWidget = QtWidgets.QCalendarWidget()
        self.calendarWidget.clicked['QDate'].connect(self.show_date_func)
        self.date = None
        self.user = user
        self.teacher = teacher
        self.users = sqlite3.connect('users.sqlite')
        self.cur1 = self.users.cursor()
        self.inf = self.cur1.execute(f"SELECT * from users where pupillogin='{self.user}'").fetchone()
        self.name, self.surname = self.inf[2], self.inf[3]
        self.label.setText(str(self.name + ' ' + self.surname))
        self.show()

    def clickBtn1(self):
        print('application')
        self.changeAvatar()

    def clickBtn2(self):
        print('fuckshit')
        sys.exit()

    def clickBtn(self):
        self.calendarWidget.show()
        print('date')

    def show_date_func(self):
        #while self.calendarWidget:
            #if self.calendarWidget.clicked():
        date = self.calendarWidget.selectedDate()
        self.date = date.toString('yyyy-MM-dd')
                #self.label_5.setText(self.date)
        self.calendarWidget.hide()

    def clickBtn3(self):
        print('application')
        users = sqlite3.connect('users.sqlite')
        cur1 = users.cursor()
        apps = sqlite3.connect('apps.sqlite')
        cur4 = apps.cursor()
        input = (self.teacher, self.user, self.lineEdit.text(), self.lineEdit_2.text(), self.date, "В рассмотрении")
        cur4.execute(
            "INSERT INTO apps (teacherlogin, pupillogin, reason, time, date, status) VALUES(?, ?, ?, ?, ?, ?)", input)
        apps.commit()
        mail = cur1.execute(f"SELECT pupilemail from users where pupillogin='{self.user}'").fetchone()
        user1 = cur1.execute(f"SELECT * from users where pupillogin='{self.user}'").fetchone()
        user_name = str(user1[2]) + ' ' + str(user1[3])
        self.send_notification(mail, user_name)
        print(user_name)
        self.hide()
        self.openMainPupil()

    def send_notification(self, user_mail, user_name):
        smtpObj = smtplib.SMTP('smtp.mail.ru', 587)
        smtpObj.starttls()
        smtpObj.login("aqwertyamkr@mail.ru", "8vEyhKXqTQMkb8SiJ9VT")
        #m = 'PUMPURUM'
        m = f"""Пользователь {user_name} отправил новую заявку.\nВы можете просмотреть её в своём личном кабинете."""
        subject = 'Новая заявка'
        msg = MIMEText(m, 'plain', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        print(msg)
        smtpObj.sendmail("aqwertyamkr@mail.ru",
                         user_mail, msg.as_string())
        smtpObj.quit()
        return 'ok'

    def changeAvatar(self):
        self.a = Avatar()

    def openMainPupil(self):
        self.hide()
        self.b = PupilMain(self.user, self.teacher)


class RegWin(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('teacher_entrance.ui', self)
        self.pushButton.clicked.connect(self.clickBtn1)
        self.pushButton_2.clicked.connect(self.clickBtn2)
        self.a = None
        self.show()

    def clickBtn1(self):
        teachers = sqlite3.connect("teachers.sqlite")
        cur1 = teachers.cursor()
        login = cur1.execute(f"SELECT * from teachers where teacherlogin='{self.lineEdit_11.text()}'").fetchone()
        print(login)
        if login is None:
            msg = QMessageBox(QMessageBox.Information, '', 'Логин не найден. \nПопробуйте ещё раз или \nсоздайте новый аккаунт', parent=self)
            msg.show()
        elif login[4].strip() == self.lineEdit_12.text():
            print('ok')
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
        uic.loadUi('teacher_register.ui', self)
        self.show()
        self.pushButton.clicked.connect(self.clickBtn)

    def password(self, x, y):
        c1 = 0
        print(x)
        if x != '':
            if 8 <= len(x) <= 20:
                if '123456' not in x:
                    if 'qwerty' not in x:
                        if 'password' not in x:
                            for i in x:
                                if i.lower() in 'qwertyuiopasdfghjklzxcvbnm1234567890!#$%^}{[]()":\|.':
                                    c1 += 1

        c2 = 0
        print(y)
        if y != '':
            if 8 <= len(y) <= 20:
                if '123456' not in y:
                    if 'qwerty' not in y:
                        if 'password' not in y:
                            for i in y:
                                if i.lower() in 'qwertyuiopasdfghjklzxcvbnm1234567890!#$%^}{[]()":\|.':
                                    c2 += 1
        print(c1)
        if c1 != len(x) or c2 != len(y):
            msg = QMessageBox(QMessageBox.Information, '', 'Некорректный логин или пароль!', parent=self)
            msg.show()
        else:
            return True

    def clickBtn(self):
        print(1)
        teachers = sqlite3.connect("teachers.sqlite")
        cur1 = teachers.cursor()
        inp = (self.lineEdit.text(), self.lineEdit_2.text(), self.lineEdit_4.text(), self.lineEdit_3.text(), self.lineEdit_6.text(), self.lineEdit_5.text(), 'avatar_default.jpg')
        print(inp)
        if self.password(self.lineEdit_3.text(), self.lineEdit_6.text()):
            cur1.execute(f"INSERT INTO teachers (teachersurname, teachername, teachername2, teacherlogin, teacherpassword, email, avatarfile) VALUES(?, ?, ?, ?, ?, ?, ?)", inp)
            teachers.commit()
            self.teacherAddPupil()

    def teacherAddPupil(self):
        self.hide()
        self.a = TeacherAddPupil(self.lineEdit_3.text())


class TeacherAddPupil(QMainWindow):
    def __init__(self, user):
        super().__init__()
        uic.loadUi('teacher_add_class.ui', self)
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

    def generate_random_login(self):
        characters = list(string.ascii_letters + string.digits)
        Length = 8
        random.shuffle(characters)
        login = []
        for i in range(Length):
            login.append(random.choice(characters))
        random.shuffle(login)
        return "".join(login)

    def generate_random_password(self):
        characters = list(string.ascii_letters + string.digits + "!@#$%^&*()")
        Length = 8
        random.shuffle(characters)
        password = []
        for i in range(Length):
            password.append(random.choice(characters))
        random.shuffle(password)
        return "".join(password)

    def openFile(self):
        self.fname = QFileDialog.getOpenFileName(self, 'Open file')[0]
        if self.fname:
            with open(self.fname, 'r', encoding='utf-8') as f:
                data = [i.rstrip() for i in f.readlines()]

                self.tableWidget.setRowCount(len(data))
                self.tableWidget.setColumnCount(5)
                self.titles = data[0].split(';')
                for i, elem in enumerate(data):
                    for j, val in enumerate(elem.split(';')):
                        self.tableWidget.setItem(i, j, QTableWidgetItem(val))
                    if i != 0:
                        login = self.generate_random_login()
                        password = self.generate_random_password()
                        b = [login] + [password] + list(elem.split(';')) + [self.user] + ['avatar_default.jpg']
                        print(self.user)
                        print(b)
                        a = tuple(b)
                        print(a)
                        if self.cur1.execute(f"SELECT * from users where pupillogin='{a[0]}'") is not None:
                            self.cur1.execute("INSERT INTO users (pupillogin, pupilpassword, pupilname, pupilsurname, pupilemail, teacherlogin, avatarfile) VALUES(?, ?, ?, ?, ?, ?, ?)", a)
                            self.users.commit()


class TeacherEntrance(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('teacher_main.ui', self)
        self.pushButton_4.clicked.connect(self.clickBtn3)
        self.pushButton.clicked.connect(self.clickBtn9)
        self.show()

    def clickBtn3(self):
        print(1)
        self.checkInquary()

    def checkInquary(self):
        self.hide()
        self.a = TeacherCheckInquary()

    def clickBtn9(self):
        print(3)
        self.changeAvatar()

    def changeAvatar(self):
        self.a = Avatar()


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
    win = RoleWindow()
    win.show()
    app.exec_()
