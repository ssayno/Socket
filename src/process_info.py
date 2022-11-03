#!/usr/bin/env python3
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QHeaderView, QTableView

process_info_qss = '''\
QTableView{
font: 20px;
}
QHeaderView{
font: 16px;
}
'''


class ProcessInfo(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setStyleSheet(process_info_qss)
        self.__setUI()

    def __setUI(self):
        model = QStandardItemModel()
        model.setColumnCount(2)
        self.setModel(model)
        model.setHorizontalHeaderLabels(['HostName', 'Status'])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
