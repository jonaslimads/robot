import os

chatbot_name = os.getenv("ROBOT_NAME", "Marvin")

chatbot_language = os.getenv("ROBOT_LANGUAGE", "english").lower()

chatbot_params: dict = dict()
