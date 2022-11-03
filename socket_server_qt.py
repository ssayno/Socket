#!/usr/bin/env python3
import os
import sys
import re
from PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtGui import QCloseEvent, QStandardItem
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QSplitter, QTabWidget, QApplication
from src.output_widget import OutputWidget
from src.client_info import ClientInfo
from src.complex_cw import ComplexCw
from src.process_info import ProcessInfo
from src.single_cw import SingleCw
#
import socket
import socketserver
import queue
from Utils.split_token import Split_Token
from src.socketserver_server import MyServer

COMMAND_QUEUE = queue.Queue(1000)

main_style = '''\
QMainWindow{
font: 20px;
}
'''
class Ui(QMainWindow):
    cs_signal = pyqtSignal(str, bool)
    ps_signal = pyqtSignal(str, int)
    queue_add_signal = pyqtSignal(str)
    output_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setStyleSheet(main_style)
        self.__queue = queue.Queue()
        self.setMinimumWidth(800)
        # 主要布局
        self.cw = QSplitter(Qt.Vertical)
        self.setCentralWidget(self.cw)
        # 维护 table 更新的 json
        self.cs_dict = {}
        self.ps_dict = {}
        #
        self.add_Widget()
        # 开一个线程启动 socket 服务器
        self.start_stocket_server()
        # 连接 signal 和槽函数
        self.connect_signal_with_slot_func()
        self.connect_button_with_slot_func()

    def add_Widget(self):
        # add command tab widget
        self.add_command_tab_widget()
        # add client info widget
        self.add_client_info_widget()

    def add_command_tab_widget(self):
        self.co = QSplitter(Qt.Horizontal)
        # command part
        self.command_tab = QTabWidget()
        self.command_tab.setMaximumHeight(400)
        self.complex_cw = ComplexCw(self.command_tab)
        self.single_cw = SingleCw(self.command_tab)
        self.command_tab.addTab(self.complex_cw, "Complex command")
        self.command_tab.addTab(self.single_cw, "Single command")
        # output part
        self.output_widget = OutputWidget(self.co)
        #
        self.co.addWidget(self.command_tab)
        self.co.addWidget(self.output_widget)
        self.cw.addWidget(self.co)

    def add_client_info_widget(self):
        self.client_widget = QSplitter(Qt.Horizontal)
        self.client_widget.setMinimumHeight(500)
        #
        self.clients_info = ClientInfo()
        self.client_widget.addWidget(self.clients_info)
        #
        self.process_info = ProcessInfo(self.client_widget)
        self.client_widget.addWidget(self.process_info)
        self.cw.addWidget(self.client_widget)

    def start_stocket_server(self):
        self.socket_server = StockServer(self.__queue, self.cs_signal, self.ps_signal, parent=self)
        self.socket_server.start()
        self.output_signal.emit('Socket Server start!!')
        self.socket_server.finished.connect(
            lambda: print('Socket Server is Closed')
        )

    def connect_button_with_slot_func(self):
        self.single_cw.start_button.clicked.connect(self.add_single_command_to_queue)
        self.complex_cw.start_button.clicked.connect(self.add_complex_command_to_queue)

    def connect_signal_with_slot_func(self):
        self.cs_signal.connect(self.print_cs_signal_message)
        self.ps_signal.connect(self.print_ps_signal_message)
        self.queue_add_signal.connect(self.add_element_to_queue)
        self.output_signal.connect(self.add_output_to_listwidget)
        # sub widget signal
        self.output_widget.o_count_signal.connect(self.update_command_queue_count)

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.socket_server.server.shutdown()
        return super().closeEvent(a0)

    def print_cs_signal_message(self, hostname, _bool):
        if hostname not in self.cs_dict:
            if _bool:
                current_row = self.clients_info.model().rowCount()
                hostitem = QStandardItem(hostname)
                hostitem.setTextAlignment(Qt.AlignCenter)
                countitem = QStandardItem('0')
                countitem.setTextAlignment(Qt.AlignCenter)
                self.clients_info.model().setItem(current_row, 0, hostitem)
                self.clients_info.model().setItem(current_row, 1, countitem)
                self.cs_dict[hostname] = current_row
        else:
            if not _bool:
                row = self.cs_dict[hostname]
                oldValue= self.clients_info.model().data(
                    self.clients_info.model().index(row, 1)
                )
                newValue = int(oldValue) + 1
                countitem = QStandardItem(f'{newValue}')
                countitem.setTextAlignment(Qt.AlignCenter)
                self.clients_info.model().setItem(row, 1, countitem)
                # update command queue count
                __queue_size = self.__queue.qsize()
                self.output_signal.emit(f'命令列表长度为 {__queue_size}')
                self.output_widget.o_count_signal.emit(__queue_size)

    def print_ps_signal_message(self, hostname, _num):
        if _num == 1:
            current_row = self.process_info.model().rowCount()
            hostitem = QStandardItem(hostname)
            hostitem.setTextAlignment(Qt.AlignCenter)
            countitem = QStandardItem('Running')
            countitem.setTextAlignment(Qt.AlignCenter)
            self.process_info.model().setItem(current_row, 0, hostitem)
            self.process_info.model().setItem(current_row, 1, countitem)
            self.ps_dict[hostname] = current_row
            # update command queue usage
            # __queue_size = self.__queue.qsize()
            # self.output_signal.emit(f'命令列表长度为 {__queue_size}')
            # self.output_widget.o_count_signal.emit(__queue_size)
        elif _num == 0:
            row = self.ps_dict[hostname]
            countitem = QStandardItem('Done')
            countitem.setTextAlignment(Qt.AlignCenter)
            self.process_info.model().setItem(row, 1, countitem)
        elif _num == -1:
            row = self.ps_dict[hostname]
            countitem = QStandardItem('Fail')
            countitem.setTextAlignment(Qt.AlignCenter)
            self.process_info.model().setItem(row, 1, countitem)

    def add_single_command_to_queue(self):
        command = self.single_cw.command_input.text().strip()
        if not command:
            QMessageBox.warning(self, 'warning', '单条命令不能为空')
            return
        self.output_signal.emit(f'Single command {command}')
        for _ in range(len(self.cs_dict)):
            self.__queue.put(command)
        __queue_size = self.__queue.qsize()
        self.output_signal.emit(f'命令列表长度为 {__queue_size}')
        self.output_widget.o_count_signal.emit(__queue_size)

    def add_complex_command_to_queue(self):
        command = re.sub(r'\s', ' ', self.complex_cw.command_input.toPlainText()).strip()
        if not command:
            QMessageBox.warning(self, 'Warning', '输入的命令不能为空白')
            return
        path_text = self.complex_cw.dir_show_line.text().strip()
        if not path_text:
            QMessageBox.warning(self, 'Warning', '不要输入空白')
            return
        dir_path = os.path.normpath(path_text)
        if not os.path.exists(dir_path):
            QMessageBox.warning(self, 'Warning', '输入合法的路径')
            return
        split_token = Split_Token(
            input_path=dir_path, command=command, signal=self.queue_add_signal, parent=self
        )
        split_token.start()

    def add_element_to_queue(self, command):
        self.output_signal.emit(f'Complex command {command}')
        self.__queue.put(command)
        __queue_size = self.__queue.qsize()
        self.output_signal.emit(f'Complex command put {__queue_size}')
        self.output_widget.o_count_signal.emit(__queue_size)

    def add_output_to_listwidget(self, _str):
        self.output_widget.output_list.addItem(_str)

    def update_command_queue_count(self, count_: int):
        self.output_widget.count_label.setText(f'{count_}')

class StockServer(QThread):
    def __init__(self, _queue: queue.Queue, cs, ps, parent=None):
        self.queue = _queue
        self.client_singal = cs
        self.proces_signal = ps
        super().__init__(parent=parent)

    def run(self) -> None:
        local_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        local_socket.connect(('8.8.8.8', 80))
        lan_ip = local_socket.getsockname()[0]
        local_socket.close()
        server_obj = MyServer
        server_obj.command_queue = self.queue
        server_obj.cs = self.client_singal
        server_obj.ps = self.proces_signal
        self.server = socketserver.ThreadingTCPServer((lan_ip, 9999), server_obj)
        self.server.serve_forever()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = Ui()
    ui.show()
    sys.exit(app.exec_())
