import numpy as np

from game_of_life.domain.engine import GameEngine
from game_of_life.domain.events import GameEvent, GameEventType
from game_of_life.domain.grid import Grid
from game_of_life.observers import Observer, SimulationSummaryObserver
from game_of_life.strategies import ConwayEvolutionStrategy, HighLifeEvolutionStrategy


class EventCollector(Observer[GameEvent]):
    def __init__(self) -> None:
        self.events: list[GameEvent] = []

    def update(self, event: GameEvent) -> None:
        self.events.append(event)


def create_blinker_engine() -> GameEngine:
    return GameEngine(
        grid=Grid(
            width=5,
            height=5,
            cells=np.array(
                [
                    [0, 0, 0, 0, 0],
                    [0, 0, 1, 0, 0],
                    [0, 0, 1, 0, 0],
                    [0, 0, 1, 0, 0],
                    [0, 0, 0, 0, 0],
                ]
            ),
        ),
        strategy=ConwayEvolutionStrategy(),
    )


def test_next_generation_updates_grid_and_generation_count() -> None:
    engine = create_blinker_engine()

    engine.next_generation()

    assert engine.generation == 1
    assert np.array_equal(
        engine.grid.cells,
        np.array(
            [
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 1, 1, 1, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
            ]
        ),
    )


def test_replace_strategy_changes_future_strategy() -> None:
    engine = create_blinker_engine()

    engine.replace_strategy(HighLifeEvolutionStrategy())

    assert isinstance(engine.strategy, HighLifeEvolutionStrategy)


def test_engine_notifies_attached_observers() -> None:
    engine = create_blinker_engine()
    collector = EventCollector()
    summary = SimulationSummaryObserver()

    engine.attach(collector)
    engine.attach(summary)
    engine.next_generation()

    assert collector.events[-1].event_type == GameEventType.GENERATION_ADVANCED
    assert collector.events[-1].generation == 1
    assert summary.generation == 1
    assert summary.living_cells == 3
    assert summary.dead_cells == 22


def test_engine_edit_operations_publish_events() -> None:
    engine = GameEngine(
        grid=Grid(width=2, height=2),
        strategy=ConwayEvolutionStrategy(),
    )
    collector = EventCollector()
    engine.attach(collector)

    engine.toggle_cell(0, 0)
    engine.clear_grid()
    engine.randomize_grid(alive_probability=1)

    assert [event.event_type for event in collector.events] == [
        GameEventType.CELL_TOGGLED,
        GameEventType.GRID_CLEARED,
        GameEventType.GRID_RANDOMIZED,
    ]
    assert collector.events[-1].living_cells == 4
