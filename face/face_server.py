import argparse
import threading
from concurrent.futures.thread import ThreadPoolExecutor
from util.fish_logger import log
from face.face_engine import FaceEngine
from face.retrieve_engine import RetrieveEngine
from util.fish_socket import ServerSocket, ClientSocket


class FaceServer:
    def __init__(self, ip, port, db_engine, face_model_args=None, threads_num=20):
        self.face_engine = FaceEngine(face_model_args)
        self.retrieve_engine = RetrieveEngine(db_engine=db_engine)
        self.net_server = ServerSocket(ip, port)
        self.pool = ThreadPoolExecutor(threads_num)

    def run(self):
        log.info('face server running')
        self.net_server.listen()

        while True:
            socket = self.net_server.accept()

            task_type = socket.recv().decode()
            if task_type == 'retrieve':
                self.pool.submit(self.process_retrieve, socket)
            else:
                log.error('except type {}'.format(task_type))

    def process_retrieve(self, socket):
        group_id = int.from_bytes(socket.recv(), byteorder='big', signed=False)
        img_data = socket.recv()

        rst = self.face_engine.recognize(img_data, True)
        if rst is not None:
            feature, bbox = rst
            user = self.retrieve_engine.research_in_group(group_id, feature)
            ans = '{} {}'.format(user.id, user.name)
            socket.send(ans)

        socket.close()

    def fe(self, data, rotate):
        rst = self.face_engine.recognize(data, True)
        if rst is None:
            return None
        return rst[0]

    def stop(self):
        # TODO
        raise Exception("not implement")
