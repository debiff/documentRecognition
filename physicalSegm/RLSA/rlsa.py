__author__ = 'Simone Biffi'

from datetime import datetime
import numpy as np
from helper import image
import cv2
contatore  = 0

def horizontal_run_length_smoothing(x, limit) :
    horizontal = np.copy(x)
    start = 0
    count = 0
    now = 0
    for i in np.nditer(horizontal):
        if i == 0:
            if count == 0:
                start = now
            count += 1
        if i == 1:
            if count <= limit:
                horizontal[start: now] = 1
                count = 0
        now += 1
    return horizontal


def vertical_run_length_smoothing(x, limit):
    vertical = np.copy(x)
    start = 0
    count = 0
    now = 0
    for i in np.nditer(vertical):
        if i == 0:
            if count == 0:
                start = now
            count += 1
        if i == 1:
            if count <= limit:
                vertical[start: now] = 1
                count = 0
        now += 1
    return vertical

timer = datetime.now()

# loads the image and convert to grayscale
img, gray = image.load_and_gray('../../samples/bolletta3.jpg')



binary = image.binarize(gray)

binary[binary == 0] = 1 # black pixel
binary[binary == 255] = 0 # white pixel

#vertical
vertical = np.apply_along_axis(vertical_run_length_smoothing, axis=0, arr=binary, limit = 280)

#horizontal
horizontal = np.apply_along_axis(horizontal_run_length_smoothing, axis=1, arr=binary, limit = 300)

tmp = np.bitwise_and(horizontal, vertical)

result = np.apply_along_axis(horizontal_run_length_smoothing, axis=1, arr=tmp, limit = 30)

result[result == 0] = 255
result[result == 1] = 0
cv2.imwrite('../../samples/rlsa.png', result)


print((datetime.now()-timer))



