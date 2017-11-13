import cv2

def rgb_histogram(img):

    hist = cv2.calcHist([img], [0], None, [256], [0, 256])
    return hist