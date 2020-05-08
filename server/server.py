# -*- coding:utf-8 -*-
import os
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
from tornado.options import define, options
import pandas as pd
import numpy as np
from collections import Counter

define("port", default=8661, help = "run on the given port", type = int)

# the path to server html, js, css files
client_file_root_path = os.path.join(os.path.split(__file__)[0], '../client')
# os.path.abspath返回绝对路径
client_file_root_path = os.path.abspath(client_file_root_path)

'''
Application对象是负责全局配置的, 包括映射请求转发给处理程序的路由表
'''
class Application(tornado.web.Application):
    def __init__ (self):
        handlers = [
            # tornado.web.StaticFileHandler是tornado用来提供静态资源文件的handler
            # path : 用来提供html文件的根路径   default_filename : 用来指定访问路由中未指明文件时, 默认提供的文件
            (r'/(.*)', tornado.web.StaticFileHandler, {'path': client_file_root_path, 'default_filename': 'index.html'}) # fetch client files
        ]

        settings = {
            'static_path': 'static',
            'debug': True
        }

        tornado.web.Application.__init__(self, handlers, **settings)

if __name__ == '__main__':
    # tornado.options模块——全局参数定义、存储、转换
    # 转换命令行参数，并将转换后的值对应的设置到全局options对象相关属性上
    tornado.options.parse_command_line()
    print('server running at 127.0.0.1:%d ...' % (tornado.options.options.port))

    app = Application()
    # 非阻塞，单线程 HTTP server 启动服务器
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    # 启动服务器之后，还需要启动 IOLoop 的实例，这样可以启动事件循环机制，配合非阻塞的 HTTP Server 工作
    tornado.ioloop.IOLoop.instance().start()

