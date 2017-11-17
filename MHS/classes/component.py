__author__ = 'Simone Biffi'


class Component():

    def __init__(self, id, xmin, ymin, xmax, ymax, contour = None):
        self.id = id
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        self.contour = contour
        self.inner_bb = None
        self.same_column = []
        self.same_row = []
        self._nr = []
        self._nl = []
        self._nnr = -1
        self._nnl = -1
        self.area = 0

    """
        GETTER AND SETTER
    """
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
    @property
    def bb_width(self):
        return self.xmax - self.xmin

    @property
    def bb_height(self):
        return self.ymax - self.ymin

    def get_boundig_box(self):
        coordinates = [(self.xmin, self.ymin), (self.xmax, self.ymax)]
        return coordinates

    def get_hw_ratio(self):
        return min(self.bb_width, self.bb_height)/ max(self.bb_width, self.bb_height)

    def get_xmin(self):
        return self.xmin

    def get_xmax(self):
        return self.xmax

    def get_ymin(self):
        return self.ymin

    def get_ymax(self):
        return self.ymax

    def get_contour(self):
        return self.contour

    def get_inner_bb(self):
        return self.inner_bb

    def get_area(self):
        return self.area

    def get_bb_area(self):
        return self.bb_height * self.bb_width









    def set_inner_bb(self, n):
        self.inner_bb = n

    def set_same_column(self, cc_list):
        self.same_column = cc_list

    def set_same_row(self, cc_list):
        self.same_row = cc_list









    def set_area(self, area):
        self.area = area
