# Copyright (c) 2016, Isotoma Limited
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Isotoma Limited nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL ISOTOMA LIMITED BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import absolute_import, unicode_literals

import json

from django.conf import settings
from django.forms import widgets
from django.utils import translation
from wagtail.utils.widgets import WidgetWithScript


from wagtail.admin.panels import FieldPanel
from wagtail.rich_text import features

from .rich_text_utils import CustomEditorHTMLConverter


class TinyMCERichTextArea(WidgetWithScript, widgets.Textarea):

    @classmethod
    def getDefaultArgs(cls):
        return {
            'buttons': [
                [
                    ['undo', 'redo', 'nonbreaking'],
                    ['bold', 'italic', 'underline', 'strikethrough', 'formatselect'],
                    ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'p'],
                    ['alignleft', 'aligncenter', 'alignright'],
                    ['bullist', 'numlist', 'formats', 'blockformats'],
                    ['wagtaillink', 'link'],
                    ['wagtailimage', 'wagtailembed', 'wagtailvideo'],
                    ['codeeditor', 'wordcount', 'code'],
                ]
            ],
            'menus': False,
            'options': {
                'browser_spellcheck': True,
                'noneditable_leave_contenteditable': True,
                'language': translation.to_locale(
                    translation.get_language() or settings.LANGUAGE_CODE),
                'language_load': True,
            },
        }

    def __init__(self, attrs=None, **kwargs):
        super(TinyMCERichTextArea, self).__init__(attrs)
        self.kwargs = self.getDefaultArgs()
        self.features = kwargs.pop('features', None)
        if kwargs is not None:
            self.kwargs.update(kwargs)

        if self.features is None:
            self.features = features.get_default_features()
            self.converter = CustomEditorHTMLConverter()

    def get_panel(self):
        return FieldPanel

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            translated_value = None
        else:
            translated_value = self.converter.from_database_format(value)
        return super(TinyMCERichTextArea, self).render(name, translated_value, attrs, renderer)

    def render_js_init(self, id_, name, value):
        kwargs = {
            'options': self.kwargs.get('options', {}),
        }

        if 'buttons' in self.kwargs:
            if self.kwargs['buttons'] is False:
                kwargs['toolbar'] = False
            else:
                kwargs['toolbar'] = [
                    ' | '.join([' '.join(groups) for groups in rows])
                    for rows in self.kwargs['buttons']
                ]

        if 'menus' in self.kwargs:
            if self.kwargs['menus'] is False:
                kwargs['menubar'] = False
            else:
                kwargs['menubar'] = ' '.join(self.kwargs['menus'])

        if 'passthru_init_keys' in self.kwargs:
            kwargs.update(self.kwargs['passthru_init_keys'])

        if 'table' in self.kwargs:
            for key, values in self.kwargs['table'].items():
                kwargs[f'table_{key}'] = values

        return "makeTinyMCEEditable({0}, {1});".format(json.dumps(id_), json.dumps(kwargs))

    def value_from_datadict(self, data, files, name):
        original_value = super(TinyMCERichTextArea, self).value_from_datadict(data, files, name)
        if original_value is None:
            return None
        return self.converter.to_database_format(original_value)
