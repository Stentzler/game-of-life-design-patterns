from typing import Protocol

from game_of_life.domain.events import GameEvent
from game_of_life.observers.base import Subscriber


class SimulationSummary(Protocol):
    """Describe the read side of the current simulation summary.

    `GameOfLifeApp` and the renderer only need to read summary values. They do
    not need to know that the concrete object is also a subscriber.

    Study note:
        This protocol applies the Dependency Inversion Principle. The app can
        depend on the small summary interface it needs, while the engine still
        depends on the separate `Subscriber[GameEvent]` interface used for event
        publication.
    """

    generation: int
    living_cells: int
    dead_cells: int
    living_percentage: float


class SimulationSummarySubscriber(Subscriber[GameEvent]):
    """Keep the latest simulation summary from game events.

    `SimulationSummarySubscriber` is a concrete subscriber. It listens to
    `GameEvent` notifications and stores the latest known state summary.

    The engine does not need to know that this class exists. The engine only
    calls `subscriber.update(event)`. This class decides what to do with the
    event.

    Study note:
        This subscriber demonstrates a useful reason to use publisher/subscriber
        event flow: a current summary is a reaction to simulation changes, but
        it is not part of the evolution algorithm itself.
    """

    def __init__(self) -> None:
        """Create an empty simulation summary subscriber.

        Before the first event arrives, all values are initialized to zero.
        After the engine publishes to this subscriber, these values mirror the
        latest event snapshot.
        """
        self.generation = 0
        self.living_cells = 0
        self.dead_cells = 0
        self.living_percentage = 0.0

    def update(self, event: GameEvent) -> None:
        """Update the current summary from a game event.

        Args:
            event: Event published by the game engine.

        Study note:
            This method does not ask the engine for data. It uses only the event
            payload. That keeps the subscriber focused and keeps coupling low.
        """
        total_cells = event.living_cells + event.dead_cells

        self.generation = event.generation
        self.living_cells = event.living_cells
        self.dead_cells = event.dead_cells
        self.living_percentage = (
            event.living_cells / total_cells * 100 if total_cells > 0 else 0.0
        )
