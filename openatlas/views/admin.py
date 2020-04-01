import datetime
import os
from os.path import basename, splitext
from typing import Optional, Union

from flask import flash, g, render_template, request, session, url_for
from flask_babel import lazy_gettext as _
from flask_login import current_user
from werkzeug.utils import redirect
from werkzeug.wrappers import Response

from openatlas import app, logger
from openatlas.forms.admin_forms import (ApiForm, GeneralForm, LogForm, LogoForm, MailForm, MapForm,
                                         NewsLetterForm, SimilarForm, TestMailForm, FileForm)
from openatlas.forms.forms import get_form_settings, set_form_settings
from openatlas.models.date import Date
from openatlas.models.entity import Entity
from openatlas.models.link import Link
from openatlas.models.node import Node
from openatlas.models.settings import Settings
from openatlas.models.user import User
from openatlas.util.table import Table
from openatlas.util.util import (convert_size, format_date, format_datetime, get_file_path,
                                 is_authorized, link, required_group, send_mail, uc_first)


@app.route('/admin')
@required_group('readonly')
def admin_index() -> str:
    export_path = app.config['EXPORT_FOLDER_PATH']
    writeable_dirs = {
        'uploads': True if os.access(app.config['UPLOAD_FOLDER_PATH'], os.W_OK) else False,
        'export/sql': True if os.access(export_path.joinpath('sql'), os.W_OK) else False,
        'export/csv': True if os.access(export_path.joinpath('csv'), os.W_OK) else False}
    return render_template('admin/index.html', writeable_dirs=writeable_dirs)


@app.route('/admin/map', methods=['POST', 'GET'])
@required_group('manager')
def admin_map() -> Union[str, Response]:
    form = MapForm(obj=session['settings'])
    if form.validate_on_submit():
        g.cursor.execute('BEGIN')
        try:
            Settings.update(form)
            logger.log('info', 'settings', 'Settings updated')
            g.cursor.execute('COMMIT')
            flash(_('info update'), 'info')
        except Exception as e:  # pragma: no cover
            g.cursor.execute('ROLLBACK')
            logger.log('error', 'database', 'transaction failed', e)
            flash(_('error transaction'), 'error')
        return redirect(url_for('admin_index'))
    set_form_settings(form)
    return render_template('admin/map.html', form=form)


@app.route('/admin/api', methods=['POST', 'GET'])
@required_group('manager')
def admin_api() -> Union[str, Response]:
    form = ApiForm(obj=session['settings'])
    if form.validate_on_submit():
        g.cursor.execute('BEGIN')
        try:
            Settings.update(form)
            logger.log('info', 'settings', 'API updated')
            g.cursor.execute('COMMIT')
            flash(_('info update'), 'info')
        except Exception as e:  # pragma: no cover
            g.cursor.execute('ROLLBACK')
            logger.log('error', 'database', 'transaction failed', e)
            flash(_('error transaction'), 'error')
        return redirect(url_for('admin_index'))
    set_form_settings(form)
    return render_template('admin/api.html', form=form)


@app.route('/admin/check_links')
@app.route('/admin/check_links/<check>')
@required_group('contributor')
def admin_check_links(check: Optional[str] = None) -> str:
    table = None
    if check:
        table = Table(['domain', 'property', 'range'])
        for result in Link.check_links():  # pragma: no cover
            table.rows.append([result['domain'], result['property'], result['range']])
    return render_template('admin/check_links.html', table=table, check=check)


@app.route('/admin/check_link_duplicates')
@app.route('/admin/check_link_duplicates/<delete>')
@required_group('contributor')
def admin_check_link_duplicates(delete: Optional[str] = None) -> Union[str, Response]:
    if delete:
        delete_count = str(Link.delete_link_duplicates())
        logger.log('info', 'admin', 'Deleted duplicate links: ' + delete_count)
        flash(_('deleted links') + ': ' + delete_count, 'info')
        return redirect(url_for('admin_check_link_duplicates'))
    table = Table(['domain', 'range', 'property_code', 'description', 'type_id', 'begin_from',
                   'begin_to', 'begin_comment', 'end_from', 'end_to', 'end_comment', 'count'])
    for result in Link.check_link_duplicates():
        table.rows.append([link(Entity.get_by_id(result.domain_id)),
                           link(Entity.get_by_id(result.range_id)),
                           link(g.properties[result.property_code]),
                           result.description,
                           link(g.nodes[result.type_id]) if result.type_id else '',
                           format_date(result.begin_from),
                           format_date(result.begin_to),
                           result.begin_comment,
                           format_date(result.end_from),
                           format_date(result.end_to),
                           result.end_comment,
                           result.count])
    duplicates = False
    if table.rows:
        duplicates = True
    else:  # If no exact duplicates where found check if single types are used multiple times
        table = Table(['entity', 'class', 'base type', 'incorrect multiple types'],
                      rows=Link.check_single_type_duplicates())
    return render_template('admin/check_link_duplicates.html', table=table, duplicates=duplicates)


@app.route('/admin/delete_single_type_duplicate/<int:entity_id>/<int:node_id>')
@required_group('contributor')
def admin_delete_single_type_duplicate(entity_id: int, node_id: int) -> Response:
    Node.remove_by_entity_and_node(entity_id, node_id)
    flash(_('link removed'), 'info')
    return redirect(url_for('admin_check_link_duplicates'))


@app.route('/admin/file', methods=['POST', 'GET'])
@required_group('manager')
def admin_file() -> Union[str, Response]:
    form = FileForm()
    if form.validate_on_submit():
        g.cursor.execute('BEGIN')
        try:
            Settings.update(form)
            logger.log('info', 'settings', 'Settings updated')
            g.cursor.execute('COMMIT')
            flash(_('info update'), 'info')
        except Exception as e:  # pragma: no cover
            g.cursor.execute('ROLLBACK')
            logger.log('error', 'database', 'transaction failed', e)
            flash(_('error transaction'), 'error')
        return redirect(url_for('admin_index'))
    set_form_settings(form)
    return render_template('admin/file.html', form=form)


@app.route('/admin/similar', methods=['POST', 'GET'])
@required_group('contributor')
def admin_check_similar() -> str:
    form = SimilarForm()
    choices = ['source', 'event', 'actor', 'place', 'feature', 'stratigraphic unit', 'find',
               'reference', 'file']
    form.classes.choices = [(x, uc_first(_(x))) for x in choices]
    table = None
    if form.validate_on_submit():
        table = Table(['name', uc_first(_('count'))])
        for sample_id, sample in Entity.get_similar_named(form).items():
            html = link(sample['entity'])
            for entity in sample['entities']:
                html += '<br><br><br><br><br>' + link(entity)  # Workaround for linebreaks in tables
            table.rows.append([html, len(sample['entities']) + 1])
    return render_template('admin/check_similar.html', table=table, form=form)


@app.route('/admin/orphans/delete/<parameter>')
@required_group('admin')
def admin_orphans_delete(parameter: str) -> Response:
    count = Entity.delete_orphans(parameter)
    flash(_('info orphans deleted:') + ' ' + str(count), 'info')
    return redirect(url_for('admin_orphans'))


@app.route('/admin/check/dates')
@required_group('contributor')
def admin_check_dates() -> str:
    # Get invalid date combinations (e.g. begin after end)
    tables = {'link_dates': Table(['link', 'domain', 'range']),
              'involvement_dates': Table(['actor', 'event', 'class', 'involvement', 'description']),
              'dates': Table(['name', 'class', 'type', 'system type', 'created', 'updated',
                              'description'])}
    for entity in Date.get_invalid_dates():
        tables['dates'].rows.append([link(entity),
                                     link(entity.class_),
                                     entity.print_base_type(),
                                     entity.system_type,
                                     format_date(entity.created),
                                     format_date(entity.modified),
                                     entity.description])
    for link_ in Date.get_invalid_link_dates():
        label = ''
        if link_.property.code == 'OA7':  # pragma: no cover
            label = 'relation'
        elif link_.property.code == 'P107':  # pragma: no cover
            label = 'member'
        elif link_.property.code in ['P11', 'P14', 'P22', 'P23']:
            label = 'involvement'
        url = url_for(label + '_update', id_=link_.id, origin_id=link_.domain.id)
        tables['link_dates'].rows.append(['<a href="' + url + '">' + uc_first(_(label)) + '</a>',
                                          link(link_.domain), link(link_.range)])
    for link_ in Date.invalid_involvement_dates():
        event = link_.domain
        actor = link_.range
        update_url = url_for('involvement_update', id_=link_.id, origin_id=actor.id)
        data = ([link(actor),
                 link(event),
                 g.classes[event.class_.code].name,
                 link_.type.name if link_.type else '',
                 link_.description,
                 '<a href="' + update_url + '">' + uc_first(_('edit')) + '</a>'])
        tables['involvement_dates'].rows.append(data)
    return render_template('admin/check_dates.html', tables=tables)


@app.route('/admin/orphans')
@required_group('contributor')
def admin_orphans() -> str:
    header = ['name', 'class', 'type', 'system type', 'created', 'updated', 'description']
    tables = {'orphans': Table(header),
              'unlinked': Table(header),
              'missing_files': Table(header),
              'circular': Table(['entity']),
              'nodes': Table(['name', 'root']),
              'orphaned_files': Table(['name', 'size', 'date', 'ext'])}
    tables['circular'].rows = [[link(entity)] for entity in Entity.get_circular()]
    for entity in Entity.get_orphans():
        name = 'unlinked' if entity.class_.code in app.config['CODE_CLASS'].keys() else 'orphans'
        tables[name].rows.append([link(entity),
                                  link(entity.class_),
                                  entity.print_base_type(),
                                  entity.system_type,
                                  format_date(entity.created),
                                  format_date(entity.modified),
                                  entity.description])
    for node in Node.get_node_orphans():
        tables['nodes'].rows.append([link(node), link(g.nodes[node.root[-1]])])

    # Get orphaned file entities (no corresponding file)
    file_ids = []
    for entity in Entity.get_by_system_type('file', nodes=True):
        file_ids.append(str(entity.id))
        if not get_file_path(entity):
            tables['missing_files'].rows.append([link(entity),
                                                 link(entity.class_),
                                                 entity.print_base_type(),
                                                 entity.system_type,
                                                 format_date(entity.created),
                                                 format_date(entity.modified),
                                                 entity.description])

    # Get orphaned files (no corresponding entity)
    with os.scandir(app.config['UPLOAD_FOLDER_PATH']) as it:
        for file in it:
            name = file.name
            if name != '.gitignore' and splitext(file.name)[0] not in file_ids:
                confirm = ' onclick="return confirm(\'' + _('Delete %(name)s?', name=name) + '\')"'
                tables['orphaned_files'].rows.append([
                    name,
                    convert_size(file.stat().st_size),
                    format_date(datetime.datetime.utcfromtimestamp(file.stat().st_ctime)),
                    splitext(name)[1],
                    '<a href="' + url_for('download_file', filename=name) + '">' + uc_first(
                        _('download')) + '</a>',
                    '<a href="' + url_for('admin_file_delete', filename=name) + '" ' +
                    confirm + '>' + uc_first(_('delete')) + '</a>'])
        return render_template('admin/orphans.html', tables=tables)


@app.route('/admin/logo/', methods=['POST', 'GET'])
@app.route('/admin/logo/<action>')
@required_group('manager')
def admin_logo(action: Optional[str] = None) -> Union[str, Response]:
    if action == 'remove':
        Settings.set_logo()
        return redirect(url_for('admin_logo'))
    if session['settings']['logo_file_id']:
        path = get_file_path(int(session['settings']['logo_file_id']))
        return render_template('admin/logo.html',
                               filename=os.path.basename(path) if path else False)
    form = LogoForm()
    if form.validate_on_submit():
        Settings.set_logo(form.file.data)
        return redirect(url_for('admin_logo'))
    return render_template('admin/logo.html', form=form)


@app.route('/admin/file/delete/<filename>')
@required_group('contributor')
def admin_file_delete(filename: str) -> Response:  # pragma: no cover
    if filename != 'all':
        try:
            os.remove(app.config['UPLOAD_FOLDER_PATH'].joinpath(filename))
            flash(filename + ' ' + _('was deleted'), 'info')
        except Exception as e:
            logger.log('error', 'file', 'deletion of ' + filename + ' failed', e)
            flash(_('error file delete'), 'error')
        return redirect(url_for('admin_orphans') + '#tab-orphaned-files')

    if is_authorized('admin'):
        # Get all files with entities
        file_ids = [str(entity.id) for entity in Entity.get_by_system_type('file')]

        # Get orphaned files (no corresponding entity)
        path = app.config['UPLOAD_FOLDER_PATH']
        for file in [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]:
            filename = basename(file)
            if filename != '.gitignore' and splitext(filename)[0] not in file_ids:
                try:
                    os.remove(app.config['UPLOAD_FOLDER_PATH'].joinpath(filename))
                except Exception as e:
                    logger.log('error', 'file', 'deletion of ' + filename + ' failed', e)
                    flash(_('error file delete'), 'error')
    return redirect(url_for('admin_orphans') + '#tab-orphaned-files')


@app.route('/admin/log', methods=['POST', 'GET'])
@required_group('admin')
def admin_log() -> str:
    form = LogForm()
    form.user.choices = [(0, _('all'))] + User.get_users()
    table = Table(['date', 'priority', 'type', 'message', 'user', 'info'], order=[[0, 'desc']])
    logs = logger.get_system_logs(form.limit.data, form.priority.data, form.user.data)
    for row in logs:
        user = None
        if row.user_id:
            try:
                user = link(User.get_by_id(row.user_id))
            except AttributeError:  # pragma: no cover - user already deleted
                user = 'id ' + str(row.user_id)
        table.rows.append([format_datetime(row.created),
                           str(row.priority) + ' ' + app.config['LOG_LEVELS'][row.priority],
                           row.type,
                           row.message,
                           user,
                           row.info])
    return render_template('admin/log.html', table=table, form=form)


@app.route('/admin/log/delete')
@required_group('admin')
def admin_log_delete() -> Response:
    logger.delete_all_system_logs()
    flash(_('Logs deleted'), 'info')
    return redirect(url_for('admin_log'))


@app.route('/admin/newsletter', methods=['POST', 'GET'])
@required_group('manager')
def admin_newsletter() -> Union[str, Response]:
    form = NewsLetterForm()
    if form.validate_on_submit():  # pragma: no cover
        recipients = 0
        for user_id in (request.form.getlist('recipient')):
            user = User.get_by_id(user_id)
            if user and user.settings['newsletter'] and user.active and user.email:
                code = User.generate_password()
                user.unsubscribe_code = code
                user.update()
                link_ = request.scheme + '://' + request.headers['Host']
                link_ += url_for('index_unsubscribe', code=code)
                unsubscribe = '\n\n' + _('To unsubscribe use the link below.') + '\n\n' + link_
                if send_mail(form.subject.data, form.body.data + unsubscribe, user.email):
                    recipients += 1
        flash(_('Newsletter send') + ': ' + str(recipients), 'info')
        return redirect(url_for('admin_index'))
    table = Table(['username', 'email', 'receiver'])
    for user in User.get_all():
        if user and user.settings['newsletter'] and user.active:  # pragma: no cover
            checkbox = '<input value="' + str(user.id) + '" name="recipient"'
            checkbox += ' type="checkbox" checked="checked">'
            table.rows.append([user.username, user.email, checkbox])
    return render_template('admin/newsletter.html', form=form, table=table)


@app.route('/admin/mail', methods=["GET", "POST"])
@required_group('admin')
def admin_mail() -> str:
    form = TestMailForm()
    settings = session['settings']
    if form.validate_on_submit() and session['settings']['mail']:  # pragma: no cover
        subject = _('Test mail from %(site_name)s', site_name=session['settings']['site_name'])
        body = _('This test mail was sent by %(username)s', username=current_user.username)
        body += ' ' + _('at') + ' ' + request.headers['Host']
        if send_mail(subject, body, form.receiver.data):
            flash(_('A test mail was sent to %(email)s.', email=form.receiver.data), 'info')
    else:
        form.receiver.data = current_user.email
    return render_template('admin/mail.html',
                           settings=settings,
                           mail_settings=get_form_settings(MailForm()),
                           form=form)


@app.route('/admin/general', methods=["GET", "POST"])
@required_group('admin')
def admin_general() -> str:
    return render_template('admin/general.html', general_settings=get_form_settings(GeneralForm()))


@app.route('/admin/general/update', methods=["GET", "POST"])
@required_group('admin')
def admin_general_update() -> Union[str, Response]:
    form = GeneralForm()
    if form.validate_on_submit():
        g.cursor.execute('BEGIN')
        try:
            Settings.update(form)
            logger.log('info', 'settings', 'Settings updated')
            g.cursor.execute('COMMIT')
            flash(_('info update'), 'info')
        except Exception as e:  # pragma: no cover
            g.cursor.execute('ROLLBACK')
            logger.log('error', 'database', 'transaction failed', e)
            flash(_('error transaction'), 'error')
        return redirect(url_for('admin_general'))
    set_form_settings(form)
    return render_template('admin/general_update.html', form=form, settings=session['settings'])


@app.route('/admin/mail/update', methods=["GET", "POST"])
@required_group('admin')
def admin_mail_update() -> Union[str, Response]:
    form = MailForm()
    if form.validate_on_submit():
        g.cursor.execute('BEGIN')
        try:
            Settings.update(form)
            logger.log('info', 'settings', 'Settings updated')
            g.cursor.execute('COMMIT')
            flash(_('info update'), 'info')
        except Exception as e:  # pragma: no cover
            g.cursor.execute('ROLLBACK')
            logger.log('error', 'database', 'transaction failed', e)
            flash(_('error transaction'), 'error')
        return redirect(url_for('admin_mail'))
    set_form_settings(form)
    return render_template('admin/mail_update.html', form=form, settings=session['settings'])
