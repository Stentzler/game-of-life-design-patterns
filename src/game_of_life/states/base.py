from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from game_of_life.domain.engine import GameEngine


class SimulationAction(Enum):
    """List the actions that can be handled by simulation states.

    These actions are intentionally independent from Pygame. Later, the Pygame
    input controller can translate keyboard and mouse events into these actions.

    Study note:
        This keeps the State pattern focused on application behavior instead of
        coupling state classes directly to one UI library.
    """

    START = "start"
    PAUSE = "pause"
    RESUME = "resume"
    EDIT = "edit"
    STOP = "stop"
    TOGGLE_CELL = "toggle_cell"
    NEXT_GENERATION = "next_generation"
    CLEAR_GRID = "clear_grid"
    RANDOMIZE_GRID = "randomize_grid"
    SWITCH_STRATEGY = "switch_strategy"


@dataclass(frozen=True)
class SimulationCommand:
    """Represent one action sent to the current simulation state.

    Args:
        action: The action requested by the user or application.
        x: Optional horizontal cell coordinate. Used by `TOGGLE_CELL`.
        y: Optional vertical cell coordinate. Used by `TOGGLE_CELL`.

    Study note:
        Some State pattern examples pass raw strings or concrete UI events into
        `handle_event`. This project uses a small command object so the state
        methods receive a clear, typed input.
    """

    action: SimulationAction
    x: int | None = None
    y: int | None = None


class StateFactory(Protocol):
    """Describe how concrete simulation states are created.

    This protocol is the small interface used by concrete states when they need
    to transition to another mode.

    Study note:
        This introduces the Factory pattern without coupling the State classes
        to each other. A state still decides *which* state comes next, but the
        factory decides *how* that next state object is built.
    """

    def create_editing(self) -> SimulationState:
        """Create the editable simulation state."""

    def create_running(self, evolution_interval: float) -> SimulationState:
        """Create the running simulation state."""

    def create_paused(self) -> SimulationState:
        """Create the paused simulation state."""


class StateContext(Protocol):
    """Describe what states need from the application context.

    States do not need to depend on the full concrete `GameOfLifeApp` class.
    They only need a small set of capabilities:

    - access to the domain engine;
    - access to the configured evolution interval;
    - access to a state factory;
    - a way to replace the current state.

    Study note:
        This protocol removes the circular import pressure between `app.py` and
        the state modules. It also follows a clean design principle: depend on
        the smallest interface you need, not a larger concrete class.
    """

    engine: GameEngine
    evolution_interval: float
    random_alive_probability: float
    state_factory: StateFactory

    def change_state(self, state: SimulationState) -> None:
        """Replace the current state."""

    def switch_to_next_strategy(self) -> None:
        """Replace the engine strategy with the next available strategy."""


class SimulationState(ABC):
    """Define the interface for application modes.

    This class is the base of the State pattern in this project.

    A state object answers two questions:

    - How should the application react to a command right now?
    - What should happen during an update tick right now?

    Study note:
        Without the State pattern, `GameOfLifeApp` would likely grow many mode
        checks:

            if mode == "editing":
                ...
            elif mode == "running":
                ...
            elif mode == "paused":
                ...

        With the State pattern, the app delegates behavior to the current state:

            current_state.handle_event(app, command)
            current_state.update(app, delta_time)

        Each concrete state owns the behavior that makes sense for that mode.
    """

    @abstractmethod
    def handle_event(self, context: StateContext, command: SimulationCommand) -> None:
        """Handle one command in the context of the current application state."""

    @abstractmethod
    def update(self, context: StateContext, delta_time: float) -> None:
        """Update the application while this state is active."""
