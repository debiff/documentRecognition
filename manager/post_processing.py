from postProcessing.classes.line import Line
from postProcessing.classes.line_collector import LineCollector


def is_near(comp_left, comp_right):
    distance_height = abs(comp_right.xmin - comp_left.xmax) <= 1.2 * max(comp_left.bb_height, comp_right.bb_height)
    if distance_height:
        return True
    return False


def create_line(comp_list):
    x_min = min(c.xmin for c in comp_list)
    x_max = max(c.xmax for c in comp_list)
    y_min = min(c.ymin for c in comp_list)
    y_max = max(c.ymax for c in comp_list)

    return Line(x_min, y_min, x_max, y_max)


def find_lines(text_component):
    lines = []
    for c in text_component.as_list():
        if not (any(c in l for l in lines)):
            line = []
            same_row = c.same_row.as_list()
            line.extend(comp for comp in same_row if comp.type == 'text')
            if len(line) != 0:
                if c not in line:
                    line.append(c)
                sorted_l = sorted(line, key=lambda comp: comp.xmin)
                lines.append(sorted_l)
    return lines


def text_segmentation(text_tree):
    l_collector = LineCollector()
    component_collector = text_tree.included.text_component()
    component_lines = find_lines(component_collector)
    chains = []
    for line in component_lines:
        chain_same_line = []
        chain = [line[0]]
        for c_id in range(len(line) - 1):
            if is_near(line[c_id], line[c_id + 1]):
                chain.append(line[c_id + 1])
            else:
                chain_same_line.append(create_line(chain))
                l_collector.add_line(create_line(chain))
                chain = [line[c_id + 1]]
            if c_id + 1 == len(line) - 1:
                chain_same_line.append(create_line(chain))
                l_collector.add_line(create_line(chain))
        chains.append(chain_same_line)

    return l_collector
