import logging

from game_of_life.domain.events import GameEvent, GameEventType
from game_of_life.observers.base import Observer

logger = logging.getLogger(__name__)


class ConsoleLoggingObserver(Observer[GameEvent]):
    """Log readable messages when the game engine publishes events.

    `ConsoleLoggingObserver` is a concrete Observer. It reacts to the same
    `GameEvent` objects as `SimulationSummaryObserver`, but its responsibility
    is different: it reports what happened through Python's logging system.

    Study note:
        This class shows why Observer helps with extension. We can add logging
        without adding log statements to `GameEngine`. The engine publishes an
        event, and this observer decides how to report it.

        This observer uses `logger.info(...)` instead of `print(...)` because
        logging is configurable. The application can decide where messages go,
        which level is visible, and how messages are formatted.
    """

    def update(self, event: GameEvent) -> None:
        """Log a message that matches the received event type.

        Args:
            event: Event published by the game engine.

        Study note:
            The observer receives every event from the subject. It can choose
            how to react based on `event.event_type`.
        """
        if event.event_type == GameEventType.GENERATION_ADVANCED:
            logger.info(
                "Generation advanced to %s. Living cells: %s. Dead cells: %s.",
                event.generation,
                event.living_cells,
                event.dead_cells,
            )
            return

        if event.event_type == GameEventType.STRATEGY_REPLACED:
            logger.info(
                "Strategy replaced with %s at generation %s.",
                event.strategy_name,
                event.generation,
            )
            return

        logger.info("Unhandled game event: %s.", event.event_type.value)
