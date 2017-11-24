from treelib import Node, Tree
import uuid


class RegionCollector:

    def __init__(self):
        self._region_tree = Tree()

    """
        GETTER AND SETTER
    """
    @property
    def region_tree(self):
        return self._region_tree

    """
        PROPERTY
    """


    """
        METHOD
    """
    def add_region(self, region, parent=None):
        node = Node(identifier=uuid.uuid4(), data=region)
        self._region_tree.add_node(node, parent)

    def add_regions(self, regions, parent=None):
        for region in regions:
            if region.bin_pixel('text')[region.bin_pixel('text') == 1].size > 0 \
                    or len(region.included.text_component().as_list()) > 0:
                node = Node(identifier=uuid.uuid4(), data=region)
                self._region_tree.add_node(node, parent)