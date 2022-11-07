import sys
import traceback

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget, QApplication, QLabel

# При нажатии кнопочки q, окно закрывается


def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("error catched!:")
    print("error message:\n", tb)
    QApplication.quit()
    # or QtWidgets.QApplication.exit(0)


sys.excepthook = excepthook


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.dots = (10,10)
        self.circles = [(self.dots[0],self.dots[1], 50, 50)]

    def initUI(self):
        self.setGeometry(300, 300, 300, 300)
        self.setWindowTitle('Координаты')

        self.coords = QLabel(self)
        self.coords.setText("Координаты: None, None")
        self.coords.move(30, 30)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.coords.setText(f"Координаты: {event.x()}, {event.y()}")
            X, Y = event.x(), event.y()
            self.dots = (X, Y)
            self.circles.append((self.dots[0],self.dots[1], 50, 50))
            self.repaint()

    def paintEvent(self, event) -> None:
        qp = QPainter()
        qp.begin(self)  # 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
        for i in self.circles:
            qp.drawEllipse(i[0], i[1], i[2], i[3])
        qp.end()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
