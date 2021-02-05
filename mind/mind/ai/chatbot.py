import os

from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

from mind.config import chatbot_name, chatbot_params, chatbot_language
from mind.logging import get_logger
from mind.messaging import Listener, Task, Queue, EmptyQueueError, publish_message
from mind.models import Text

logger = get_logger(__name__)


class ChatBotListenerTask(Listener, Task):

    queue: Queue = Queue(maxsize=20)

    running = False

    chatbot: ChatBot

    def __init__(self, auto_start: bool = True):
        super().__init__(auto_start)

        self.chatbot = ChatBot(
            chatbot_name,
            logger=logger,
            **chatbot_params,
        )

    def run(self):
        while self.running:
            try:
                text = self.queue.get(timeout=2)
                self.process_text(text)
                self.queue.task_done()
            except EmptyQueueError:
                continue

    def process_text(self, text: Text):
        if not text.value:
            return
        response = self.chatbot.get_response(text.value)
        if response.text:
            publish_message(self, Text(response.text))


def train_chatterbot_corpus():
    _chatbot = ChatBot(
        chatbot_name,
        logger=logger,
        **chatbot_params,
    )

    trainer = ChatterBotCorpusTrainer(_chatbot)

    trainer.train(f"chatterbot.corpus.{chatbot_language}")  # make sure the corpus contains your language

    response = _chatbot.get_response("How are you doing today?")
    print(response)
