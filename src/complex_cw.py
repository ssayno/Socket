#!/usr/bin/env python3
import os
from PyQt5.QtWidgets import (QFileDialog, QLabel, QLineEdit, QPushButton, QTextEdit,
                             QVBoxLayout, QWidget)

complex_qss = '''\
QWidget{
font: 20px;
}
QLabel{
qproperty-alignment: AlignCenter;
font: 20px;
}
QTextEdit{
padding: 5px 20px;
background-color: #C7FC98;
color: black;
}
'''
class ComplexCw(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setStyleSheet(complex_qss)
        self._setUI()
        self.connect_button_with_slot_func()

    def _setUI(self):
        _layout = QVBoxLayout()
        self.setLayout(_layout)
        #
        label = QLabel('Complex')
        _layout.addWidget(label)
        #
        self.command_input = QTextEdit(self)
        self.command_input.setFixedHeight(140)
        self.command_input.setMinimumWidth(400)
        _layout.addWidget(self.command_input)
        #
        self.dir_path = QPushButton("选择路径")
        _layout.addWidget(self.dir_path)
        self.dir_show_line = QLineEdit()
        _layout.addWidget(self.dir_show_line)
        #
        self.start_button = QPushButton("开始分发命令")
        _layout.addWidget(self.start_button)

    def connect_button_with_slot_func(self):
        self.dir_path.clicked.connect(self.ask_directory)

    def ask_directory(self):
        gets_ = QFileDialog().getExistingDirectory(self, caption='Get Directory',
                                                   directory=os.path.join(os.path.expanduser('~'), 'Desktop'))
        if gets_ == "":
            return
        self.dir_show_line.setText(gets_)
