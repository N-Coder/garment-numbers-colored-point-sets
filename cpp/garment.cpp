// garment — find empty monochromatic structures in a bichromatic point set
//
// Usage: garment [--only <shape>]... [--add] <file.csv>
//
// For each empty monochromatic structure found, prints one JSON object per line:
//   {"color":..., "type":..., "points":[[x,y],...], "shape":[[[x,y],...], ...]}
// where "shape" is a list of polygon outlines (one per connected component).
//
// Summary stats are written to stderr.

#include "lib.hpp"
#include "util.hpp"

#include <cmath>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

// ── Minimal JSON helpers ──────────────────────────────────────────────────────

static std::string json_num(double v) {
    // Output integers without a decimal point to match Python's output for
    // integer-coordinate points.
    if (v == std::floor(v) && std::abs(v) < 1e15)
        return std::to_string((long long)v);
    std::ostringstream ss;
    ss << v;
    return ss.str();
}

static std::string json_point(const Point_2& p) {
    return "[" + json_num(CGAL::to_double(p.x()))
         + "," + json_num(CGAL::to_double(p.y())) + "]";
}

static std::string json_polygon(const Poly& poly) {
    std::string s = "[";
    bool first = true;
    for (auto v = poly.vertices_begin(); v != poly.vertices_end(); ++v) {
        if (!first) s += ",";
        s += json_point(*v);
        first = false;
    }
    return s + "]";
}

static std::string json_region(const Region& region) {
    std::string s = "[";
    bool first = true;
    for (const auto& pwh : region) {
        if (!first) s += ",";
        s += json_polygon(pwh.outer_boundary());
        first = false;
    }
    return s + "]";
}

static std::string json_structure(const Structure& st) {
    std::string pts = "[";
    for (size_t i = 0; i < st.points.size(); i++) {
        if (i) pts += ",";
        pts += json_point(st.points[i]);
    }
    pts += "]";

    return "{\"color\":\"" + st.color + "\","
           "\"type\":\""   + st.type  + "\","
           "\"points\":"   + pts      + ","
           "\"shape\":"    + json_region(st.shape) + "}";
}

// ── CLI parsing ───────────────────────────────────────────────────────────────

struct Args {
    std::string            file;
    std::set<std::string>  only;
    bool                   add = false;
};

static void usage(const char* prog) {
    std::cerr << "Usage: " << prog
              << " [--only <shape>]... [--add] <file.csv>\n"
              << "  --only  one of: cravat necklace bowtie skirt pant\n"
              << "  --add   add one random point before searching\n";
}

static Args parse_args(int argc, char* argv[]) {
    Args a;
    for (int i = 1; i < argc; i++) {
        std::string arg = argv[i];
        if (arg == "--only" || arg == "-o") {
            if (++i >= argc) throw std::runtime_error("--only requires a value");
            std::string shape = argv[i];
            if (!ALL_SHAPES.count(shape))
                throw std::runtime_error("unknown shape: " + shape);
            a.only.insert(shape);
        } else if (arg == "--add" || arg == "-a") {
            a.add = true;
        } else if (arg[0] != '-') {
            if (!a.file.empty()) throw std::runtime_error("unexpected argument: " + arg);
            a.file = arg;
        } else {
            throw std::runtime_error("unknown option: " + arg);
        }
    }
    if (a.file.empty()) throw std::runtime_error("missing input file");
    return a;
}

// ── Main ──────────────────────────────────────────────────────────────────────

int main(int argc, char* argv[]) {
    Args args;
    try {
        args = parse_args(argc, argv);
    } catch (const std::exception& e) {
        std::cerr << "error: " << e.what() << "\n";
        usage(argv[0]);
        return 1;
    }

    auto raw   = load_csv(args.file);
    auto parts = partition(raw);

    std::string stats;
    for (const auto& [c, ps] : parts) {
        if (!stats.empty()) stats += ", ";
        stats += std::to_string(ps.size()) + " " + c;
    }
    std::cerr << "Set contains " << raw.size() << " points (" << stats << ").\n";

    if (args.add) {
        auto rp = random_point(raw, parts);
        raw.push_back(rp);
        parts[rp.color].emplace_back(rp.x, rp.y);
        std::cerr << "Adding point (" << rp.x << ", " << rp.y
                  << ", " << rp.color << ").\n";
    }

    int found = 0;
    find_empty_monochromatic_structures(parts, args.only,
        [&](const Structure& s) {
            ++found;
            std::cout << json_structure(s) << "\n";
            return true;  // continue searching
        });

    std::cerr << "Found " << found << " empty monochromatic structures.\n";
    return 0;
}
