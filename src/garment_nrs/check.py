import random
from pathlib import Path

import click

from garment_nrs.lib import CONVEX_SHAPES, NONCONVEX_SHAPES, find_empty_monochromatic_structures
from garment_nrs.util import *


def strengthen_filter(only):
    convex = 0
    if "cravat" in only:
        convex = 1
    elif "necklace" in only:
        convex = 2
    elif "bowtie" in only:
        convex = 3

    noncon = 0
    if "skirt" in only:
        noncon = 1
    elif "pant" in only:
        noncon = 2

    CONVEX = [None, "cravat", "necklace", "bowtie"]
    NONCON = [None, "skirt", "pant"]

    if convex < 3:
        if noncon:
            yield [CONVEX[convex + 1], NONCON[noncon]]
        else:
            yield [CONVEX[convex + 1]]
    if noncon < 2:
        if convex:
            yield [CONVEX[convex], NONCON[noncon + 1]]
        else:
            yield [NONCON[noncon + 1]]


ALL_SHAPES = [*CONVEX_SHAPES.keys(), *NONCONVEX_SHAPES.keys()]


@click.command()
@click.argument("dir", type=click.Path(exists=True, file_okay=False))
def main(dir):
    checked = []
    dir = Path(dir)
    for file in dir.rglob("*.csv"):
        if not file.is_file(): continue

        points = load_points_from_csv(file)
        parts = partition_points(points)
        ignore = {f"n{len(points)}", "c2", "no", "mc"}
        only = [s for s in file.stem.split("_") if not s in ignore]

        stats = ", ".join(f"{len(ps)} {c}" for c, ps in parts.items())
        checked.append((file, len(points), stats, only))
        print(f"File {file} contains {len(points)} points ({stats}) for {only}.")

        if any(find_empty_monochromatic_structures(parts, only)):
            print(f"File {file} contains an empty {only} structure.")
            return 1

        for _ in range(10):
            p = (random_point(points), random.choice(list(parts.keys())))
            points.append(p)
            parts[p[1]].append(p[0])
            print(f"Adding point {p} ({len(points)} points, {len(parts[p[1]])} {p[1]})")
            if not any(find_empty_monochromatic_structures(parts, only)):
                print(f"Adding point {p} to file {file} still yields no empty {only} structure.")
                return 2
            del points[-1]
            del parts[p[1]][-1]

        for s_only in strengthen_filter(only):
            print(f"Strengthening filter {only} to {s_only}")
            if not any(find_empty_monochromatic_structures(parts, s_only)):
                print(f"Strengthening the filter from {only} to {s_only} "
                      f"for file {file} still yields no empty structure.")
                return 3
        print()

    print(f"Checked {len(checked)} files:")
    for file, points, stats, only in checked:
        print(f"\t{file} with {points} points ({stats}) contains no empty {only}")

    return 0


if __name__ == "__main__":
    main()
