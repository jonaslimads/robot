import os

from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

from mind.config import chatbot_name, chatbot_params, chatbot_language
from mind.logging import get_logger
from mind.messaging import Listener, Task, Queue, EmptyQueueError
from mind.models import Text

logger = get_logger(__name__)

db_path = os.path.join(os.path.dirname(__file__), f"../../models/chatterbot/{chatbot_language}.db")


class ChatBotListenerTask(Listener, Task):

    queue: Queue = Queue(maxsize=20)

    running = False

    def __init__(self):
        self.chatbot = ChatBot(
            chatbot_name,
            logger=get_logger(__name__),
            database_uri=f"sqlite:///{os.path.abspath(db_path)}",
            **chatbot_params,
        )

    def enqueue(self, text: Text) -> None:
        super().enqueue(text)

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
        # logger.info(f"--> Processing {text}")


def train_chatterbot_corpus():
    _chatbot = ChatBot(
        chatbot_name,
        database_uri=f"sqlite:///{os.path.abspath(db_path)}",
    )

    trainer = ChatterBotCorpusTrainer(_chatbot)

    trainer.train(f"chatterbot.corpus.{chatbot_language}")  # make sure the corpus contains your language

    response = _chatbot.get_response("How are you doing today?")
    print(response)
