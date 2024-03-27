#include <pybind11/pybind11.h>

#include "solver/Solver.hpp"
#include <algorithm>
#include <cmath>
#include <iostream>
#include <vector>
#include <string>

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
  GameSolver::Connect4::Solver solver;
  bool weak = false;

  std::string opening_book = "solver/7x6.book";

  solver.loadBook(opening_book);

  GameSolver::Connect4::Position P;
  if(P.play(line) != line.size()) {
    std::cerr << "Invalid move: " << (P.nbMoves() + 1) << " \"" << line << "\"" << std::endl;
  } else {
    std::vector<int> scores = solver.analyze(P, weak);
    return std::distance(scores.begin(), std::max_element(scores.begin(), scores.end())) + 1;
  }
  return -1;
}

PYBIND11_MODULE(example, m) {
    m.doc() = "Connect 4 Solver Module";

    m.def("solve", &solve, "A function that returns solved");
}