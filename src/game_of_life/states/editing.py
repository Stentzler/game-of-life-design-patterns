from __future__ import annotations

from game_of_life.states.base import (
    SimulationAction,
    SimulationCommand,
    SimulationState,
    StateContext,
)


class EditingState(SimulationState):
    """Represent the editable, stopped simulation mode.

    In editing mode, the simulation is not advancing automatically. The user can
    change the grid by toggling cells and can optionally advance one generation
    manually.

    Study note:
        Editing is different from paused. Both stop automatic evolution, but
        editing allows board changes while paused locks the board.
    """

    def handle_event(self, context: StateContext, command: SimulationCommand) -> None:
        """Handle commands that are valid while editing.

        Supported commands:

        - `START`: transition to `RunningState`;
        - `TOGGLE_CELL`: change one cell in the grid;
        - `NEXT_GENERATION`: advance exactly one generation manually.
        - `CLEAR_GRID`: remove all living cells;
        - `RANDOMIZE_GRID`: fill the board with random living cells.
        - `SWITCH_STRATEGY`: replace the evolution rule used by the engine.

        Other commands are ignored because they do not make sense while editing.
        """
        if command.action == SimulationAction.START:
            next_state = context.state_factory.create_running(
                evolution_interval=context.evolution_interval
            )
            context.change_state(next_state)
            return

        if command.action == SimulationAction.TOGGLE_CELL:
            self._toggle_cell(context, command)
            return

        if command.action == SimulationAction.NEXT_GENERATION:
            context.engine.next_generation()
            return

        if command.action == SimulationAction.CLEAR_GRID:
            context.engine.clear_grid()
            return

        if command.action == SimulationAction.RANDOMIZE_GRID:
            context.engine.randomize_grid(context.random_alive_probability)
            return

        if command.action == SimulationAction.SWITCH_STRATEGY:
            context.switch_to_next_strategy()

    def update(self, context: StateContext, delta_time: float) -> None:
        """Do nothing while editing.

        Editing mode is intentionally passive. Time can pass, but generations do
        not advance unless the user explicitly requests `NEXT_GENERATION`.
        """

    def _toggle_cell(self, context: StateContext, command: SimulationCommand) -> None:
        """Toggle the cell described by a command.

        Raises:
            ValueError: If the command does not include both cell coordinates.
        """
        if command.x is None or command.y is None:
            raise ValueError("TOGGLE_CELL requires x and y coordinates.")

        context.engine.toggle_cell(command.x, command.y)
