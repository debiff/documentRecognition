class Component:

    def __init__(self, xmin, ymin, xmax, ymax ):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        self.n_right = None
        self.n_up = None
        self.n_left = None
        self.n_down = None

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

    def enlarge(self, amount):
        self.set_component_coordinates(self.xmin-(amount/2), self.ymin-(amount/2), self.xmax+(amount/2),
                                       self.ymax+(amount/2))

    def get_xmin(self):
        return self.xmin

    def get_xmax(self):
        return self.xmax

    def get_ymin(self):
        return self.ymin

    def get_ymax(self):
        return self.ymax