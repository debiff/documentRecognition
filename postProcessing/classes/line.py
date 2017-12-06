
class Line:
    def __init__(self, x_min, y_min, x_max, y_max):
        self._xmin = x_min
        self._ymin = y_min
        self._xmax = x_max
        self._ymax = y_max

    @property
    def xmin(self):
        return self._xmin

    @property
    def ymin(self):
        return self._ymin

    @property
    def xmax(self):
        return self._xmax

    @property
    def ymax(self):
        return self._ymax