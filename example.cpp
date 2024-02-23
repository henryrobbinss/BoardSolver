#include <pybind11/pybind11.h>

#include "solver/Solver.hpp"
#include <algorithm>
#include <cmath>
#include <iostream>
#include <vector>
#include <string>

int add(int i, int j) {
    return i + j;
}

using namespace GameSolver::Connect4;

/**
 * Main function.
 * Reads Connect 4 positions, line by line, from standard input
 * and writes one line per position to standard output containing:
 *  - score of the position
 *  - number of nodes explored
 *  - time spent in microsecond to solve the position.
 *
 *  Any invalid position (invalid sequence of move, or already won game)
 *  will generate an error message to standard error and an empty line to standard output.
 */
int solve(std::string line) {
  Solver solver;
  bool weak = false;

  std::string opening_book = "solver/7x6.book";

  solver.loadBook(opening_book);

  Position P;
  std::vector<int> scores = solver.analyze(P, weak);
  return *std::max_element(scores.begin(), scores.end());
}

PYBIND11_MODULE(example, m) {
    m.doc() = "Connect 4 Solver Module";

    m.def("solve", &solve, "A function that returns solved");
}