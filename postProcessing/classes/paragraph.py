from postProcessing.classes.line_collector import LineCollector


class Paragraph:

    def __init__(self):
        self._line_collector = LineCollector()
        self._contour = None

    @property
    def line_collector(self):
        return self._line_collector

    @line_collector.setter
    def line_collector(self, line_collector):
        self._line_collector = line_collector

    @property
    def bounding_box(self):
        xmin = min(l.xmin for l in self._line_collector.as_list())
        ymin = min(l.ymin for l in self._line_collector.as_list())
        xmax = max(l.xmax for l in self._line_collector.as_list())
        ymax = max(l.ymax for l in self._line_collector.as_list())
        return [xmin, ymin, xmax, ymax]

    @property
    def contour(self):
        return self._contour

    @contour.setter
    def contour(self, contour):
        self._contour = contour