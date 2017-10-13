class Component:

    def __init__(self, xmin, ymin, xmax, ymax ):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax

    def get_boundig_box(self):
        coordinates = [(self.xmin, self.ymin), (self.xmax, self.ymin), (self.xmax, self.ymax), (self.xmin, self.ymax)]
        return coordinates

    def set_component_coordinates(self, xmin, ymin, xmax, ymax):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax

    def get_x_coordinates(self):
        return [self.xmin, self.xmax]

    def get_y_coordinates(self):
        return [self.ymin, self.ymax]