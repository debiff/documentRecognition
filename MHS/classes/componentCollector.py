__author__ = 'Simone Biffi'


class ComponentCollector:

    def __init__(self):
        self._components = []
        self._cached_bounding_boxes = None
        self._cached_dict = {}

    """
        GETTER AND SETTER
    """

    """
        PROPERTY
    """

    @property
    def as_dict(self):
        if self._cached_dict:
            return self._cached_dict

        self._cached_dict = {v.id: v for v in self._components  }
        # for val in self._components:
        #     self._cached_dict[val.id] = val
        #
        return self._cached_dict

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


