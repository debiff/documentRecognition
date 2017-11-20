__author__ = 'Simone Biffi'

import numpy as np
from MHS.classes.component_collector import ComponentCollector

class Component:

    def __init__(self, id_component, xmin, ymin, xmax, ymax, type, area=None, contour=None):
        self._id = id_component
        self._xmin = xmin
        self._ymin = ymin
        self._xmax = xmax
        self._ymax = ymax
        self._contour = contour
        self._inner_components = ComponentCollector()
        self._same_column = ComponentCollector()
        self._same_row = ComponentCollector()
        self._nr = ComponentCollector()
        self._nl = ComponentCollector()
        self._nnr = 0
        self._nnl = 0
        self._area = area
        self._type = type

        """
            CACHED
        """
        self._cached_same_row = []
        self._cached_same_column = []

    """
        GETTER AND SETTER
    """
    @property
    def id(self):
        return self._id

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
    def inner_components(self):
        return self._inner_components

    @inner_components.setter
    def inner_components(self, cc_list):
        self._inner_components.add_components(cc_list)

    @property
    def same_column(self):
        return self._same_column

    @same_column.setter
    def same_column(self, cc_list):
        self._same_column.add_components(cc_list)

    @property
    def same_row(self):
        return self._same_row

    @same_row.setter
    def same_row(self, cc_list):
        self._same_row.add_components(cc_list)

    @property
    def nr(self):
        """Return the list of nearest right neighbours. Each neighbour is a reference to a component object"""
        return self._nr

    @nr.setter
    def nr(self, comp):
        """Append a component object to the list of nearest right neighbours"""
        if comp not in self._nr.as_list():
            self._nr.add_component(comp)

    @property
    def nl(self):
        """Return the list of nearest left neighbours. Each neighbour is a reference to a component object"""
        return self._nl

    @nl.setter
    def nl(self, comp):
        """Append a component object to the list of nearest left neighbours"""
        if comp not in self._nl.as_list():
            self._nl.add_component(comp)

    @property
    def nnr(self):
        """Return the right nearest neighbour. Is a reference to a component object"""
        return self._nnr

    @nnr.setter
    def nnr(self, comp):
        """Set a component object as the right nearest neighbour"""
        self._nnr = comp

    @property
    def nnl(self):
        """Return the left nearest neighbour. Is a reference to a component object"""
        return self._nnl

    @nnl.setter
    def nnl(self, comp):
        """Set a component object as the left nearest neighbour"""
        self._nnl = comp

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, t):
        self._type = t

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
        return min(self.bb_width, self.bb_height) / max(self.bb_width, self.bb_height)

    @property
    def density(self):
        return self.area / (self.bb_width * self.bb_height)

    """
        METHOD
    """
