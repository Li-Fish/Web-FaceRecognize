import argparse
import socket
import threading
import time
from concurrent.futures.thread import ThreadPoolExecutor
from util.common_tools import rotate_img

import cv2
import numpy as np

from face.base import face_model

model = None
data_que = None
pool = None

data_base = {
    'Fish': {
        'src': '/home/fish/work/insightface/deploy/upload_image/Fish.jpg'
    },
    'Trump': {
        'src': '/home/fish/work/insightface/deploy/upload_image/Trump.jpeg',
    },
    'Obama': {
        'src': '/home/fish/work/insightface/deploy/upload_image/Obama.jpg',
    }
}


def init_data_base():
    for key in data_base:
        file_path = data_base[key]['src']
        print(key)
        with open(file_path, 'rb') as f:
            data = f.read()
        vec, bbox = do_recognize(data)
        print(vec.T)
        data_base[key]['vec'] = vec


def search(f1):
    data = []
    for key in data_base:
        f2 = data_base[key]['vec']
        dist = np.sum(np.square(f1 - f2))
        data.append((key, dist))
    data = sorted(data, key=lambda x: x[1])
    return data


def do_recognize(data, rotate=False):
    rimg = np.asarray(bytearray(data), dtype="uint8")
    rimg = cv2.imdecode(rimg, cv2.IMREAD_COLOR)

    if rotate:
        rimg = rotate_img(rimg)

    rst = model.get_input(rimg)
    if rst is None:
        return None

    img, bbox = rst

    rst = model.get_feature(img)

    return rst, bbox


def do_detect(data, rotate=False):
    rimg = np.asarray(bytearray(data), dtype="uint8")
    rimg = cv2.imdecode(rimg, cv2.IMREAD_COLOR)

    if rotate:
        rimg = rotate_img(rimg)

    st = time.time()
    rst = model.get_input(rimg)

    if rst is None:
        return None

    img, bbox = rst

    f2 = model.get_feature(img)
    print(f2)
    end = time.time()
    print(end - st)

    return bbox[0, 0:4]


def recognize_asyn(data, rotate=False):
    rst = pool.submit(do_recognize, data, rotate)
    return rst


def recognize_syn(data, rotate=False):
    rst = recognize_asyn(data, rotate)
    return rst.result()


def init_model():
    parser = argparse.ArgumentParser(description='face model test')
    parser.add_argument('--image-size', default='112,112', help='')
    parser.add_argument('--model', default='/home/fish/PycharmProjects/Web&FaceRecognize/model/model-r100-ii/model,0',
                        help='path to load model.')
    parser.add_argument('--det-model-path', default='/home/fish/PycharmProjects/Web&FaceRecognize/model/mtcnn-model',
                        help='path to load model.')
    parser.add_argument('--cpu', default=0, type=int, help='cpu id')
    parser.add_argument('--det', default=0, type=int,
                        help='mtcnn option, 1 means using R+O, 0 means detect from begining')
    parser.add_argument('--flip', default=0, type=int, help='whether do lr flip aug')
    parser.add_argument('--threshold', default=1.24, type=float, help='ver dist threshold')
    args = parser.parse_args()

    global model
    model = face_model.FaceModel(args)


def client_thread(clientsocket):
    data = []

    lenData = clientsocket.recv(4)
    print(lenData)
    imgLen = int(lenData[0]) * (2 ** 24) + int(lenData[1]) * (2 ** 16) + \
             int(lenData[2]) * (2 ** 8) + int(lenData[3]) * (2 ** 0)
    print(lenData)
    print("img len is {}".format(imgLen))
    lenSum = 0
    while True:
        chunk = clientsocket.recv(2048)
        if len(chunk) == 0:
            break
        data.append(chunk)
        lenSum += len(chunk)
        if lenSum == imgLen:
            break

    # print(data[0])

    # cur_time = time.time()
    #
    # seed = random.randint(1, 10000)
    #
    # with open("upload_image/{}{}.jpg".format(cur_time, seed), "wb") as f:
    #     for x in data:
    #         f.write(x)
    rst = recognize_syn(b''.join(data), True)
    if rst is not None:
        f1, rect = rst
        ans = search(f1)

        print(rect)
        print(ans)

        message = '{},{},{},{}\n{}\n{}'.format(int(rect[0]), int(rect[1]), int(rect[2]), int(rect[3]), ans, ans[0][0])
        clientsocket.send(message.encode('utf8'))

    clientsocket.close()


def start_net():
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind the socket to a public host, and a well-known port
    print(socket.gethostname())
    serversocket.bind(("192.168.199.136", 11234))
    # become a server socket
    serversocket.listen(5)

    while True:
        (clientsocket, address) = serversocket.accept()
        st = time.time()
        client_thread(clientsocket)
        en = time.time()
        print(en - st)


def test():
    with open('../images/upload_image/Fish.jpg', 'rb') as f:
        data = f.read()
    f, bbox = do_recognize(data)
    # print(f)
    st = time.time()
    search(f)
    end = time.time()
    print(end - st)


if __name__ == '__main__':
    init_model()
    init_data_base()

    pool = ThreadPoolExecutor(2)

    th = threading.Thread(target=start_net, args=())
    th.start()
    while True:
        th.join()
