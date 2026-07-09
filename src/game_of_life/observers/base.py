from abc import ABC, abstractmethod
from typing import Generic, TypeVar


# Event is a placeholder type.
# We do not know the exact event type yet.
# A concrete subscriber will specify it later, for example Subscriber[GameEvent].
Event = TypeVar("Event")

# Generic[Event] means this class is parameterized by an event type. Once a
# concrete subscriber chooses the type, update() should receive that type.
class Subscriber(ABC, Generic[Event]):
    """Define the receiver side of a publisher/subscriber event flow.

    A subscriber is any object that wants to react when a publisher announces
    that something happened.

    This base class is generic:

    - `Subscriber[GameEvent]` means "a subscriber that receives GameEvent
      objects".
    - A future `Subscriber[InventoryEvent]` could receive inventory events.

    Study note:
        This is still the same family of ideas as the Observer pattern, but the
        naming is closer to event-driven systems: publishers emit events, and
        subscribers react to them.

        The important design decision is that the publisher does not know
        concrete subscriber classes. It only knows that every subscriber has an
        `update` method. That keeps the publisher from depending on classes such
        as `SimulationSummarySubscriber` or `ConsoleLoggingSubscriber`.
    """

    @abstractmethod
    def update(self, event: Event) -> None:
        """React to a notification sent by a subject.

        Args:
            event: Data object describing what happened.

        Study note:
            Some examples pass many arguments to `update`, and others pass the
            publisher itself. This project passes one event object because it
            keeps the method signature stable as event data grows.
        """


class Publisher(ABC, Generic[Event]):
    """Define the sender side of a publisher/subscriber event flow.

    A publisher owns a list of subscribers and publishes events when something
    relevant happens.

    Study note:
        `Publisher` is generic for the same reason as `Subscriber`: it describes
        the kind of event being sent. `Publisher[GameEvent]` means "a publisher
        that sends GameEvent objects to subscribers".
    """

    @abstractmethod
    def subscribe(self, subscriber: Subscriber[Event]) -> None:
        """Register a subscriber to receive future events."""

    @abstractmethod
    def unsubscribe(self, subscriber: Subscriber[Event]) -> None:
        """Remove a subscriber so it no longer receives events."""

    @abstractmethod
    def publish(self, event: Event) -> None:
        """Send one event to all currently subscribed subscribers."""
