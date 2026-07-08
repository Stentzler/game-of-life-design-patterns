from abc import ABC, abstractmethod

import numpy as np

from game_of_life.domain.grid import Grid


class EvolutionStrategy(ABC):
    """Define the interface for Game of Life evolution rules.

    This class is the base of the Strategy pattern in this project.

    A strategy object answers one question:

    "Given the current grid, what should the next generation look like?"

    `GameEngine` will depend on this abstraction instead of depending directly
    on Conway's rules. That means the engine can run Conway, HighLife, or any
    future cellular automaton rule without changing its own code.

    Study note:
        The Strategy pattern is useful when one part of the system needs to
        perform an operation, but the exact algorithm should be replaceable.
        Here, the operation is "calculate the next generation", and each
        concrete strategy provides a different algorithm.
    """

    @abstractmethod
    def calculate_next_state(self, grid: Grid) -> np.ndarray:
        """Calculate and return the next generation for a grid.

        Args:
            grid: Current board state.

        Returns:
            A new NumPy array with the same shape as `grid.cells`.

        Important:
            A strategy should not mutate `grid` directly. It should calculate a
            new matrix and return it. The `GameEngine` will decide when to apply
            that new matrix by calling `grid.replace_cells(...)`.

        Why this matters:
            In Game of Life, every cell in the next generation must be based on
            the same current generation. If we changed cells directly while
            calculating, later cells could accidentally read already-updated
            neighbors.
        """

    def _count_alive_neighbors(self, grid: Grid, x: int, y: int) -> int:
        """Count the living neighbors around one cell.

        Args:
            grid: Board containing the current generation.
            x: Horizontal coordinate of the cell being inspected.
            y: Vertical coordinate of the cell being inspected.

        Returns:
            The number of alive cells in the eight neighboring positions.

        Study note:
            This is a protected method because it is shared behavior for
            strategies, not part of the public API that the engine needs to
            call.

            This project keeps the same wrap-around behavior as the original
            script. The grid behaves like its edges are connected:

            - moving left from column `0` reaches the last column;
            - moving right from the last column reaches column `0`;
            - moving above row `0` reaches the last row;
            - moving below the last row reaches row `0`.

            This is called a toroidal grid. It avoids special edge checks and
            preserves the behavior from `game_of_life_001.py`.
        """
        alive_neighbors = 0

        for y_offset in (-1, 0, 1):
            for x_offset in (-1, 0, 1):
                if x_offset == 0 and y_offset == 0:
                    continue

                neighbor_x = (x + x_offset) % grid.width
                neighbor_y = (y + y_offset) % grid.height

                if grid.is_alive(neighbor_x, neighbor_y):
                    alive_neighbors += 1

        return alive_neighbors
