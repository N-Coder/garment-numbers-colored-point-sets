import matplotlib.pyplot as plt

from fourholes.lib import *
from fourholes.util import *

for name, quad in [
    ("nonconvex", [(0, 0), (1, 1), (0, 2), (0.5, 1)]),
    ("convex", [(0, 0), (1, 1), (0, 1), (1, 0)]),
]:
    count = 0
    for type, struct in list(all_substructures_from_quad(quad)):
        count += 1
        print("\t", name, count, type, struct)
        fig, ax = plt.subplots()
        plot_polygon(ax, struct)
        ax.set_aspect('equal')
        plt.savefig(f"{name}-{type}-{count}.png")
        plt.close(fig)
