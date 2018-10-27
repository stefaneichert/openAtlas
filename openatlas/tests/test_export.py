from flask import url_for

from openatlas import app
from openatlas.models.date import DateMapper
from openatlas.test_base import TestBaseCase


class ExportTest(TestBaseCase):

    def test_export(self):
        date_string = DateMapper.current_date_for_filename()
        with app.app_context():
            self.login()

            # SQL export
            rv = self.app.get(url_for('admin_export_sql'))
            assert b'Export SQL' in rv.data
            rv = self.app.post(url_for('admin_export_sql'), follow_redirects=True)
            assert b'Data was exported as SQL' in rv.data
            self.app.get(url_for('download_sql', filename=date_string + '_dump.sql'))
            rv = self.app.get(url_for('delete_sql', filename=date_string + '_dump.sql'),
                              follow_redirects=True)
            assert b'File deleted' in rv.data

            # CSV export
            rv = self.app.get(url_for('admin_export_csv'))
            assert b'Export CSV' in rv.data
            rv = self.app.post(url_for('admin_export_csv'), follow_redirects=True,
                               data={'zip': True, 'model_class': True,
                                     'gis_point': True, 'gis': 'wkt'})
            assert b'Data was exported as CSV' in rv.data
            rv = self.app.post(url_for('admin_export_csv'), follow_redirects=True,
                               data={'model_class': True, 'timestamps': True,
                                     'gis_polygon': True, 'gis': 'postgis'})
            assert b'Data was exported as CSV' in rv.data
            self.app.get(url_for('download_csv', filename=date_string + '_csv.zip'))
            rv = self.app.get(url_for('delete_csv', filename=date_string + '_csv.zip'),
                              follow_redirects=True)
            assert b'File deleted' in rv.data
