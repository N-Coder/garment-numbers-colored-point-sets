#pragma once

#include "lib.hpp"

#include <filesystem>
#include <string>
#include <vector>

// ── CSV point type ────────────────────────────────────────────────────────────

struct RawPoint { double x, y; std::string color; };

// ── I/O ───────────────────────────────────────────────────────────────────────

// Load (x, y, color) triples from a CSV file (one point per line).
std::vector<RawPoint> load_csv(const std::filesystem::path& path);

// Group points by color into a PartitionedPointSet.
PartitionedPointSet partition(const std::vector<RawPoint>& pts);

// ── Random points ─────────────────────────────────────────────────────────────

// Generate a random point with integer coordinates in an expanded bounding box
// and a randomly chosen color from parts.  Mirrors Python's random_point().
RawPoint random_point(const std::vector<RawPoint>& pts,
                      const PartitionedPointSet& parts);
