import itertools
from math import comb
from typing import List, Tuple, Optional, Dict, Generator, TypeAlias

from more_itertools import one
from shapely import contains_xy, Polygon, Geometry
from shapely.coords import CoordinateSequence

__all__ = [
    "is_convex_quad", "is_nonconvex_quad", "all_substructures_from_quad", "contains_any",
    "find_empty_monochromatic_substructures", "CONVEX_SHAPES", "NONCONVEX_SHAPES",
    "Point", "PointSet", "FilterList", "PartitionedPointSet"
]

Point: TypeAlias = Tuple[float, float]
PointSet: TypeAlias = List[Point]
FilterList: TypeAlias = Optional[List[str]]
PartitionedPointSet: TypeAlias = Dict[str, PointSet]


def is_convex_quad(hull: Polygon) -> bool:
    return len(hull.exterior.coords) == 5


def is_nonconvex_quad(hull: Polygon) -> bool:
    return len(hull.exterior.coords) == 4


def get_triangle(p: PointSet | CoordinateSequence, i: int) -> Polygon:
    """ Build a triangle from a convex 4gon by dropping the (i+3)rd coordinate """
    assert len(p) == 5
    return Polygon([p[i % 4], p[(i + 1) % 4], p[(i + 2) % 4]])


###########################################################

def cravats_convex(hull: Polygon, pts: PointSet = None):
    assert is_convex_quad(hull)
    yield hull


def necklaces_convex(hull: Polygon, pts: PointSet = None):
    assert is_convex_quad(hull)
    # a necklace is built by dropping one edge from the convex 4gon
    # and unioning the two triangles based on the remaining sides plus the diagonals
    # we have 4 edges to consider -> range(5)
    for t1, t2 in itertools.pairwise(get_triangle(hull.exterior.coords, i) for i in range(5)):
        yield t1.union(t2)


def bowties_convex(hull: Polygon, pts: PointSet = None):
    assert is_convex_quad(hull)
    # we have two forms (bowtie and hourglass) to consider -> range(3)
    for t1, t2 in itertools.pairwise(get_triangle(hull.exterior.coords, i) for i in range(3)):
        yield t1.symmetric_difference(t2)


def skirts_nonconvex(hull: Polygon, pts: PointSet = None):
    assert is_nonconvex_quad(hull)
    yield hull


def pants_nonconvex(hull: Polygon, pts: PointSet = None):
    assert is_nonconvex_quad(hull)
    hull_pts = hull.exterior.coords
    interior = one(p for p in pts if p not in hull_pts)
    # there are 3 points on the convex hull, so three edges on which we can insert the interior point
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


def all_substructures_from_quad(pts: PointSet, only: FilterList = None) -> Generator[Tuple[str, Geometry]]:
    """ Build all possible substructures from a (convex or non-convex) set of 4 points.

    Yield tuples of (substructure name, shapely polygon).
    If only is non-empty, only returns substructures whose name is in the list.
    """
    hull = Polygon(pts).convex_hull
    shapes = CONVEX_SHAPES if is_convex_quad(hull) else NONCONVEX_SHAPES
    for shape, func in shapes.items():
        if only and shape not in only:
            continue
        for region in func(hull, pts):
            yield shape, region


###########################################################

def contains_any(region: Geometry, points: PointSet) -> bool:
    """ Check if region contains any of points """
    return any(contains_xy(region, *p) for p in points)


def get_all_other_colored_points(parts: PartitionedPointSet, not_color: str):
    """ Return a list of all points that do not have the given color """
    other_colors = [ps for (c, ps) in parts.items() if c != not_color]
    if len(other_colors) == 1:  # no merging needed
        return other_colors[0]
    else:
        return list(itertools.chain(*other_colors))


def find_empty_monochromatic_substructures(parts: PartitionedPointSet, only: FilterList = None):
    from tqdm import tqdm

    for color in parts.keys():
        same_color = parts[color]
        other_color = get_all_other_colored_points(parts, color)

        quads = itertools.combinations(same_color, 4)
        quads = tqdm(quads, total=comb(len(same_color), 4), desc=f"Processing 4-tuples for {color}")
        for quad in quads:
            for kind, region in all_substructures_from_quad(quad, only):
                if not contains_any(region, other_color):
                    yield {  # found an empty substructure
                        "color": color,
                        "type": kind,
                        "points": quad,
                        "shape": region,
                    }
