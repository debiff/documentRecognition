__author__ = 'Simone Biffi'
import numpy as np
from helper import component as h_comp
import cv2


class Region:

    def __init__(self, xmin, ymin, xmax, ymax, component_collector):
        self._pixels = None
        self._xmin = xmin
        self._ymin = ymin
        self._xmax = xmax
        self._ymax = ymax
        self._included = component_collector

        self.draw('text')
        kernel = np.ones((5, 5), np.uint8)
        self._pixels = cv2.erode(self._pixels, kernel, iterations=1)

        """
            histograms are stored with 0 value where there aren't any black pixel
            and -1 value where there is at least one black pixel
        """
        self._vertical_histogram = None
        self._horizontal_histogram = None
        self._set_histograms()

        self._vertical_rle = []
        self._horizontal_rle = []
        self._set_rle()

        self._vertical_black, self._vertical_white = self._separate_b_w('vertical')
        self._horizontal_black, self._horizontal_white = self._separate_b_w('horizontal')

        self._vertical_median_black = np.median(self._vertical_black) if (self._vertical_black.size > 0) else 0
        self._vertical_median_white = np.median(self._vertical_white) if (self._vertical_white.size > 0) else 0
        self._vertical_variance_black = np.var(self._vertical_black) if (self._vertical_black.size > 0) else 0
        self._vertical_variance_white = np.var(self._vertical_white) if (self._vertical_white.size > 0) else 0

        self._horizontal_median_black = np.median(self._horizontal_black) if (self._horizontal_black.size > 0) else 0
        self._horizontal_median_white = np.median(self._horizontal_white) if (self._horizontal_white.size > 0) else 0
        self._horizontal_variance_black = np.var(self._horizontal_black) if (self._horizontal_black.size > 0) else 0
        self._horizontal_variance_white = np.var(self._horizontal_white) if (self._horizontal_white.size > 0) else 0

    """
            GETTER AND SETTER
    """

    @property
    def pixels(self):
        return self._pixels

    @pixels.setter
    def pixels(self, pixels):
        self._pixels = pixels

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
    def vertical_histogram(self):
        return self._vertical_histogram

    @property
    def horizontal_histogram(self):
        return self._horizontal_histogram

    @property
    def vertical_rle(self):
        return self._vertical_rle

    @property
    def horizontal_rle(self):
        return self._horizontal_rle

    @property
    def vertical_black(self):
        return self._vertical_black

    @property
    def vertical_white(self):
        return self._vertical_white

    @property
    def horizontal_black(self):
        return self._horizontal_black

    @property
    def horizontal_white(self):
        return self._horizontal_white

    @property
    def vertical_median_black(self):
        return self._vertical_median_black

    @property
    def vertical_median_white(self):
        return self._vertical_median_white

    @property
    def vertical_variance_black(self):
        return self._vertical_variance_black

    @property
    def vertical_variance_white(self):
        return self._vertical_variance_white

    @property
    def horizontal_median_black(self):
        return self._horizontal_median_black

    @property
    def horizontal_median_white(self):
        return self._horizontal_median_white

    @property
    def horizontal_variance_black(self):
        return self._horizontal_variance_black

    @property
    def horizontal_variance_white(self):
        return self._horizontal_variance_white

    @property
    def included(self):
        return self._included

    @included.setter
    def included(self, component_collector):
        self._included = component_collector

    """
        PROPERTY
    """
    @property
    def switch_to_bin(self):
        self.pixels[self.pixels == 0] = 1
        self.pixels[self.pixels == 255] = 0
        return self.pixels

    @property
    def switch_to_printable(self):
        self.pixels[self.pixels == 0] = 255
        self.pixels[self.pixels == 1] = 0
        return self.pixels

    """
        METHOD
    """
    def draw(self, type):
        if self._pixels is not None:
            return self._pixels

        self._pixels = np.ones((self.ymax - self.ymin, self.xmax - self.xmin), dtype="uint8") * 255

        component_list = self.included.text_component().as_list() if type == 'text' else self.included.non_text_component().as_list()
        for c in component_list:
            fitted_contours = c.contour
            fitted_contours[:, :, 0] -= self.xmin
            fitted_contours[:, :, 1] -= self.ymin
            cv2.drawContours(self._pixels, [fitted_contours], -1, 0, cv2.FILLED)
        return self._pixels

    def save(self, path):
        if self._pixels is None:
            self.draw('text')
        h_comp.save(self._pixels, path)

    def _set_histograms(self):
        self.pixels = self.switch_to_bin
        self._vertical_histogram = np.array(np.sum(self._pixels, axis=0), dtype='int64')
        self._vertical_histogram[self._vertical_histogram > 0] = -1
        self._horizontal_histogram = np.array(np.sum(self._pixels, axis=1), dtype='int64')
        self._horizontal_histogram[self._horizontal_histogram > 0] = -1

    def _set_rle(self):
        self._vertical_rle = self._rle('vertical')
        self._horizontal_rle = self._rle('horizontal')

    def _rle(self, direction):
        count = 1
        rle_list = []
        histogram = self._vertical_histogram if direction == 'vertical' else self._horizontal_histogram
        for i, x in np.ndenumerate(histogram):
            if i[0] + 1 > histogram.size - 1:
                rle_list.extend([x, count])
                return rle_list
            if x != histogram[i[0]+1]:
                rle_list.extend([x, count])
                count = 1
            else:
                count += 1

    def _separate_b_w(self, direction):
        rle = self._vertical_rle if direction == 'vertical' else self._horizontal_rle

        b_list = np.array([x for i, x in enumerate(rle) if (x > 0) and (rle[i - 1] < 0)])
        w_list = np.array([x for i, x in enumerate(rle) if (x > 0) and (rle[i - 1] == 0)])

        return np.array(b_list), np.array(w_list)


