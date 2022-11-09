import sys
import traceback
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.header    import Header

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


class TeacherEntrance(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('teacher_main_new.ui', self)
        self.pushButton_3.clicked.connect(self.clickBtn3)
        self.pushButton_6.clicked.connect(self.clickBtn6)
        self.pushButton_5.clicked.connect(self.clickBtn5)
        self.show()

    def clickBtn6(self):
        print(3)
        #self.changeAvatar()

    def clickBtn3(self):
        print(1)
        #self.checkInquary()

    def clickBtn5(self):
        print(5)
        #self.checkInquary()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = TeacherEntrance()
    win.show()
    app.exec_()