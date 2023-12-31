# coding:utf-8
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout

from qmaterialwidgets import CheckBox, setTheme, Theme


class Demo(QWidget):

    def __init__(self):
        super().__init__()
        # setTheme(Theme.DARK)
        # self.setStyleSheet('Demo{background:rgb(32,32,32)}')

        self.hBoxLayout = QHBoxLayout(self)
        self.checkBox = CheckBox('This is a check box', self)
        self.checkBox.setTristate(True)

        self.hBoxLayout.addWidget(self.checkBox, 1, Qt.AlignCenter)
        self.resize(400, 400)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Demo()
    w.show()
    app.exec()