import socket
import struct
import threading
from util.fish_logger import log
from queue import Queue


class ServerSocket():
    def __init__(self, ip, port):
        self.listen_thread = None
        self.ip = ip
        self.port = port
        self.listener = None
        self.server_socket = None

    def listen(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(5)

        log.info("start listen on {}:{}".format(self.ip, self.port))
        self.listener = self.do_accept()

    def do_accept(self):
        while True:
            (clientsocket, address) = self.server_socket.accept()
            log.info("accept client socket {}".format(address))
            yield ClientSocket(clientsocket)

    def accept(self):
        return next(self.listener)


class ClientSocket():
    def __init__(self, raw_socket):
        self.socket = raw_socket

    @staticmethod
    def connect_socket(ip, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        return ClientSocket(s)

    def recv(self):
        data = []

        lenData = self.socket.recv(4)
        len_data = int.from_bytes(lenData, byteorder='big', signed=False)

        log.info("receive data len {}".format(len_data))

        lenSum = 0
        while True:
            chunk = self.socket.recv(min(len_data - lenSum, 2048))
            if len(chunk) == 0:
                break
            data.append(chunk)
            lenSum += len(chunk)
            if lenSum == len_data:
                break

        if lenSum != len_data:
            raise RuntimeError("接受长度不符合预期")

        return b''.join(data)

    def send(self, data):
        if type(data) is str:
            data = bytes(data, encoding="utf8")
        len_data = struct.pack("!i", len(data))
        self.socket.send(len_data)
        self.socket.send(data)

    def raw_recv(self, buf_size=2048):
        return self.socket.recv(buf_size)

    def raw_send(self, data):
        self.socket.send(bytes(data, encoding="utf8"))

    def close(self):
        self.socket.close()


if __name__ == '__main__':
    test = ServerSocket("192.168.123.136", 11234)
    test.listen()
    while True:
        t = test.accept()
        print(t.recv())
