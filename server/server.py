#! /usr/bin/python
# -*- coding:utf-8 -*-

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
from tornado.options import define, options
import json
import os

define("port", default=8661, help="run on the given port", type=int)

# the path to server html, js, css files
client_file_root_path = os.path.join(os.path.split(__file__)[0], '../client')
client_file_root_path = os.path.abspath(client_file_root_path)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/(.*)', tornado.web.StaticFileHandler, {'path': client_file_root_path, 'default_filename': 'index.html'})
            # fetch client files
        ]

        settings = {
            'static_path': 'static',
            'debug': True
        }

        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == '__main__':
    tornado.options.parse_command_line()
    print('server running at 127.0.0.1:%d ...' % (tornado.options.options.port))

    app = Application()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
