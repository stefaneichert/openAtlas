# Copyright 2017 by Alexander Watzinger and others. Please see README.md for licensing information
import ast

from flask import flash, render_template, url_for, request
from flask_babel import lazy_gettext as _
from werkzeug.utils import redirect
from wtforms import HiddenField, SubmitField, TextAreaField, SelectField
from wtforms.validators import InputRequired

import openatlas
from openatlas import app, NodeMapper
from openatlas.forms import DateForm, TableMultiField, build_form
from openatlas.models.date import DateMapper
from openatlas.models.entity import EntityMapper
from openatlas.models.link import LinkMapper
from openatlas.util.util import required_group


class ActorForm(DateForm):
    actor = TableMultiField(_('actor'), validators=[InputRequired()])
    event = TableMultiField(_('event'), validators=[InputRequired()])
    activity = SelectField(_('activity'))
    description = TextAreaField(_('description'))
    save = SubmitField(_('insert'))
    insert_and_continue = SubmitField(_('insert and continue'))
    continue_ = HiddenField()


@app.route('/involvement/insert/<int:origin_id>', methods=['POST', 'GET'])
@required_group('editor')
def involvement_insert(origin_id):
    origin = EntityMapper.get_by_id(origin_id)
    origin_class = openatlas.app.config['CODE_CLASS'][origin.class_.code]
    form = build_form(ActorForm, 'Involvement')
    if origin_class == 'event':
        del form.event
    if origin_class == 'actor':
        del form.actor
    form.activity.choices = [('P11', openatlas.properties['P11'].name)]
    if origin.class_.code in ['E7', 'E8', 'E12']:
        form.activity.choices.append(('P14', openatlas.properties['P14'].name))
    if origin.class_.code == 'E8':
        form.activity.choices.append(('P22', openatlas.properties['P22'].name))
        form.activity.choices.append(('P23', openatlas.properties['P23'].name))
    if form.validate_on_submit():
        openatlas.get_cursor().execute('BEGIN')
        if origin_class == 'event':
            for actor_id in ast.literal_eval(form.actor.data):
                link_id = origin.link(form.activity.data, actor_id, form.description.data)
                DateMapper.save_link_dates(link_id, form)
                NodeMapper.save_link_nodes(link_id, form)
        else:
            for event_id in ast.literal_eval(form.event.data):
                link_id = LinkMapper.insert(
                    event_id,
                    form.activity.data,
                    origin.id,
                    form.description.data)
                DateMapper.save_link_dates(link_id, form)
                NodeMapper.save_link_nodes(link_id, form)
        openatlas.get_cursor().execute('COMMIT')
        flash(_('entity created'), 'info')
        if form.continue_.data == 'yes':
            return redirect(url_for('involvement_insert', origin_id=origin_id))
        tab = 'actor' if origin_class == 'event' else 'event'
        return redirect(url_for(origin_class + '_view', id_=origin.id) + '#tab-' + tab)
    return render_template('involvement/insert.html', origin=origin, form=form)


@app.route('/involvement/update/<int:id_>/<int:origin_id>', methods=['POST', 'GET'])
@required_group('editor')
def involvement_update(id_, origin_id):
    link_ = LinkMapper.get_by_id(id_)
    event = EntityMapper.get_by_id(link_.domain.id)
    actor = EntityMapper.get_by_id(link_.range.id)
    origin = event if origin_id == event.id else actor
    form = build_form(ActorForm, 'Involvement', link_, request)
    form.save.label.text = _('save')
    del form.actor, form.event, form.insert_and_continue
    form.activity.choices = [('P11', openatlas.properties['P11'].name)]
    if event.class_.code in ['E7', 'E8', 'E12']:
        form.activity.choices.append(('P14', openatlas.properties['P14'].name))
    if event.class_.code == 'E8':
        form.activity.choices.append(('P22', openatlas.properties['P22'].name))
        form.activity.choices.append(('P23', openatlas.properties['P23'].name))
    if form.validate_on_submit():
        openatlas.get_cursor().execute('BEGIN')
        link_.delete()
        link_id = event.link(form.activity.data, actor, form.description.data)
        DateMapper.save_link_dates(link_id, form)
        NodeMapper.save_link_nodes(link_id, form)
        openatlas.get_cursor().execute('COMMIT')
        class_ = openatlas.app.config['CODE_CLASS'][origin.class_.code]
        tab = 'actor' if class_ == 'event' else 'event'
        return redirect(url_for(class_ + '_view', id_=origin.id) + '#tab-' + tab)
    form.activity.data = link_.property.code
    form.description.data = link_.description
    link_.set_dates()
    form.populate_dates(link_)
    return render_template(
        'involvement/update.html',
        origin=origin,
        form=form,
        linked_object=event if origin_id != event.id else actor)
