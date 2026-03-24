#pragma once

#include <CGAL/Exact_predicates_exact_constructions_kernel.h>
#include <CGAL/Polygon_2.h>
#include <CGAL/Polygon_with_holes_2.h>
#include <CGAL/Polygon_set_2.h>
#include <CGAL/convex_hull_2.h>

#include <functional>
#include <map>
#include <set>
#include <string>
#include <vector>

// ── CGAL type aliases ─────────────────────────────────────────────────────────

using K       = CGAL::Exact_predicates_exact_constructions_kernel;
using Point_2 = K::Point_2;
using Poly    = CGAL::Polygon_2<K>;
using PWH     = CGAL::Polygon_with_holes_2<K>;
using Region  = std::vector<PWH>;   // result of a boolean set operation

using PartitionedPointSet = std::map<std::string, std::vector<Point_2>>;

extern const std::set<std::string> CONVEX_SHAPES;
extern const std::set<std::string> NONCONVEX_SHAPES;
extern const std::set<std::string> ALL_SHAPES;

// ── Result type ───────────────────────────────────────────────────────────────

struct Structure {
    std::string        color;
    std::string        type;
    std::vector<Point_2> points;  // the 4 quad vertices
    Region             shape;
};

// ── Public API ────────────────────────────────────────────────────────────────

// All structures (name + region) that can be formed from a quad of 4 points.
// If only is non-empty, only structures whose name is in only are returned.
std::vector<std::pair<std::string, Region>>
all_structures_from_quad(const std::vector<Point_2>& pts,
                         const std::set<std::string>& only);

// Iterate over every empty monochromatic structure in parts.
// on_found is called for each; returning false stops the search early.
void find_empty_monochromatic_structures(
    const PartitionedPointSet& parts,
    const std::set<std::string>& only,
    std::function<bool(const Structure&)> on_found);

// Returns true iff at least one empty monochromatic structure exists.
bool has_empty_monochromatic_structure(
    const PartitionedPointSet& parts,
    const std::set<std::string>& only);
