import sys
import traceback
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import string
import random
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QPushButton, QApplication,
                             QWidget, QMainWindow,
                             QFileDialog, QLabel, QInputDialog,
                             QMessageBox, QLineEdit)
from PyQt5 import uic, QtWidgets
from docxtpl import DocxTemplate


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
        uic.loadUi('pupil_entrance_new.ui', self)
        self.pushButton.clicked.connect(self.clickBtn1)
        self.pushButton_2.clicked.connect(self.clickBtn2)
        self.user = None
        self.teacher = None
        self.show()

    def clickBtn1(self):
        users = sqlite3.connect("users.sqlite")
        cur1 = users.cursor()
        login = cur1.execute(f"SELECT * from users where pupillogin='{self.lineEdit_4.text().strip()}'").fetchone()
        print(login)
        if login is None:
            self.openEntranceError()
        elif login[1] == self.lineEdit_7.text().strip():
            self.user = self.lineEdit_4.text().strip()
            self.teacher = login[5]
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
        uic.loadUi('pupil_error_entrance_new.ui', self)
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
        uic.loadUi('pupil_password_recovery_new.ui', self)
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
            self.generate_random_login()
            self.generate_random_password()
            if self.send_new_password(string) == 'ok':
                msg = QMessageBox(QMessageBox.Information, '',
                                  'Письмо с новым логином и паролем \n отправлены на Вашу почту\n Если письмо не пришло, \nпроверьте папку "Спам"', parent=self)
                print(self.new_login)
                print(self.new_password)
                self.cur1.execute(f"UPDATE users SET pupillogin='{self.new_login}', pupilpassword='{self.new_password}' WHERE pupilemail='{string}'")
                self.users.commit()
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
        uic.loadUi('pupil_main_new.ui', self)
        self.users = sqlite3.connect('users.sqlite')
        self.cur1 = self.users.cursor()
        self.inf = self.cur1.execute(f"SELECT * from users where pupillogin='{user}'").fetchone()
        self.name, self.surname = self.inf[2], self.inf[3]
        self.label.setText(str(self.name + ' ' + self.surname))
        pixmap = QPixmap(self.inf[6])
        self.label_6.setPixmap(pixmap)
        self.label_6.setFixedSize(60, 60)
        self.pushButton_5.clicked.connect(self.clickBtn1)
        self.pushButton_2.clicked.connect(self.clickBtn2)
        self.pushButton_3.clicked.connect(self.clickBtn3)
        self.apps = sqlite3.connect('apps.sqlite')
        self.cur2 = self.apps.cursor()
        self.teachers = sqlite3.connect('teachers.sqlite')
        self.cur3 = self.teachers.cursor()
        apps_list = list(self.cur2.execute(f"SELECT * FROM apps WHERE pupillogin='{user}'"))
        self.reason = None
        print(apps_list)
        for i in range(len(apps_list)):
            self.tableWidget.insertRow(i)
            inf = self.cur3.execute(f"SELECT * from teachers WHERE teacherlogin='{teacher}'").fetchone()
            ava = str(inf[6])
            print(str(ava))
            user_name = str(inf[1] + ' ' + inf[0])
            status = apps_list[i][7]
            self.label = QLabel(self.tableWidget)
            pixmap = QPixmap(ava)
            self.label.setPixmap(pixmap)
            self.label.setFixedSize(60, 60)
            self.tableWidget.setCellWidget(i, 0, self.label)
            self.tableWidget.setItem(i, 1, QTableWidgetItem(user_name))
            self.btn = QPushButton(self.tableWidget)
            self.btn.setText(status)
            self.tableWidget.setCellWidget(i, 2, self.btn)
            if apps_list[i][7] == 'Отклонена':
                print(apps_list[i][6])
                self.reason = apps_list[i][6]
                self.btn.clicked.connect(self.see_reason)
        self.user = user
        self.teacher = teacher
        self.show()
        self.tableWidget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()

    def see_reason(self):
        message = f'Причина отказа:\n "{str(self.reason)}"'
        msg = QMessageBox(QMessageBox.Information, '', message, parent=self)
        msg.show()

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
        self.a = Avatar(self.user, 'u')

    def application(self):
        self.b = PupilApplication(self.user, self.teacher)


class Avatar(QWidget):
    def __init__(self, user, caller):
        super().__init__()
        uic.loadUi('all_avatar_new.ui', self)
        self.user = user
        self.caller = caller
        self.users = sqlite3.connect('users.sqlite')
        self.cur1 = self.users.cursor()
        self.teachers = sqlite3.connect('teachers.sqlite')
        self.cur2 = self.teachers.cursor()
        self.pushButton_9.clicked.connect(self.clickBtn9)
        self.pushButton_2.clicked.connect(self.clickBtn2)
        self.pushButton_4.clicked.connect(self.clickBtn4)
        self.pushButton_3.clicked.connect(self.clickBtn3)
        if self.caller == 'u':
            self.inf = self.cur1.execute(f"SELECT * from users where pupillogin='{self.user}'").fetchone()
            self.name, self.surname = self.inf[2], self.inf[3]
            self.label_5.setText(str(self.name + ' ' + self.surname))
            ava = self.cur1.execute(f"SELECT avatarfile from users WHERE pupillogin='{self.user}'").fetchone()
        else:
            self.inf = self.cur2.execute(f"SELECT * from teachers where teacherlogin='{self.user}'").fetchone()
            self.name, self.surname = self.inf[1], self.inf[0]
            self.label_5.setText(str(self.name + ' ' + self.surname))
            ava = self.cur2.execute(f"SELECT avatarfile from teachers WHERE teacherlogin='{self.user}'").fetchone()
        ava = str(ava[0])
        print(ava)
        pixmap = QPixmap(ava)
        self.label.setPixmap(pixmap)
        self.label.setFixedSize(60, 60)
        pixmap = QPixmap('avatar_default.jpg')
        self.label_2.setPixmap(pixmap)
        self.label_2.setFixedSize(60, 60)
        pixmap = QPixmap('avatar2.jpg')
        self.label_3.setPixmap(pixmap)
        self.label_3.setFixedSize(60, 60)
        pixmap = QPixmap('avatar4.jpg')
        self.label_4.setPixmap(pixmap)
        self.label_4.setFixedSize(60, 60)
        self.show()

    def clickBtn2(self):
        if self.caller == 'u':
            self.cur1.execute(f"UPDATE users SET avatarfile='avatar_default.jpg' WHERE pupillogin='{self.user}'")
            self.users.commit()
        elif self.caller == 't':
            self.cur2.execute(f"UPDATE teachers SET avatarfile='avatar_default.jpg' WHERE teacherlogin='{self.user}'")
            self.teachers.commit()
        print('avatar changed')

    def clickBtn4(self):
        if self.caller == 'u':
            self.cur1.execute(f"UPDATE users SET avatarfile='avatar2.jpg' WHERE pupillogin='{self.user}'")
            self.users.commit()
        elif self.caller == 't':
            self.cur2.execute(f"UPDATE teachers SET avatarfile='avatar2.jpg' WHERE teacherlogin='{self.user}'")
            self.teachers.commit()
        print('avatar changed')

    def clickBtn3(self):
        if self.caller == 'u':
            self.cur1.execute(f"UPDATE users SET avatarfile='avatar4.jpg' WHERE pupillogin='{self.user}'")
            self.users.commit()
        elif self.caller == 't':
            self.cur2.execute(f"UPDATE teachers SET avatarfile='avatar4.jpg' WHERE teacherlogin='{self.user}'")
            self.teachers.commit()
        print('avatar changed')

    def clickBtn9(self):
        print('no')
        self.hide()


class PupilApplication(QMainWindow):
    def __init__(self, user, teacher):
        super().__init__()
        uic.loadUi('pupil_application_new.ui', self)
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
        self.apps = sqlite3.connect('apps.sqlite')
        self.cur2 = self.apps.cursor()
        self.inf = self.cur1.execute(f"SELECT * from users where pupillogin='{self.user}'").fetchone()
        self.name, self.surname = self.inf[2], self.inf[3]
        self.label_4.setText(str(self.name + ' ' + self.surname))
        pixmap = QPixmap(self.inf[6])
        self.label_6.setPixmap(pixmap)
        self.label_6.setFixedSize(60, 60)
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
        date = self.calendarWidget.selectedDate()
        self.date = date.toString('yyyy-MM-dd')
        local_date = date.toString('dd.MM.yyyy')
        self.calendarWidget.hide()
        self.label_5.setText(local_date)

    def clickBtn3(self):
        print('application')
        users = sqlite3.connect('users.sqlite')
        cur1 = users.cursor()
        teachers = sqlite3.connect('teachers.sqlite')
        cur2 = teachers.cursor()
        apps = sqlite3.connect('apps.sqlite')
        cur4 = apps.cursor()
        if self.lineEdit.text() == '':
            msg = QMessageBox(QMessageBox.Information, '', 'Введите причину ухода.', parent=self)
            msg.show()
        elif self.lineEdit_2.text() == '':
            msg = QMessageBox(QMessageBox.Information, '', 'Введите время ухода.', parent=self)
            msg.show()
        elif self.date is None:
            msg = QMessageBox(QMessageBox.Information, '', 'Выберите дату ухода.', parent=self)
            msg.show()
        else:
            input = (self.teacher, self.user, self.lineEdit.text(), self.lineEdit_2.text(), self.date, "В рассмотрении")
            cur4.execute(
                "INSERT INTO apps (teacherlogin, pupillogin, reason, time, date, status) VALUES(?, ?, ?, ?, ?, ?)", input)
            apps.commit()
            print(self.teacher)
            mail = cur2.execute(f"SELECT email from teachers where teacherlogin='{self.teacher}'").fetchone()
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
        #m = 'pamparam'
        m = f"""Пользователь {user_name} отправил новую заявку.\nВы можете просмотреть её в своём личном кабинете."""
        subject = 'Новая заявка'
        msg = MIMEText(m, 'plain', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        print(msg)
        smtpObj.sendmail("aqwertyamkr@mail.ru", user_mail, msg.as_string())
        smtpObj.quit()
        return 'ok'

    def changeAvatar(self):
        self.a = Avatar(self.user, 'u')

    def openMainPupil(self):
        self.hide()
        self.b = PupilMain(self.user, self.teacher)


class RegWin(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('teacher_entrance_new.ui', self)
        self.pushButton.clicked.connect(self.clickBtn1)
        self.pushButton_2.clicked.connect(self.clickBtn2)
        self.a = None
        self.teacher = None
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
            self.teacher = str(login[3])
            self.openTeacherEntrance()
        print(1)

    def clickBtn2(self):
        print(1)
        self.openTeacherCheckin()

    def openTeacherEntrance(self):
        self.hide()
        self.a = TeacherEntrance(self.teacher)

    def openTeacherCheckin(self):
        self.hide()
        self.a = TeacherCheckin()


class TeacherCheckin(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('teacher_register_new.ui', self)
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
        inp = (self.lineEdit.text().strip(), self.lineEdit_2.text().strip(), self.lineEdit_4.text().strip(), self.lineEdit_3.text().strip(), self.lineEdit_6.text().strip(), self.lineEdit_5.text().strip(), 'avatar_default.jpg')
        print(inp)
        if self.password(self.lineEdit_3.text().strip(), self.lineEdit_6.text().strip()):
            teacher = self.lineEdit_3.text().strip()
            cur1.execute(f"INSERT INTO teachers (teachersurname, teachername, teachername2, teacherlogin, teacherpassword, email, avatarfile) VALUES(?, ?, ?, ?, ?, ?, ?)", inp)
            teachers.commit()
            self.teacherAddPupil(teacher)

    def teacherAddPupil(self, teacher):
        self.hide()
        self.a = TeacherAddPupil(teacher)


class TeacherAddPupil(QMainWindow):
    def __init__(self, teacher):
        super().__init__()
        uic.loadUi('teacher_add_class_new.ui', self)
        self.show()
        self.teacher = teacher
        self.pushButton.clicked.connect(self.clickBtn)
        self.pushButton_2.clicked.connect(self.openFile)
        self.users = sqlite3.connect("users.sqlite")
        self.cur1 = self.users.cursor()

    def clickBtn(self):
        print(1)
        self.openTeacherEntrance()

    def openTeacherEntrance(self):
        self.hide()
        self.a = TeacherEntrance(self.teacher)

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
    def __init__(self, teacher):
        super().__init__()
        uic.loadUi('teacher_main_new.ui', self)
        self.teacher = teacher
        self.users = sqlite3.connect('users.sqlite')
        self.cur1 = self.users.cursor()
        self.pushButton.clicked.connect(self.clickBtn9)
        self.pushButton_2.clicked.connect(self.clickBtn2)
        self.apps = sqlite3.connect('apps.sqlite')
        self.cur2 = self.apps.cursor()
        self.teachers = sqlite3.connect('teachers.sqlite')
        self.cur3 = self.teachers.cursor()
        self.inf = self.cur3.execute(f"SELECT * from teachers where teacherlogin='{self.teacher}'").fetchone()
        self.name, self.surname = self.inf[1], self.inf[0]
        self.label.setText(str(self.name + ' ' + self.surname))
        pixmap = QPixmap(self.inf[6])
        self.label_3.setPixmap(pixmap)
        self.label_3.setFixedSize(60, 60)
        apps_list = list(self.cur2.execute(f"SELECT * FROM apps WHERE teacherlogin='{self.teacher}'"))
        print(apps_list)
        for i in range(len(apps_list)):
            self.tableWidget.insertRow(i)
            local_inf = apps_list[i]
            inf = self.cur1.execute(f"SELECT * from users WHERE pupillogin='{local_inf[1]}'").fetchone()
            ava = str(inf[6])
            print(str(ava))
            user_name = str(inf[2] + ' ' + inf[3])
            status = apps_list[i][7]
            self.label = QLabel(self.tableWidget)
            pixmap = QPixmap(ava)
            self.label.setPixmap(pixmap)
            self.label.setFixedSize(60, 60)
            self.tableWidget.setCellWidget(i, 0, self.label)
            self.tableWidget.setItem(i, 1, QTableWidgetItem(user_name))
            self.btn = QPushButton(self.tableWidget)
            self.btn.setText(status)
            self.tableWidget.setCellWidget(i, 2, self.btn)
            if status == 'В рассмотрении':
                self.data = apps_list[i]
                self.btn.clicked.connect(self.checkInquary)
        self.tableWidget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()
        self.show()


    def checkInquary(self):
        self.hide()
        self.a = TeacherCheckInquary(self.teacher, self.data)

    def clickBtn9(self):
        print(3)
        self.changeAvatar()

    def changeAvatar(self):
        self.a = Avatar(self.teacher, 't')

    def clickBtn2(self):
        sys.exit()



class TeacherCheckInquary(QMainWindow):
    def __init__(self, teacher, data):
        super().__init__()
        uic.loadUi('teacher_application_new.ui', self)
        self.data = data
        self.teacher = teacher
        self.teachers = sqlite3.connect('teachers.sqlite')
        self.cur1 = self.teachers.cursor()
        self.apps = sqlite3.connect('apps.sqlite')
        self.cur2 = self.apps.cursor()
        self.inf = self.cur1.execute(f"SELECT * from teachers where teacherlogin='{self.teacher}'").fetchone()
        self.name, self.surname = self.inf[1], self.inf[0]
        self.label_4.setText(str(self.name + ' ' + self.surname))
        self.pushButton_3.clicked.connect(self.clickBtn3)
        self.pushButton_4.clicked.connect(self.clickBtn4)
        self.pushButton_6.clicked.connect(self.clickBtn6)
        self.pushButton_5.clicked.connect(self.clickBtn5)
        self.label_6.setText(self.data[2])
        self.label_9.setText(self.data[3])
        self.label_8.setText(self.data[4])
        pixmap = QPixmap(self.inf[6])
        self.label_5.setPixmap(pixmap)
        self.label_5.setFixedSize(60, 60)
        self.show()
        self.le = QLineEdit(self)
        self.le.move(130, 22)


    def clickBtn3(self):
        print(1)
        self.approveInquary()

    def approveInquary(self):
        self.hide()
        self.data = tuple(list(self.data[:5]) + [self.data[7]])
        self.cur2.execute(
            """UPDATE apps SET status="Одобрена" WHERE (teacherlogin, pupillogin, reason, time, date, status)=(?, ?, ?, ?, ?, ?)""",
            self.data)
        self.apps.commit()
        self.a = FileLoad(self.teacher, self.data)
        self.hide()

    def clickBtn4(self):
        print(1)
        self.approveInquary2()

    def approveInquary2(self):
        text, ok = QInputDialog.getText(self, 'Отклонить', 'Введите причину отказа:')

        if ok:
            print(text)
            self.le.setText(str(text))
        self.data = tuple([text] + list(self.data[:5]) + [self.data[7]])
        self.cur2.execute(
            """UPDATE apps SET teacherreason=?, status="Отклонена" WHERE (teacherlogin, pupillogin, reason, time, date, status)=(?, ?, ?, ?, ?, ?)""",
            self.data)
        self.apps.commit()
        self.hide()
        self.a = TeacherEntrance(self.teacher)

    def clickBtn6(self):
        self.a = Avatar(self.teacher, 't')

    def clickBtn5(self):
        sys.exit()


class FileLoad(QWidget):
    def __init__(self, teacher, information):
        super().__init__()
        uic.loadUi('teacher_save_file.ui', self)
        self.pushButton.clicked.connect(self.clickBtn1)
        self.show()
        self.teacher = teacher
        self.information = information
        self.teachers = sqlite3.connect('teachers.sqlite')
        self.cur1 = self.teachers.cursor()
        self.inf = self.cur1.execute(f"SELECT * from teachers where teacherlogin='{self.teacher}'").fetchone()
        self.users = sqlite3.connect('users.sqlite')
        self.cur2 = self.users.cursor()
        self.inf2 = self.cur2.execute(f"SELECT * from users where pupillogin='{self.information[1]}'").fetchone()
        self.teacher_name = ' '.join([self.inf[0], self.inf[1], self.inf[2]])
        self.pupil_name = ' '.join([self.inf2[3], self.inf2[2]])
        self.lesson_num = self.information[3]
        self.date = self.information[4]
        self.reason = self.information[2]

    def clickBtn1(self):
        doc = DocxTemplate("pass.docx")
        context = {
            'teacher_name': self.teacher_name,
            'name': self.pupil_name,
            'lesson_num': self.lesson_num,
            'date': self.date,
            'reason': self.reason
        }

        doc.render(context)
        doc.save("res.docx")
        msg = QMessageBox(QMessageBox.Information, '', 'Файл успешно скачан.', parent=self)
        msg.show()
        self.hide()
        self.a = TeacherEntrance(self.teacher)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = RoleWindow()
    win.show()
    app.exec_()
