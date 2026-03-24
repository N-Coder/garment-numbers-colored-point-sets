// garment-check — verify counterexample CSV files in a directory
//
// For each *.csv file, checks that:
//   1. No empty monochromatic structure of the type encoded in the filename exists.
//   2. Adding 10 random points individually still yields at least one empty structure.
//   3. Every strengthened filter also yields at least one empty structure.
//
// Returns 0 on full success, non-zero on the first failure.

#include "lib.hpp"
#include "util.hpp"

#include <filesystem>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

// ── strengthen_filter ─────────────────────────────────────────────────────────

// Mirrors Python's strengthen_filter(): returns the next harder filter(s).
// Convex shapes are ordered cravat < necklace < bowtie (indices 1–3);
// non-convex shapes are ordered skirt < pant (indices 1–2).
static std::vector<std::set<std::string>>
strengthen_filter(const std::set<std::string>& only)
{
    const std::string CONVEX[] = {"", "cravat", "necklace", "bowtie"};
    const std::string NONCON[] = {"", "skirt",  "pant"              };

    int convex = 0, noncon = 0;
    if      (only.count("cravat"))   convex = 1;
    else if (only.count("necklace")) convex = 2;
    else if (only.count("bowtie"))   convex = 3;
    if      (only.count("skirt")) noncon = 1;
    else if (only.count("pant"))  noncon = 2;

    std::vector<std::set<std::string>> result;
    if (convex < 3) {
        std::set<std::string> s = {CONVEX[convex + 1]};
        if (noncon) s.insert(NONCON[noncon]);
        result.push_back(s);
    }
    if (noncon < 2) {
        std::set<std::string> s = {NONCON[noncon + 1]};
        if (convex) s.insert(CONVEX[convex]);
        result.push_back(s);
    }
    return result;
}

// ── Main ──────────────────────────────────────────────────────────────────────

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: garment-check <directory>\n";
        return 1;
    }

    namespace fs = std::filesystem;
    fs::path dir = argv[1];

    struct Summary { fs::path path; size_t n; std::string stats; std::set<std::string> only; };
    std::vector<Summary> checked;

    for (const auto& entry : fs::recursive_directory_iterator(dir)) {
        if (!entry.is_regular_file() || entry.path().extension() != ".csv") continue;

        auto raw   = load_csv(entry.path());
        auto parts = partition(raw);

        // Extract filter: keep only tokens that are valid structure names.
        std::set<std::string> only;
        {
            std::istringstream ss(entry.path().stem().string());
            std::string tok;
            while (std::getline(ss, tok, '_'))
                if (ALL_SHAPES.count(tok)) only.insert(tok);
        }

        std::string stats, only_str;
        for (const auto& [c, ps] : parts) {
            if (!stats.empty()) stats += ", ";
            stats += std::to_string(ps.size()) + " " + c;
        }
        for (const auto& s : only) only_str += (only_str.empty() ? "" : ", ") + s;

        std::cout << "File " << entry.path().filename().string()
                  << " (" << raw.size() << " points: " << stats
                  << ") for [" << only_str << "]\n";

        if (has_empty_monochromatic_structure(parts, only)) {
            std::cout << "FAIL: file already contains an empty structure.\n";
            return 1;
        }

        for (int trial = 0; trial < 10; trial++) {
            auto rp = random_point(raw, parts);
            raw.push_back(rp);
            parts[rp.color].emplace_back(rp.x, rp.y);
            std::cout << "  +random (" << rp.x << "," << rp.y << "," << rp.color
                      << ") — " << raw.size() << " pts\n";
            if (!has_empty_monochromatic_structure(parts, only)) {
                std::cout << "FAIL: adding point removes all empty structures.\n";
                return 2;
            }
            raw.pop_back();
            parts[rp.color].pop_back();
        }

        for (const auto& s_only : strengthen_filter(only)) {
            std::string sl;
            for (const auto& s : s_only) sl += (sl.empty() ? "" : ", ") + s;
            std::cout << "  strengthen → [" << sl << "]\n";
            if (!has_empty_monochromatic_structure(parts, s_only)) {
                std::cout << "FAIL: strengthened filter yields no empty structure.\n";
                return 3;
            }
        }
        std::cout << "  OK\n\n";

        checked.push_back({entry.path(), raw.size(), stats, only});
    }

    std::cout << "Checked " << checked.size() << " files:\n";
    for (const auto& [path, n, stats, only] : checked) {
        std::string ol;
        for (const auto& s : only) ol += (ol.empty() ? "" : ", ") + s;
        std::cout << "  " << path.filename().string()
                  << "  " << n << " pts (" << stats << ")  [" << ol << "]\n";
    }
    return 0;
}
