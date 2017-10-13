from helper import image
from physicalSegm.connectedComponent import cclabel
from physicalSegm.xyCut import xyCut

img = image.load_and_show('./samples/CI.jpg', True)
binary = image.binarize(img)
label, cc_list = cclabel.find(binary)
# xyCut.valleys(cc_list)
