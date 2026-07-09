from __future__ import annotations

from game_of_life.states.base import (
    SimulationAction,
    SimulationCommand,
    SimulationState,
    StateContext,
)


class RunningState(SimulationState):
    """Represent the active simulation mode.

    In running mode, the grid evolves automatically over time. The user cannot
    edit cells directly while this state is active.

    Args:
        evolution_interval: Number of seconds between automatic generations.

    Study note:
        This is the concrete State that owns automatic evolution behavior. The
        application does not need an `if running` block. It simply calls
        `current_state.update(app, delta_time)`, and this state decides when the
        engine should advance.
    """

    def __init__(self, evolution_interval: float = 1.0):
        """Create a running state with a generation interval.

        Raises:
            ValueError: If `evolution_interval` is not greater than zero.

        Study note:
            The timer here is intentionally small. It is not a separate design
            pattern yet. If timing rules become more complex later, we can
            extract this into an `EvolutionClock` object.
        """
        if evolution_interval <= 0:
            raise ValueError("Evolution interval must be greater than zero.")

        self.evolution_interval = evolution_interval
        self._elapsed_time = 0.0

    def handle_event(self, context: StateContext, command: SimulationCommand) -> None:
        """Handle commands that are valid while running.

        Supported commands:

        - `PAUSE`: transition to `PausedState`;
        - `EDIT`: transition to `EditingState`.

        Cell editing is ignored while running because this mode represents an
        active simulation.
        """
        if command.action == SimulationAction.PAUSE:
            # Local import avoids circular imports between concrete states.
            from game_of_life.states.paused import PausedState

            context.change_state(PausedState())
            return

        if command.action == SimulationAction.EDIT:
            # Local import avoids circular imports between concrete states.
            from game_of_life.states.editing import EditingState

            context.change_state(EditingState())

    def update(self, context: StateContext, delta_time: float) -> None:
        """Advance generations when enough time has passed.

        Args:
            context: Application context that owns the engine.
            delta_time: Seconds elapsed since the previous update.

        Study note:
            Pygame will eventually provide `delta_time` from its main loop. This
            state accumulates that time and advances the engine whenever the
            configured interval is reached.
        """
        self._elapsed_time += delta_time

        while self._elapsed_time >= self.evolution_interval:
            context.engine.next_generation()
            self._elapsed_time -= self.evolution_interval
