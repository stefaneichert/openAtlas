# Copyright 2017 by Alexander Watzinger and others. Please see the file README.md for licensing information
import openatlas
from flask import flash, session, render_template, url_for
from flask_wtf import Form
from openatlas import app
from openatlas.models.content import ContentMapper
from openatlas.util import util
from werkzeug.utils import redirect
from wtforms import TextAreaField

from openatlas.util.util import required_group


class ContentForm(Form):
    pass


@app.route('/content')
@required_group('manager')
def content_index():
    header = ['name']
    for language in openatlas.app.config['LANGUAGES'].keys():
        header.append(language)
    header.append('text')
    table_content = {
        'name': 'content',
        'header': header,
        'hide_pager': True,
        'data': []}
    for item, languages in ContentMapper.get_content().items():
        content = ['<a href="/content/view/' + item + '">' + util.uc_first(item) + '</a>']
        html_ok = '<img src="/images/icons/dialog-apply.png" alt="ok" \>'
        for language in openatlas.app.config['LANGUAGES'].keys():
            content.append(html_ok if languages[language] else '')
        content.append(languages[session['language']])
        table_content['data'].append(content)
    return render_template('content/index.html', table_content=table_content)


@app.route('/content/view/<string:item>')
@required_group('manager')
def content_view(item):
    return render_template('content/view.html', item=item, content=ContentMapper.get_content())


@app.route('/content/update/<string:item>', methods=["GET", "POST"])
@required_group('manager')
def content_update(item):
    languages = openatlas.app.config['LANGUAGES'].keys()
    for language in languages:
        setattr(ContentForm, language, TextAreaField())
    form = ContentForm()
    if form.validate_on_submit():
        ContentMapper.update_content(item, form)
        flash('info update', 'info')
        return redirect(url_for('content_view', item=item))
    content = ContentMapper.get_content()
    for language in languages:
        form.__getattribute__(language).data = content[item][language]
    return render_template('content/update.html', item=item, form=form, languages=languages)