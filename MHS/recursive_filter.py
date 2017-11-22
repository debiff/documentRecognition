import numpy as np
import math
from MHS.classes.component import Component
from MHS.classes.component_collector import ComponentCollector
from MHS.classes.region import Region
from MHS import cc_analysis


def homogeneity(node, direction):
    region = node.data
    if direction == 'vertical' and (region.vertical_variance_black > 1.3 or region.vertical_variance_white > 1.3):
        max_black = np.amax(region.vertical_black)
        max_white = np.amax(region.vertical_white)
        if ((region.vertical_variance_black > region.vertical_variance_white) and (max_black > region.vertical_median_black)) or\
            ((region.vertical_variance_white > region.vertical_variance_black) and (max_white > region.vertical_median_white)):
            return False

    if direction == 'horizontal' and region.horizontal_variance_black > 1.3 and region.horizontal_variance_white > 1.3:
        max_black = np.amax(region.horizontal_black)
        max_white = np.amax(region.horizontal_white)
        if ((region.horizontal_variance_black > region.horizontal_variance_white) and (max_black > region.horizontal_median_black)) or\
            ((region.horizontal_variance_white > region.horizontal_variance_black) and (max_white > region.horizontal_median_white)):
            return False

    return True


def split(node, direction, region_collector):
    node_id = node.identifier
    region = node.data
    splitted_region = []

    if direction == 'vertical':
        if region.vertical_variance_black > region.vertical_variance_white:
            splitted_region = split_black(region, direction)
        else:
            splitted_region = split_white(region, direction)

    elif direction == 'horizontal':
        if region.horizontal_variance_black > region.horizontal_variance_white:
            splitted_region = split_black(region, direction)
        else:
            splitted_region = split_white(region, direction)

    region_collector.add_regions(splitted_region, node_id)


def split_black(region, direction):
    rle = region.vertical_rle if direction == 'vertical' else region.horizontal_rle
    i_max_black = np.argmax(region.vertical_black) if direction == 'vertical' else np.argmax(region.horizontal_black)
    i_max_rle = ((i_max_black + 1) * 4) - 1 if rle[0] == 0 else (i_max_black * 4) + 1
    bb_list = []
    region_list = []
    count = 0
    for i in range(1, i_max_rle + 1, 2):
        if (i_max_rle == i == 1) or (i_max_rle == i + 2 == 3):
            """
            Cut first black space and region start with black space
            |------    ---   ---   ---|

            or

            Cut first black space and region start with white space
            |    -----   ---   ---|

            """
            count += rle[i] + rle[i + 2]

            region_left = [region.xmin, region.ymin, region.xmin + count, region.ymax] if direction == 'vertical' \
                else [region.xmin, region.ymin, region.xmax, region.ymin + count]
            region_right = [region.xmin + count + 1, region.ymin, region.xmax, region.ymax] if direction == 'vertical' \
                else [region.xmin, region.ymin + count + 1, region.xmax, region.ymax]

            bb_list.extend([region_left, region_right])
            break

        elif (i_max_rle == i + 2 == len(rle) - 1) or (i_max_rle + 2 == i + 2 == len(rle) - 1):
            """
            Cut last black space and region end with black space
            |    ---   ---   -----|

            or

            Cut last black space and region end with white space
            |---   ---   -----   |
            """
            region_left = [region.xmin, region.ymin, region.xmin + count, region.ymax] if direction == 'vertical' \
                else [region.xmin, region.ymin, region.xmax, region.ymin + count]
            region_right = [region.xmin + count + 1, region.ymin, region.xmax, region.ymax] if direction == 'vertical' \
                else [region.xmin, region.ymin + count + 1, region.xmax, region.ymax]

            bb_list.extend([region_left, region_right])
            break

        elif i + 2 == i_max_rle:
            """
            Cut black space among two white space
            |---   ---   ----------   ---|
            """
            count += math.ceil(rle[i] / 2)
            cut_left = count

            region_left = [region.xmin, region.ymin, region.xmin + cut_left, region.ymax] if direction == 'vertical' \
                else [region.xmin, region.ymin, region.xmax, region.ymin + cut_left]

            count += math.floor(rle[i] / 2) + rle[i + 2] + math.ceil(rle[i + 4] / 2)
            cut_right = count

            region_center = [region.xmin + cut_left + 1, region.ymin, region.xmin + cut_right, region.ymax] if direction == 'vertical' \
                else [region.xmin, region.ymin + cut_left + 1, region.xmax, region.ymin + cut_right]

            region_right = [region.xmin + cut_right + 1, region.ymin, region.xmax, region.ymax] if direction == 'vertical' \
                else [region.xmin, region.ymin + cut_right + 1, region.xmax, region.ymax]

            bb_list.extend([region_left, region_center, region_right])
            break

        else:
            count += rle[i]

    for bb in bb_list:
        bb_comp = Component(None, bb[0], bb[1], bb[2], bb[3])
        comp_collector = ComponentCollector()
        inner_components = cc_analysis.inner_bb_new(region.included.as_matrix_bb(), bb_comp)
        comp_collector.add_components([region.included.as_list()[c] for c in inner_components])
        region_list.append(Region(bb[0], bb[1], bb[2], bb[3], comp_collector))

    return region_list


def split_white(region, direction):
    rle = region.vertical_rle if direction == 'vertical' else region.horizontal_rle
    i_max_white = np.argmax(region.vertical_white) if direction == 'vertical' else np.argmax(region.horizontal_white)
    i_max_rle = ((i_max_white + 1) * 4) - 1 if rle[0] == -1 else (i_max_white * 4) + 1
    bb_list = []
    region_list = []
    count = 0
    for i in range(1, i_max_rle + 1, 2):
        if (i_max_rle == i == 1) or (i_max_rle == i == 3):
            """
            Cut first white space and region start with white space
            |       ---    ---   ---   ---|

            or

            Cut first white space and region start with black space
            |---       ---   ---   ---|
            """
            count += rle[i]
            region_left = [region.xmin, region.ymin, region.xmin + count, region.ymax] if direction == 'vertical' \
                else [region.xmin, region.ymin, region.xmax, region.ymin + count]
            region_right = [region.xmin + count + 1, region.ymin, region.xmax, region.ymax] if direction == 'vertical' \
                else [region.xmin, region.ymin + count + 1, region.xmax, region.ymax]
            bb_list.extend([region_left, region_right])
            break

        elif (i_max_rle == i == len(rle) - 1) or ((i_max_rle + 2) == (i + 2) == len(rle) - 1):
            """
            Cut last white space and region end with white space
            |---    ---   ---   ---        |

            or

            Cut first white space and region end with black space
            |---    ---   ---           ---|
            """
            region_left = [region.xmin, region.ymin, region.xmin + count, region.ymax] if direction == 'vertical' \
                else [region.xmin, region.ymin, region.xmax, region.ymin + count]
            region_right = [region.xmin + count + 1, region.ymin, region.xmax, region.ymax] if direction == 'vertical' \
                else [region.xmin, region.ymin + count + 1, region.xmax, region.ymax]
            bb_list.extend([region_left, region_right])
            break

        elif i_max_rle == i:
            """
            Cut last white space between two black space
            |---    ---            ---   ---|
            """
            region_left = [region.xmin, region.ymin, region.xmin + count, region.ymax] if direction == 'vertical' \
                else [region.xmin, region.ymin, region.xmax, region.ymin + count]
            count += rle[i]
            region_right = [region.xmin + count, region.ymin, region.xmax, region.ymax] if direction == 'vertical' \
                else [region.xmin, region.ymin + count, region.xmax, region.ymax]
            bb_list.extend([region_left, region_right])
        else:
            count += rle[i]

    for bb in bb_list:
        bb_comp = Component(None, bb[0], bb[1], bb[2], bb[3])
        comp_collector = ComponentCollector()
        inner_components = cc_analysis.inner_bb_new(region.included.as_matrix_bb(), bb_comp)
        comp_collector.add_components([region.included.as_list()[c] for c in inner_components])
        region_list.append(Region(bb[0], bb[1], bb[2], bb[3], comp_collector))

    return region_list


def recursive_splitting(node, direction, region_collector):
    if homogeneity(node, direction):
        return
    split(node, direction, region_collector)
    for leaves in region_collector.region_tree.leaves(node.identifier):
        recursive_splitting(leaves, direction, region_collector)


def multilevel_classification(node, region_collector):
    recursive_splitting(node, 'vertical', region_collector)
    for leaves in region_collector.region_tree.leaves(node.identifier):
        recursive_splitting(leaves, 'horizontal', region_collector)