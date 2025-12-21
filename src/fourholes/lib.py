import itertools
from math import comb
from typing import List, Tuple, Optional, Dict, Generator

from more_itertools import one
from shapely import contains_xy, Polygon, Geometry

__all__ = [
    "is_convex_quad", "is_nonconvex_quad", "all_substructures_from_quad", "contains_any",
    "find_empty_monochromatic_substructures"
]


def is_convex_quad(hull: Polygon) -> bool:
    return len(hull.exterior.coords) == 5


def is_nonconvex_quad(hull: Polygon) -> bool:
    return len(hull.exterior.coords) == 4


def get_triangle(p: List[Tuple[float, float]], i: int) -> Polygon:
    assert len(p) == 5
    return Polygon([p[i % 4], p[(i + 1) % 4], p[(i + 2) % 4]])


###########################################################

def cravats_convex(hull, pts=None):
    assert is_convex_quad(hull)
    yield hull


def necklaces_convex(hull, pts=None):
    assert is_convex_quad(hull)
    # we have 4 pairs to consider -> range(5)
    for t1, t2 in itertools.pairwise(get_triangle(hull.exterior.coords, i) for i in range(5)):
        yield t1.union(t2)


def bowties_convex(hull, pts=None):
    assert is_convex_quad(hull)
    # we have two pairs to consider -> range(3)
    for t1, t2 in itertools.pairwise(get_triangle(hull.exterior.coords, i) for i in range(3)):
        yield t1.symmetric_difference(t2)


def skirts_nonconvex(hull, pts=None):
    assert is_nonconvex_quad(hull)
    yield hull


def pants_nonconvex(hull, pts):
    assert is_nonconvex_quad(hull)
    hull_pts = hull.exterior.coords
    interior = one(p for p in pts if p not in hull_pts)
    for i in range(3):
        yield Polygon([
            hull_pts[i],
            interior,
            hull_pts[(i + 1) % 3],
            hull_pts[(i + 2) % 3]
        ])


CONVEX_SHAPES = {
    "cravat": cravats_convex,
    "necklace": necklaces_convex,
    "bowtie": bowties_convex,
}
NONCONVEX_SHAPES = {
    "skirt": skirts_nonconvex,
    "pant": pants_nonconvex,
}


def all_substructures_from_quad(pts: List[Tuple[float, float]], only: Optional[List[str]] = None) \
        -> Generator[Tuple[str, Geometry]]:
    hull = Polygon(pts).convex_hull
    shapes = CONVEX_SHAPES if is_convex_quad(hull) else NONCONVEX_SHAPES
    for shape, func in shapes.items():
        if only and shape not in only:
            continue
        for region in func(hull, pts):
            yield shape, region


###########################################################

def contains_any(region: Geometry, points: List[Tuple[float, float]]) -> bool:
    return any(contains_xy(region, *p) for p in points)


def find_empty_monochromatic_substructures(
        parts: Dict[str, List[Tuple[float, float]]], only: Optional[List[str]] = None):
    from tqdm import tqdm

    for color in parts.keys():
        same_color = parts[color]
        other_colors = [ps for (c, ps) in parts.items() if c != color]
        if len(other_colors) == 1:
            other_color = other_colors[0]
        else:
            other_color = list(itertools.chain(*other_colors))

        quads = itertools.combinations(same_color, 4)
        quads = tqdm(quads, total=comb(len(same_color), 4), desc=f"Processing 4-tuples for {color}")
        for quad in quads:
            for kind, region in all_substructures_from_quad(quad, only):
                if not contains_any(region, other_color):
                    yield {
                        "color": color,
                        "type": kind,
                        "points": quad,
                        "shape": region,
                    }
