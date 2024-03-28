/*
 * This file is part of Connect4 Game Solver <http://connect4.gamesolver.org>
 * Copyright (C) 2017-2019 Pascal Pons <contact@gamesolver.org>
 *
 * Connect4 Game Solver is free software: you can redistribute it and/or
 * modify it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * Connect4 Game Solver is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with Connect4 Game Solver. If not, see <http://www.gnu.org/licenses/>.
 */

#include "solver/Solver.hpp"
#include <iostream>

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
int main() {
  Solver solver;
  bool weak = false;

  std::string opening_book = "7x6.book";

  solver.loadBook(opening_book);

  std::string line = "172737";

  Position P;
  if(P.play(line) != line.size()) {
    std::cerr << "Invalid move: " << (P.nbMoves() + 1) << " \"" << line << "\"" << std::endl;
  } else {
    std::cout << line;
    std::vector<int> scores = solver.analyze(P, weak);
    for(int i = 0; i < Position::WIDTH; i++) std::cout << " " << scores[i];
    int score = solver.solve(P, weak);
    std::cout << " " << score;
    std::cout << std::endl;
  }
}
