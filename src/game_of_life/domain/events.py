from dataclasses import dataclass
from enum import Enum


class GameEventType(Enum):
    """List the domain events that `GameEngine` can publish.

    Each value describes something meaningful that happened in the simulation.

    Study note:
        Event types let observers decide which notifications they care about.
        For example, a summary observer may update on every event, while a
        console logger may log different messages for different event types.
    """

    GENERATION_ADVANCED = "generation_advanced"
    STRATEGY_REPLACED = "strategy_replaced"


@dataclass(frozen=True)
class GameEvent:
    """Describe one notification sent from the game engine to observers.

    Args:
        event_type: Kind of event that happened.
        generation: Current generation number after the event.
        living_cells: Number of alive cells in the grid.
        dead_cells: Number of dead cells in the grid.
        strategy_name: Name of the strategy currently used by the engine.

    Study note:
        This object is the payload of the Observer pattern in this project.
        Instead of calling observers with several loose arguments, the engine
        sends a single object that groups the notification data.

        The dataclass is frozen because events should be snapshots. Once an
        event is published, observers should not mutate it.
    """

    event_type: GameEventType
    generation: int
    living_cells: int
    dead_cells: int
    strategy_name: str
