# -*- coding: utf-8 -*-
from wtforms_tornado import Form
from wtforms import fields
from wtforms import validators


class AddUrlForm(Form):
    href = (fields.StringField(u'Адрес',
            [validators.required(message=u'Обязательное поле'),
             validators.URL(message=u'Неверный формат адреса')]))


class EditUrlForm(AddUrlForm):
    ready = fields.BooleanField(u'Обработан')
    show = fields.BooleanField(u'Показывать на основной странице')


class LoginForm(Form):
    username = (fields.StringField(u'Имя пользователя',
                [validators.required(message=u'Обязательное поле')]))
