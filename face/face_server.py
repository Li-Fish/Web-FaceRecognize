import argparse
import threading

from face.face_engine import FaceEngine
from face.retrieve_engine import RetrieveEngine
from util.fish_socket import ServerSocket, ClientSocket


class FaceServer:
    def __init__(self, ip, port, db_engine, face_model_args=None):
        self.face_engine = FaceEngine(face_model_args)
        self.retrieve_engine = RetrieveEngine(db_engine=db_engine)
        self.net_server = ServerSocket(ip, port)

    def run(self):
        socket = self.net_server.listen()

    def process(self):
        pass

    def stop(self):
        # TODO
        raise Exception("not implement")
