import cv2
import statistics
import numpy as np
from shapely.geometry import Polygon


__author__ = 'Simone Biffi'


def total_weight(total, weight):
    total += weight
    return True

# return True if G.nodes[id1] is totally contained in G.nodes[id2] or viceversa
def included(G, id1, id2):
    n1 = G.nodes[id1]
    n2 = G.nodes[id2]
    n2_in_n1 = (n1['xmin'] <= n2['xmin'] <= n2['xmax'] <= n1['xmax'] and n1['ymin'] <= n2['ymin'] <= n2['ymax'] <= n1['ymax'])
    n1_in_n2 = (n2['xmin'] <= n1['xmin'] <= n1['xmax'] <= n2['xmax'] and n2['ymin'] <= n1['ymin'] <= n1['ymax'] <= n2['ymax'])
    return not(n2_in_n1 or n1_in_n2)


# return True if it meets our criterion
def comparable(G, id1, id2):
    n1 = G.nodes[id1]
    n2 = G.nodes[id2]
    w1 = n1['xmax'] - n1['xmin']
    w2 = n2['xmax'] - n2['xmin']
    h1 = n1['ymax'] - n1['ymin']
    h2 = n2['ymax'] - n2['ymin']
    r1 = h1/w1
    r2 = h2/w2
    if r1 - ((r1 * 0.1) <= r2 <= (r1 * 0.1) + r1) and (h2 < h1*2) and (w2 < w1*2):
        return True
    return True


# return the Graph, the rTree index and the rect dictionary each containing the id of the components and the
# bounding box
def create_bb(G, contours_list, rtree_index, increment):
    rect = {}
    id_r = 0
    list_arr = []

    for cont in contours_list:
        area = cv2.contourArea(cont)
        if area > 30:
            x, y, w, h = cv2.boundingRect(cont)
            x -= increment
            y -= increment
            w += increment * 2
            h += increment * 2
            ratio = w / h
            if (ratio > 0, 33) and (ratio < 3):
                rtree_index.insert(id_r, [x, y, x + w, y + h])
                rect[id_r] = [x, y, x + w, y + h]
                G.add_node(id_r)
                G.nodes[id_r]['xmin'] = x
                G.nodes[id_r]['ymin'] = y
                G.nodes[id_r]['xmax'] = x + w
                G.nodes[id_r]['ymax'] = y + h
                list_arr.append([x, y, x + w, y + h])
                id_r += 1
    cc_arr = np.array(list_arr)
    return G, rtree_index, rect, cc_arr


# return the intersection between a dictionary of rectangles and the rectangles in the rTree index
def find_intersection(rect_dict, rtree_index):
    intersection = {}
    for i, r in rect_dict.items():
        intersection[i] = list(rtree_index.intersection(r))
    return intersection


# return the K-nearest neighbors between a dictionary of rectangles and the rectangles in the rTree index
def find_k_nearest_neighbors(rect_dict, rtree_index, k=5):
    knn = {}
    for i, r in rect_dict.items():
        knn[i] = list(rtree_index.nearest(r, k))
    return knn


#
def connect_intersected(G, intersection_dict):
    for node in intersection_dict:
        edges = list(filter(lambda x: included(G, x[0], x[1]) and comparable(G, x[0], x[1]),
                            map(lambda x: (node, x), intersection_dict[node])))
        G.add_edges_from(edges)
    return G


def connect_with_distance(G, knn_dict):
    for node in knn_dict:
        total = 0
        edges = list(filter(lambda x: included(G, x[0], x[1]) and comparable(G, x[0], x[1]),
                            map(lambda x: (node, x, rect_distance(G, node, x)), knn_dict[node])))
        if len(edges) != 0:
            weights = list(i for _, _, i in edges)
            median = statistics.median_high(weights)
            edges = list(filter(lambda x: x[2] <= median, edges))



        G.add_weighted_edges_from(edges)
    return G


# Given a graph and a list of node connected return it unify the overlapping component
def unify_overlap(G, k_edge_list, img=None, path=False):
    for i, c in enumerate(k_edge_list):
        if len(c) != 1:
            x_min = min(list(map(lambda x: G.nodes[x]['xmin'], c)))
            x_max = max(list(map(lambda x: G.nodes[x]['xmax'], c)))
            y_min = min(list(map(lambda x: G.nodes[x]['ymin'], c)))
            y_max = max(list(map(lambda x: G.nodes[x]['ymax'], c)))
            if path and img is not None:
                cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (176, 27, 27), 2)
        else:
            if path and img is not None:
                cv2.rectangle(img, (G.nodes[c[0]]['xmin'], G.nodes[c[0]]['ymin']),
                              (G.nodes[c[0]]['xmax'], G.nodes[c[0]]['ymax']), (13, 237, 27), 2)
    if path and img is not None:
        cv2.imwrite('./samples/result.png', img)


# return the contours list of the connected component
def find_component(gray):
    ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    return contours, hierarchy[0]


# return the contours list of the connected component starting from the dawnsampled image
def find_component_downsampling(gray):

    # morphological gradient
    morph_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    grad = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, morph_kernel)

    # binarize
    _, bw = cv2.threshold(src=grad, thresh=0, maxval=255, type=cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    morph_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 1))

    # connect horizontally oriented regions
    connected = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, morph_kernel)
    mask = np.zeros(bw.shape, np.uint8)

    # find contours
    im2, contours, hierarchy = cv2.findContours(connected, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    return contours


def create_bb_downsampled(G, contours_list, rtree_index, increment):
    rect = {}
    id_r = 0

    for cont in contours_list:
        area = cv2.contourArea(cont)
        x, y, rect_width, rect_height = cv2.boundingRect(cont)
        if area > 0 :
            r = rect_width / rect_height
            if r > 0.45 and rect_height > 8 and rect_width > 8:
                x -= increment
                y -= increment
                w = rect_width + (increment * 2)
                h = rect_height + (increment * 2)
                rtree_index.insert(id_r, [x, y, x + w, y + h])
                rect[id_r] = [x, y, x + w, y + h]
                G.add_node(id_r)
                G.nodes[id_r]['xmin'] = x
                G.nodes[id_r]['ymin'] = y
                G.nodes[id_r]['xmax'] = x + w
                G.nodes[id_r]['ymax'] = y + h
                id_r += 1
    return G, rtree_index, rect


def rect_distance(G, id1, id2):
    n1 = G.nodes[id1]
    n2 = G.nodes[id2]
    vertex1 = [(n1['xmin'], n1['ymin']), (n1['xmax'], n1['ymin']), (n1['xmax'], n1['ymax']), (n1['xmin'], n1['ymax'])]
    vertex2 = [(n2['xmin'], n2['ymin']), (n2['xmax'], n2['ymin']), (n2['xmax'], n2['ymax']), (n2['xmin'], n2['ymax'])]
    poly1 = Polygon(vertex1)
    poly2 = Polygon(vertex2)
    return poly1.distance(poly2)


def draw_rect_from_list(img, rect_list):
    for c in rect_list:
        cv2.rectangle(img, (rect_list[c][0],rect_list[c][1]),(rect_list[c][2],rect_list[c][3]), (36, 127, 227), 1)
    #cv2.imwrite('./samples/result.png', img)


def draw_rect(img, xmin, ymin, xmax, ymax, color):
    cv2.rectangle(img, (xmin,ymin),(xmax,ymax), color, 2)
    #cv2.imwrite('./samples/result.png', img)


def draw_line(img, rect_list, k_edge):
    for c in rect_list:
        for e in k_edge:
            for l in e:
                cv2.line(img, (rect_list[c][0], rect_list[c][1]), (rect_list[l][0], rect_list[l][1]), (25,64,128))


def draw(image, component):
    cv2.drawContours(image, [component.contour], -1, 0, cv2.FILLED)


def save(image, path):
    cv2.imwrite(path, image)
