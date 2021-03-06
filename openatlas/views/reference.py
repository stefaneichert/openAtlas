# Created by Alexander Watzinger and others. Please see README.md for licensing information
from flask import flash, g, render_template, request, url_for
from flask_babel import lazy_gettext as _
from flask_wtf import Form
from werkzeug.utils import redirect
from wtforms import HiddenField, StringField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, URL

import openatlas
from openatlas import app, logger
from openatlas.forms.forms import TableField, build_form
from openatlas.models.entity import EntityMapper
from openatlas.models.link import LinkMapper
from openatlas.util.table import Table
from openatlas.util.util import (display_remove_link, get_base_table_data, get_entity_data,
                                 is_authorized, link, required_group, truncate_string, uc_first,
                                 was_modified, get_profile_image_table_link)


class ReferenceForm(Form):
    name = StringField(_('name'), render_kw={'autofocus': True})
    description = TextAreaField(_('description'))
    save = SubmitField(_('insert'))
    insert_and_continue = SubmitField(_('insert and continue'))
    continue_ = HiddenField()
    opened = HiddenField()


class AddReferenceForm(Form):
    reference = TableField(_('reference'), [InputRequired()])
    page = StringField(_('page'))
    save = SubmitField(_('insert'))


class AddSourceForm(Form):
    source = TableField(_('source'), [InputRequired()])
    page = StringField(_('page'))
    save = SubmitField(_('insert'))


class AddEventForm(Form):
    event = TableField(_('event'), [InputRequired()])
    page = StringField(_('page'))
    save = SubmitField(_('insert'))


class AddActorForm(Form):
    actor = TableField(_('actor'), [InputRequired()])
    page = StringField(_('page'))
    save = SubmitField(_('insert'))


class AddPlaceForm(Form):
    place = TableField(_('place'), [InputRequired()])
    page = StringField(_('page'))
    save = SubmitField(_('insert'))


class AddFileForm(Form):
    file = TableField(_('file'), [InputRequired()])
    page = StringField(_('page'))
    save = SubmitField(_('insert'))


@app.route('/reference/add/<int:origin_id>', methods=['POST', 'GET'])
@required_group('editor')
def reference_add(origin_id):
    """ Link an entity to reference coming from the entity."""
    origin = EntityMapper.get_by_id(origin_id)
    form = AddReferenceForm()
    if form.validate_on_submit():
        EntityMapper.get_by_id(form.reference.data).link('P67', origin, form.page.data)
        return redirect(url_for(origin.view_name + '_view', id_=origin.id) + '#tab-reference')
    form.page.label.text = uc_first(_('page / link text'))
    return render_template('reference/add.html', origin=origin, form=form)


@app.route('/reference/add2/<int:reference_id>/<class_name>', methods=['POST', 'GET'])
@required_group('editor')
def reference_add2(reference_id, class_name):
    """ Link an entity to reference coming from the reference."""
    reference = EntityMapper.get_by_id(reference_id)
    form = getattr(openatlas.views.reference, 'Add' + uc_first(class_name) + 'Form')()
    if form.validate_on_submit():
        property_code = 'P128' if reference.class_.code == 'E84' else 'P67'
        entity = EntityMapper.get_by_id(getattr(form, class_name).data)
        reference.link(property_code, entity, form.page.data)
        return redirect(url_for('reference_view', id_=reference.id) + '#tab-' + class_name)
    if reference.system_type == 'external reference':
        form.page.label.text = uc_first(_('link text'))
    return render_template('reference/add2.html', reference=reference, form=form,
                           class_name=class_name)


@app.route('/reference/link-update/<int:link_id>/<int:origin_id>', methods=['POST', 'GET'])
@required_group('editor')
def reference_link_update(link_id, origin_id):
    link_ = LinkMapper.get_by_id(link_id)
    origin = EntityMapper.get_by_id(origin_id)
    form = AddReferenceForm()
    del form.reference
    if form.validate_on_submit():
        link_.description = form.page.data
        link_.update()
        flash(_('info update'), 'info')
        tab = '#tab-reference'
        if origin.view_name == 'reference':
            tab = '#tab-' + link_.range.view_name
        return redirect(url_for(origin.view_name + '_view', id_=origin.id) + tab)
    form.save.label.text = _('save')
    form.page.data = link_.description
    if link_.domain.system_type == 'external reference':
        form.page.label.text = uc_first(_('link text'))
    linked_object = link_.domain if link_.domain.id != origin.id else link_.range
    return render_template('reference/link-update.html', origin=origin, form=form,
                           linked_object=linked_object)


@app.route('/reference/view/<int:id_>')
@required_group('readonly')
def reference_view(id_):
    reference = EntityMapper.get_by_id(id_, nodes=True)
    tables = {'info': get_entity_data(reference),
              'file': Table(Table.HEADERS['file'] + ['page', _('main image')])}
    for name in ['source', 'event', 'actor', 'place', 'feature', 'stratigraphic-unit', 'find']:
        header_label = 'link text' if reference.system_type == 'external reference' else 'page'
        tables[name] = Table(Table.HEADERS[name] + [header_label])
    for link_ in reference.get_links('P67', True):
        domain = link_.domain
        data = get_base_table_data(domain)
        if is_authorized('editor'):
            url = url_for('link_delete', id_=link_.id, origin_id=reference.id) + '#tab-file'
            data.append(display_remove_link(url, domain.name))
        tables['file'].rows.append(data)
    profile_image_id = reference.get_profile_image_id()
    for link_ in reference.get_links(['P67', 'P128']):
        range_ = link_.range
        data = get_base_table_data(range_)
        data.append(truncate_string(link_.description))
        if range_.view_name == 'file':  # pragma: no cover
            ext = data[3].replace('.', '')
            data.append(get_profile_image_table_link(range_, reference, ext, profile_image_id))
            if not profile_image_id and ext in app.config['DISPLAY_FILE_EXTENSIONS']:
                profile_image_id = range_.id
        if is_authorized('editor'):
            url = url_for('reference_link_update', link_id=link_.id, origin_id=reference.id)
            data.append('<a href="' + url + '">' + uc_first(_('edit')) + '</a>')
            url = url_for('link_delete', id_=link_.id, origin_id=reference.id)
            data.append(display_remove_link(url + '#tab-' + range_.table_name, range_.name))
        tables[range_.table_name].rows.append(data)
    return render_template('reference/view.html', reference=reference, tables=tables,
                           profile_image_id=profile_image_id)


@app.route('/reference')
@required_group('readonly')
def reference_index():
    table = Table(Table.HEADERS['reference'] + ['description'])
    for reference in EntityMapper.get_by_codes('reference'):
        data = get_base_table_data(reference)
        data.append(truncate_string(reference.description))
        table.rows.append(data)
    return render_template('reference/index.html', table=table)


@app.route('/reference/insert/<code>', methods=['POST', 'GET'])
@app.route('/reference/insert/<code>/<int:origin_id>', methods=['POST', 'GET'])
@required_group('editor')
def reference_insert(code, origin_id=None):
    origin = EntityMapper.get_by_id(origin_id) if origin_id else None
    type_name = code
    if code == 'carrier':
        type_name = 'Information Carrier'
    elif code == 'external_reference':
        type_name = 'External Reference'
    form = build_form(ReferenceForm, type_name)
    if code == 'external_reference':
        form.name.validators = [InputRequired(), URL()]
        form.name.label.text = 'URL'
    else:
        form.name.validators = [InputRequired()]
    if origin:
        del form.insert_and_continue
    if form.validate_on_submit():
        return redirect(save(form, code=code, origin=origin))
    return render_template('reference/insert.html', form=form, code=code, origin=origin)


@app.route('/reference/delete/<int:id_>')
@required_group('editor')
def reference_delete(id_):
    EntityMapper.delete(id_)
    logger.log_user(id_, 'delete')
    flash(_('entity deleted'), 'info')
    return redirect(url_for('reference_index'))


@app.route('/reference/update/<int:id_>', methods=['POST', 'GET'])
@required_group('editor')
def reference_update(id_):
    reference = EntityMapper.get_by_id(id_, nodes=True)
    form = build_form(ReferenceForm, reference.system_type.title(), reference, request)
    if reference.system_type == 'external reference':
        form.name.validators = [InputRequired(), URL()]
        form.name.label.text = 'URL'
    else:  # pragma: no cover
        form.name.validators = [InputRequired()]
    if form.validate_on_submit():
        if was_modified(form, reference):  # pragma: no cover
            del form.save
            flash(_('error modified'), 'error')
            modifier = link(logger.get_log_for_advanced_view(reference.id)['modifier'])
            return render_template(
                'reference/update.html', form=form, reference=reference, modifier=modifier)
        save(form, reference)
        return redirect(url_for('reference_view', id_=id_))
    return render_template('reference/update.html', form=form, reference=reference)


def save(form, reference=None, code=None, origin=None):
    g.cursor.execute('BEGIN')
    log_action = 'update'
    try:
        if not reference:
            log_action = 'insert'
            class_code = 'E84' if code == 'carrier' else 'E31'
            system_type = 'information carrier' if code == 'carrier' else code.replace('_', ' ')
            reference = EntityMapper.insert(class_code, form.name.data, system_type)
        reference.name = form.name.data
        reference.description = form.description.data
        reference.update()
        reference.save_nodes(form)
        url = url_for('reference_view', id_=reference.id)
        if origin:
            link_id = reference.link('P67', origin)
            url = url_for('reference_link_update', link_id=link_id, origin_id=origin.id)
        if form.continue_.data == 'yes' and code:
            url = url_for('reference_insert', code=code)
        g.cursor.execute('COMMIT')
        logger.log_user(reference.id, log_action)
        flash(_('entity created') if log_action == 'insert' else _('info update'), 'info')
    except Exception as e:  # pragma: no cover
        g.cursor.execute('ROLLBACK')
        logger.log('error', 'database', 'transaction failed', e)
        flash(_('error transaction'), 'error')
        url = url_for('reference_index')
    return url
