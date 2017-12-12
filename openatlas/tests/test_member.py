# Copyright 2017 by Alexander Watzinger and others. Please see README.md for licensing information
from flask import url_for
from openatlas import app, EntityMapper
from openatlas.models.link import LinkMapper
from openatlas.test_base import TestBaseCase


class MemberTests(TestBaseCase):

    def test_member(self):
        self.login()
        with app.app_context():
            actor_id = EntityMapper.insert('E21', 'Ripley').id
            group_id = EntityMapper.insert('E74', 'Space Marines').id

            # add membership
            rv = self.app.get(url_for('member_insert', origin_id=group_id))
            assert b'Actor Function' in rv.data
            rv = self.app.post(
                url_for('membership_insert', origin_id=actor_id),
                data={'group': '[' + str(group_id) + ']'},
                follow_redirects=True)
            assert b'Space Marines' in rv.data
            rv = self.app.post(
                url_for('membership_insert', origin_id=actor_id),
                data={'group': '[' + str(group_id) + ']', 'continue_': 'yes'},
                follow_redirects=True)
            assert b'Space Marines' in rv.data

            # add member to group
            rv = self.app.post(
                url_for('member_insert', origin_id=group_id),
                data={'actor': '[' + str(actor_id) + ']'},
                follow_redirects=True)
            assert b'Ripley' in rv.data
            rv = self.app.post(
                url_for('member_insert', origin_id=group_id),
                data={'actor': '[' + str(actor_id) + ']', 'continue_': 'yes'},
                follow_redirects=True)
            assert b'Ripley' in rv.data

            # update member
            link_id = LinkMapper.get_links(group_id, 'P107')[0].id
            rv = self.app.get(url_for('member_update', id_=link_id, origin_id=group_id))
            assert b'Ripley' in rv.data
            rv = self.app.post(
                url_for('member_update', id_=link_id, origin_id=group_id),
                data={'description': 'We are here to help you.'},
                follow_redirects=True)
            assert b'here to help' in rv.data