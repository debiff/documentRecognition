__author__ = 'Simone Biffi'


class Component():

    def __init__(self, id, xmin, ymin, xmax, ymax, area=None, contour=None):
        self.id = id
        self._xmin = xmin
        self._ymin = ymin
        self._xmax = xmax
        self._ymax = ymax
        self._contour = contour
        self._inner_bb = None
        self._same_column = []
        self._same_row = []
        self._nr = []
        self._nl = []
        self._nnr = -1
        self._nnl = -1
        self._area = area

    """
        GETTER AND SETTER
    """
    @property
    def xmin(self):
        return self._xmin

    @property
    def xmax(self):
        return self._xmax

    @property
    def ymin(self):
        return self._ymin

    @property
    def ymax(self):
        return self._ymax

    @property
    def area(self):
        return self._area

    @property
    def contour(self):
        return self._contour

    @property
    def inner_bb(self):
        return self._inner_bb

    @inner_bb.setter
    def inner_bb(self, n):
        self._inner_bb = n

    @property
    def same_column(self):
        return self._same_column

    @same_column.setter
    def same_column(self, cc_list):
        self._same_column = cc_list

    @property
    def same_row(self):
        return self._same_row

    @same_row.setter
    def same_row(self, cc_list):
        self._same_row = cc_list

    @property
    def nr(self):
        """Return the list of nearest right neighbours. Each neighbour is a reference to a component object"""
        return self._nr

    @nr.setter
    def nr(self, obj):
        """Append a component object to the list of nearest right neighbours"""
        if obj not in self._nr:
            self._nr.append(obj)

    @property
    def nl(self):
        """Return the list of nearest left neighbours. Each neighbour is a reference to a component object"""
        return self._nl

    @nl.setter
    def nl(self, obj):
        """Append a component object to the list of nearest left neighbours"""
        if obj not in self._nl:
            self._nl.append(obj)

    @property
    def nnr(self):
        """Return the right nearest neighbour. Is a reference to a component object"""
        return self._nnr

    @nnr.setter
    def nnr(self, index):
        """Set a component object as the right nearest neighbour"""
        self._nnr = index

    @property
    def nnl(self):
        """Return the left nearest neighbour. Is a reference to a component object"""
        return self._nnl

    @nnl.setter
    def nnl(self, index):
        """Set a component object as the left nearest neighbour"""
        self._nnl = index

    """
        PROPERTY
    """

    """
        Bounding box property
    """
    @property
    def bb_width(self):
        return self.xmax - self.xmin

    @property
    def bb_height(self):
        return self.ymax - self.ymin

    @property
    def bounding_box(self):
        coordinates = [(self.xmin, self.ymin), (self.xmax, self.ymax)]
        return coordinates

    @property
    def bb_area(self):
        return self.bb_height * self.bb_width

    @property
    def hw_ratio(self):
        return min(self.bb_width, self.bb_height)/ max(self.bb_width, self.bb_height)
