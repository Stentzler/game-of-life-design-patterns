# State Class Implementation

```mermaid
classDiagram
    class GameOfLifeApp {
        -current_state
        +handle_event(command)
        +update(delta_time)
        +change_state(state)
        +stop()
    }

    class SimulationState {
        <<interface>>
        +handle_event(context, command)
        +update(context, delta_time)
    }

    class StateContext {
        <<protocol>>
        +engine
        +evolution_interval
        +random_alive_probability
        +change_state(state)
    }

    class SimulationCommand {
        +action
        +x
        +y
    }

    class SimulationAction {
        <<enumeration>>
        START
        PAUSE
        RESUME
        EDIT
        STOP
        TOGGLE_CELL
        NEXT_GENERATION
        CLEAR_GRID
        RANDOMIZE_GRID
    }

    class EditingState {
    }

    class RunningState {
    }

    class PausedState {
    }

    GameOfLifeApp --> SimulationState : current state
    GameOfLifeApp ..|> StateContext : satisfies
    SimulationState --> StateContext : uses
    SimulationState --> SimulationCommand : handles
    SimulationCommand --> SimulationAction : contains
    SimulationState <|-- EditingState : implements
    SimulationState <|-- RunningState : implements
    SimulationState <|-- PausedState : implements
```
---
# State Workflow

```mermaid
graph TD
    Start([Start]) --> Editing[Editing]
    
    Editing -->|Start| Running[Running]
    Editing -->|Toggle Cell| Editing
    Editing -->|Next Generation| Editing
    Editing -->|Randomize Grid| Editing
    Editing -->|Clear Grid| Editing
    Running -->|Edit| Editing
    
    Running -->|Pause| Paused[Paused]
    Paused -->|Resume| Running
    Editing -->|Stop| Stopped([Stopped])
    Running -->|Stop| Stopped
    Paused -->|Stop| Stopped
```
