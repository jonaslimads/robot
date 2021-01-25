import os
import signal
import asyncio
from functools import partial
from typing import List, Any
from concurrent import futures

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.log

from mind import __version__, get_logger, routes, start_tasks, stop_tasks
from mind.signal import signal_handler

logger = get_logger(__name__)


def make_app(port: int):
    tornado.log.enable_pretty_logging()

    logger.info(f"Starting Robot's mind server at port {port}...")

    app = tornado.web.Application(routes)

    server = tornado.httpserver.HTTPServer(app)
    server.listen(port)

    signal.signal(signal.SIGTERM, partial(signal_handler, server, stop_tasks))
    signal.signal(signal.SIGINT, partial(signal_handler, server, stop_tasks))

    io_loop = tornado.ioloop.IOLoop.current()
    start_tasks(io_loop)
    io_loop.start()

    return app


if __name__ == "__main__":
    port = int(os.getenv("ROBOT_SERVER_PORT", 8765))
    make_app(port)
