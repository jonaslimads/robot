import os

from chatterbot import ChatBot as ChatBotInstance
from chatterbot.trainers import ChatterBotCorpusTrainer
from tornado.queues import Queue, QueueFull

from mind.config import chatbot_name, chatbot_params, chatbot_language
from mind.messaging import Listener
from mind.models import Text

db_path = os.path.join(os.path.dirname(__file__), f"../../models/chatterbot/{chatbot_language}.db")


class ChatBotListener(Listener):

    queue: Queue = Queue(maxsize=20)

    def enqueue(self, text: Text) -> None:
        super().enqueue(text)

    async def listen(self):
        await ChatBot(self.queue).process_texts()


class ChatBot:

    queue: Queue

    chatbot: ChatBotInstance

    def __init__(self, queue: Queue):
        self.queue = queue
        self.chatbot = ChatBotInstance(
            chatbot_name,
            logger=get_logger(__name__),
            database_uri=f"sqlite:///{os.path.abspath(db_path)}",
            **chatbot_params,
        )

    async def process_texts(self):
        pass
        # async for text in self.queue:
        #     logger.warning(text)


def train_chatterbot_corpus():
    _chatbot = ChatBot(
        chatbot_name,
        database_uri=f"sqlite:///{os.path.abspath(db_path)}",
    )

    trainer = ChatterBotCorpusTrainer(_chatbot)

    trainer.train(f"chatterbot.corpus.{chatbot_language}")  # make sure the corpus contains your language

    response = _chatbot.get_response("How are you doing today?")
    print(response)


# to prevent circular import
from mind import get_logger

logger = get_logger(__name__)
