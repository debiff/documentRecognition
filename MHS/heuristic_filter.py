__author__ = 'Simone Biffi'


# rect_list è un dizionario di oggetti component
def heuristic_f(cc_dict, t_inside):
    text_element = {}
    non_text_element = {}
    for index, cc in cc_dict.items():
        if (cc[0].inner_components > t_inside):
            non_text_element[index] = cc
        else:
            text_element[index] = cc
    return text_element, non_text_element


def heuristic_f_new(component_collector, t_inside):
    for cc in component_collector.as_list():
        if len(cc.inner_components.as_list()) > t_inside:
            cc.type = 'non_text'
