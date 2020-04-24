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
        self.open_socket_list = Queue()

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
            except socket.timeout:
                pass

    def start_listen(self):
        self.listen_thread = threading.Thread(target=self.listen, args=())
        self.listen_thread.start()

    def close_listen(self):
        self.is_listen = False
        if self.listen_thread is not None:
            self.listen_thread.join()
