import numpy as np

from game_of_life.domain.grid import Grid
from game_of_life.strategies.base import EvolutionStrategy


class ConwayEvolutionStrategy(EvolutionStrategy):
    """Calculate generations using Conway's original Game of Life rules.

    Conway's Game of Life uses four core rules:

    1. A live cell with fewer than two live neighbors dies.
    2. A live cell with two or three live neighbors survives.
    3. A live cell with more than three live neighbors dies.
    4. A dead cell with exactly three live neighbors becomes alive.

    Study note:
        This class is a concrete Strategy. It implements the same public method
        required by `EvolutionStrategy`, but it decides the next state using
        Conway's specific rules.

        Later, `GameEngine` will not need to know these rules. It will only call
        `strategy.calculate_next_state(grid)`.
    """

    def calculate_next_state(self, grid: Grid) -> np.ndarray:
        """Return the next generation using Conway's rules.

        Args:
            grid: Current board state.

        Returns:
            A new matrix with the next generation.

        Study note:
            We start from a copy of the current matrix because unchanged cells
            can keep their current value. Then we overwrite only the cells whose
            next state is determined by the rules.
        """
        next_cells = np.copy(grid.cells)

        for y in range(grid.height):
            for x in range(grid.width):
                alive_neighbors = self._count_alive_neighbors(grid, x, y)

                if grid.is_alive(x, y):
                    next_cells[y, x] = 1 if alive_neighbors in (2, 3) else 0
                else:
                    next_cells[y, x] = 1 if alive_neighbors == 3 else 0

        return next_cells
