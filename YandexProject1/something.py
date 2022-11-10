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

apps = sqlite3.connect('apps.sqlite')
cur = apps.cursor()

pampam = list(cur.execute("SELECT * FROM apps WHERE teacherlogin='zhuy@mail.ru'"))
print(pampam)