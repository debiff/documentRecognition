import cv2
import numpy as np

img = cv2.imread('./samples/CI.jpg')
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
im2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_TC89_KCOS)

for cont in zip(contours, hierarchy):
    area = cv2.contourArea(cont[0])

    if (area > 20):
        x, y, w, h = cv2.boundingRect(cont[0])
        ratio = w/h
        if (ratio > 0, 33) and (ratio < 3):
            cv2.rectangle(img, (x, y), (x + w, y + h), (78,255,120), 2)
            #cv2.rectangle(img, (5,5), (200,200), 50, 2)
    cv2.drawContours(img, [cont[0]], 0, (0, 0 ,0), 1)



cv2.imwrite('./samples/result.png', img)



