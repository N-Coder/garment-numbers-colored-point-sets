cmake_minimum_required(VERSION 3.14)
project(garment CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(CGAL REQUIRED)

# Shared geometry/IO library
add_library(garment_lib STATIC lib.cpp util.cpp)
target_link_libraries(garment_lib PUBLIC CGAL::CGAL)

# garment: find and output empty monochromatic structures
add_executable(garment garment.cpp)
target_link_libraries(garment PRIVATE garment_lib)

# garment-check: verify counterexample CSV files
add_executable(garment-check check.cpp)
target_link_libraries(garment-check PRIVATE garment_lib)
