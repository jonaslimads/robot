from abc import abstractmethod
import asyncio
from typing import Callable, List, Tuple, Type, Union

from tornado import gen
from tornado.testing import gen_test, main, AsyncHTTPTestCase
from tornado.platform.asyncio import AnyThreadEventLoopPolicy
from tornado.web import Application

from mind.logging import get_logger
from mind.messaging import (
    registry,
    Listener,
    Queue,
    Task,
    EmptyQueueError,
    ListenerClassMessageClassesList,
    TaskClassAutoStartList,
)
from mind.models import Message, Text, AudioFrame, VideoFrame


logger = get_logger(__name__)


class BreakLoopException(Exception):
    pass


class BaseListenerTaskTest(AsyncHTTPTestCase):
    @property
    @abstractmethod
    def task_class_auto_start_list(self) -> TaskClassAutoStartList:
        raise NotImplementedError

    @property
    @abstractmethod
    def listener_class_message_classes_list(self) -> ListenerClassMessageClassesList:
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

    def start_tasks(self):
        registry.start_tasks()

    def publish_message(self, message: Message):
        registry._publish_message(message)

    async def consume_queue(self, callback: Callable, *args, **kwargs):
        while True:
            try:
                message = BaseListenerTaskTest._Listener.queue.get(timeout=2)
                BaseListenerTaskTest._Listener.queue.task_done()
                callback(message, *args, **kwargs)
            except EmptyQueueError:
                await gen.sleep(1)
            except BreakLoopException:
                break
        self.stop()

    def break_loop(self):
        raise BreakLoopException
