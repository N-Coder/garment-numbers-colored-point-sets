#include "util.hpp"

#include <algorithm>
#include <fstream>
#include <random>
#include <sstream>

// ── CSV loading ───────────────────────────────────────────────────────────────

std::vector<RawPoint> load_csv(const std::filesystem::path& path) {
    std::ifstream f(path);
    std::vector<RawPoint> pts;
    std::string line;
    while (std::getline(f, line)) {
        std::istringstream ss(line);
        double x, y; char comma; std::string color;
        if (ss >> x >> comma >> y >> comma && std::getline(ss >> std::ws, color)) {
            while (!color.empty() && std::isspace((unsigned char)color.back()))
                color.pop_back();
            pts.push_back({x, y, color});
        }
    }
    return pts;
}

PartitionedPointSet partition(const std::vector<RawPoint>& pts) {
    PartitionedPointSet parts;
    for (const auto& p : pts) parts[p.color].emplace_back(p.x, p.y);
    return parts;
}

// ── Random point ──────────────────────────────────────────────────────────────

static std::mt19937 rng(std::random_device{}());

// Mirrors Python's random_point(): integer coords within an expanded bounding box,
// random color drawn from the existing colors in parts.
RawPoint random_point(const std::vector<RawPoint>& pts,
                      const PartitionedPointSet& parts)
{
    double min_x = pts[0].x, max_x = pts[0].x;
    double min_y = pts[0].y, max_y = pts[0].y;
    for (const auto& p : pts) {
        min_x = std::min(min_x, p.x); max_x = std::max(max_x, p.x);
        min_y = std::min(min_y, p.y); max_y = std::max(max_y, p.y);
    }
    double dx = (max_x - min_x) / pts.size();
    double dy = (max_y - min_y) / pts.size();

    // randrange(a, b) = uniform in [a, b-1]
    std::uniform_int_distribution<int> distx(int(min_x - dx), int(max_x + dx) - 1);
    std::uniform_int_distribution<int> disty(int(min_y - dy), int(max_y + dy) - 1);

    std::vector<std::string> colors;
    for (const auto& [c, _] : parts) colors.push_back(c);
    std::uniform_int_distribution<int> distc(0, (int)colors.size() - 1);

    return {(double)distx(rng), (double)disty(rng), colors[distc(rng)]};
}
