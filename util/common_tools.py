from random import choice

import numpy as np
import io
import cv2

from util.fish_logger import log


def executor_callback(worker):
    worker_exception = worker.exception()
    if worker_exception:
        log.exception("Worker return exception: {}".format(worker_exception))


def rotate_img(img, angle=90):
    # 获取输入图像的信息，生成旋转操作所需的参数（padding: 指定零填充的宽度； canter: 指定旋转的轴心坐标）
    h, w = img.shape[:2]
    padding = (w - h) // 2
    center = (w // 2, w // 2)

    # 在原图像两边做对称的零填充，使得图片由矩形变为方形
    img_padded = np.zeros(shape=(w, w, 3), dtype=np.uint8)
    img_padded[padding:padding + h, :, :] = img

    # 逆时针-90°(即顺时针90°)旋转填充后的方形图片
    M = cv2.getRotationMatrix2D(center, angle, 1)
    rotated_padded = cv2.warpAffine(img_padded, M, (w, w))

    # 从旋转后的图片中截取出我们需要的部分，作为最终的输出图像
    output = rotated_padded[:, padding:padding + h, :]
    return output


def array_to_bin(data):
    out = io.BytesIO()
    np.save(out, data)
    out.seek(0)
    return out.read()


def bin_to_array(data):
    out = io.BytesIO(data)
    out.seek(0)
    return np.load(out)


def generator_random_code(lenght, char_table=None):
    seed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if char_table is not None:
        seed = char_table
    sa = []
    for i in range(lenght):
        sa.append(choice(seed))
    salt = ''.join(sa)
    return salt


if __name__ == '__main__':
    # z = np.zeros((2, 2), dtype=[('x', 'i4'), ('y', 'i4')])
    # z = array_to_bin(z)
    # print(z)
    print(generator_random_code(10))