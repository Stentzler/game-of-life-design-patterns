from game_of_life.domain.grid import Grid
from game_of_life.strategies.base import EvolutionStrategy


class GameEngine:
    """Coordinate the domain rules of the Game of Life simulation.

    `GameEngine` is part of the domain/model layer. It does not know anything
    about Pygame, windows, buttons, mouse clicks, fonts, or colors.

    Its current responsibilities are:

    - keep a reference to the current `Grid`;
    - keep a reference to the selected `EvolutionStrategy`;
    - ask the strategy to calculate the next generation;
    - apply the calculated generation back into the grid;
    - count how many generations have been applied.

    Study note:
        The engine does not create the grid by itself. A `Grid` is passed into
        the constructor. This is called dependency injection: instead of hiding
        dependencies inside the class, we provide them from the outside.

        The engine also does not implement Conway or HighLife rules. A strategy
        object is passed into the constructor, and the engine only calls the
        strategy interface:

            next_cells = strategy.calculate_next_state(grid)

        That is where the Strategy pattern becomes useful. The engine can work
        with any object that follows the `EvolutionStrategy` contract.

    Observer note:
        Later, when we implement the Observer pattern, this class will also
        notify observers after important domain events. We are not adding that
        yet because the event object and observer interface do not exist.
    """

    def __init__(self, grid: Grid, strategy: EvolutionStrategy):
        """Create a game engine with an existing grid and evolution strategy.

        Args:
            grid: Current board state. The engine stores this object and updates
                it when a new generation is applied.
            strategy: Rule object used to calculate the next generation.

        Study note:
            Passing `grid` and `strategy` from the outside keeps this class
            focused on coordination. It also lets tests create tiny custom grids
            and swap strategies without changing the engine code.

            The type hints define the constructor contract. We assume callers
            create the engine with a real `Grid` and a real `EvolutionStrategy`.
            Runtime validation can be added later if the engine starts receiving
            dependencies from untrusted input.
        """
        self.grid = grid
        self.strategy = strategy
        self.generation = 0

    def next_generation(self) -> None:
        """Advance the simulation by one generation.

        This method coordinates the core simulation flow:

        1. Give the current grid to the selected strategy.
        2. Receive a new matrix representing the next generation.
        3. Replace the grid's current cells with that new matrix.
        4. Increase the generation counter.

        Study note:
            The engine does not calculate neighbor counts or cell survival
            rules. Those details belong to the strategy. The engine only
            decides when the calculation happens and when the grid is updated.
        """
        next_cells = self.strategy.calculate_next_state(self.grid)
        self.grid.replace_cells(next_cells)
        self.generation += 1

    def replace_strategy(self, strategy: EvolutionStrategy) -> None:
        """Replace the evolution strategy used by the engine.

        Args:
            strategy: New rule object used for future generations.

        Study note:
            This method is the practical switch point for the Strategy pattern.
            Existing grid data stays the same, but future calls to
            `next_generation()` use different evolution rules.

            Like the constructor, this method relies on the type hint as the
            contract: callers should pass a valid `EvolutionStrategy`.
        """
        self.strategy = strategy
