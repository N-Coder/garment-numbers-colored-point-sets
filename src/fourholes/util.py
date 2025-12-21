from collections import defaultdict
from typing import List, Tuple

from shapely import MultiPolygon, Polygon

__all__ = [
    "partition_points", "load_points_from_csv", "write_points_to_csv", "plot_polygon", "minimize"
]


def partition_points(points) -> dict[str, list]:
    parts = defaultdict(list)
    for p, c in points:
        parts[c.strip()].append(p)
    return parts


def load_points_from_csv(path) -> List[Tuple[Tuple[int, int], str]]:
    import pandas as pd

    return [((row[0], row[1]), row[2]) for (idx, row) in pd.read_csv(path, header=None).iterrows()]


def write_points_to_csv(parts, file):
    import csv

    w = csv.writer(file)
    for c, ps in parts.items():
        w.writerows((*p, c) for p in ps)


def plot_polygon(ax: 'matplotlib.Axes', polygon: Polygon, points=None, color: str = '#6699cc'):
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


def minimize(parts, only):
    from fourholes.lib import find_empty_monochromatic_substructures
    from tqdm import tqdm

    for c, ps in parts.items():
        for i in tqdm(range(len(ps)), desc=f"Minimizing {c} points"):
            inst = dict([*parts.items(), (c, ps[:i] + ps[i + 1:])])
            mcss = any(find_empty_monochromatic_substructures(inst, only))
            if not mcss:
                return c, i, inst
    return None, None, None
