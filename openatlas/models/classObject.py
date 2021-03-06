# Created by Alexander Watzinger and others. Please see README.md for licensing information
from flask import g, session

import openatlas
from openatlas import app, debug_model


class ClassObject:

    def __init__(self, row):
        self._comment = ''
        self._name = row.name
        self.code = row.code
        self.id = row.id
        self.i18n = {}
        self.sub = []
        self.super = []

    @property
    def name(self):
        return self.get_i18n('name')

    @property
    def comment(self):
        return self.get_i18n('comment')

    def get_i18n(self, attribute):
        locale_session = openatlas.get_locale()
        locale_default = session['settings']['default_language']
        if locale_session in self.i18n and attribute in self.i18n[locale_session]:
            return self.i18n[locale_session][attribute]
        elif locale_default in self.i18n and attribute in self.i18n[locale_default]:
            return self.i18n[locale_default][attribute]
        return getattr(self, '_' + attribute)  # pragma: no cover


class ClassMapper:

    @staticmethod
    def get_all():
        g.cursor.execute("SELECT id, code, name FROM model.class;")
        debug_model['div sql'] += 1
        classes = {row.code: ClassObject(row) for row in g.cursor.fetchall()}
        g.cursor.execute("SELECT super_code, sub_code FROM model.class_inheritance;")
        debug_model['div sql'] += 1
        for row in g.cursor.fetchall():
            classes[row.super_code].sub.append(row.sub_code)
            classes[row.sub_code].super.append(row.super_code)
        sql = """
            SELECT class_code, language_code, attribute, text FROM model.class_i18n
            WHERE language_code IN %(language_codes)s;"""
        g.cursor.execute(sql, {'language_codes': tuple(app.config['LANGUAGES'].keys())})
        debug_model['div sql'] += 1
        for row in g.cursor.fetchall():
            class_ = classes[row.class_code]
            if row.language_code not in class_.i18n:
                class_.i18n[row.language_code] = {}
            class_.i18n[row.language_code][row.attribute] = row.text
        return classes
