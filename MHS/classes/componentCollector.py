__author__ = 'Simone Biffi'

import numpy as np

class ComponentCollector:

    def __init__(self):
        self._components = []
        self._cached_bounding_boxes = None
        self._cached_dict = {}
        self._cached_matrix = None

    """
        GETTER AND SETTER
    """

    """
        PROPERTY
    """

    @property
    def as_list(self):
        return self._components

    @property
    def as_dict(self):
        if self._cached_dict:
            return self._cached_dict

        self._cached_dict = {v.id: v for v in self._components}
        return self._cached_dict

    @property
    def as_matrix(self):
        if self._cached_matrix is not None:
            return self._cached_matrix

        self._cached_matrix = np.array([[v.xmin, v.ymin, v.xmax, v.ymax] for v in self._components])
        return self._cached_matrix

    """
        METHOD
    """

    def add_component(self, component):
        self._components.append(component)
        self._clear_cache()

    def remove_component(self, component):
        self._components.pop(self._components.index(component))
        self._clear_cache()

    def _clear_cache(self):
        self._cached_bounding_boxes = None
        self._cached_dict = {}
        self._cached_matrix = None


