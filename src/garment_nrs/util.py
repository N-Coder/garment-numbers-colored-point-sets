from collections import defaultdict
from typing import List, Tuple, TypeAlias

from shapely import MultiPolygon, Polygon

from garment_nrs.lib import *

RawColoredPointSet: TypeAlias = List[Tuple[Point, str]]

__all__ = [
    "partition_points", "load_points_from_csv", "write_points_to_csv", "plot_polygon", "minimize", "bounding_box",
    "RawColoredPointSet", "random_point"
]


def load_points_from_csv(path) -> RawColoredPointSet:
    import pandas as pd

    return [((row[0], row[1]), row[2]) for (idx, row) in pd.read_csv(path, header=None).iterrows()]


def partition_points(points: RawColoredPointSet) -> PartitionedPointSet:
    parts = defaultdict(list)
    for p, c in points:
        parts[c.strip()].append(p)
    return parts


def write_points_to_csv(parts: PartitionedPointSet, file):
    import csv

    w = csv.writer(file)
    for c, ps in parts.items():
        w.writerows((*p, c) for p in ps)


def plot_polygon(ax: 'matplotlib.Axes', polygon: Polygon, points: PointSet = None, color: str = '#6699cc'):
    # merged = polygon.buffer(0.00001).buffer(-0.00001)
    merged = polygon
    parts = merged.geoms if isinstance(merged, MultiPolygon) else [merged]
    for part in parts:
        if not part.is_empty:
            x, y = part.exterior.xy
            ax.fill(x, y, color=color, alpha=0.3, zorder=1)
            ax.plot(x, y, color=color, alpha=0.7, linewidth=3, solid_capstyle='round', zorder=2)
    if points:
        px, py = zip(*points)
        ax.scatter(px, py, color=color, zorder=3)


def minimize(parts: PartitionedPointSet, only: FilterList):
    from tqdm import tqdm

    for c, ps in parts.items():
        for i in tqdm(range(len(ps)), desc=f"Minimizing {c} points"):
            inst = dict([*parts.items(), (c, ps[:i] + ps[i + 1:])])
            mcss = any(find_empty_monochromatic_structures(inst, only))
            if not mcss:
                return c, i, inst
    return None, None, None


def bounding_box(points: RawColoredPointSet) -> tuple[float, float, float, float]:
    min_x = min(p[0][0] for p in points)
    max_x = max(p[0][0] for p in points)
    min_y = min(p[0][1] for p in points)
    max_y = max(p[0][1] for p in points)
    return min_x, max_x, min_y, max_y


def random_point(points: RawColoredPointSet) -> Point:
    import random
    min_x, max_x, min_y, max_y = bounding_box(points)
    delta_x = max_x - min_x
    delta_y = max_y - min_y
    return (
        random.randrange(int(min_x - delta_x / len(points)), int(max_x + delta_x / len(points))),
        random.randrange(int(min_y - delta_y / len(points)), int(max_y + delta_y / len(points)))
    )
