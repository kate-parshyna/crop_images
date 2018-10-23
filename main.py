import os
import cv2
import numpy
import argparse

from PIL import Image
from convert import  convert_png


def find_if_close(cnt1,cnt2):
    row1,row2 = cnt1.shape[0],cnt2.shape[0]
    for i in range(row1):
        for j in range(row2):
            dist = numpy.linalg.norm(cnt1[i]-cnt2[j])
            if abs(dist) < 25:
                return True
            elif i==row1-1 and j==row2-1:
                return False


def convert_to_jpg(path, image_name):
    extension = os.path.splitext(image_name)[1]
    if extension.lower() == '.png':
        try:
            im = Image.open(path + image_name)
            bg = Image.new("RGB", im.size, (255, 255, 255))
            bg.paste(im, (0, 0), im)
            open_cv_image = numpy.array(bg)
            open_cv_image = open_cv_image[:, :, ::-1].copy()
            return open_cv_image
        except ValueError:
            return cv2.imread(path + image_name)
    else:
        return cv2.imread(path + image_name)


def get_contours(contours):
    LENGTH = len(contours)
    status = numpy.zeros((LENGTH, 1))
    for i, cnt1 in enumerate(contours):
        x = i
        if i != LENGTH - 1:
            for j, cnt2 in enumerate(contours[i + 1:]):
                x = x + 1
                dist = find_if_close(cnt1, cnt2)
                if dist == True:
                    val = min(status[i], status[x])
                    status[x] = status[i] = val
                else:
                    if status[x] == status[i]:
                        status[x] = i + 1
    unified = []
    maximum = int(status.max()) + 1
    for i in range(maximum):
        pos = numpy.where(status == i)[0]
        if pos.size != 0:
            cont = numpy.vstack(contours[i] for i in pos)
            hull = cv2.convexHull(cont)
            unified.append(hull)
    return unified


def crop_image(image_name):
    first_im = cv2.imread(path+'/'+image_name, cv2.IMREAD_UNCHANGED)
    image = convert_to_jpg(path, image_name)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edge = cv2.Canny(gray, 10, 250)
    kernel = numpy.ones((5, 5), numpy.uint8)
    dilation = cv2.dilate(edge, kernel, iterations=1)
    closing = cv2.morphologyEx(dilation, cv2.MORPH_CLOSE, kernel)
    contours = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1]
    unified = get_contours(contours)
    result_points = []
    res_c = []
    for c in unified:
        res_c.append(len(c))
    max_c = max(res_c)
    new_unified = []
    for c in unified:
        if len(c) > max_c * 0.5:
            new_unified.append(c)
            (x, y, w, h) = cv2.boundingRect(c)
            result_points.append([[x,y],[x + w, y + h]])
    min_x = []
    min_y = []
    max_x = []
    max_y = []
    for i in result_points:
        min_x.append(i[0][0])
        min_y.append(i[0][1])
        max_x.append(i[1][0])
        max_y.append(i[1][1])
    extension = os.path.splitext(image_name)[1]
    if len(new_unified) == 1:
        #crop = first_im[y:y + h, x:x + w]
        print('first point:', x,";",y)
        print('second point:', x,";",h)
        print('third point:', w,";",y)
        print('fourth point:', w,";",h)
        #cv2.imwrite(result_path +'/' + image_name, crop)
        # if extension.lower() == '.png':
        #     convert_png(result_path +'/' + image_name)
    else:
        x = min(min_x)
        y = min(min_y)
        w = max(max_x)
        h = max(max_y)
        #crop = first_im[y:h, x:w]
        print('first point:', x,";",y)
        print('second point:', x,";",h)
        print('third point:', w,";",y)
        print('fourth point:', w,";",h)
        #cv2.imwrite(result_path +'/' + image_name, crop)
        # if extension.lower() == '.png':
        #     convert_png(result_path +'/' + image_name)

parser = argparse.ArgumentParser()
parser.add_argument("--path", type=str,
                    help="path to folder with images")
args = parser.parse_args()
path = args.path+'/'

# result_path = 'results'
# if not os.path.exists(result_path):
#     os.makedirs(result_path)

for image_name in os.listdir(path):
    print(image_name)
    crop_image(image_name)