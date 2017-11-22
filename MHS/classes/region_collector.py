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
            node = Node(identifier=uuid.uuid4(), data=region)
            self._region_tree.add_node(node, parent)