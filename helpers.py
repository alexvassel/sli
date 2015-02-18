# -*- coding: utf-8 -*-
import sqlite3
import tornado.web

# Имя таблицы с адресами
SQLITE_URLS_TABLE = 'url'


class BaseHandler(tornado.web.RequestHandler):
    """
    Проверка авторизации
    """
    def get_current_user(self):
        return self.get_secure_cookie('user')


# Для более сложной БД стоит использовать ORM (sqlalchemy, например)
def execute(query):
    """Выполнение запроса к sqlite"""
    dbPath = 'sli.sqlite'
    connection = sqlite3.connect(dbPath)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    connection.commit()
    connection.close()
    return result
