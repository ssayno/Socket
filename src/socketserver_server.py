#!/usr/bin/env python3
from queue import Queue
import socketserver
from PyQt5.QtCore import pyqtSignal


class MyServer(socketserver.BaseRequestHandler):
    command_queue: Queue
    cs: pyqtSignal
    ps: pyqtSignal

    def setup(self) -> None:
        return super().setup()

    def handle(self):
        conn = self.request
        conn.sendall('欢迎加入服务器'.encode())
        remote_hostname = conn.recv(1024).decode()
        self.cs.emit(remote_hostname, True)
        conn.sendall('开始监听'.encode())
        while True:
            data = conn.recv(1024).decode()
            if data == "exit":
                print("断开与%s的连接！" % (self.client_address,))
                break
            if data == 'success':
                self.ps.emit(remote_hostname, 0)
            elif data == 'fail':
                self.ps.emit(remote_hostname, -1)
            print("[来自%s的客户端的消息]：%s" % (self.client_address, data))
            if not self.command_queue.empty():
                command = self.command_queue.get()
                conn.sendall(command.encode())
                self.cs.emit(remote_hostname, False)
                self.ps.emit(remote_hostname, 1)
            else:
                command = 'exit'
                conn.sendall(command.encode())
        print('Exit server loop')
