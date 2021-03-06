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
from tornado.platform.asyncio import AnyThreadEventLoopPolicy

from mind import __version__, get_logger, routes, setup_registry, registry
from mind.signal import signal_handler

logger = get_logger(__name__)


def make_app(port: int):
    asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())
    tornado.log.enable_pretty_logging()

    logger.info(f"Starting Robot's mind server at port {port}...")

    setup_registry()

    app = tornado.web.Application(routes)

    server = tornado.httpserver.HTTPServer(app)
    server.listen(port)

    signal.signal(signal.SIGTERM, partial(signal_handler, server, registry.stop_tasks))
    signal.signal(signal.SIGINT, partial(signal_handler, server, registry.stop_tasks))

    io_loop = tornado.ioloop.IOLoop.current()
    registry.start_tasks()
    io_loop.start()

    return app


if __name__ == "__main__":
    port = int(os.getenv("ROBOT_SERVER_PORT", 8765))
    make_app(port)
