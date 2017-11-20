
def maximum_median(region):

    included = region.included.text_component()
    area_median = included.median_area
    area_mean = included.mean_area
    t_area = max(area_mean, area_median)/min(area_mean, area_median)

    if included.max_area_component.area > (t_area * area_median):
        width_median = included.median_width
        width_mean = included.mean_width
        t_width = max(width_mean, width_median) / min(width_mean, width_median)

        height_median = included.median_height
        height_mean = included.mean_height
        t_height = max(height_mean, height_median) / min(height_mean, height_median)

        if ((included.max_area_component.bb_width == included.max_width_component.bb_width and
            included.max_area_component.bb_width > (t_width * width_median)) or
            (included.max_area_component.bb_height == included.max_height_component.bb_height and
             included.max_area_component.bb_height > (t_height * height_median))):

            r_white_space = included.max_area_component.nnr.xmin - included.max_area_component.xmax \
                if included.max_area_component.nnr != 0 else 0
            l_white_space = included.max_area_component.xmin - included.max_area_component.nnl.xmax \
                if included.max_area_component.nnr != 0 else 0
            r_l_white_space_max = max(r_white_space, l_white_space)
            r_l_white_space_min = min(r_white_space, l_white_space)

            if ((r_l_white_space_min > max(included.mean_white_space, included.mean_white_space)) and
               ((r_l_white_space_max >= included.max_white_space) or (r_l_white_space_min >=(2 * included.mean_white_space)))) or\
               (max(len(included.max_area_component.nr.as_list()), len(included.max_area_component.nl.as_list())) > 2):

                return True
    return False


def minimum_median(region):
    included = region.included.text_component()
    area_median = included.median_area
    area_mean = included.mean_area
    t_area = max(area_mean, area_median) / min(area_mean, area_median)

    if included.max_area_component.area < (area_median / t_area):
        width_median = included.median_width
        width_mean = included.mean_width
        t_width = max(width_mean, width_median) / min(width_mean, width_median)

        height_median = included.median_height
        height_mean = included.mean_height
        t_height = max(height_mean, height_median) / min(height_mean, height_median)

        if ((included.min_area_component.bb_width == included.min_width_component.bb_width and
            included.min_area_component.bb_width < (width_median / t_width)) or
            (included.min_area_component.bb_height == included.min_height_component.bb_height and
             included.min_area_component.bb_height < (height_median / t_height))):

            r_white_space = included.min_area_component.nnr.xmin - included.min_area_component.xmax \
                if included.min_area_component.nnr != 0 else 0
            l_white_space = included.min_area_component.xmin - included.min_area_component.nn.xmax \
                if included.min_area_component.nnr != 0 else 0
            r_l_white_space_max = max(r_white_space, l_white_space)
            r_l_white_space_min = min(r_white_space, l_white_space)

            if ((r_l_white_space_min > max(included.mean_white_space, included.mean_white_space)) and
                    ((r_l_white_space_max >= included.max_white_space) or (
                        r_l_white_space_min >= (2 * included.mean_white_space)))) or \
                    (max(len(included.min_area_component.nr.as_list()),
                         len(included.min_area_component.nl.as_list())) > 2):
                return True
    return False
