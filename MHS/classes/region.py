__author__ = 'Simone Biffi'
import numpy as np
from helper import component as h_comp


class Region:

    def __init__(self, xmin, ymin, xmax, ymax, component_collector):
        self._cached_pixels = None
        self._xmin = xmin
        self._ymin = ymin
        self._xmax = xmax
        self._ymax = ymax
        self._included = component_collector

    """
            GETTER AND SETTER
    """

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
    def included(self):
        return self._included

    @included.setter
    def included(self, component_collector):
        self._included = component_collector

    """
        PROPERTY
    """


    """
        METHOD
    """
    def pixels(self, type):
        if self._cached_pixels is not None:
            return self._cached_pixels
        self._cached_pixels = np.ones((self.ymax, self.xmax), dtype="uint8") * 255
        for c in self.included.as_list():
            if c.type == type:
                h_comp.draw(self._cached_pixels, c)
        return self._cached_pixels

    def save(self, path):
        if self._cached_pixels is None:
            self.pixels('text')
        h_comp.save(self._cached_pixels, path)
