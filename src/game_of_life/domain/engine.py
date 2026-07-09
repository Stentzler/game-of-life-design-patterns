from game_of_life.domain.events import GameEvent, GameEventType
from game_of_life.domain.grid import Grid
from game_of_life.observers.base import Observer, Subject
from game_of_life.strategies.base import EvolutionStrategy


class GameEngine(Subject[GameEvent]):
    """Coordinate the domain rules of the Game of Life simulation.

    `GameEngine` is part of the domain/model layer. It does not know anything
    about Pygame, windows, buttons, mouse clicks, fonts, or colors.

    Its current responsibilities are:

    - keep a reference to the current `Grid`;
    - keep a reference to the selected `EvolutionStrategy`;
    - keep a list of attached observers;
    - ask the strategy to calculate the next generation;
    - apply the calculated generation back into the grid;
    - count how many generations have been applied.
    - publish events after important simulation changes.

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
        `GameEngine` is the concrete Subject in the Observer pattern. It knows
        only the `Observer[GameEvent]` interface, not concrete classes such as
        `SimulationSummaryObserver` or `ConsoleLoggingObserver`.
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
        self._observers: list[Observer[GameEvent]] = []

    def attach(self, observer: Observer[GameEvent]) -> None:
        """Register an observer to receive engine events.

        Args:
            observer: Object that implements `Observer[GameEvent]`.

        Study note:
            This is the subscription method from the Observer pattern. The
            engine stores the observer but does not care what concrete class it
            is. It may be a summary holder, logger, history tracker, or a future
            observer we have not written yet.
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer[GameEvent]) -> None:
        """Unregister an observer from future engine events.

        Args:
            observer: Previously attached observer.

        Study note:
            Detaching matters because the subject keeps references to observers.
            If an observer should no longer react, it should be removed from the
            subject's observer list.
        """
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event: GameEvent) -> None:
        """Send an event to every attached observer.

        Args:
            event: Snapshot describing what happened in the engine.

        Study note:
            This method is the core notification loop of the Observer pattern.
            Notice that it calls the same `update(event)` method on every
            observer. The engine does not need `if observer is summary` or `if
            observer is logger` branches.
        """
        for observer in self._observers:
            observer.update(event)

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
        self.notify(self._create_event(GameEventType.GENERATION_ADVANCED))

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
        self.notify(self._create_event(GameEventType.STRATEGY_REPLACED))

    def toggle_cell(self, x: int, y: int) -> None:
        """Toggle one cell and notify observers.

        Study note:
            Editing the grid through the engine keeps observer notifications
            consistent. If states modified `grid` directly, observers such as
            `SimulationSummaryObserver` would not know that the board changed.
        """
        self.grid.toggle_cell(x, y)
        self.notify(self._create_event(GameEventType.CELL_TOGGLED))

    def clear_grid(self) -> None:
        """Clear the grid and notify observers."""
        self.grid.clear()
        self.notify(self._create_event(GameEventType.GRID_CLEARED))

    def randomize_grid(self, alive_probability: float = 0.2) -> None:
        """Randomize the grid and notify observers.

        Args:
            alive_probability: Probability that each cell becomes alive.
        """
        self.grid.randomize(alive_probability)
        self.notify(self._create_event(GameEventType.GRID_RANDOMIZED))

    def _create_event(self, event_type: GameEventType) -> GameEvent:
        """Create a `GameEvent` snapshot from the current engine state.

        Args:
            event_type: The reason this event is being published.

        Returns:
            A frozen event object containing generation, cell counts, and the
            active strategy name.

        Study note:
            Keeping event creation in one helper avoids repeating summary
            calculations in every engine method that needs to notify observers.
        """
        living_cells = int(self.grid.cells.sum())
        total_cells = self.grid.width * self.grid.height

        return GameEvent(
            event_type=event_type,
            generation=self.generation,
            living_cells=living_cells,
            dead_cells=total_cells - living_cells,
            strategy_name=self.strategy.__class__.__name__,
        )
