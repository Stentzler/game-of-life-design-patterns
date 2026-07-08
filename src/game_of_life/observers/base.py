from abc import ABC, abstractmethod
from typing import Generic, TypeVar


# Event is a placeholder type.
# We do not know the exact event type yet.
# A concrete observer will specify it later, for example Observer[GameEvent].
Event = TypeVar("Event")

# Generic[Event] means this class is parameterized by an event type.
# Once a concrete observer chooses the type, update() should receive that type.
class Observer(ABC, Generic[Event]):
    """Define the receiver side of the Observer pattern.

    In the Observer pattern, an observer is any object that wants to react when
    a subject announces that something happened.

    This base class is generic:

    - `Observer[GameEvent]` means "an observer that receives GameEvent objects".
    - A future `Observer[InventoryEvent]` could receive inventory events.

    Study note:
        The important design decision is that the subject does not know concrete
        observer classes. It only knows that every observer has an `update`
        method. That keeps the subject from depending on classes such as
        `SimulationSummaryObserver` or `ConsoleLoggingObserver`.
    """

    @abstractmethod
    def update(self, event: Event) -> None:
        """React to a notification sent by a subject.

        Args:
            event: Data object describing what happened.

        Study note:
            Some Observer examples pass many arguments to `update`, and others
            pass the subject itself. This project passes one event object because
            it keeps the method signature stable as event data grows.
        """


class Subject(ABC, Generic[Event]):
    """Define the sender side of the Observer pattern.

    A subject owns a list of observers and notifies them when something relevant
    happens. The subject is also called an observable in some books and
    frameworks.

    Study note:
        `Subject` is generic for the same reason as `Observer`: it describes the
        kind of event being sent. `Subject[GameEvent]` means "a subject that
        notifies observers with GameEvent objects".
    """

    @abstractmethod
    def attach(self, observer: Observer[Event]) -> None:
        """Register an observer to receive future notifications."""

    @abstractmethod
    def detach(self, observer: Observer[Event]) -> None:
        """Remove an observer so it no longer receives notifications."""

    @abstractmethod
    def notify(self, event: Event) -> None:
        """Send one event to all currently attached observers."""
