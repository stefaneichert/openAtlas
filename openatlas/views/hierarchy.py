# Copyright 2017 by Alexander Watzinger and others. Please see README.md for licensing information
from flask import render_template, flash, url_for
from flask_babel import lazy_gettext as _
from flask_wtf import Form
from werkzeug.utils import redirect
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectMultipleField
from wtforms import widgets
from wtforms.validators import InputRequired

import openatlas
from openatlas import app, NodeMapper, EntityMapper
from openatlas.forms import build_form
from openatlas.util.util import required_group, sanitize, uc_first


class HierarchyForm(Form):
    name = StringField(_('name'), validators=[InputRequired()])
    multiple = BooleanField(_('multiple'),description=_('tooltip hierarchy multiple'))
    forms = SelectMultipleField(
        _('forms'),
        render_kw={'disabled': True},
        description=_('tooltip hierarchy forms'),
        choices=NodeMapper.get_form_choices(),
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False),
        coerce=int)
    description = TextAreaField(_('description'))
    save = SubmitField(_('insert'))


@app.route('/hierarchy/insert', methods=['POST', 'GET'])
@required_group('manager')
def hierarchy_insert():
    form = build_form(HierarchyForm, 'hierarchy')
    if form.validate_on_submit():
        node = save(form)
        flash(_('entity created'), 'info')
        return redirect(url_for('node_index') + '#tab-' + str(node.id))
    return render_template('hierarchy/insert.html', form=form)


@app.route('/hierarchy/update/<int:id_>', methods=['POST', 'GET'])
@required_group('manager')
def hierarchy_update(id_):
    node = openatlas.nodes[id_]
    if node.system:
        flash(_('error forbidden'), 'error')
        return redirect(url_for('node_view', id_=id_))
    form = build_form(HierarchyForm, 'hierarchy', node)
    if node.multiple:
        form.multiple.render_kw = {'disabled': 'disabled'}
    if form.validate_on_submit():
        flash(_('info update'), 'info')
        return redirect(url_for('node_index') + '#tab-' + str(node.id))
    form.multiple = node.multiple
    return render_template(
        'hierarchy/update.html',
        node=node,
        form=form,
        forms=[form.id for form in form.forms])


@app.route('/hierarchy/delete/<int:id_>', methods=['POST', 'GET'])
@required_group('manager')
def hierarchy_delete(id_):
    node = openatlas.nodes[id_]
    if node.system or node.subs or node.count:
        flash(_('error forbidden'), 'error')
        return redirect(url_for('node_view', id_=id_))
    openatlas.get_cursor().execute('BEGIN')
    EntityMapper.delete(node.id)
    openatlas.get_cursor().execute('COMMIT')
    flash(_('entity deleted'), 'info')
    return redirect(url_for('node_index'))


def save(form, node=None):
    openatlas.get_cursor().execute('BEGIN')
    if not node:
        node = NodeMapper.insert('E55', sanitize(form.name.data, 'node'))
        NodeMapper.insert_hierarchy(node, form)
    else:
        node = openatlas.nodes[node.id]
        NodeMapper.update_hierarchy(node, form)
    node.name = sanitize(form.name.data, 'node')
    node.description = form.description.data
    node.update()
    openatlas.get_cursor().execute('COMMIT')
    return node