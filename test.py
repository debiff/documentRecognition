import cv2
import numpy as np
from datetime import datetime
from rtree import index
import networkx as nx
import matplotlib.pyplot as plt


def included(G, id1, id2):
    n1 = G.nodes[id1]
    n2 = G.nodes[id2]
    n2_in_n1 = (n1['xmin'] <= n2['xmin'] <= n2['xmax'] <= n1['xmax'] and n1['ymin'] <= n2['ymin'] <= n2['ymax'] <= n1['ymax'])
    n1_in_n2 = (n2['xmin'] <= n1['xmin'] <= n1['xmax'] <= n2['xmax'] and n2['ymin'] <= n1['ymin'] <= n1['ymax'] <= n2['ymax'])
    return not(n2_in_n1 or n1_in_n2)


timer = datetime.now()
img = cv2.imread('./samples/example.png')
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
im2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_TC89_KCOS)
idx = index.Index()
rect = {}
id_r = 0
intersection = {}
G = nx.Graph()

for cont in contours:
    area = cv2.contourArea(cont)
    if area > 20:
        x, y, w, h = cv2.boundingRect(cont)
        ratio = w/h
        if (ratio > 0, 33) and (ratio < 3):
            idx.insert(id_r, [x, y, x+w, y+h])
            rect[id_r] = [x, y, x+w, y+h]
            G.add_node(id_r)
            G.nodes[id_r]['xmin'] = x
            G.nodes[id_r]['ymin'] = y
            G.nodes[id_r]['xmax'] = x + w
            G.nodes[id_r]['ymax'] = y + h
            id_r += 1


for i, r in rect.items():
    intersection[i]=list(idx.intersection(r))

for node in intersection:
    edges = list(filter(lambda x: included(G, x[0],x[1]), map(lambda x: (node, x), intersection[node])))
    G.add_edges_from(edges)


plt.subplot(121)
nx.draw(G, with_labels=True, font_weight='bold')
plt.show()
print((datetime.now()-timer).microseconds)



#cv2.imwrite('./samples/result.png', img)



