#!/usr/bin/env python3

import socketserver
import queue
COMMAND_QUEUE = queue.Queue(1000)
for i in range(100):
    COMMAND_QUEUE.put(f'echo "{i}" && git --version')

class MyServer(socketserver.BaseRequestHandler):
    """
    必须继承socketserver.BaseRequestHandler类
    """
    def handle(self):
        """
        必须实现这个方法！
        :return:
        """
        conn = self.request         # request里封装了所有请求的数据
        conn.sendall('欢迎加入服务器'.encode())
        while True:
            data = conn.recv(1024).decode()
            if data == "exit":
                print("断开与%s的连接！" % (self.client_address,))
                break
            print("[来自%s的客户端的消息]：%s" % (self.client_address, data))
            if not COMMAND_QUEUE.empty():
                command = COMMAND_QUEUE.get()
                conn.sendall(command.encode())
            else:
                command = 'exit'
                conn.sendall(command.encode())


if __name__ == '__main__':
    # 创建一个多线程TCP服务器
    server = socketserver.ThreadingTCPServer(('10.0.24.81', 9999), MyServer)
    print("启动socketserver服务器！")
    # 启动服务器，服务器将一直保持运行状态
    server.serve_forever()
