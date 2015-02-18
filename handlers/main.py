# -*- coding: utf-8 -*-
import httplib
import functools
from bs4 import BeautifulSoup

from tornado.escape import json_encode
from tornado.httpclient import AsyncHTTPClient
import tornado.web

from helpers import execute, SQLITE_URLS_TABLE, BaseHandler

import forms


class Index(tornado.web.RequestHandler):
    """
    Вывод урлов на index.html
    """

    def get(self):
        urls = execute('SELECT * FROM {} WHERE show="True"'.format(SQLITE_URLS_TABLE))
        self.render('index.html', urls=urls)


class InitiateRequests(tornado.web.RequestHandler):
    """
    Получение id адресов из шаблона и инициализация запросов на получение
    тайтлов с последующим сохранением заголовков в БД
    """
    URL_ERROR = u'Ошибка получения заголовка'

    @tornado.web.asynchronous
    def get(self):
        """
        создание по каждому id асинхронного запроса на получение тела страницы
        """
        ids = self.get_argument('urlIds', '')
        urls = execute('SELECT * FROM {} WHERE id IN ({})'.format(SQLITE_URLS_TABLE, ids))

        for url in urls:
            # Если тайтл по адресу уже был получен, то еще раз мы его не спрашиваем, отдаем из БД
            if url['ready'] == 'False':
                http_client = AsyncHTTPClient()
                # В callback необходимо передать id урла
                http_client.fetch(url['href'], callback=functools.partial(self._handle_url_response,
                                                                          url['id']))

        self.write(json_encode({'status': httplib.OK}))
        self.finish()

    def _handle_url_response(self, url_id, response):
        """
        Получение тела страницы, выделение title, сохранение его в
        БД и возврат этих значений
        """
        try:
            response = BeautifulSoup(response.body).title.text
        except (AttributeError, TypeError):
            response = self.URL_ERROR

        # Вставка в БД полученного title
        (execute('UPDATE {} SET "response"="{}", "ready"="{}" WHERE id={}'
                 .format(SQLITE_URLS_TABLE, response.encode('utf-8'), True, url_id)))


class CheckResponses(tornado.web.RequestHandler):
    """
    Проверить получен ли ответ по id урла
    """
    def get(self):
        ids = self.get_argument('urlIds', '')
        urls = (execute('SELECT * FROM {} WHERE id IN ({}) AND ready="True"'
                        .format(SQLITE_URLS_TABLE, ids)))

        response = {url['id']: url['response'] for url in urls}

        self.write(json_encode(response))


class Login(tornado.web.RequestHandler):
    """
        Авторизация намеренно упрощена
    """
    def get(self):
        form = forms.LoginForm()
        self.render('admin/login.html', form=form)

    def post(self):
        self.set_secure_cookie('user', self.get_argument('username'))
        self.redirect('/admin/')


class AdminIndex(BaseHandler):
    def get(self):
        if not self.current_user:
            self.redirect('/login')
            return
        urls = execute('SELECT * FROM {}'.format(SQLITE_URLS_TABLE))
        self.render('admin/index.html', form=forms.AddUrlForm(), urls=urls)

    def post(self):
        form = forms.AddUrlForm(self.request.arguments)

        if form.validate():
            execute('INSERT INTO {} (href) VALUES ("{}")'.format(SQLITE_URLS_TABLE,
                                                                 form.href.data))
            self.redirect('/admin/')
        else:
            urls = execute('SELECT * FROM {}'.format(SQLITE_URLS_TABLE))
            self.render('admin/index.html', form=form, urls=urls)


class AdminUrlDetails(BaseHandler):
    """
    Редактирование конкретного адреса
    """
    url = None

    def get(self, url_id):
        url = (execute('SELECT * FROM {} WHERE id="{}"'.format(SQLITE_URLS_TABLE, url_id)))[0]
        form = forms.EditUrlForm(href=url['href'], ready=True if url['ready'] == 'True' else False,
                                 show=True if url['show'] == 'True' else False)
        self.render('admin/edit_url.html', form=form, url=url)

    def post(self, url_id):
        form = forms.EditUrlForm(self.request.arguments)
        url = (execute('SELECT * FROM {} WHERE id="{}"'.format(SQLITE_URLS_TABLE, url_id)))[0]

        if form.validate():
            (execute('UPDATE {} SET "href"="{}", "ready"="{}", "show"="{}" WHERE id={}'
                     .format(SQLITE_URLS_TABLE, form.href.data, form.ready.data, form.show.data,
                             url_id)))
            self.redirect('/admin/')
        else:
            self.render('admin/edit_url.html'.format(url_id), form=form, url=url)
