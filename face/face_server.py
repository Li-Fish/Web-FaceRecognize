import os
import time
from concurrent.futures.thread import ThreadPoolExecutor

from util.common_tools import executor_callback, array_to_bin
from util.database_engine import DatabaseEngine
from util.fish_logger import log
from face.face_engine import FaceEngine
from face.retrieve_engine import RetrieveEngine
from util.fish_socket import ServerSocket, ClientSocket


class FaceServer:
    def __init__(self, ip, port, db_engine, face_model_args=None, threads_num=1):
        self.face_engine = FaceEngine(face_model_args)
        self.db_engine = db_engine
        self.retrieve_engine = RetrieveEngine(db_engine=db_engine)
        self.net_server = ServerSocket(ip, port)
        self.pool = ThreadPoolExecutor(threads_num)

    def run(self):
        log.info('face server running')
        self.net_server.listen()

        while True:
            socket = self.net_server.accept()
            self.pool.submit(self.handle_request, socket).add_done_callback(executor_callback)

    def handle_request(self, socket):
        _type = socket.recv()
        if _type == b'0':
            self.process_retrieve(socket)
        elif _type == b'1':
            self.process_fe(socket)
        else:
            raise Exception('unknown request type {}'.format(_type))

    def process_fe(self, socket):
        img_data = socket.recv()
        rst = self.face_engine.recognize(img_data, True)
        if rst is not None:
            socket.send(array_to_bin(rst[0]))
        socket.close()

    def process_retrieve(self, socket):
        group_id = int.from_bytes(socket.recv(), byteorder='big', signed=False)
        group_code = socket.recv()
        log.info("group id is {}:{}".format(group_id, group_code))
        img_data = socket.recv()

        if not self.db_engine.check_attendance(group_id, group_code):
            log.info('error id code not match id:{} code:{}'.format(group_id, group_code.decode('utf-8')))
            socket.close()
            return

        rst = self.face_engine.recognize(img_data, True)

        if rst is not None:
            feature, bbox = rst
            user = self.retrieve_engine.research_in_group(group_id, feature)

            if user is None:
                log.info("retrieve error")
                socket.close()
                return

            date_id = self.db_engine.check_record(group_id, user['id'])
            if date_id is None:
                log.info('not match attendance date')
                socket.close()
                return

            ans = '{}\n{}'.format(user["id"], user["name"])

            log.info(ans)

            img_path = '../record_image/' + str(int(time.time() * 10 ** 7)) + '.jpg'

            img_path = os.path.abspath(img_path)

            log.info(img_path)

            open(img_path, 'wb').write(img_data)
            self.db_engine.insert_record(user["id"], group_id, img_path, feature, date_id)

            socket.raw_send(ans)

        socket.close()

    def stop(self):
        # TODO
        raise Exception("not implement")


if __name__ == '__main__':
    db_engine = DatabaseEngine()
    face_server = FaceServer("192.168.123.136", 11234, db_engine)
    face_server.run()
