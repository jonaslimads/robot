import os

from mind.logging import get_logger
from mind.messaging import Listener, Task, Queue, EmptyQueueError, publish_message
from mind.models import Text
from mind.messaging import registry

logger = get_logger(__name__)


class TextToSpeechListenerTask(Listener, Task):

    queue: Queue = Queue(maxsize=20)

    running = False

    def run(self):
        while self.running:
            try:
                text = self.queue.get(timeout=2)
                if isinstance(text, Text):
                    self.speak(text.value)
                self.queue.task_done()
            except EmptyQueueError:
                continue

    def speak(self, text: str):
        logger.info(f"--- Speaking {text}")
        publish_message(self, Text(value=text + "."))
