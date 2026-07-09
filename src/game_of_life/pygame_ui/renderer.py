from dataclasses import dataclass

import pygame

from game_of_life import config
from game_of_life.app import GameOfLifeApp
from game_of_life.states import SimulationAction
from game_of_life.states.editing import EditingState
from game_of_life.states.paused import PausedState
from game_of_life.states.running import RunningState


@dataclass(frozen=True)
class Button:
    """Represent one clickable UI button."""

    label: str
    action: SimulationAction
    rect: pygame.Rect


class PygameRenderer:
    """Draw the Game of Life application with Pygame.

    The renderer is the View layer. It reads the current app state and draws it,
    but it does not modify the grid, advance generations, or change states.
    """

    def __init__(self, screen: pygame.Surface):
        """Create a renderer for a Pygame screen surface."""
        self.screen = screen
        self.font = pygame.font.Font(None, 26)
        self.small_font = pygame.font.Font(None, 22)

    def render(self, app: GameOfLifeApp) -> None:
        """Draw the full frame."""
        self.screen.fill(config.WHITE)
        self._draw_cells(app)
        self._draw_grid_lines()
        self._draw_toolbar(app)
        pygame.display.flip()

    def get_button_at(
        self,
        position: tuple[int, int],
        app: GameOfLifeApp,
    ) -> Button | None:
        """Return the button at a screen position, if any."""
        for button in self._build_buttons(app):
            if button.rect.collidepoint(position):
                return button

        return None

    def grid_position_from_screen(
        self,
        position: tuple[int, int],
    ) -> tuple[int, int] | None:
        """Convert a screen position to grid coordinates.

        Returns `None` when the position is outside the grid area.
        """
        screen_x, screen_y = position

        if screen_x < 0 or screen_x >= config.GRID_WIDTH:
            return None

        if screen_y < 0 or screen_y >= config.GRID_HEIGHT:
            return None

        return screen_x // config.CELL_SIZE, screen_y // config.CELL_SIZE

    def _draw_cells(self, app: GameOfLifeApp) -> None:
        """Draw all living cells."""
        grid = app.engine.grid

        for y in range(grid.height):
            for x in range(grid.width):
                if not grid.is_alive(x, y):
                    continue

                cell = pygame.Rect(
                    x * config.CELL_SIZE,
                    y * config.CELL_SIZE,
                    config.CELL_SIZE,
                    config.CELL_SIZE,
                )
                pygame.draw.rect(self.screen, config.BLACK, cell)

    def _draw_grid_lines(self) -> None:
        """Draw the grid line overlay."""
        for x in range(0, config.GRID_WIDTH + 1, config.CELL_SIZE):
            pygame.draw.line(
                self.screen,
                config.LIGHT_GRAY,
                (x, 0),
                (x, config.GRID_HEIGHT),
            )

        for y in range(0, config.GRID_HEIGHT + 1, config.CELL_SIZE):
            pygame.draw.line(
                self.screen,
                config.LIGHT_GRAY,
                (0, y),
                (config.GRID_WIDTH, y),
            )

    def _draw_toolbar(self, app: GameOfLifeApp) -> None:
        """Draw controls and summary below the grid."""
        toolbar_rect = pygame.Rect(
            0,
            config.GRID_HEIGHT,
            config.SCREEN_WIDTH,
            config.TOOLBAR_HEIGHT,
        )
        pygame.draw.rect(self.screen, config.DARK_GRAY, toolbar_rect)

        for button in self._build_buttons(app):
            self._draw_button(button)

        self._draw_summary(app)

    def _draw_button(self, button: Button) -> None:
        """Draw one button."""
        pygame.draw.rect(self.screen, config.BLUE, button.rect, border_radius=4)
        text = self.font.render(button.label, True, config.WHITE)
        text_rect = text.get_rect(center=button.rect.center)
        self.screen.blit(text, text_rect)

    def _draw_summary(self, app: GameOfLifeApp) -> None:
        """Draw current state and summary values."""
        state_name = app.current_state.__class__.__name__.replace("State", "")
        summary = app.summary

        living_cells = int(app.engine.grid.cells.sum())
        dead_cells = app.engine.grid.width * app.engine.grid.height - living_cells
        living_percentage = (
            summary.living_percentage if summary is not None else 0.0
        )

        if summary is not None:
            living_cells = summary.living_cells
            dead_cells = summary.dead_cells

        lines = [
            f"State: {state_name}",
            f"Strategy: {app.current_strategy_name}",
            f"Generation: {app.engine.generation}",
            f"Living: {living_cells}",
            f"Dead: {dead_cells}",
            f"Alive: {living_percentage:.2f}%",
        ]

        x = 500
        y = config.GRID_HEIGHT + 10

        for line in lines:
            text = self.small_font.render(line, True, config.WHITE)
            self.screen.blit(text, (x, y))
            y += 15

    def _build_buttons(self, app: GameOfLifeApp) -> list[Button]:
        """Build the visible buttons for the current state."""
        actions = self._actions_for_state(app)
        buttons: list[Button] = []

        button_width = 88
        button_height = 32
        spacing = 10
        x = 12
        y = config.GRID_HEIGHT + 16

        for label, action in actions:
            rect = pygame.Rect(x, y, button_width, button_height)
            buttons.append(Button(label=label, action=action, rect=rect))
            x += button_width + spacing

        return buttons

    def _actions_for_state(
        self,
        app: GameOfLifeApp,
    ) -> list[tuple[str, SimulationAction]]:
        """Return toolbar actions available for the current state."""
        if isinstance(app.current_state, EditingState):
            return [
                ("Start", SimulationAction.START),
                ("Next", SimulationAction.NEXT_GENERATION),
                ("Random", SimulationAction.RANDOMIZE_GRID),
                ("Clear", SimulationAction.CLEAR_GRID),
                ("Strategy", SimulationAction.SWITCH_STRATEGY),
            ]

        if isinstance(app.current_state, RunningState):
            return [
                ("Pause", SimulationAction.PAUSE),
                ("Edit", SimulationAction.EDIT),
            ]

        if isinstance(app.current_state, PausedState):
            return [("Resume", SimulationAction.RESUME)]

        return []
