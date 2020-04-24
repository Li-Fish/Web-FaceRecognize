import socket
import threading
from util.fish_logger import log
from queue import Queue


class ServerSocket():
    def __init__(self, ip, port):
        self.is_listen = False
        self.listen_thread = None
        self.ip = ip
        self.port = port
        self.open_socket_list = Queue(1024)

    def listen(self):
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        serversocket.bind((self.ip, self.port))
        serversocket.listen(5)

        log.info("start listen on {}:{}".format(self.ip, self.port))

        self.is_listen = True

        while self.is_listen:
            serversocket.settimeout(5)
            try:
                (clientsocket, address) = serversocket.accept()
                log.info("accept client socket {}, queue size is {}".format(address, self.open_socket_list.qsize()))
                self.open_socket_list.put(ClientSocket(clientsocket))
            except socket.timeout:
                pass

    def start_listen(self):
        self.listen_thread = threading.Thread(target=self.listen, args=())
        self.listen_thread.start()

    def close_listen(self):
        self.is_listen = False
        if self.listen_thread is not None:
            self.listen_thread.join()


class ClientSocket():
    def __init__(self, raw_socket):
        self.socket = raw_socket

    def recv(self):
        data = []

        lenData = self.socket.recv(4)
        len_data = int(lenData[0]) * (2 ** 24) + int(lenData[1]) * (2 ** 16) + \
                   int(lenData[2]) * (2 ** 8) + int(lenData[3]) * (2 ** 0)

        log.info("receive data len {}".format(len_data))

        lenSum = 0
        while True:
            chunk = self.socket.recv(2048)
            if len(chunk) == 0:
                break
            data.append(chunk)
            lenSum += len(chunk)
            if lenSum == len_data:
                break

        if lenSum != len_data:
            raise RuntimeError("接受长度不符合预期")

        return b''.join(data)

    def raw_recv(self, buf_size=2048):
        return self.socket.recv(buf_size)

    def raw_send(self, data):
        self.socket.send(data)

    def close(self):
        self.socket.close()


if __name__ == '__main__':
    test = ServerSocket("192.168.1.136", 11234)
    test.start_listen()
    while True:
        s = test.open_socket_list.get()
        data = s.recv()
        print(data)
