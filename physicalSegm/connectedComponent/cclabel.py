#!/usr/bin/python

#
# Implements 8-connectivity connected component labeling
# 
# Algorithm obtained from "Optimizing Two-Pass Connected-Component Labeling 
# by Kesheng Wu, Ekow Otoo, and Kenji Suzuki
#

from PIL import Image, ImageDraw
import random
from itertools import product
from physicalSegm.connectedComponent.ufarray import UFarray
from physicalSegm.connectedComponent.component import Component
from helper import component


def draw_bounding_box(image, cc_list):
    draw = ImageDraw.Draw(image)

    for index, comp in cc_list.items():
        draw.polygon(comp.get_boundig_box(), None, 'red')
    return image


def connected_components_list(coordinates_list):
    cc_dict = {}
    cc_list = []
    for index, comp in coordinates_list.items():
        h = abs(comp[1] - comp[3])
        w = abs(comp[0] - comp[2])
        if (h != 0) and (w != 0):
            ratio = w/h
            area = w * h
            if (area > 20) and (area < 150000):
                if (ratio > 0,33) and (ratio < 3):
                    c_temp = Component(comp[0], comp[1], comp[2], comp[3])
                    cc_dict[index] = c_temp
                    cc_list.append(index)
    return cc_dict, cc_list


def compose(cc_dict, cc_list):

    i = 0
    j = 0
    l_cc = len(cc_list)
    mod = False
    cc_new_dict = {}

    for index, comp in cc_dict.items():
        comp.enlarge(20)

    while i < l_cc:
        j = 0
        while j < l_cc:
            if i != j:
                if component.is_overlapped(cc_dict[cc_list[i]], cc_dict[cc_list[j]]):
                    temp = component.unify(cc_dict[cc_list[i]], cc_dict[cc_list[j]])
                    cc_dict[cc_list[i]] = temp
                    cc_list.remove(cc_list[j])
                    l_cc = len(cc_list)
                    mod = True
                    break
            j += 1
        if mod:
            i = 0
            continue
        i += 1

    while i < l_cc:
        cc_new_dict[cc_list[i]] = cc_dict[cc_list[i]]
        i += 1

    return cc_new_dict, cc_list


def run(img):

    data = img.load()
    width, height = img.size
 
    # Union find data structure
    uf = UFarray()
 
    #
    # First pass
    #
 
    # Dictionary of point:label pairs
    labels = {}

    # Dictionary of point:coordinate pairs [xmin,ymin,xmax,ymax]
    bb_coordinates = {}
 
    for y, x in product(range(height), range(width)):
 
        #
        # Pixel names were chosen as shown:
        #
        #   -------------
        #   | a | b | c |
        #   -------------
        #   | d | e |   |
        #   -------------
        #   |   |   |   |
        #   -------------
        #
        # The current pixel is e
        # a, b, c, and d are its neighbors of interest
        #
        # 255 is white, 0 is black
        # White pixels part of the background, so they are ignored
        # If a pixel lies outside the bounds of the image, it default to white
        #
 
        # If the current pixel is white, it's obviously not a component...
        if data[x, y] == 255:
            pass
 
        # If pixel b is in the image and black:
        #    a, d, and c are its neighbors, so they are all part of the same component
        #    Therefore, there is no reason to check their labels
        #    so simply assign b's label to e
        elif y > 0 and data[x, y-1] == 0:
            labels[x, y] = labels[(x, y-1)]
 
        # If pixel c is in the image and black:
        #    b is its neighbor, but a and d are not
        #    Therefore, we must check a and d's labels
        elif x+1 < width and y > 0 and data[x+1, y-1] == 0:
 
            c = labels[(x+1, y-1)]
            labels[x, y] = c
 
            # If pixel a is in the image and black:
            #    Then a and c are connected through e
            #    Therefore, we must union their sets
            if x > 0 and data[x-1, y-1] == 0:
                a = labels[(x-1, y-1)]
                uf.union(c, a)
 
            # If pixel d is in the image and black:
            #    Then d and c are connected through e
            #    Therefore we must union their sets
            elif x > 0 and data[x-1, y] == 0:
                d = labels[(x-1, y)]
                uf.union(c, d)
 
        # If pixel a is in the image and black:
        #    We already know b and c are white
        #    d is a's neighbor, so they already have the same label
        #    So simply assign a's label to e
        elif x > 0 and y > 0 and data[x-1, y-1] == 0:
            labels[x, y] = labels[(x-1, y-1)]
 
        # If pixel d is in the image and black
        #    We already know a, b, and c are white
        #    so simpy assign d's label to e
        elif x > 0 and data[x-1, y] == 0:
            labels[x, y] = labels[(x-1, y)]
 
        # All the neighboring pixels are white,
        # Therefore the current pixel is a new component
        else: 
            labels[x, y] = uf.makeLabel()
 
    #
    # Second pass
    #
 
    uf.flatten()
 
    colors = {}

    # Image to display the components in a nice, colorful way
    output_img = Image.new("RGB", (width, height))
    outdata = output_img.load()

    for (x, y) in labels:
 
        # Name of the component the current point belongs to
        component = uf.find(labels[(x, y)])

        # Update the labels with correct information
        labels[(x, y)] = component
 
        # Associate a random color with this component 
        if component not in colors: 
            colors[component] = (random.randint(0,255), random.randint(0,255),random.randint(0,255))

        # Associate the bounding box coordinates with this component
        if component not in bb_coordinates:
            x_min = x
            y_min = y
            x_max = x
            y_max = y
            bb_coordinates[component] = [x_min, y_min, x_max, y_max]
        else:
            # check x_min
            if x < bb_coordinates[component][0]:
                bb_coordinates[component][0] = x

            # check x_max
            elif x > bb_coordinates[component][2]:
                bb_coordinates[component][2] = x

            # check y_min
            if y < bb_coordinates[component][1]:
                bb_coordinates[component][1] = y

            # check y_max
            elif y > bb_coordinates[component][3]:
                bb_coordinates[component][3] = y


        # Colorize the image
        outdata[x, y] = colors[component]

    return labels, output_img, bb_coordinates


def find(img):

    img = Image.fromarray(img)
    (labels, output_img, cc_coordinates) = run(img)
    cc_dict, cc_list = connected_components_list(cc_coordinates)
    #cc_dict, cc_list = compose(cc_dict, cc_list)
    output_img = draw_bounding_box(output_img, cc_dict)
    output_img.show()
    return labels, cc_list



