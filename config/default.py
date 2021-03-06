# Don't edit this file. To override settings please use instance/production.py
import os
from collections import OrderedDict

from flask_babel import lazy_gettext as _

VERSION = '3.17.0'
DEMO_MODE = False  # If in demo mode some options are disabled and the login form is pre filled

LANGUAGES = {'en': 'English', 'de': 'Deutsch'}
DEBUG = False

DATABASE_NAME = 'openatlas'
DATABASE_USER = 'openatlas'
DATABASE_HOST = 'localhost'
DATABASE_PORT = 5432
DATABASE_PASS = 'CHANGE ME'
MAIL_PASSWORD = 'CHANGE ME'
SECRET_KEY = 'CHANGE ME'

IMPORT_FOLDER_PATH = '/tmp'  # Needed for processing of import files, any temp folder will do
IMPORT_FILE_EXTENSIONS = ['csv', 'xls', 'xlsx']
EXPORT_FOLDER_PATH = os.path.dirname(__file__) + '/../openatlas/export'
UPLOAD_FOLDER_PATH = os.path.dirname(__file__) + '/../openatlas/uploads'
DISPLAY_FILE_EXTENSIONS = ['bmp', 'gif', 'ico', 'jpeg', 'jpg', 'png', 'svg']

# Security
SESSION_COOKIE_SECURE = False  # Should be set to True in production.py if using HTTPS only
REMEMBER_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'Lax'

# JavaScript credentials
GEONAMES_USERNAME = 'openatlas'
THUNDERFOREST_KEY = '7878b4fb224f4902ab42fc846e92b96a'

DEFAULT_TABLE_ROWS = OrderedDict()  # type: OrderedDict
DEFAULT_TABLE_ROWS[10] = '10'
DEFAULT_TABLE_ROWS[20] = '20'
DEFAULT_TABLE_ROWS[50] = '50'
DEFAULT_TABLE_ROWS[100] = '100'

MIN_CHARS_JSTREE_SEARCH = 1

LOG_LEVELS = OrderedDict()  # type: OrderedDict
LOG_LEVELS[0] = 'emergency'
LOG_LEVELS[1] = 'alert'
LOG_LEVELS[2] = 'critical'
LOG_LEVELS[3] = 'error'
LOG_LEVELS[4] = 'warn'
LOG_LEVELS[5] = 'notice'
LOG_LEVELS[6] = 'info'
LOG_LEVELS[7] = 'debug'

FEEDBACK_SUBJECTS = OrderedDict()  # type: OrderedDict
FEEDBACK_SUBJECTS[_('suggestion').title()] = _('suggestion').title()
FEEDBACK_SUBJECTS[_('question').title()] = _('question').title()
FEEDBACK_SUBJECTS[_('problem').title()] = _('problem').title()

CODE_CLASS = {
    'E33': 'source',
    'E6': 'event',
    'E7': 'event',
    'E8': 'event',
    'E12': 'event',
    'E21': 'actor',
    'E40': 'actor',
    'E74': 'actor',
    'E18': 'place',
    'E22': 'place',
    'E31': 'reference',
    'E84': 'reference'}

CLASS_CODES = {
    'source': ['E33'],
    'event': ['E7', 'E8', 'E12', 'E6'],
    'actor': ['E21', 'E74', 'E40'],
    'group': ['E40', 'E74'],
    'place': ['E18', 'E22'],
    'reference': ['E31', 'E84']}

PROPERTY_TYPES = ['Actor Actor Relation', 'Actor Function', 'Involvement']

BASE_TYPES = ['Place', 'Information Carrier', 'Bibliography', 'Source', 'Edition', 'Event', 'Actor',
              'Stratigraphic Unit', 'Feature', 'Find']
