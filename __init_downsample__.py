from datetime import datetime
from rtree import index
import networkx as nx
from helper import component, image
import matplotlib.pyplot as plt


timer = datetime.now()

# data structures needed to store connected components
idx = index.Index()
G = nx.Graph()

# loads the image and convert to grayscale
img, sampled, gray = image.load_downsample_gray('./samples/icdar.jpg')

# finds component through findcontours
contours = component.find_component_downsampling(gray)


# creates the bounding box and insert in Graph, rTree and rect
G, idx, rect = component.create_bb_downsampled(G, contours, idx, 0)

# finds the intersection between all the bounding box
intersection = component.find_intersection(rect, idx)

# connects the chains of intersected bounding boxes that aren't totally included each other
G = component.connect_intersected(G, intersection)

# finds the chain of connected bounding box (connected node in the graph)
k_edge = sorted(map(sorted, nx.k_edge_components(G, k=1)))

# unify the bounding box belonging to the same chain
component.unify_overlap(G, k_edge, sampled, True)

# Print the graph
#plt.plot(121)
#nx.draw(G, with_labels=True, font_weight='bold')
#plt.show()

print((datetime.now()-timer))



