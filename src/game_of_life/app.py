import logging

from game_of_life import config
from game_of_life.domain.engine import GameEngine
from game_of_life.domain.grid import Grid
from game_of_life.observers import ConsoleLoggingObserver, SimulationSummaryObserver
from game_of_life.states.base import (
    SimulationAction,
    SimulationCommand,
    SimulationState,
)
from game_of_life.states.editing import EditingState
from game_of_life.strategies import ConwayEvolutionStrategy


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
        summary: SimulationSummaryObserver | None = None,
    ):
        """Create an application context.

        Args:
            engine: Domain engine used by states when generations need to
                advance or cells need to be edited.
            initial_state: Optional starting state. If omitted, the application
                starts in `EditingState`.
            evolution_interval: Seconds between generations while running.
            random_alive_probability: Probability used by the randomize button.
            summary: Optional observer that stores the latest simulation summary
                for the renderer.

        Study note:
            The engine still owns simulation rules and grid updates. The app
            owns application mode. Keeping those responsibilities separate makes
            the design easier to reason about.
        """
        self.engine = engine
        self.current_state = initial_state or EditingState()
        self.evolution_interval = evolution_interval
        self.random_alive_probability = random_alive_probability
        self.summary = summary
        self.is_running = True

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
    grid, engine, strategy, observers, and app context.
    """
    grid = Grid(width=config.GRID_COLUMNS, height=config.GRID_ROWS)
    engine = GameEngine(
        grid=grid,
        strategy=ConwayEvolutionStrategy(),
    )
    summary = SimulationSummaryObserver()

    engine.attach(summary)
    engine.attach(ConsoleLoggingObserver())
    engine.randomize_grid(config.RANDOM_ALIVE_PROBABILITY)

    return GameOfLifeApp(
        engine=engine,
        evolution_interval=config.EVOLUTION_INTERVAL,
        random_alive_probability=config.RANDOM_ALIVE_PROBABILITY,
        summary=summary,
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
