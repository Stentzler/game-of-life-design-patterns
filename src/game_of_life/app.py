import logging

from game_of_life import config
from game_of_life.domain.engine import GameEngine
from game_of_life.domain.grid import Grid
from game_of_life.observers import ConsoleLoggingSubscriber, SimulationSummarySubscriber
from game_of_life.states.base import (
    SimulationAction,
    SimulationCommand,
    SimulationState,
    StateFactory,
)
from game_of_life.states.factory import SimulationStateFactory
from game_of_life.strategies import (
    ConwayEvolutionStrategy,
    EvolutionStrategy,
    HighLifeEvolutionStrategy,
)


class GameOfLifeApp:
    """Application context for the Game of Life.

    `GameOfLifeApp` is the context class in the State pattern. It owns the
    current state and delegates behavior to that state.

    The app does not decide directly what `START`, `PAUSE`, or `RESUME` means in
    every mode. Instead, it forwards commands to `current_state`.

    Study note:
        In the State pattern, the context holds a reference to a state object.
        The state object can ask the context to transition to another state by
        calling `app.change_state(...)`.
    """

    def __init__(
        self,
        engine: GameEngine,
        initial_state: SimulationState | None = None,
        evolution_interval: float = config.EVOLUTION_INTERVAL,
        random_alive_probability: float = config.RANDOM_ALIVE_PROBABILITY,
        summary: SimulationSummarySubscriber | None = None,
        state_factory: StateFactory | None = None,
        available_strategies: list[EvolutionStrategy] | None = None,
    ):
        """Create an application context.

        Args:
            engine: Domain engine used by states when generations need to
                advance or cells need to be edited.
            initial_state: Optional starting state. If omitted, the application
                starts in `EditingState`.
            evolution_interval: Seconds between generations while running.
            random_alive_probability: Probability used by the randomize button.
            summary: Optional subscriber that stores the latest simulation
                summary for the renderer.
            state_factory: Optional factory used to create concrete application
                states. If omitted, the default `SimulationStateFactory` is used.
            available_strategies: Ordered strategy objects available to the
                Strategy switch button. If omitted, Conway and HighLife are
                available.

        Study note:
            The engine still owns simulation rules and grid updates. The app
            owns application mode and the list of selectable strategies. Keeping
            those responsibilities separate makes the design easier to reason
            about.
        """
        self.engine = engine
        self.summary = summary
        self.is_running = True
        self.evolution_interval = evolution_interval
        self.random_alive_probability = random_alive_probability
        self.state_factory = state_factory or SimulationStateFactory()
        self.available_strategies = (
            available_strategies or self._create_default_strategies()
        )
        self.current_state = initial_state or self.state_factory.create_editing()

    def handle_event(self, command: SimulationCommand) -> None:
        """Delegate one command to the current state.

        `STOP` is handled by the app itself because quitting the application is
        global behavior, not behavior specific to editing, running, or paused.
        """
        if command.action == SimulationAction.STOP:
            self.stop()
            return

        self.current_state.handle_event(self, command)

    def update(self, delta_time: float) -> None:
        """Delegate an update tick to the current state."""
        if self.is_running:
            self.current_state.update(self, delta_time)

    def change_state(self, state: SimulationState) -> None:
        """Replace the current application state.

        Args:
            state: New state object that will receive future commands and update
                ticks.
        """
        self.current_state = state

    def switch_to_next_strategy(self) -> None:
        """Replace the engine strategy with the next available strategy.

        This method is called by `EditingState`, because editing mode decides
        that strategy switching is allowed. The app owns the available strategy
        list, and the engine only receives the selected strategy through
        `replace_strategy(...)`.

        Study note:
            This keeps the Strategy pattern boundary clear:

            - `GameOfLifeApp` knows which strategies are available;
            - `EditingState` knows when switching is allowed;
            - `GameEngine` only knows how to replace its current strategy.
        """
        current_index = self._current_strategy_index()
        next_index = (current_index + 1) % len(self.available_strategies)
        self.engine.replace_strategy(self.available_strategies[next_index])

    @property
    def current_strategy_name(self) -> str:
        """Return a readable name for the active evolution strategy."""
        return self._strategy_name(self.engine.strategy)

    @property
    def next_strategy_name(self) -> str:
        """Return a readable name for the next selectable strategy."""
        current_index = self._current_strategy_index()
        next_index = (current_index + 1) % len(self.available_strategies)

        return self._strategy_name(self.available_strategies[next_index])

    def _current_strategy_index(self) -> int:
        """Return the index of the active strategy in `available_strategies`.

        Strategies are compared by concrete class. This allows the engine to be
        created with one `ConwayEvolutionStrategy` instance while the app owns
        another `ConwayEvolutionStrategy` instance in its selectable list.
        """
        current_strategy_type = type(self.engine.strategy)

        for index, strategy in enumerate(self.available_strategies):
            if type(strategy) is current_strategy_type:
                return index

        return -1

    def _strategy_name(self, strategy: EvolutionStrategy) -> str:
        """Return the UI-friendly name for a strategy object."""
        return strategy.__class__.__name__.replace("EvolutionStrategy", "")

    def _create_default_strategies(self) -> list[EvolutionStrategy]:
        """Create the default strategy list available in the UI."""
        return [
            ConwayEvolutionStrategy(),
            HighLifeEvolutionStrategy(),
        ]

    def stop(self) -> None:
        """Mark the application as no longer running."""
        self.is_running = False

    def run(self) -> None:
        """Run the Pygame application loop.

        Study note:
            Pygame imports are kept inside this method so the domain and state
            examples can still run in environments where Pygame is not
            installed. The UI is the only layer that should require Pygame.
        """
        import pygame

        from game_of_life.pygame_ui.controller import InputController
        from game_of_life.pygame_ui.renderer import PygameRenderer

        pygame.init()
        screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption("Game of Life - Design Patterns")

        clock = pygame.time.Clock()
        renderer = PygameRenderer(screen)
        controller = InputController(renderer)

        while self.is_running:
            delta_time = clock.tick(config.FPS) / 1000

            controller.process_events(self)
            self.update(delta_time)
            renderer.render(self)

        pygame.quit()


def create_default_app() -> GameOfLifeApp:
    """Create a runnable application with default dependencies.

    This function is the composition root for the project: it wires together the
    grid, engine, strategy, subscribers, and app context.
    """
    grid = Grid(width=config.GRID_COLUMNS, height=config.GRID_ROWS)
    available_strategies: list[EvolutionStrategy] = [
        ConwayEvolutionStrategy(),
        HighLifeEvolutionStrategy(),
    ]
    engine = GameEngine(
        grid=grid,
        strategy=available_strategies[0],
    )
    summary = SimulationSummarySubscriber()

    engine.subscribe(summary)
    engine.subscribe(ConsoleLoggingSubscriber())
    engine.randomize_grid(config.RANDOM_ALIVE_PROBABILITY)

    return GameOfLifeApp(
        engine=engine,
        evolution_interval=config.EVOLUTION_INTERVAL,
        random_alive_probability=config.RANDOM_ALIVE_PROBABILITY,
        summary=summary,
        available_strategies=available_strategies,
    )


def main() -> None:
    """Run the Pygame version of the application."""
    logging.basicConfig(
        level=config.LOG_LEVEL,
        format="%(levelname)s:%(name)s:%(message)s",
    )
    create_default_app().run()


if __name__ == "__main__":
    main()
