__author__ = 'Simone Biffi'

from datetime import datetime
import cv2
from helper import component, image
from MHS import cc_analysis, heuristic_filter, recursive_filter
from MHS.classes.region import Region
import numpy as np

timer = datetime.now()

# loads the image and convert to grayscale
img, gray = image.load_and_gray('./samples/00000201.jpg')
binary = image.binarize(gray)

kernel = np.ones((5, 5), np.uint8)
dilation = cv2.erode(binary, kernel, iterations=1)
# finds component through findcontours
contours, hierarchy = component.find_component(binary)

print((datetime.now()-timer))
comp_collector = cc_analysis.create_component_new(contours, 6, 0.15, 0.06)
print((datetime.now()-timer))

document = Region(0, 0, img.shape[1], img.shape[0], comp_collector)
heuristic_filter.heuristic_f_new(document, 4)
document.included.statistics()

document.save('./samples/teasdasd.png')
print((datetime.now()-timer))