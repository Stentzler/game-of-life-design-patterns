from __future__ import annotations

from game_of_life.states.base import SimulationState
from game_of_life.states.editing import EditingState
from game_of_life.states.paused import PausedState
from game_of_life.states.running import RunningState


class SimulationStateFactory:
    """Create concrete simulation states.

    This class is a small Factory pattern implementation.

    The factory has one responsibility: centralize the creation of concrete
    State objects. It does not decide when transitions happen. That decision
    remains inside `EditingState`, `RunningState`, and `PausedState`.

    Study note:
        This is useful because concrete states often need to transition to one
        another. If every state imports every other state directly, circular
        imports can appear. The factory gives states a single creation API:

            context.state_factory.create_running(...)

        So the state keeps the transition rule, while object construction lives
        in one place.
    """

    def create_editing(self) -> SimulationState:
        """Create the editable state.

        Editing mode allows the user to toggle cells and manually advance one
        generation.
        """
        return EditingState()

    def create_running(self, evolution_interval: float) -> SimulationState:
        """Create the running state.

        Args:
            evolution_interval: Number of seconds between automatic generation
                updates.
        """
        return RunningState(evolution_interval=evolution_interval)

    def create_paused(self) -> SimulationState:
        """Create the paused state.

        Paused mode stops automatic evolution and locks grid editing.
        """
        return PausedState()
