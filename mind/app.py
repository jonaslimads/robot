import os
import signal
import asyncio
from functools import partial
from typing import List, Any

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.log

from mind import __version__, get_logger, routes
from mind.messaging import publisher
from mind.signal import signal_handler

logger = get_logger(__name__)


def make_app(port: int):
    tornado.log.enable_pretty_logging()

    logger.info(f"Starting Robot's mind server at port {port}...")

    app = tornado.web.Application(routes)

    server = tornado.httpserver.HTTPServer(app)
    server.listen(port)

    signal.signal(signal.SIGTERM, partial(signal_handler, server))
    signal.signal(signal.SIGINT, partial(signal_handler, server))

    io_loop = tornado.ioloop.IOLoop.current()
    publisher.spawn_listeners()
    io_loop.start()

    logger.info("Bye")

    return app


if __name__ == "__main__":
    port = int(os.getenv("ROBOT_SERVER_PORT", 8765))
    make_app(port)
