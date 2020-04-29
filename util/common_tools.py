import numpy as np
import io
import cv2


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
