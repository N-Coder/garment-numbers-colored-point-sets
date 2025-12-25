import json
import random
import sys

import click
from tqdm import tqdm

from fourholes.lib import CONVEX_SHAPES, NONCONVEX_SHAPES, find_empty_monochromatic_substructures
from fourholes.util import *


@click.command()
@click.argument("file", type=click.File("r"))
@click.option("-o", "--only",
              type=click.Choice([*CONVEX_SHAPES.keys(), *NONCONVEX_SHAPES.keys()], False),
              multiple=True)
@click.option("-m", "--minimal", type=click.File("wt"), default=None)
@click.option("-a", "--add", type=click.File("wt"), default=None)
@click.option("-p", "--plot", type=click.Path(writable=True, dir_okay=False), default=None)
def main(file, only, minimal, add, plot):
    points = load_points_from_csv(file)
    parts = partition_points(points)

    if plot:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()

        for c, ps in parts.items():
            px, py = zip(*ps)
            ax.scatter(px, py, color=c, zorder=4)

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
    tqdm.write(f"Found {found} substructures")

    if plot:
        ax.set_aspect('equal')
        plt.savefig(plot)
        plt.close(fig)

    if minimal:
        if found:
            tqdm.write(f"Cannot check minimality as points already do contain {found} substructures")
            return
        c, i, inst = minimize(parts, only)
        if c is not None:
            tqdm.write(f"Removing {c} point {i} {parts[c][i]} also yields no empty substructures")
            write_points_to_csv(inst, minimal)
        else:
            tqdm.write("Instance is minimal!")

    elif add:
        if found:
            tqdm.write(f"Cannot add anything as points already do contain {found} substructures")
            return
        min_x, max_x, min_y, max_y = bounding_box(points)
        delta_x = max_x - min_x
        delta_y = max_y - min_y
        p = ((
                 random.randrange(int(min_x - delta_x / len(points)), int(max_x + delta_x / len(points))),
                 random.randrange(int(min_y - delta_y / len(points)), int(max_y + delta_y / len(points)))
             ), random.choice(list(parts.keys())))
        points.append(p)
        parts[p[1]].append(p[0])
        mcss = any(find_empty_monochromatic_substructures(parts, only))
        if mcss:
            tqdm.write(f"Adding point {p} now already yields at least one empty substructure")
        else:
            tqdm.write(f"Found larger counterexample! Adding point {p} yields no empty substructure")


if __name__ == "__main__":
    main()
