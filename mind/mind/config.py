import os

chatbot_name = os.getenv("ROBOT_NAME", "Marvin")

chatbot_language = os.getenv("ROBOT_LANGUAGE", "english").lower()

# TODO use env vars instead, and fix mongo-init.js to also create the chatterbot db

chatbot_params: dict = dict(
    storage_adapter="chatterbot.storage.MongoDatabaseAdapter",
    database_uri="mongodb://chatterbot:password@127.0.0.1:27017/chatterbot",
)
