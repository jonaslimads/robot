import unittest

import tornado.ioloop
import tornado.web
from tornado.testing import main, AsyncHTTPTestCase

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


def make_app():
    app = tornado.web.Application(
        [
            (r"/", MainHandler),
        ]
    )
    return app


class TestHttpEndpoint(AsyncHTTPTestCase):
    def get_app(self):
        return make_app()

    def test_homepage(self):
        response = self.fetch("/")
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, b"Hello, world")


if __name__ == "__main__":
    unittest.main()
