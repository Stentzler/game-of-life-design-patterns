```mermaid
classDiagram
    class Subject {
        <<interface>>
        +attach(observer)
        +detach(observer)
        +notify(event)
    }

    class Observer {
        <<interface>>
        +update(event)
    }

    class GameEngine {
        -observers
        +next_generation()
        +toggle_cell()
        +clear_grid()
        +randomize_grid()
        +attach(observer)
        +detach(observer)
        +notify(event)
    }

    class GameEvent {
        +event_type
        +generation
        +living_cells
        +dead_cells
        +strategy_name
    }

    class GameEventType {
        <<enumeration>>
        GENERATION_ADVANCED
        STRATEGY_REPLACED
        CELL_TOGGLED
        GRID_CLEARED
        GRID_RANDOMIZED
    }

    class SimulationSummaryObserver {
    }

    class ConsoleLoggingObserver {
    }

    Subject <|-- GameEngine : implements
    Observer <|-- SimulationSummaryObserver : implements
    Observer <|-- ConsoleLoggingObserver : implements
    GameEngine --> Observer : notifies
    GameEngine --> GameEvent : creates
    GameEvent --> GameEventType : has type
    Observer --> GameEvent : receives
```
