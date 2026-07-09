# Game of Life Design Patterns Study

This project refactors a small Pygame implementation of Conway's Game of Life
to study design patterns in a practical codebase.

The original version is kept in `game_of_life_001.py` as a reference. The
refactored implementation lives under `src/game_of_life/`.

## Architecture

The project follows a simple Model-View-Controller-style structure:

| Layer | Responsibility | Main files |
| --- | --- | --- |
| Model / Domain | Grid data, generations, rules, events | `domain/`, `strategies/`, `observers/` |
| View | Drawing cells, controls, and summary values | `pygame_ui/renderer.py` |
| Controller | Translating Pygame input into app commands | `pygame_ui/controller.py` |
| Application | Connecting engine, state, renderer, and controller | `app.py` |

The key rule is that Pygame stays in the UI layer. Domain classes such as
`Grid`, `GameEngine`, and the strategies do not import Pygame.

## Design Patterns

### Strategy

The evolution rules are implemented as interchangeable strategies:

- `EvolutionStrategy`
- `ConwayEvolutionStrategy`
- `HighLifeEvolutionStrategy`

`GameEngine` does not know the details of Conway or HighLife. It only calls:

```python
next_cells = strategy.calculate_next_state(grid)
```

This lets the app replace the evolution algorithm without rewriting the engine.

### Observer

`GameEngine` is a `Subject[GameEvent]`. It publishes events when the simulation
changes.

Current observers:

- `SimulationSummaryObserver`: keeps the latest generation/cell summary.
- `ConsoleLoggingObserver`: logs engine events through Python logging.

The engine only knows the `Observer[GameEvent]` interface, not concrete observer
classes.

### State

`GameOfLifeApp` owns the current `SimulationState`.

Current states:

- `EditingState`: stopped and editable.
- `RunningState`: advances generations automatically.
- `PausedState`: stopped and locked.

The app delegates commands and update ticks to the current state:

```python
current_state.handle_event(app, command)
current_state.update(app, delta_time)
```

This avoids spreading `if mode == ...` checks across the application.

## Project Structure

```text
src/game_of_life/
├── app.py
├── config.py
├── domain/
│   ├── engine.py
│   ├── events.py
│   └── grid.py
├── observers/
│   ├── base.py
│   ├── console_logger.py
│   └── simulation_summary.py
├── pygame_ui/
│   ├── controller.py
│   └── renderer.py
├── states/
│   ├── base.py
│   ├── editing.py
│   ├── paused.py
│   └── running.py
└── strategies/
    ├── base.py
    ├── conway.py
    └── highlife.py
```

## Diagrams

- [Class diagram](docs/class_diagram.md)
- [Observer diagram](docs/observer_diagram.md)
- [State diagram](docs/state_diagram.md)

## Install

Create and activate a virtual environment, then install the project in editable
mode:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Runtime dependencies:

- `numpy`
- `pygame`

Development dependency:

- `pytest`

## Run

After installing the project:

```bash
python -m game_of_life.app
```

Without installing the project, use:

```bash
PYTHONPATH=src python -m game_of_life.app
```

## Controls

Editing mode:

- Click cells to toggle them.
- `Start`: begin automatic evolution.
- `Next`: advance one generation manually.
- `Random`: randomize the grid.
- `Clear`: clear all cells.

Running mode:

- `Pause`: pause the simulation.
- `Edit`: return to editing mode.

Paused mode:

- `Resume`: continue running.

## Tests

Run the real test suite:

```bash
pytest
```

The root-level `test_*.py` files are manual learning playgrounds. They print
step-by-step examples and can be deleted later.

## Implementation Notes

The implementation plan is tracked in [implementation.md](implementation.md).
