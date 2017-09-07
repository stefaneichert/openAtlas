# Copyright 2017 by Alexander Watzinger and others. Please see README.md for licensing information
from openatlas.test_base import TestBaseCase


class UserTests(TestBaseCase):

    def test_user(self):
        form_data = {
            'active': '',
            'username': 'Ripley',
            'email': 'ripley@nostromo.org',
            'password': 'you_never_guess_this',
            'password2': 'you_never_guess_this',
            'group': 'admin',
            'name': 'Ripley Weaver',
            'description': '',
            'send_info': ''
        }
        self.login()
        rv = self.app.get('/user/insert')
        assert b'+ User' in rv.data
        rv = self.app.post('/user/insert', data=form_data)
        user_id = rv.location.split('/')[-1]
        form_data['password2'] = 'same same, but different'
        rv = self.app.post('/user/insert', data=form_data)
        assert b'match' in rv.data
        rv = self.app.get('/user/view/' + user_id)
        assert b'Ripley' in rv.data
        rv = self.app.get('/user/update/' + user_id)
        assert b'ripley@nostromo.org' in rv.data
        form_data['description'] = 'The warrant officer'
        rv = self.app.post('/user/update/' + user_id, data=form_data, follow_redirects=True)
        assert b'The warrant officer' in rv.data
        rv = self.app.get('/user/delete/' + user_id, follow_redirects=True)
        assert b'A user was deleted' in rv.data