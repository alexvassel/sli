# -*- coding: utf-8 -*-
import tornado.httpserver
import tornado.ioloop
import tornado.web

from handlers import main

APP_SETTINGS = {'template_path': 'templates', 'debug': True,
                'cookie_secret': 'some_secret', 'autoescape': None}

application = tornado.web.Application([
                (r'/', main.Index),
                (r'/initiate_requests/', main.InitiateRequests),
                (r'/check_responses/', main.CheckResponses),
                (r'/login', main.Login),
                (r'/admin/', main.AdminIndex),
                (r'/admin/url/(\d+)/', main.AdminUrlDetails),
                (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static'})
    ], **APP_SETTINGS)

http_server = tornado.httpserver.HTTPServer(application)
http_server.listen(3333)
tornado.ioloop.IOLoop.current().start()
