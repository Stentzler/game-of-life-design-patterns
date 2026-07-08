# Game of Life Design Patterns Study

This project refactors a small Pygame implementation of Conway's Game of Life
to study design patterns in a practical codebase.

The original version is kept in `game_of_life_001.py` as a reference. The new
implementation is organized under `src/game_of_life/` so each responsibility has
a clear place.

## Architecture Overview

The project follows a simple Model-View-Controller-style structure:

| Layer | Responsibility | Package |
| --- | --- | --- |
| Model | Grid data, generations, and Game of Life rules | `domain/`, `strategies/` |
| View | Drawing the grid, cells, controls, and statistics | `pygame_ui/renderer.py` |
| Controller | Reading user input and delegating behavior | `pygame_ui/controller.py` |
| Application | Connecting the model, view, controller, and current state | `app.py` |

MVC is used here as an architectural guide. The design patterns are introduced
inside that structure only where they solve a real coupling problem.

## Design Patterns

### Strategy

The evolution rules are moved out of the game loop and into interchangeable
strategy classes.

`GameEngine` will ask an `EvolutionStrategy` to calculate the next grid state.
This lets us use Conway rules first and later add alternatives such as HighLife
without changing the engine.

### State

The application behavior depends on whether the user is editing, running, or
paused.

Instead of spreading mode checks across the code, the app will delegate input
and update behavior to the current `SimulationState`.

### Observer

The domain layer will publish events when the simulation changes.

Observers such as `SimulationSummaryObserver` and `ConsoleLoggingObserver` can
react to those events without forcing `GameEngine` to know about summary views,
logging, or future features.

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

## Implementation Order

The implementation plan is tracked in [implementation.md](implementation.md).
