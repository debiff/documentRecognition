import numpy as np
from postProcessing.classes.paragraph import Paragraph


class ParagraphCollector:

    def __init__(self):
        self._paragraph_list = []
        self._cached_matrix = None

    def add_paragraph(self, paragraph):
        self._paragraph_list.append(paragraph)
        self._cached_matrix = None

    def add_paragraphs(self, paragraphs):
        self._paragraph_list.extend(paragraphs)
        self._cached_matrix = None

    def as_matrix(self):
        if self._cached_matrix is not None:
            return self._cached_matrix

        self._cached_matrix = np.array([[v.xmin, v.ymin, v.xmax, v.ymax] for v in self._paragraph_list])
        return self._cached_matrix

    def as_list(self):
        return self._paragraph_list
