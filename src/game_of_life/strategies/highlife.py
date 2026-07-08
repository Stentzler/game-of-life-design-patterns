import numpy as np

from game_of_life.domain.grid import Grid
from game_of_life.strategies.base import EvolutionStrategy


class HighLifeEvolutionStrategy(EvolutionStrategy):
    """Calculate generations using the HighLife cellular automaton rules.

    HighLife is a variation of Conway's Game of Life.

    The survival rule is the same:

    - A live cell survives with two or three live neighbors.

    The birth rule is different:

    - A dead cell becomes alive with exactly three live neighbors.
    - A dead cell also becomes alive with exactly six live neighbors.

    That extra "birth on six neighbors" rule is what makes HighLife different
    from Conway.

    Study note:
        This class demonstrates why Strategy is useful. `GameEngine` can receive
        either `ConwayEvolutionStrategy` or `HighLifeEvolutionStrategy` and call
        the same method. The engine does not need an `if strategy == ...` block.
    """

    def calculate_next_state(self, grid: Grid) -> np.ndarray:
        """Return the next generation using HighLife rules.

        Args:
            grid: Current board state.

        Returns:
            A new matrix with the next generation.

        Study note:
            The structure is almost identical to Conway's strategy. The useful
            difference is isolated in one line: dead cells are born with three
            or six living neighbors.
        """
        next_cells = np.copy(grid.cells)

        for y in range(grid.height):
            for x in range(grid.width):
                alive_neighbors = self._count_alive_neighbors(grid, x, y)

                if grid.is_alive(x, y):
                    next_cells[y, x] = 1 if alive_neighbors in (2, 3) else 0
                else:
                    next_cells[y, x] = 1 if alive_neighbors in (3, 6) else 0

        return next_cells
