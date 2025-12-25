from itertools import combinations, pairwise

import click

from fourholes.ipe.lib import *
from fourholes.util import *


@click.command()
@click.argument("file", type=click.Path(readable=True, dir_okay=False, exists=True))
@click.option("-o", "--out", type=click.Path(writable=True, dir_okay=False), default=None)
@click.option("-s", "--size", type=int, default=100)
@click.option("-d", "--offset", type=int, default=100)
@click.option("-c", "--convex-hull", is_flag=True, default=False)
@click.option("-t", "--opacity", type=click.FloatRange(0.0, 1.0), default=1.0)
def main(file, out, size, offset, convex_hull, opacity):
    size_x = size_y = size
    off_x = off_y = offset

    raw_points = load_points_from_csv(file)
    min_x, max_x, min_y, max_y = bounding_box(raw_points)
    scale_x = (max_x - min_x) / size_x
    scale_y = (max_y - min_y) / size_y
    points = [
        (((x - min_x) / scale_x + off_x, (y - min_y) / scale_y + off_y), c)
        for ((x, y), c) in raw_points
    ]
    parts = partition_points(points)

    doc = make_document()
    page = make_page()
    doc.push_back(page)

    if opacity > 0:
        if opacity < 1:
            sheet = ipe.StyleSheet()
            sheet.setName("stroke-opacity")
            sheet.add(ipe.Kind.EOpacity, ipe.Attribute(True, "default-stroke-opacity"), ipe.Fixed.fromDouble(opacity))
            sheet.__python_owns__ = False
            doc.cascade().insert(0, sheet)

        if convex_hull:
            from shapely.geometry import Polygon
            hull = Polygon([p for p, c in points]).convex_hull.exterior.coords
            lookup = dict(points)
            page.append(make_group([
                make_segment(a, b, stroke="gray", dashStyle="dotted")
                for a, b in pairwise(hull) if lookup[a] != lookup[b]]))

        for c, ps in parts.items():
            page.append(make_group([
                make_segment(a, b, stroke=c, strokeOpacity="default-stroke-opacity" if opacity < 1 else None)
                for a, b in combinations(ps, 2)]))

    for c, ps in parts.items():
        page.append(make_group([
            make_node(pos=p, fill=c, stroke="white") for p in ps
        ]))

    if not out:
        out = Path(file).with_suffix("")
    save(doc, out)


if __name__ == "__main__":
    main()
