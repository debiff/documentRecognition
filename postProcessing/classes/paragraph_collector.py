import numpy as np
from postProcessing.classes.paragraph import Paragraph


class ParagraphCollector:

    def __init__(self):
        self._paragraph_list = []
        self._cached_matrix = None

    def add(self, paragraph):
        if len(self._paragraph_list) > 0:
            intersected = self.intersect(paragraph)
            if len(intersected) > 0:
                paragraph = self.unify(intersected, paragraph)
        self._paragraph_list.append(paragraph)
        self._cached_matrix = None

    def intersect(self, paragraph):
        xmin_less_pmin = self.as_matrix()[:, 0] <= paragraph.xmin
        pmin_less_xmax = paragraph.xmin <= self.as_matrix()[:, 2]
        pmin_x_intersect = np.bitwise_and(xmin_less_pmin, pmin_less_xmax)

        ymin_less_pmin = self.as_matrix()[:, 1] <= paragraph.ymin
        pmin_less_ymax =  paragraph.ymin <= self.as_matrix()[:, 3]
        pmin_y_intersect = np.bitwise_and(ymin_less_pmin, pmin_less_ymax)

        xmin_less_pmax = self.as_matrix()[:, 0] <= paragraph.xmax
        pmax_less_xmax = paragraph.xmax <= self.as_matrix()[:, 2]
        pmax_x_intersect = np.bitwise_and(xmin_less_pmax, pmax_less_xmax)

        ymin_less_pmax = self.as_matrix()[:, 1] <= paragraph.ymax
        pmax_less_ymax = paragraph.ymax <= self.as_matrix()[:, 3]
        pmax_y_intersect = np.bitwise_and(ymin_less_pmax, pmax_less_ymax)

        # Check the four vertex of the bounding box in clockwise order
        p_min_min_intersect = np.bitwise_and(pmin_x_intersect, pmin_y_intersect)
        p_max_min_intersect = np.bitwise_and(pmax_x_intersect, pmin_y_intersect)
        p_max_max_intersect = np.bitwise_and(pmax_x_intersect, pmax_y_intersect)
        p_min_max_intersect = np.bitwise_and(pmin_x_intersect, pmax_y_intersect)

        inters1 = np.bitwise_or(p_min_min_intersect, p_max_min_intersect)
        inters2 = np.bitwise_or(p_max_max_intersect, p_min_max_intersect)
        inters = np.bitwise_or(inters1, inters2)

        inters_id = np.where(inters)[0].tolist()
        return inters_id

    def unify(self, intersected, paragraph):
        x_min = min(paragraph.xmin, min(self.as_list()[i].xmin for i in intersected))
        x_max = max(paragraph.xmax, max(self.as_list()[i].xmax for i in intersected))
        y_min = min(paragraph.ymin, min(self.as_list()[i].ymin for i in intersected))
        y_max = max(paragraph.ymax, max(self.as_list()[i].ymax for i in intersected))
        for index in sorted(intersected, reverse=True):
            del self._paragraph_list[index]
        return Paragraph(x_min, y_min, x_max, y_max)

    def as_matrix(self):
        if self._cached_matrix is not None:
            return self._cached_matrix

        self._cached_matrix = np.array([[v.xmin, v.ymin, v.xmax, v.ymax] for v in self._paragraph_list])
        return self._cached_matrix

    def as_list(self):
        return self._paragraph_list
