__author__ = 'Simone Biffi'


class Component():

    def __init__(self, id, xmin, ymin, xmax, ymax, contour):
        self.id = id
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        self.contour = contour
        self.bb_width = xmax - xmin
        self.bb_height = ymax - ymin
        self.inner_bb = None
        self.same_column = []
        self.same_row = []

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

    def get_bb_width(self):
        return self.bb_width

    def get_bb_height(self):
        return self.bb_height

    def get_contour(self):
        return self.contour

    def get_inner_bb(self):
        return self.inner_bb

    def set_inner_bb(self, n):
        self.inner_bb = n

    def set_same_column(self, cc_list):
        self.same_column = cc_list

    def set_same_row(self, cc_list):
        self.same_row = cc_list
