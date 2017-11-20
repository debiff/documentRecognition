import numpy as np

__author__ = 'Simone Biffi'


def clear_cache(f):
    def wrapper(*args, **kwargs):
        self = args[0]
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

        self._max_white_space = None
        self._min_white_space = None
        self._mean_white_space = None
        self._median_white_space = None

        return f(*args)
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

        self._max_white_space = None
        self._min_white_space = None
        self._mean_white_space = None
        self._median_white_space = None

    """
        GETTER AND SETTER
    """
    @property
    def max_area_component(self):
        if self._max_area_component is not None:
            return self._max_area_component
        self.statistics()
        return self._max_area_component

    @property
    def min_area_component(self):
        if self._min_area_component is not None:
            return self._min_area_component
        self.statistics()
        return self._min_area_component

    @property
    def mean_area(self):
        if self._mean_area is not None:
            return self._mean_area
        self.statistics()
        return self._mean_area

    @property
    def median_area(self):
        if self._median_area is not None:
            return self._median_area
        self.statistics()
        return self._median_area

    @property
    def max_width_component(self):
        if self._max_width_component is not None:
            return self._max_width_component
        self.statistics()
        return self._max_width_component

    @property
    def min_width_component(self):
        if self._min_width_component is not None:
            return self._min_width_component
        self.statistics()
        return self._min_width_component

    @property
    def mean_width(self):
        if self._mean_width is not None:
            return self._mean_width
        self.statistics()
        return self._mean_width

    @property
    def median_width(self):
        if self._median_width is not None:
            return self._median_width
        self.statistics()
        return self._median_width

    @property
    def max_height_component(self):
        if self._max_height_component is not None:
            return self._max_height_component
        self.statistics()
        return self._max_height_component

    @property
    def min_height_component(self):
        if self._min_height_component is not None:
            return self._min_height_component
        self.statistics()
        return self._min_height_component

    @property
    def mean_height(self):
        if self._mean_height is not None:
            return self._mean_height
        self.statistics()
        return self._mean_height

    @property
    def median_height(self):
        if self._median_height is not None:
            return self._median_height
        self.statistics()
        return self._median_height

    @property
    def max_white_space(self):
        if self._max_white_space is not None:
            return self._max_white_space
        self.statistics()
        return self._max_white_space

    @property
    def min_white_space(self):
        if self._min_white_space is not None:
            return self._min_white_space
        self.statistics()
        return self._min_white_space

    @property
    def mean_white_space(self):
        if self._mean_white_space is not None:
            return self._mean_white_space
        self.statistics()
        return self._mean_white_space

    @property
    def median_white_space(self):
        if self._median_white_space is not None:
            return self._median_white_space
        self.statistics()
        return self._median_white_space
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
        self._max_area_component = max(self.text_component().as_list(), key=lambda x: x.area)
        self._min_area_component = min(self.text_component().as_list(), key=lambda x: x.area)
        # self._mean_area = sum(self.as_list(), key=lambda x: x.area) / len(self.as_list())
        self._mean_area = np.mean([x.area for x in self.text_component().as_list()])
        self._median_area = np.median([x.area for x in self.text_component().as_list()])

        self._max_width_component = max(self.text_component().as_list(), key=lambda x: x.bb_width)
        self._min_width_component = min(self.text_component().as_list(), key=lambda x: x.bb_width)
        # self._mean_width = sum(self.as_list(), key=lambda x: x.bb_width) / len(self.as_list())
        self._mean_width = np.mean([x.bb_width for x in self.text_component().as_list()])
        self._median_width = np.median([x.bb_width for x in self.text_component().as_list()])

        self._max_height_component = max(self.text_component().as_list(), key=lambda x: x.bb_height)
        self._min_height_component = min(self.text_component().as_list(), key=lambda x: x.bb_height)
        # self._mean_height = sum(self.as_list(), key=lambda x: x.bb_height) / len(self.as_list())
        self._mean_height = np.mean([x.bb_height for x in self.text_component().as_list()])
        self._median_height = np.median([x.bb_height for x in self.text_component().as_list()])

        self._max_white_space = np.max([(x.nnr.xmin - x.xmax if x.nnr != 0 else 0) for x in self.text_component().as_list()])
        self._min_white_space = np.min([(x.nnr.xmin - x.xmax if x.nnr != 0 else 0) for x in self.text_component().as_list()])
        self._mean_white_space = np.mean([(x.nnr.xmin - x.xmax if x.nnr != 0 else 0) for x in self.text_component().as_list()])
        self._median_white_space = np.median([(x.nnr.xmin - x.xmax if x.nnr != 0 else 0) for x in self.text_component().as_list()])

    @clear_cache
    def manually_clear_cache(self):
        return True






