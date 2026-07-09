from __future__ import annotations

from game_of_life.states.base import (
    SimulationAction,
    SimulationCommand,
    SimulationState,
    StateContext,
)


class PausedState(SimulationState):
    """Represent the stopped and locked simulation mode.

    In paused mode, the simulation does not advance and the grid cannot be
    edited. The only state command this class handles is `RESUME`.

    Study note:
        Paused is intentionally stricter than editing. Both states stop
        automatic evolution, but only editing allows the grid to change.
    """

    def handle_event(self, context: StateContext, command: SimulationCommand) -> None:
        """Handle commands that are valid while paused.

        Supported commands:

        - `RESUME`: transition back to `RunningState`.

        All other commands are ignored because paused mode is locked.
        """
        if command.action == SimulationAction.RESUME:
            # Local import avoids circular imports between concrete states.
            from game_of_life.states.running import RunningState

            context.change_state(RunningState(evolution_interval=context.evolution_interval))

    def update(self, context: StateContext, delta_time: float) -> None:
        """Do nothing while paused.

        Time can pass while paused, but generations do not advance and the grid
        is not modified.
        """
