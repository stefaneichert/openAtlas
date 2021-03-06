# Created by Alexander Watzinger and others. Please see README.md for licensing information
import locale
import os
import sys
import time
from collections import OrderedDict

import psycopg2.extras
from flask import Flask, g, request, session
from flask_babel import Babel, lazy_gettext as _
from flask_wtf import Form
from flask_wtf.csrf import CsrfProtect
from wtforms import StringField, SubmitField

try:
    import mod_wsgi
except ImportError:
    mod_wsgi = None

app = Flask(__name__, instance_relative_config=True)
csrf = CsrfProtect(app)  # Make sure all forms are CSRF protected

# Use the test database if running tests
instance_name = 'production' if 'test_runner.py' not in sys.argv[0] else 'testing'
app.config.from_object('config.default')  # Load config/INSTANCE_NAME.py
app.config.from_pyfile(instance_name + '.py')  # Load instance/INSTANCE_NAME.py

if os.name == "posix":  # For other operating systems e.g. Windows, we would need adaptions here
    locale.setlocale(locale.LC_ALL, 'en_US.utf-8')  # pragma: no cover

babel = Babel(app)
debug_model = OrderedDict()  # type: OrderedDict


class GlobalSearchForm(Form):
    term = StringField('', render_kw={"placeholder": _('search term')})
    search = SubmitField(_('search'))


from openatlas.models.logger import DBHandler

logger = DBHandler()

from openatlas.util import filters
from openatlas.views import (actor, admin, ajax, content, event, export, hierarchy, index,
                             involvement, imports, link, login, types, model, place, profile,
                             reference, source, translation, user, relation, member, search, file)


@babel.localeselector
def get_locale():
    if 'language' in session:
        return session['language']
    best_match = request.accept_languages.best_match(app.config['LANGUAGES'].keys())
    # Check if best_match is set (in tests it isn't)
    return best_match if best_match else session['settings']['default_language']


def connect():
    try:
        connection_ = psycopg2.connect(database=app.config['DATABASE_NAME'],
                                       user=app.config['DATABASE_USER'],
                                       password=app.config['DATABASE_PASS'],
                                       port=app.config['DATABASE_PORT'],
                                       host=app.config['DATABASE_HOST'])
        connection_.autocommit = True
        return connection_
    except Exception as e:  # pragma: no cover
        print("Database connection error.")
        raise Exception(e)


@app.before_request
def before_request():
    debug_model['div sql'] = 0
    from openatlas.models.classObject import ClassMapper
    from openatlas.models.node import NodeMapper
    from openatlas.models.property import PropertyMapper
    from openatlas.models.settings import SettingsMapper
    if request.path.startswith('/static'):  # pragma: no cover
        return  # Only needed if not running with apache and static alias
    debug_model['current'] = time.time()
    g.db = connect()
    g.cursor = g.db.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    g.classes = ClassMapper.get_all()
    g.properties = PropertyMapper.get_all()
    g.nodes = NodeMapper.get_all_nodes()
    session['settings'] = SettingsMapper.get_settings()
    session['language'] = get_locale()
    # Set max file upload in MB
    app.config['MAX_CONTENT_LENGTH'] = session['settings']['file_upload_max_size'] * 1024 * 1024
    debug_model['by codes'] = 0
    debug_model['by id'] = 0
    debug_model['link sql'] = 0
    debug_model['user'] = 0
    debug_model['model'] = time.time() - debug_model['current']
    debug_model['current'] = time.time()

    # Workaround overlay maps for Thanados until #978 is implemented
    session['settings']['overlay_hack'] = False
    if session['settings']['site_name'] == 'Thanados':
        session['settings']['overlay_hack'] = True  # pragma: no cover


@app.after_request
def apply_caching(response):
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'

    # Todo: activate Content-Security-Policy after removal of every inline CSS and JavaScript
    # response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()


@app.context_processor
def inject_search_form():
    return dict(search_form=GlobalSearchForm(prefix="global"))


app.register_blueprint(filters.blueprint)
app.add_template_global(debug_model, 'debug_model')


@app.context_processor
def inject_debug():
    return dict(debug=app.debug)


if __name__ == "__main__":  # pragma: no cover
    app.run()
