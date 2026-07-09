import numpy as np

from game_of_life.app import GameOfLifeApp
from game_of_life.domain.engine import GameEngine
from game_of_life.domain.grid import Grid
from game_of_life.states import (
    EditingState,
    PausedState,
    RunningState,
    SimulationAction,
    SimulationCommand,
)
from game_of_life.strategies import ConwayEvolutionStrategy, HighLifeEvolutionStrategy


def create_app(evolution_interval: float = 1.0) -> GameOfLifeApp:
    available_strategies = [
        ConwayEvolutionStrategy(),
        HighLifeEvolutionStrategy(),
    ]
    engine = GameEngine(
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
        strategy=available_strategies[0],
    )
    return GameOfLifeApp(
        engine=engine,
        available_strategies=available_strategies,
        evolution_interval=evolution_interval,
    )


def test_app_starts_in_editing_state() -> None:
    app = create_app()

    assert isinstance(app.current_state, EditingState)


def test_editing_state_allows_cell_toggle() -> None:
    app = create_app()

    app.handle_event(
        SimulationCommand(
            action=SimulationAction.TOGGLE_CELL,
            x=0,
            y=0,
        )
    )

    assert app.engine.grid.is_alive(0, 0)


def test_editing_state_can_start_running_state() -> None:
    app = create_app()

    app.handle_event(SimulationCommand(SimulationAction.START))

    assert isinstance(app.current_state, RunningState)


def test_editing_state_can_switch_strategy() -> None:
    app = create_app()

    app.handle_event(SimulationCommand(SimulationAction.SWITCH_STRATEGY))

    assert isinstance(app.engine.strategy, HighLifeEvolutionStrategy)


def test_running_state_advances_after_interval() -> None:
    app = create_app(evolution_interval=1.0)
    app.handle_event(SimulationCommand(SimulationAction.START))

    app.update(delta_time=0.5)
    assert app.engine.generation == 0

    app.update(delta_time=0.5)
    assert app.engine.generation == 1


def test_running_state_ignores_cell_toggle() -> None:
    app = create_app()
    app.handle_event(SimulationCommand(SimulationAction.START))

    app.handle_event(
        SimulationCommand(
            action=SimulationAction.TOGGLE_CELL,
            x=0,
            y=0,
        )
    )

    assert not app.engine.grid.is_alive(0, 0)


def test_running_state_ignores_strategy_switch() -> None:
    app = create_app()
    app.handle_event(SimulationCommand(SimulationAction.START))

    app.handle_event(SimulationCommand(SimulationAction.SWITCH_STRATEGY))

    assert isinstance(app.engine.strategy, ConwayEvolutionStrategy)


def test_running_can_pause_and_paused_can_resume() -> None:
    app = create_app()
    app.handle_event(SimulationCommand(SimulationAction.START))

    app.handle_event(SimulationCommand(SimulationAction.PAUSE))
    assert isinstance(app.current_state, PausedState)

    app.handle_event(SimulationCommand(SimulationAction.RESUME))
    assert isinstance(app.current_state, RunningState)


def test_paused_state_does_not_update_or_edit() -> None:
    app = create_app()
    app.handle_event(SimulationCommand(SimulationAction.START))
    app.handle_event(SimulationCommand(SimulationAction.PAUSE))

    app.update(delta_time=10)
    app.handle_event(
        SimulationCommand(
            action=SimulationAction.TOGGLE_CELL,
            x=0,
            y=0,
        )
    )

    assert app.engine.generation == 0
    assert not app.engine.grid.is_alive(0, 0)


def test_stop_command_stops_app() -> None:
    app = create_app()

    app.handle_event(SimulationCommand(SimulationAction.STOP))

    assert not app.is_running
