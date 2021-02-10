from abc import ABC, abstractmethod
from concurrent import futures
from queue import Queue, Full as FullQueueError, Empty as EmptyQueueError
from typing import Any, Callable, Dict, List, Tuple, Type, Union

from tornado.concurrent import run_on_executor
from tornado.ioloop import IOLoop

from mind.logging import get_logger
from mind.models import Message


logger = get_logger(__name__)


"""
This is an implementation of the [https://refactoring.guru/design-patterns/observer](Observer) design pattern.

It has interfaces (Listener and Tasks) and a Registry that orchestrates Listeners and Tasks.
"""


ListenerClassMessageClassesList = List[Tuple[Type["Listener"], Union[Type["Message"], List[Type["Message"]]]]]


TaskClassArgsList = List[Union[Type["Task"], Tuple[Type["Task"], Tuple]]]


class NotRegisteredError(Exception):
    def __init__(self, _class: Union[Type["Listener"], Type["Task"]]):
        super().__init__(f"{_class.__name__} is not registered")


class NoSubscribedListenerForMessageError(Exception):
    def __init__(self, message_class: Type["Message"]):
        super().__init__(f"No subscribed listeners for {message_class.__name__}")


class Listener(ABC):
    """
    A Listener will have its own Message queue, which stores messages published by any other Task or WebHandler.
    These messages are consumed by a Task.

    Listener is a passive actor from the implementation of Observer design pattern.
    """

    @property
    @abstractmethod
    def queue(self) -> Queue:
        raise NotImplementedError

    def enqueue(self, message) -> None:
        try:
            self.queue.put_nowait(message)
        except FullQueueError as e:
            logger.warning(f"{self.__class__.__name__} queue(maxsize={self.queue.maxsize}) is full")


class Task(ABC):
    """
    A Task implements methods to consume from a Listener's queue.

    Task is an active actor from the implementation of Observer design pattern.

    Usually Task is implemented along with Interface, but it is not always the case:
        MicrophoneStreamTask does not consume from any queue, it only publishes to other queues, so it only implements Task interface.
    """

    executor = futures.ThreadPoolExecutor(10)  # TODO check for this number

    def __init__(self, auto_start: bool = True):
        self.auto_start = auto_start
        self.running = False

    @abstractmethod
    def run(self):
        raise NotImplementedError

    def start(self):
        if self.running:
            return logger.warning(f"{self.__class__.__name__} is already started")
        IOLoop.current().spawn_callback(self._start)

    def stop(self):
        if not self.running:
            return logger.warning(f"{self.__class__.__name__} is already stopped")
        self.running = False

    @run_on_executor
    def _start(self):
        self.running = True

        logger.info(f"Started {self.__class__.__name__}")
        self.run()
        logger.info(f"Stopped {self.__class__.__name__}")

        try:
            IOLoop.current().spawn_callback(self._start)  # to remove it from IOLoop
        except RuntimeError as e:
            logger.warning(e)


class Registry:
    """
    Registry orchestrates the Messaging architecture, which is based on Observer design pattern.

    It makes sure Tasks and Listeners are only instanced once to prevent unexpected behaviors
    such as two Tasks consuming the same queue, which is not allowed.

    It also exposes a method to publish message directly to each subscribed listener's queue.
    """

    _tasks: List[Task] = []

    _listeners: List[Listener] = []

    _subscriptions: Dict[Type[Message], List[Listener]] = {}

    def publish_message(self, context: Union[Listener, Task], message: Message, previous_src: List[Type] = []) -> None:
        message.append_src(previous_src).append_src(context.__class__)
        self._publish_message(message.append_src(previous_src).append_src(context.__class__))

    def get_task(self, task_class: Type[Task]) -> Task:
        for task in self._tasks:
            if task.__class__ == task_class:
                return task
        raise NotRegisteredError(task_class)

    def get_listener(self, listener_class: Type[Listener]) -> Listener:
        for listener in self._listeners:
            if listener.__class__ == listener_class:
                return listener
        raise NotRegisteredError(listener_class)

    def register_listeners(self, listener_class_message_classes_list: ListenerClassMessageClassesList) -> None:
        for listener_class, message_classes in listener_class_message_classes_list:
            if not isinstance(message_classes, list):
                message_classes = [message_classes]
            self.register_listener(listener_class, message_classes)

    def register_listener(self, listener_class: Type[Listener], message_classes: List[Type[Message]]) -> None:
        if listener_class in [l.__class__ for l in self._listeners]:
            logger.warning(f"{listener_class.__name__} is already registered")
            return

        # Task can also be implemented together with Listener
        for task in self._tasks:
            if isinstance(task, Listener) and task.__class__ == listener_class:
                self._listeners.append(task)
                self._subscribe_listener_to_message_classes(task, message_classes)
                return

        listener = listener_class()
        self._listeners.append(listener)
        self._subscribe_listener_to_message_classes(listener, message_classes)

    def register_tasks(self, task_class_args_list: TaskClassArgsList) -> None:
        for task_class_args in task_class_args_list:

            task_class: Type[Task]
            args: Tuple = tuple()

            if isinstance(task_class_args, tuple):
                task_class = task_class_args[0]
                try:
                    args = task_class_args[1]
                except IndexError:
                    pass
            else:
                task_class = task_class_args

            self.register_task(task_class, *args)

    def register_task(self, task_class: Type[Task], *args) -> None:
        if task_class in [t.__class__ for t in self._tasks]:
            logger.warning(f"{task_class.__name__} is already registered")
            return

        # Listener can also be implemented together with Task
        for listener in self._listeners:
            if isinstance(listener, Task) and listener.__class__ == task_class:
                self._tasks.append(listener)
                return

        self._tasks.append(task_class(*args))

    def start_tasks(self) -> None:
        for task in self._tasks:
            if task.auto_start:
                task.start()

    def stop_tasks(self) -> None:
        for task in self._tasks:
            task.stop()

    def clean(self) -> None:
        self.stop_tasks()
        self._tasks = []
        self._listeners = []
        self._subscriptions = {}

    def _publish_message(self, message: Message) -> None:
        try:
            for listener in self._subscriptions[type(message)]:
                if listener.__class__ not in message.src:
                    listener.enqueue(message)
        except KeyError:
            raise NoSubscribedListenerForMessageError(type(message))

    def _subscribe_listener_to_message_classes(self, listener: Listener, message_classes: List[Type[Message]]) -> None:
        for message_class in message_classes:
            self._subscriptions[message_class] = list(set(self._subscriptions.get(message_class, []) + [listener]))


registry = Registry()

publish_message = registry.publish_message

start_task: Callable[[Type[Task]], None] = lambda task_class: registry.get_task(task_class).start()

stop_task: Callable[[Type[Task]], None] = lambda task_class: registry.get_task(task_class).stop()
