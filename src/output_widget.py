#!/usr/bin/env python3

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QListWidget, QVBoxLayout, QWidget


output_qss = '''\
QLabel{
border: 2px solid red;
qproperty-alignment: AlignCenter;
font: 20px;
}
QListWidget{
font: 20px;
padding: 5px;
}
'''
class OutputWidget(QWidget):
    o_count_signal = pyqtSignal(int)
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setStyleSheet(output_qss)
        self._setUI()

    def _setUI(self):
        label_layout = QHBoxLayout()
        # name lable
        _layout = QVBoxLayout()
        _layout.setContentsMargins(0, 0, 0, 0)
        #
        self.name_label = QLabel("命令队列的长度")
        self.name_label.setAlignment(Qt.AlignRight)
        label_layout.addWidget(self.name_label, stretch=3)
        self.count_label = QLabel('0')
        self.count_label.setAlignment(Qt.AlignLeft)
        label_layout.addWidget(self.count_label, stretch=1)
        #
        _layout.addLayout(label_layout)
        #
        self.setLayout(_layout)
        self.output_list = QListWidget()
        self.output_list.setMinimumWidth(600)
        _layout.addWidget(self.output_list)
