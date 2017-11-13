__author__ = 'Simone Biffi'

from datetime import datetime
import numpy as np
import cv2
from helper import component, image
from MHS import cc_analysis, heuristic_filter, recursive_filter

#todo elaborare analisi spazi bianchi

timer = datetime.now()

# loads the image and convert to grayscale
img, gray = image.load_and_gray('./samples/icdar.jpg')
binary = image.binarize(gray)

# finds component through findcontours
contours, hierarchy = component.find_component(binary)

print((datetime.now()-timer))
rect, cc_arr = cc_analysis.create_component(contours, 10, 0.06)


#Textmask = np.ones(img.shape[:2], dtype="uint8") * 255
NonTextmask = np.ones(img.shape[:2], dtype="uint8") * 255
text_element, non_text_element = heuristic_filter.heuristic_f(rect, 4)
for index, cc in text_element.items():
    if cc[0].get_inner_bb() > 1:
        cv2.drawContours(NonTextmask, [cc[0].get_contour()], -1, 0, 1)
    else:
        cv2.drawContours(NonTextmask, [cc[0].get_contour()], -1, 0, cv2.FILLED)
    #cv2.drawContours(NonTextmask, [cc[0].get_contour()], -1, 0, cv2.FILLED)
    #component.draw_rect(img, cc[0].get_xmin(), cc[0].get_ymin(), cc[0].get_xmax(), cc[0].get_ymax(), (36, 127, 227))

#for index, cc in non_text_element.items():
    #component.draw_rect(img, cc[0].get_xmin(), cc[0].get_ymin(), cc[0].get_xmax(), cc[0].get_ymax(), (12, 127, 19))

recursive_filter.run(NonTextmask, False, './samples/split/')

#cv2.imwrite('./samples/NonTextmask.png', NonTextmask)

#text = cv2.bitwise_and(binary, binary, mask=NonTextmask)
#text = cv2.bitwise_and(binary, NonTextmask)
#nonText = cv2.bitwise_and(img, img, mask = cv2.bitwise_not(Textmask))
#cv2.imwrite('./samples/textElement.png', text)
#cv2.imwrite('./samples/textElementMask.png', Textmask)
#cv2.imwrite('./samples/nontextElementMask.png', nonText)

print((datetime.now()-timer))



