__author__ = 'Simone Biffi'

from datetime import datetime
import numpy as np
import cv2
from helper import component, image
from MHS import cc_analysis, heuristic_filter, recursive_filter
from MHS.classes import component as comp

timer = datetime.now()

# loads the image and convert to grayscale
img, gray = image.load_and_gray('./samples/icdar.jpg')
binary = image.binarize(gray)

# finds component through findcontours
contours, hierarchy = component.find_component(binary)

print((datetime.now()-timer))
comp_collector = cc_analysis.create_component_new(contours, 6, 0.15, 0.06)
print((datetime.now()-timer))