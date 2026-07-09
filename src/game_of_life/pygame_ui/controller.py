import pygame

from game_of_life.app import GameOfLifeApp
from game_of_life.pygame_ui.renderer import PygameRenderer
from game_of_life.states import SimulationAction, SimulationCommand


class InputController:
    """Translate Pygame input into application commands.

    The controller is the Controller layer. It knows about Pygame events and UI
    hit testing, but it does not implement simulation rules.
    """

    def __init__(self, renderer: PygameRenderer):
        """Create a controller that can query renderer button/grid layout."""
        self.renderer = renderer

    def process_events(self, app: GameOfLifeApp) -> None:
        """Process all pending Pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                app.handle_event(SimulationCommand(SimulationAction.STOP))
                continue

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_left_click(app, event.pos)

    def _handle_left_click(
        self,
        app: GameOfLifeApp,
        position: tuple[int, int],
    ) -> None:
        """Translate a left mouse click into a simulation command."""
        button = self.renderer.get_button_at(position, app)

        if button is not None:
            app.handle_event(SimulationCommand(button.action))
            return

        grid_position = self.renderer.grid_position_from_screen(position)

        if grid_position is None:
            return

        x, y = grid_position
        app.handle_event(
            SimulationCommand(
                action=SimulationAction.TOGGLE_CELL,
                x=x,
                y=y,
            )
        )
