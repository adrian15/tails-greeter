#!/usr/bin/python
#
# Copyright 2011 Max <govnototalitarizm@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>
#
"""
Greeter program for GDM using gtk (nothing else works)
"""

import logging

from gtkme.listview import text_combobox
from GdmGreeter.language import TranslatableWindow, LANGS, ln_cc

class LangselectWindow(TranslatableWindow):
    """Display language selection window"""
    name = 'langselect'
    primary = False
    language_name = None

    def __init__(self, *args, **kwargs):
        TranslatableWindow.__init__(self, *args, **kwargs)
        text_combobox(self.widget('lang_list_combobox'), self.widget('languages'))
        self.populate()
        self.widget('lang_list_combobox').set_active(0)

    def populate(self):
        """Create all the required entries"""
        for l in LANGS:
            self.widget('languages').append([l])

    def translate_to(self, lang):
        """Press the selected language's button"""
        lang = self.language(lang)
        TranslatableWindow.translate_to(self, lang)
        logging.debug('translating to %s', lang)

    def translate_action(self, widget):
        """Signal event to translate entire app"""
        self.language_name = self.widget('lang_list_combobox').get_active_text()
        self.gapp.SelectLanguage(ln_cc(self.language_name))

    def next_button_clicked(self, widget):
        """Signal event to translate entire app"""
        self.translate_action(widget)
        self.gapp.SwitchVisibility()

    def skip_button_clicked(self, widget):
        """Initiate immediate login"""
        self.gapp.ForcedLogin()