from physicalSegm.connectedComponent.component import Component


# join two components and return a new component
# todo posso aggiornare un albero per far si che i due componenti risultino all'interno di quello nuovo
def unify(comp1, comp2):
    x1_min, x1_max = comp1.get_x_coordinates()
    y1_min, y1_max = comp1.get_y_coordinates()
    x2_min, x2_max = comp2.get_x_coordinates()
    y2_min, y2_max = comp2.get_y_coordinates()

    x_min = min(x1_min, x2_min)
    x_max = max(x1_max, x2_max)
    y_min = min(y1_min, y2_min)
    y_max = max(y1_max, y2_max)

    unified = Component(x_min, y_min, x_max, y_max)

    return unified


# check if two components are overlapped
def is_overlapped(comp1, comp2):
    x1_min, x1_max = comp1.get_x_coordinates()
    y1_min, y1_max = comp1.get_y_coordinates()
    x2_min, x2_max = comp2.get_x_coordinates()
    y2_min, y2_max = comp2.get_y_coordinates()

    # checks if x1 is contained in x2
    if ((x1_min >= x2_min) and (x1_min <= x2_max)) or ((x1_max >= x2_min) and (x1_max <= x2_max)):
        if ((y1_min >= y2_min) and (y1_min <= y2_max)) or ((y1_max >= y2_min) and (y1_max <= y2_max)):
            return True
    # checks if x2 is contained in x1
    if ((x2_min >= x1_min) and (x2_min <= x1_max)) or ((x2_max >= x1_min) and (x2_max <= x1_max)):
        if ((y2_min >= y1_min) and (y2_min <= y1_max)) or ((y2_max >= y1_min) and (y2_max <= y1_max)):
            return True
    return False
