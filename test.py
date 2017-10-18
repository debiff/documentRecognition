import cv2
from datetime import datetime
from rtree import index
import networkx as nx
from helper import component
import matplotlib.pyplot as plt


timer = datetime.now()

# instatiation data structure needed to store connected component
idx = index.Index()
G = nx.Graph()

img = cv2.imread('./samples/CI.jpg')
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS)


# create the bounding box and insert in Graph, rTree and rect
G, idx, rect = component.create_bb(G, contours, idx)

# find the intersection between all the bounding box
intersection = component.find_intersection(rect, idx)

# connect the chains of intersected bounding boxes that aren't totally included each other
G = component.connect_intersected(G, intersection)

# find the chain of connected bounding box (connected node in the graph)
k_edge = sorted(map(sorted, nx.k_edge_components(G, k=1)))

# unify the bounding box belonging to the same chain
component.unify_overlap(G, k_edge, img, True)

# Print the graph
#plt.subplot(121)
#nx.draw(G, with_labels=True, font_weight='bold')
#plt.show()

print((datetime.now()-timer))



