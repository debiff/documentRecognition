__author__ = 'Simone Biffi'

import numpy as np


class ComponentCollector:

    def __init__(self):
        self._components = []
        self._cached_bounding_boxes = None
        self._cached_dict = {}
        self._cached_matrix = None
        self._cached_text_components = None
        self._cached_non_text_components = None

    """
        GETTER AND SETTER
    """

    """
        PROPERTY
    """

    """
        METHOD
    """

    def add_component(self, component):
        self._components.append(component)
        self._clear_cache()

    def add_components(self, components):
        self._components.extend(components)
        self._clear_cache()

    def remove_component(self, component):
        self._components.pop(self._components.index(component))
        self._clear_cache()

    def _clear_cache(self):
        self._cached_bounding_boxes = None
        self._cached_dict = {}
        self._cached_matrix = None
        self._cached_text_components = None
        self._cached_non_text_components = None

    def as_list(self):
        return self._components

    def as_dict(self):
        if self._cached_dict:
            return self._cached_dict

        self._cached_dict = {v.id: v for v in self._components}
        return self._cached_dict

    def as_matrix(self):
        if self._cached_matrix is not None:
            return self._cached_matrix

        self._cached_matrix = np.array([[v.xmin, v.ymin, v.xmax, v.ymax] for v in self._components])
        return self._cached_matrix

    def text_component(self):
        if self._cached_text_components:
            return self._cached_text_components

        self._cached_text_components = ComponentCollector()
        for c in self.as_list():
            if c.type == 'text':
                self._cached_text_components.add_component(c)

        return self._cached_text_components

    def non_text_component(self):
        if self._cached_non_text_components:
            return self._cached_non_text_components

        self._cached_non_text_components = ComponentCollector()
        for c in self.as_list():
            if c.type == 'non_text':
                self._cached_non_text_components.add_component(c)

        return self._cached_non_text_components

