__author__ = 'Simone Biffi'

import numpy as np
import statistics


def clear_cache(f):
    def wrapper(self, component):
        self._cached_bounding_boxes = None
        self._cached_dict = {}
        self._cached_matrix = None
        self._cached_text_components = None
        self._cached_non_text_components = None
        self._max_area_component = None
        self._min_area_component = None
        self._mean_area = None
        self._median_area = None

        self._max_width_component = None
        self._min_width_component = None
        self._mean_width = None
        self._median_width = None

        self._min_height_component = None
        self._max_height_component = None
        self._mean_height = None
        self._median_height = None

        return f(self, component)
    return wrapper

class ComponentCollector:

    def __init__(self):
        self._components = []
        self._cached_bounding_boxes = None
        self._cached_dict = {}
        self._cached_matrix = None
        self._cached_text_components = None
        self._cached_non_text_components = None

        self._max_area_component = None
        self._min_area_component = None
        self._mean_area = None
        self._median_area = None

        self._max_width_component = None
        self._min_width_component = None
        self._mean_width = None
        self._median_width = None

        self._min_height_component = None
        self._max_height_component = None
        self._mean_height = None
        self._median_height = None

    """
        GETTER AND SETTER
    """

    """
        PROPERTY
    """

    """
        METHOD
    """
    @clear_cache
    def add_component(self, component):
        self._components.append(component)

    @clear_cache
    def add_components(self, components):
        self._components.extend(components)

    @clear_cache
    def remove_component(self, component):
        self._components.pop(self._components.index(component))

    def as_list(self):
        return self._components

    def as_dict(self):
        if self._cached_dict:
            return self._cached_dict

        self._cached_dict = {v.id: v for v in self._components}
        return self._cached_dict

    def as_matrix_bb(self):
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

    def statistics(self):
        self._max_area_component = max(self.as_list(), key=lambda x: x.area)
        self._min_area_component = min(self.as_list(), key=lambda x: x.area)
        # self._mean_area = sum(self.as_list(), key=lambda x: x.area) / len(self.as_list())
        self._mean_area = np.mean([x.area for x in self.as_list()])
        self._median_area = np.median([x.area for x in self.as_list()])

        self._max_width_component = max(self.as_list(), key=lambda x: x.bb_width)
        self._min_width_component = min(self.as_list(), key=lambda x: x.bb_width)
        # self._mean_width = sum(self.as_list(), key=lambda x: x.bb_width) / len(self.as_list())
        self._mean_width = np.mean([x.bb_width for x in self.as_list()])
        self._median_width = np.median([x.bb_width for x in self.as_list()])

        self._max_height_component = max(self.as_list(), key=lambda x: x.bb_height)
        self._min_height_component = min(self.as_list(), key=lambda x: x.bb_height)
        # self._mean_height = sum(self.as_list(), key=lambda x: x.bb_height) / len(self.as_list())
        self._mean_height = np.mean([x.bb_height for x in self.as_list()])
        self._median_height = np.median([x.bb_height for x in self.as_list()])





