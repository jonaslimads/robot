from abc import abstractmethod
import asyncio
from typing import List, Tuple, Type

from tornado import gen
from tornado.testing import gen_test, main, AsyncHTTPTestCase
from tornado.platform.asyncio import AnyThreadEventLoopPolicy
from tornado.web import Application

from mind.logging import get_logger
from mind.messaging import registry, Listener, Queue, Task
from mind.models import Message, Text


logger = get_logger(__name__)


class BaseListenerTaskTest(AsyncHTTPTestCase):
    @property
    @abstractmethod
    def task_class_auto_start_list(self) -> List[Tuple[Type[Task], bool]]:
        raise NotImplementedError

    @property
    @abstractmethod
    def listener_class_message_classes_list(self) -> List[Tuple[Type[Listener], List[Type[Message]]]]:
        raise NotImplementedError

    class _Listener(Listener):
        queue: Queue = Queue(maxsize=5)

    def get_app(self):
        asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())
        app = Application()

        registry.register_tasks(self.task_class_auto_start_list)
        registry.register_listeners(self.listener_class_message_classes_list)

        return app

    def stop(self):
        """Clean registry up to prevent passing state (such as queue) from one test to another,
        so the next registry.start_.. will recreate the tasks and listeners.
        """
        super().stop()
        registry.clean()

    def _publish_message(self, message: Message):
        registry._publish_message(message)
