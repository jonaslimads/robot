"""

Shutdown server upon signal.

Sources:

https://gist.github.com/wonderbeyond/d38cd85243befe863cdde54b84505784
https://gist.github.com/wonderbeyond/d38cd85243befe863cdde54b84505784#gistcomment-3204938

"""

import time
import signal
import asyncio

import tornado.ioloop

from mind import get_logger

logger = get_logger(__name__)


def signal_handler(server, sig, frame):
    io_loop = tornado.ioloop.IOLoop.instance()

    def stop_loop(server, deadline):
        now = time.time()

        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task() and not t.done()]
        if now < deadline and len(tasks) > 0:
            logger.debug(f"Awaiting {len(tasks)} pending tasks: {tasks}")
            io_loop.add_timeout(now + 1, stop_loop, server, deadline)
            return

        pending_connection = len(server._connections)
        if now < deadline and pending_connection > 0:
            logger.debug(f"Waiting on {pending_connection} connections to complete.")
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
