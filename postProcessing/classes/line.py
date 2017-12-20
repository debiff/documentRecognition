class Line:
    def __init__(self, x_min, y_min, x_max, y_max):
        self._xmin = x_min
        self._ymin = y_min
        self._xmax = x_max
        self._ymax = y_max
        self._below_lines = []

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

    @property
    def below_lines(self):
        return self._below_lines

    @below_lines.setter
    def below_lines(self, below_list):
        self._below_lines = below_list

    @property
    def bounding_box(self):
        return [self._xmin, self._ymin], [self._xmin, self._ymax], [self._xmax, self._ymax], [self._xmax, self._ymin]

    @property
    def height(self):
        return self._ymax - self._ymin