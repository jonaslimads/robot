import os
import signal
import asyncio
from functools import partial
from typing import List, Any

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.log
from tornado.options import parse_command_line, define, options

from mind import __version__, get_logger
from mind.server import routes
from mind.speech_to_text.SpeechToText import SpeechToText
from mind.signal_handler import signal_handler

logger = get_logger(__name__)

define("port", default=int(os.getenv("ROBOT_SERVER_PORT", 8765)))


def start_background_tasks():
    SpeechToText().start()


def run_server():
    tornado.log.enable_pretty_logging()
    parse_command_line()

    logger.info(f"Starting Robot's mind server at port {options.port}...")

    app = tornado.web.Application(routes)

    server = tornado.httpserver.HTTPServer(app)
    server.listen(options.port)

    signal.signal(signal.SIGTERM, partial(signal_handler, server))
    signal.signal(signal.SIGINT, partial(signal_handler, server))

    io_loop = tornado.ioloop.IOLoop.current()
    start_background_tasks()
    io_loop.start()

    logger.info("Bye")


if __name__ == "__main__":
    run_server()
