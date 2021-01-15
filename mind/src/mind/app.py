import os
import time
import signal
import logging
import asyncio
from functools import partial
from typing import List, Any

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.log
from tornado.options import define, options

from mind import __version__, get_logger
from mind.server.handlers import CameraWebSocketHandler, LogWebSocketHandler, MicrophoneWebSocketHandler, MqttWebHandler

__author__ = "Jonas Lima"
__copyright__ = "Jonas Lima"
__license__ = "gpl"

logger = get_logger(__name__)

routes = [
    (r"/ws/camera", CameraWebSocketHandler),
    (r"/ws/boards/head/log", LogWebSocketHandler),  # use regex
    (r"/ws/microphone", MicrophoneWebSocketHandler),
    (r"/command", MqttWebHandler),
]


# sources: https://gist.github.com/wonderbeyond/d38cd85243befe863cdde54b84505784
#         https://gist.github.com/wonderbeyond/d38cd85243befe863cdde54b84505784#gistcomment-3204938
def sig_handler(server, sig, frame):
    io_loop = tornado.ioloop.IOLoop.instance()

    def stop_loop(server, deadline):
        now = time.time()

        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task() and not t.done()]
        if now < deadline and len(tasks) > 0:
            logger.info(f"Awaiting {len(tasks)} pending tasks: {tasks}")
            io_loop.add_timeout(now + 1, stop_loop, server, deadline)
            return

        pending_connection = len(server._connections)
        if now < deadline and pending_connection > 0:
            logger.info(f"Waiting on {pending_connection} connections to complete.")
            io_loop.add_timeout(now + 1, stop_loop, server, deadline)
        else:
            logger.info(f"Continuing with {pending_connection} connections open.")
            logger.info("Stopping IOLoop")
            io_loop.stop()
            logger.info("Shutdown complete.")

    def shutdown():
        max_wait_seconds_before_shutdown = 3

        logger.info(f"Will shutdown in {max_wait_seconds_before_shutdown} seconds ...")
        try:
            stop_loop(server, time.time() + max_wait_seconds_before_shutdown)
        except BaseException as e:
            logger.info(f"Error trying to shutdown Tornado: {str(e)}")

    logger.warning(f"Caught signal: {sig}")
    io_loop.add_callback_from_signal(shutdown)


def run_server():
    tornado.log.enable_pretty_logging()

    port = os.getenv("ROBOT_SERVER_PORT", 8765)
    logger.info(f"Starting Robot's mind server at port {port}...")

    app = tornado.web.Application(routes)

    server = tornado.httpserver.HTTPServer(app)
    server.listen(port)

    signal.signal(signal.SIGTERM, partial(sig_handler, server))
    signal.signal(signal.SIGINT, partial(sig_handler, server))

    tornado.ioloop.IOLoop.instance().start()

    logger.info("Exit...")


if __name__ == "__main__":
    run_server()
