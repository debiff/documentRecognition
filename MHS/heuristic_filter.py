__author__ = 'Simone Biffi'


# rect_list è un dizionario di oggetti component
def heuristic_f(cc_dict, t_inside):
    text_element = {}
    non_text_element = {}
    for index, cc in cc_dict.items():
        if (cc[0].inner_bb > t_inside):
            non_text_element[index] = cc
        else:
            text_element[index] = cc
    return text_element, non_text_element
