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

from query_search import *
from tolerant_search import *
from utils import *

define("port", default=8661, help="run on the given port", type=int)

# the path to server html, js, css files
client_file_root_path = os.path.join(os.path.split(__file__)[0], '../client')
client_file_root_path = os.path.abspath(client_file_root_path)


# load index
index_path = os.path.join(os.path.split(__file__)[0], '../index')
index_path = os.path.abspath(index_path)

DICTIONARY_FILE = os.path.join(index_path, 'dictionary')
POSTINGS_FILE = os.path.join(index_path, 'postings')

# open files
dict_file = codecs.open(DICTIONARY_FILE, encoding='utf-8')
post_file = io.open(POSTINGS_FILE, 'rb')

# load dictionary to memory
(dictionary, indexed_docIDs) = load_dictionary(dict_file)
dict_file.close()


class Boolean_search(tornado.web.RequestHandler):
    def get(self):
        value = (json.loads(self.get_argument('value')))
        print(value)

        result = process_query(value, dictionary, post_file, indexed_docIDs)

        evt_unpacked = {'result': result}
        evt = json.dumps(evt_unpacked)
        self.write(evt)


class Tolerant_search(tornado.web.RequestHandler):
    def get(self):
        value = (json.loads(self.get_argument('value')))
        print(value)

        code, result = tolerant_search(value, dictionary, post_file)

        evt_unpacked = {"code": code, 'result': result}
        evt = json.dumps(evt_unpacked)
        self.write(evt)


class Query_search(tornado.web.RequestHandler):
    def get(self):
        value = (json.loads(self.get_argument('value')))
        print(value)

        result = query_search(value)

        evt_unpacked = {'result': result}
        evt = json.dumps(evt_unpacked)
        self.write(evt)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/Boolean_search', Boolean_search),
            (r'/Tolerant_search', Tolerant_search),
            (r'/Query_search', Query_search),
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
