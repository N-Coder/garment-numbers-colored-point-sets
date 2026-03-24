#include "lib.hpp"

#include <algorithm>
#include <iterator>

// ── Shape name sets ───────────────────────────────────────────────────────────

const std::set<std::string> CONVEX_SHAPES    = {"cravat", "necklace", "bowtie"};
const std::set<std::string> NONCONVEX_SHAPES = {"skirt",  "pant"              };
const std::set<std::string> ALL_SHAPES       = {"cravat", "necklace", "bowtie",
                                                 "skirt",  "pant"              };

// ── Internal geometry helpers (anonymous namespace) ───────────────────────────

namespace {

using PSet = CGAL::Polygon_set_2<K>;

template<typename Iter>
Poly make_polygon(Iter first, Iter last) {
    Poly p(first, last);
    if (p.is_clockwise_oriented()) p.reverse_orientation();
    return p;
}

Poly make_polygon(std::initializer_list<Point_2> pts) {
    return make_polygon(pts.begin(), pts.end());
}

Poly convex_hull(const std::vector<Point_2>& pts) {
    std::vector<Point_2> hull;
    CGAL::convex_hull_2(pts.begin(), pts.end(), std::back_inserter(hull));
    return make_polygon(hull.begin(), hull.end());
}

Region as_region(const Poly& p) { return {PWH(p)}; }

Region polygon_union(const Poly& p1, const Poly& p2) {
    PSet ps;
    ps.join(p1);
    ps.join(p2);
    Region r;
    ps.polygons_with_holes(std::back_inserter(r));
    return r;
}

Region polygon_sym_diff(const Poly& p1, const Poly& p2) {
    PSet ps;
    ps.join(p1);
    ps.symmetric_difference(p2);
    Region r;
    ps.polygons_with_holes(std::back_inserter(r));
    return r;
}

bool region_contains(const Region& region, const Point_2& pt) {
    for (const auto& pwh : region) {
        if (pwh.outer_boundary().bounded_side(pt) != CGAL::ON_BOUNDED_SIDE)
            continue;
        bool in_hole = false;
        for (auto h = pwh.holes_begin(); h != pwh.holes_end(); ++h)
            if (h->bounded_side(pt) == CGAL::ON_BOUNDED_SIDE) { in_hole = true; break; }
        if (!in_hole) return true;
    }
    return false;
}

bool contains_any(const Region& region, const std::vector<Point_2>& pts) {
    return std::any_of(pts.begin(), pts.end(),
        [&](const Point_2& p) { return region_contains(region, p); });
}

// ── Shape generators ──────────────────────────────────────────────────────────

// Closed vertex list of hull: first vertex repeated at end (5 elements for a quad).
std::vector<Point_2> hull_coords(const Poly& hull) {
    std::vector<Point_2> c(hull.vertices_begin(), hull.vertices_end());
    c.push_back(c[0]);
    return c;
}

// Triangle from closed 4-gon coords by picking vertices i%4, (i+1)%4, (i+2)%4.
Poly get_triangle(const std::vector<Point_2>& p, int i) {
    return make_polygon({p[i % 4], p[(i + 1) % 4], p[(i + 2) % 4]});
}

using ShapeOut = std::vector<std::pair<std::string, Region>>;

void cravats_convex(const Poly& hull, const std::vector<Point_2>&, ShapeOut& out) {
    out.emplace_back("cravat", as_region(hull));
}

// Necklace = union of each consecutive pair of triangles from range(5).
void necklaces_convex(const Poly& hull, const std::vector<Point_2>&, ShapeOut& out) {
    auto c = hull_coords(hull);
    for (int i = 0; i < 4; i++)
        out.emplace_back("necklace",
            polygon_union(get_triangle(c, i), get_triangle(c, i + 1)));
}

// Bowtie = symmetric difference of each consecutive pair of triangles from range(3).
void bowties_convex(const Poly& hull, const std::vector<Point_2>&, ShapeOut& out) {
    auto c = hull_coords(hull);
    for (int i = 0; i < 2; i++)
        out.emplace_back("bowtie",
            polygon_sym_diff(get_triangle(c, i), get_triangle(c, i + 1)));
}

void skirts_nonconvex(const Poly& hull, const std::vector<Point_2>&, ShapeOut& out) {
    out.emplace_back("skirt", as_region(hull));
}

// Pant: for each edge of the 3-hull, the quad formed by inserting the interior point.
void pants_nonconvex(const Poly& hull, const std::vector<Point_2>& pts, ShapeOut& out) {
    std::vector<Point_2> hv(hull.vertices_begin(), hull.vertices_end());
    Point_2 interior;
    for (const auto& p : pts)
        if (std::find(hv.begin(), hv.end(), p) == hv.end()) { interior = p; break; }
    for (int i = 0; i < 3; i++)
        out.emplace_back("pant", as_region(make_polygon(
            {hv[i], interior, hv[(i + 1) % 3], hv[(i + 2) % 3]})));
}

} // anonymous namespace

// ── Public implementations ────────────────────────────────────────────────────

std::vector<std::pair<std::string, Region>>
all_structures_from_quad(const std::vector<Point_2>& pts,
                         const std::set<std::string>& only)
{
    ShapeOut out;
    auto hull  = convex_hull(pts);
    auto want  = [&](const std::string& s) { return only.empty() || only.count(s); };

    if (hull.size() == 4) {  // convex quad
        if (want("cravat"))   cravats_convex(hull, pts, out);
        if (want("necklace")) necklaces_convex(hull, pts, out);
        if (want("bowtie"))   bowties_convex(hull, pts, out);
    } else {                  // non-convex quad (3 hull vertices + 1 interior)
        if (want("skirt")) skirts_nonconvex(hull, pts, out);
        if (want("pant"))  pants_nonconvex(hull, pts, out);
    }
    return out;
}

void find_empty_monochromatic_structures(
    const PartitionedPointSet& parts,
    const std::set<std::string>& only,
    std::function<bool(const Structure&)> on_found)
{
    for (const auto& [color, same] : parts) {
        std::vector<Point_2> other;
        for (const auto& [c, ps] : parts)
            if (c != color) other.insert(other.end(), ps.begin(), ps.end());

        int n = same.size();
        bool keep_going = true;
        for (int a = 0; a < n && keep_going; a++)
        for (int b = a+1; b < n && keep_going; b++)
        for (int c = b+1; c < n && keep_going; c++)
        for (int d = c+1; d < n && keep_going; d++) {
            std::vector<Point_2> quad = {same[a], same[b], same[c], same[d]};
            for (auto& [name, region] : all_structures_from_quad(quad, only)) {
                if (!contains_any(region, other)) {
                    Structure s{color, name, quad, std::move(region)};
                    if (!on_found(s)) { keep_going = false; break; }
                }
            }
        }
    }
}

bool has_empty_monochromatic_structure(
    const PartitionedPointSet& parts,
    const std::set<std::string>& only)
{
    bool found = false;
    find_empty_monochromatic_structures(parts, only,
        [&](const Structure&) { found = true; return false; });
    return found;
}
