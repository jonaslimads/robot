from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any

from tornado.ioloop import IOLoop
from tornado.queues import Queue, QueueFull

from mind.logging import get_logger
from mind.models import Message


logger = get_logger(__name__)


class Listener(ABC):

    spawned = False

    auto_spawn = True

    @property
    @abstractmethod
    def queue(self) -> Queue:
        raise NotImplementedError

    @abstractmethod
    def enqueue(self, message) -> None:
        try:
            self.queue.put_nowait(message)
        except QueueFull as e:
            logger.warning(f"{self.__class__.__name__} queue(maxsize={self.queue.maxsize}) is full")

    @abstractmethod
    async def listen(self):
        raise NotImplementedError


class Publisher:

    subscriptions: Dict[str, List[Listener]] = {}

    def publish(self, message: Any) -> None:
        message_class = type(message).__name__
        try:
            for listener in self.subscriptions[message_class]:
                listener.enqueue(message)
        except KeyError:
            logger.error(f"Could not find listeners for {message_class}")

    def subscribe_and_spawn(self, class_name: str, listener: Listener) -> None:
        """ Used when the instance that implements Listener is already created, such as WebHandlers """
        self.subscribe_many({class_name: [listener]})
        self.spawn_listener(listener)

    # TODO search by class name to prevent something like:
    # [<mind.server.BoardWebSocketHandler.BoardWebSocketHandler object at 0x7f4e08263370>, <mind.server.BoardWebSocketHandler.BoardWebSocketHandler object at 0x7f4df84f9520>]
    def subscribe_many(self, subscriptions: Dict[str, List[Listener]]) -> None:
        """ It must not assign directly to self.subscriptions to not overwrite existing subscriptions """
        for class_name, listeners in subscriptions.items():
            self.subscriptions[class_name] = list(set(self.subscriptions.get(class_name, []) + listeners))
            # c = self.subscriptions.get(class_name, [])
            # [c.append(l) for l in listeners if l not in c]
            # self.subscriptions[class_name] = c

    def spawn_listeners(self) -> None:
        for listener in [l for l in self.listeners if l.auto_spawn]:
            self.spawn_listener(listener)

    def spawn_listener(self, listener: Listener) -> None:
        if listener.spawned:
            logger.debug(f"{listener.__class__.__name__} already spawned...")
            return
        listener.spawned = True
        IOLoop.current().spawn_callback(listener.listen)
        logger.debug(f"Spawned {listener.__class__.__name__}")

    def find_listener(self, class_name: str) -> Listener:
        for l in self.listeners:
            if l.__class__.__name__ == class_name:
                return l
        raise KeyError(f"Listener {class_name} not found")

    @property
    def listeners(self) -> List[Listener]:
        _listeners: set = set()
        for _, listeners in self.subscriptions.items():
            _listeners = _listeners | set(listeners)
        return list(_listeners)


publisher = Publisher()
