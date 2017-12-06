import numpy as np
from postProcessing.classes.line import Line

class LineCollector:

    def __init__(self):
        self._line_list = []
        self._cached_matrix = None

    def add_line(self, line):
        if len(self._line_list) > 0:
            overlapped = self.overlap(line)
            if len(overlapped) > 0:
                line = self.unify(overlapped, line)
        self._line_list.append(line)
        self._cached_matrix = None

    def as_matrix(self):
        if self._cached_matrix is not None:
            return self._cached_matrix

        self._cached_matrix = np.array([[v.xmin, v.ymin, v.xmax, v.ymax] for v in self._line_list])
        return self._cached_matrix

    def as_list(self):
        return self._line_list

    def overlap(self, line):
        xmin_less_linemin = self.as_matrix()[:, 0] <= line.xmin
        linemin_less_xmax = line.xmin <= self.as_matrix()[:, 2]
        and_1_2 = np.bitwise_and(xmin_less_linemin, linemin_less_xmax)

        linemin_less_xmin = line.xmin <= self.as_matrix()[:, 0]
        xmin_less_linemax = self.as_matrix()[:, 0] <= line.xmax
        and_3_4 = np.bitwise_and(linemin_less_xmin, xmin_less_linemax)

        same_row = (np.maximum(self.as_matrix()[:, 1], line.ymin) - np.minimum(self.as_matrix()[:, 3], line.ymax))  < 0
        return np.where(np.bitwise_and(np.bitwise_or(and_1_2, and_3_4), same_row))[0].tolist()

    def unify(self, overlapped, line):
        x_min = min(line.xmin, min(self.as_list()[i].xmin for i in overlapped))
        x_max = max(line.xmax, max(self.as_list()[i].xmax for i in overlapped))
        y_min = min(line.ymin, min(self.as_list()[i].ymin for i in overlapped))
        y_max = max(line.ymax, max(self.as_list()[i].ymax for i in overlapped))
        for index in sorted(overlapped, reverse=True):
            del self._line_list[index]
        return Line(x_min, y_min, x_max, y_max)
