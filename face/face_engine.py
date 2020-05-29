import argparse
from concurrent.futures.thread import ThreadPoolExecutor

from util.common_tools import rotate_img, executor_callback
import numpy as np
import cv2
from face.base import face_model
from util.fish_logger import log


class FaceEngine:
    def __init__(self, args=None, threads_num=2):
        if args is None:
            args = self.get_simple_args()

        self.model = face_model.FaceModel(args)
        self.pool = ThreadPoolExecutor(threads_num)

    def do_recognize(self, data, rotate=False):
        rimg = np.asarray(bytearray(data), dtype="uint8")
        rimg = cv2.imdecode(rimg, cv2.IMREAD_COLOR)

        sp = rimg.shape
        if sp[2] != 3 or sp[0] > 1920 or sp[1] > 1920 or sp[0] <= 0 or sp[1] <= 0:
            log.info('img format error {}'.format(sp))
            return None

        if rotate:
            rimg = rotate_img(rimg)

        rst = self.model.get_input(rimg)
        if rst is None:
            return None

        img, bbox = rst

        rst = self.model.get_feature(img)

        return rst, bbox

    def do_detect(self, data, rotate=False):
        rimg = np.asarray(bytearray(data), dtype="uint8")
        rimg = cv2.imdecode(rimg, cv2.IMREAD_COLOR)

        if rotate:
            rimg = rotate_img(rimg)

        rst = self.model.get_input(rimg)

        if rst is None:
            return None

        img, bbox = rst

        return bbox[0, 0:4]

    def recognize_asyn(self, data, rotate=False):
        rst = self.pool.submit(self.do_recognize, data, rotate)
        rst.add_done_callback(executor_callback)
        return rst

    def recognize(self, data, rotate=False):
        rst = self.recognize_asyn(data, rotate)
        return rst.result()

    @staticmethod
    def get_simple_args():
        parser = argparse.ArgumentParser(description='face model test')
        parser.add_argument('--image-size', default='112,112', help='')
        parser.add_argument('--model',
                            default='/home/fish/PycharmProjects/Web&FaceRecognize/model/model-r100-ii/model,0',
                            help='path to load model.')
        parser.add_argument('--det-model-path',
                            default='/home/fish/PycharmProjects/Web&FaceRecognize/model/mtcnn-model',
                            help='path to load model.')
        parser.add_argument('--cpu', default=0, type=int, help='cpu id')
        parser.add_argument('--det', default=0, type=int,
                            help='mtcnn option, 1 means using R+O, 0 means detect from begining')
        parser.add_argument('--flip', default=0, type=int, help='whether do lr flip aug')
        parser.add_argument('--threshold', default=1.24, type=float, help='ver dist threshold')
        args = parser.parse_args()
        return args
