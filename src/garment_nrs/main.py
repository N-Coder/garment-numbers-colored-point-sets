import json
import random
import sys

import click
from tqdm import tqdm

from garment_nrs.lib import CONVEX_SHAPES, NONCONVEX_SHAPES, find_empty_monochromatic_substructures
from garment_nrs.util import *


@click.command()
@click.argument("file", type=click.File("r"))
@click.option("-o", "--only",
              type=click.Choice([*CONVEX_SHAPES.keys(), *NONCONVEX_SHAPES.keys()], False),
              multiple=True, help="The types of substructures for which to check, can be specified multiple times.")
@click.option("-a", "--add", is_flag=True, default=False, help="Add a random point to the instance before checking.")
@click.option("-p", "--plot", type=click.Path(writable=True, dir_okay=False), default=None,
              help="Plot the figure and all non-empty monochromatic substructures to the given file.")
def main(file, only, add, plot):
    points = load_points_from_csv(file)
    parts = partition_points(points)

    if plot:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()

        for c, ps in parts.items():
            px, py = zip(*ps)
            ax.scatter(px, py, color=c, zorder=4)

    stats = ", ".join(f"{len(ps)} {c}" for c, ps in parts.items())
    tqdm.write(f"Set contains {len(points)} points ({stats}).")
    if add:
        min_x, max_x, min_y, max_y = bounding_box(points)
        delta_x = max_x - min_x
        delta_y = max_y - min_y
        p = ((
                 random.randrange(int(min_x - delta_x / len(points)), int(max_x + delta_x / len(points))),
                 random.randrange(int(min_y - delta_y / len(points)), int(max_y + delta_y / len(points)))
             ), random.choice(list(parts.keys())))
        points.append(p)
        parts[p[1]].append(p[0])
        tqdm.write(f"Adding point {p}.")

    found = 0
    for s in find_empty_monochromatic_substructures(parts, only):
        found += 1
        if plot:
            plot_polygon(
                ax, s["shape"],
                color=s['color'])

        with tqdm.external_write_mode():
            json.dump(s, sys.stdout, default=str)
            print()
    tqdm.write(f"Found {found} empty monochromatic substructures.")

    if plot:
        ax.set_aspect('equal')
        plt.savefig(plot)
        plt.close(fig)

    return found


if __name__ == "__main__":
    main()
