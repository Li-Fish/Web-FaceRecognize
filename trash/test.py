from face import face_model
import argparse
import cv2
import numpy as np

model = None


def do_recognize(rimg):
    img, bbox = model.get_input(rimg)
    f1 = model.get_feature(img)
    return f1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='face model test')
    # general
    parser.add_argument('--image-size', default='112,112', help='')
    parser.add_argument('--model', default='/home/fish/work/insightface/models/model-r100-ii/model,0',
                        help='path to load model.')
    parser.add_argument('--ga-model', default='/home/fish/work/insightface/models/gamodel-r50/model,0',
                        help='path to load model.')
    # parser.add_argument('--gpu', default=0, type=int, help='gpu id')
    parser.add_argument('--cpu', default=0, type=int, help='cpu id')
    parser.add_argument('--det', default=0, type=int,
                        help='mtcnn option, 1 means using R+O, 0 means detect from begining')
    parser.add_argument('--flip', default=0, type=int, help='whether do lr flip aug')
    parser.add_argument('--threshold', default=1.24, type=float, help='ver dist threshold')
    args = parser.parse_args()
    model = face_model.FaceModel(args)

    rimg = cv2.imread('../upload_image/Trump.jpeg')
    f1 = do_recognize(rimg)
    rimg = cv2.imread('../upload_image/Fish.jpg')
    f2 = do_recognize(rimg)
    rimg = cv2.imread('../upload_image/Trump1.jpeg')
    f3 = do_recognize(rimg)

    dist = np.sum(np.square(f1 - f2))
    print(dist)
    dist = np.sum(np.square(f1 - f3))
    print(dist)

    sim = np.dot(f1, f2.T)
    print(sim)
    sim = np.dot(f1, f3.T)
    print(sim)

    # print(f1[0:10])
    # gender, age = model.get_ga(img)
    # print(gender)
    # print(age)

    # f2 = model.get_feature(img)
    # print(f2)

    # import os
    # for root, dirs, files in os.walk("./upload_image", topdown=False):
    #     for name in files:
    #         path = os.path.join(root, name)
    #         print(path)
    #         rimg = cv2.imread(path)
    #         rimg = rotate_img(rimg)
    #         st = time.time()
    #         bbox, points = model.get_det(rimg)
    #         end = time.time()
    #         print(bbox)
    #         print(end - st)

    # while True:
    #     img = model.get_input(rimg)
    #     st = time.time()
    # bbox, points = model.get_det(rimg)
    #     end = time.time()
    #
    #     print(end - st)

    # print((int(bbox[0][0]), int(bbox[0][1])), (int(bbox[0][2]), int(bbox[0][3])))
    # cv2.rectangle(rimg, (int(bbox[0][0]), int(bbox[0][1])), (int(bbox[0][2]), int(bbox[0][3])), (0,0,255))
    # cv2.rectangle(rimg, (100, 100), (200, 200), (0,255,0))
    # cv2.rectangle(rimg, (int(bbox[1][0]), int(bbox[1][1])), (int(bbox[1][2]), int(bbox[1][3])), (0,255,0))
    # cv2.rectangle(rimg, (int(bbox[2][0]), int(bbox[2][1])), (int(bbox[2][2]), int(bbox[2][3])), (255,0,0))
    #
    # cv2.imshow("test", rimg)
    #
    # cv2.waitKey(0)
    # sys.exit(0)
    # img = cv2.imread('/raid5data/dplearn/megaface/facescrubr/112x112/Tom_Hanks/Tom_Hanks_54733.png')
    # f2 = model.get_feature(img)
    # dist = np.sum(np.square(f1-f2))
    # print(dist)
    # sim = np.dot(f1, f2.T)
    # print(sim)
    # #diff = np.subtract(source_feature, target_feature)
    # #dist = np.sum(np.square(diff),1)
