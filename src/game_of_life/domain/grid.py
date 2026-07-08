import numpy as np


class Grid:
    """Represent the current board of the Game of Life.

    In the architecture of this project, `Grid` is part of the domain/model
    layer. Its job is to own the cell matrix and expose clear operations for
    reading or changing that matrix.

    The grid stores cells in a two-dimensional NumPy array with shape
    `(height, width)`, because NumPy prints the first dimension as rows and the
    second dimension as columns.

    - `0` means the cell is dead.
    - `1` means the cell is alive.

    The public methods still receive coordinates as `(x, y)`, because that is
    the natural way to think about screen positions: `x` is horizontal and `y`
    is vertical. Internally, the grid translates that to `cells[y, x]`.

    Other parts of the application should not need to know how the cells are
    stored internally. For example, the renderer can ask whether a cell is
    alive, and the engine can replace the whole matrix after calculating a new
    generation.
    """

    def __init__(self, width: int, height: int, cells: np.ndarray | None = None):
        """Create a grid with the given dimensions.

        Args:
            width: Number of columns in the board.
            height: Number of rows in the board.
            cells: Optional existing cell matrix. This is useful in tests and
                when recreating a known pattern. If omitted, the grid starts
                empty, with all cells dead.

        Raises:
            ValueError: If width or height is not positive, or if `cells` does
                not match the expected grid shape.

        Study note:
            We copy the received `cells` array instead of storing it directly.
            That prevents outside code from accidentally changing the grid by
            mutating the same NumPy array reference.
        """
        if width <= 0:
            raise ValueError("Grid width must be greater than zero.")

        if height <= 0:
            raise ValueError("Grid height must be greater than zero.")

        self.width = width
        self.height = height
        self.cells = np.zeros((height, width), dtype=int)

        if cells is not None:
            self.replace_cells(cells)

    def is_alive(self, x: int, y: int) -> bool:
        """Return whether the cell at the given position is alive.

        Args:
            x: Horizontal cell coordinate.
            y: Vertical cell coordinate.

        Returns:
            `True` when the cell contains `1`, otherwise `False`.

        Study note:
            This method hides the numeric representation from callers. The rest
            of the program can ask a domain question, "is this cell alive?",
            instead of checking `grid.cells[x, y] == 1` everywhere.
        """
        self._validate_position(x, y)
        return self.cells[y, x] == 1

    def toggle_cell(self, x: int, y: int) -> None:
        """Switch a cell between dead and alive.

        Args:
            x: Horizontal cell coordinate.
            y: Vertical cell coordinate.

        Study note:
            This method will be used by the editing state when the user clicks
            the board. Keeping the operation here means input handling does not
            need to know NumPy details.
        """
        self._validate_position(x, y)
        self.cells[y, x] = 0 if self.is_alive(x, y) else 1

    def replace_cells(self, new_cells: np.ndarray) -> None:
        """Replace the whole board with a new matrix.

        Args:
            new_cells: Matrix containing the next cell state.

        Raises:
            ValueError: If the new matrix does not have the same shape as this
                grid.

        Study note:
            Game of Life generations should be calculated from the current
            board and then applied all at once. This method gives `GameEngine`
            a safe way to replace the current generation with the next one.
        """
        if new_cells.shape != (self.height, self.width):
            raise ValueError(
                "New cells must have shape "
                f"({self.height}, {self.width}), got {new_cells.shape}."
            )

        self.cells = new_cells.astype(int, copy=True)

    def clear(self) -> None:
        """Mark every cell as dead.

        Study note:
            Clearing is a board operation, so it belongs in `Grid`. The app,
            renderer, or controller should not loop through the matrix manually
            to perform this behavior.
        """
        self.cells.fill(0)

    def randomize(self, alive_probability: float = 0.2) -> None:
        """Fill the board with random dead and alive cells.

        Args:
            alive_probability: Probability that each cell becomes alive. The
                default value, `0.2`, means roughly 20% of cells should start
                alive.

        Raises:
            ValueError: If `alive_probability` is outside the inclusive range
                from `0` to `1`.

        Study note:
            Randomizing is still a grid operation because it changes the board
            contents. The chosen probability is configuration; the way cells are
            written belongs here.
        """
        if not 0 <= alive_probability <= 1:
            raise ValueError("Alive probability must be between 0 and 1.")

        self.cells = np.random.choice(
            [0, 1],
            size=(self.height, self.width),
            p=[1 - alive_probability, alive_probability],
        )

    def _validate_position(self, x: int, y: int) -> None:
        """Raise an error when a coordinate is outside the grid.

        This private helper keeps the public methods small and makes the
        boundary rule consistent across all cell-level operations.
        """
        if not 0 <= x < self.width:
            raise ValueError(f"Cell x position must be between 0 and {self.width - 1}.")

        if not 0 <= y < self.height:
            raise ValueError(f"Cell y position must be between 0 and {self.height - 1}.")
