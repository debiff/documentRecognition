class NonTextElementCollector:
    def __init__(self):
        self._non_text_element = []
        self._cached_matrix = None

    def add_paragraph(self, paragraph):
        self._non_text_element.append(paragraph)

    def as_list(self):
        return self._non_text_element
