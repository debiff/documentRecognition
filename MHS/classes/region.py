__author__ = 'Simone Biffi'

class Region:

    def __init__(self, pixels, xmin, ymin):
        self._pixels = pixels
        self._xmin = xmin
        self._ymin = ymin
        self._included = []

    """
            GETTER AND SETTER
    """
    @property
    def pixels(self):
        return self._pixels

    @pixels.setter
    def pixels(self, pixels):
        self.pixels = pixels

    @property
    def xmin(self):
        return self._xmin

    @property
    def ymin(self):
        return self._ymin
