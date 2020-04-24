# create an INET, STREAMing socket
import random
import socket
import _thread
import time
from concurrent.futures.thread import ThreadPoolExecutor


def client_thread(clientsocket):
    # data = []
    #
    # lenData = clientsocket.recv(4)
    # print(lenData)
    # imgLen = int(lenData[0]) * (2 ** 24) + int(lenData[1]) * (2 ** 16) + \
    #          int(lenData[2]) * (2 ** 8) + int(lenData[3]) * (2 ** 0)
    # print(lenData)
    # print("img len is {}".format(imgLen))
    # lenSum = 0
    while True:
        chunk = clientsocket.recv(2048)
        if len(chunk) == 0:
            break
        # data.append(chunk)
        # lenSum += len(chunk)
        # if lenSum == imgLen:
        #     break
        print(chunk)

    # print(data[0])
    #
    # cur_time = time.time()
    #
    # seed = random.randint(1, 10000)
    #
    # with open("upload_image/{}{}.jpg".format(cur_time, seed), "wb") as f:
    #     for x in data:
    #         f.write(x)
    #
    clientsocket.close()


if __name__ == '__main__':
    executor = ThreadPoolExecutor(max_workers=5)

    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind the socket to a public host, and a well-known port
    print(socket.gethostname())
    serversocket.bind(("192.168.1.136", 11234))
    # become a server socket
    serversocket.listen(5)

    while True:
        (clientsocket, address) = serversocket.accept()
        _thread.start_new_thread(client_thread, (clientsocket,))
