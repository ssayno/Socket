#!/usr/bin/env python3

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QLineEdit, QSplitter, QVBoxLayout, QWidget,
                             QPushButton)


class SingleCw(QSplitter):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setOrientation(Qt.Vertical)
        self._setUI()

    def _setUI(self):
        self.command_input = QLineEdit(self)
        self.command_input.setFixedHeight(30)
        self.addWidget(self.command_input)
        #
        self.start_button = QPushButton("开始分发命令")
        self.addWidget(self.start_button)
#
