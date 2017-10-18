from physicalSegm.connectedComponent.component import Component
import cv2

# join two components and return a new component DEPRECATED
def unify(comp1, comp2):
    x1_min, x1_max = comp1.get_x_coordinates()
    y1_min, y1_max = comp1.get_y_coordinates()
    x2_min, x2_max = comp2.get_x_coordinates()
    y2_min, y2_max = comp2.get_y_coordinates()

    x_min = min(x1_min, x2_min)
    x_max = max(x1_max, x2_max)
    y_min = min(y1_min, y2_min)
    y_max = max(y1_max, y2_max)

    unified = Component(x_min, y_min, x_max, y_max)

    return unified


# check if two components are overlapped DEPRECATED
def is_overlapped(comp1, comp2):
    x1_min, x1_max = comp1.get_x_coordinates()
    y1_min, y1_max = comp1.get_y_coordinates()
    x2_min, x2_max = comp2.get_x_coordinates()
    y2_min, y2_max = comp2.get_y_coordinates()

    # checks if x1 is contained in x2
    if ((x1_min >= x2_min) and (x1_min <= x2_max)) or ((x1_max >= x2_min) and (x1_max <= x2_max)):
        if ((y1_min >= y2_min) and (y1_min <= y2_max)) or ((y1_max >= y2_min) and (y1_max <= y2_max)):
            return True
    # checks if x2 is contained in x1
    if ((x2_min >= x1_min) and (x2_min <= x1_max)) or ((x2_max >= x1_min) and (x2_max <= x1_max)):
        if ((y2_min >= y1_min) and (y2_min <= y1_max)) or ((y2_max >= y1_min) and (y2_max <= y1_max)):
            return True
    return False


# return True if G.nodes[id1] is totally contained in G.nodes[id2] or viceversa
def included(G, id1, id2):
    n1 = G.nodes[id1]
    n2 = G.nodes[id2]
    n2_in_n1 = (n1['xmin'] <= n2['xmin'] <= n2['xmax'] <= n1['xmax'] and n1['ymin'] <= n2['ymin'] <= n2['ymax'] <= n1['ymax'])
    n1_in_n2 = (n2['xmin'] <= n1['xmin'] <= n1['xmax'] <= n2['xmax'] and n2['ymin'] <= n1['ymin'] <= n1['ymax'] <= n2['ymax'])
    return not(n2_in_n1 or n1_in_n2)


# return True if it meets our criterion
def comparable(G, id1, id2):
    #n1 = G.nodes[id1]
    #n2 = G.nodes[id2]
    #same_y = (n2['ymin'] - 2) <= n1['ymin'] <= (n2['ymin'] + 2)
    #same_x = (n2['xmin'] - 2) <= n1['xmin'] <= (n2['xmin'] + 2)
    #return same_y or same_x
    return True


# return the Graph, the rTree index and the rect dictionary each containing the id of the components and the
# bounding box
def create_bb(G, contours_list, rtree_index, increment):
    rect = {}
    id_r = 0

    for cont in contours_list:
        area = cv2.contourArea(cont)
        if area > 20:
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
                id_r += 1

    return G, rtree_index, rect


# return the intersection between a dictionary of rectangles and the rectangles in the rTree index
def find_intersection(rect_dict, rtree_index):
    intersection = {}
    for i, r in rect_dict.items():
        intersection[i] = list(rtree_index.intersection(r))
    return intersection


#
def connect_intersected(G, intersection_dict):
    for node in intersection_dict:
        edges = list(filter(lambda x: included(G, x[0], x[1]) and comparable(G, x[0], x[1]),
                            map(lambda x: (node, x), intersection_dict[node])))
        G.add_edges_from(edges)
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
                cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (78, 255, 120), 2)
        else:
            if path and img is not None:
                cv2.rectangle(img, (G.nodes[c[0]]['xmin'], G.nodes[c[0]]['ymin']),
                              (G.nodes[c[0]]['xmax'], G.nodes[c[0]]['ymax']), (176, 27, 27), 2)
    if path and img is not None:
        cv2.imwrite('./samples/result.png', img)