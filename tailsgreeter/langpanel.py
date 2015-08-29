#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2012-2013 Tails developers <tails@boum.org>
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
"""Localization panel

"""

from gi.repository import Gdk, Gtk
import logging, gettext, os
_ = gettext.gettext
from tailsgreeter.language import TranslatableWindow
import tailsgreeter
import tailsgreeter.language as language

class LangDialog(TranslatableWindow):
    """Language selection dialog"""

    def __init__(self):
        builder = Gtk.Builder()
        builder.set_translation_domain(tailsgreeter.__appname__)
        builder.add_from_file(os.path.join(tailsgreeter.GLADE_DIR, "langdialog.glade"))
        self.dialog = builder.get_object("languages_dialog")
        self.treeview = builder.get_object("languages_treeview")
        self.liststore = builder.get_object("languages_liststore")
        builder.connect_signals(self)

        tvcolumn = Gtk.TreeViewColumn(_("Language"))
        self.treeview.append_column(tvcolumn)
        cell = Gtk.CellRendererText()
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', 1)

        TranslatableWindow.__init__(self, self.dialog)

    def cb_langdialog_key_press(self, widget, event, data=None):
        """Handle key press in langdialog"""
        if event.keyval in [ Gdk.KEY_Return, Gdk.KEY_KP_Enter ]:
            self.dialog.response(True)

    def cb_langdialog_button_press(self, widget, event, data=None):
        """Handle mouse click in langdialog"""
        if (event.type == Gdk.EventType._2BUTTON_PRESS or
                event.type == Gdk.EventType._3BUTTON_PRESS):
            self.dialog.response(True)

class LangPanel(TranslatableWindow):
    """Display language and layout selection panel"""

    def __init__(self, greeter):
        self.greeter = greeter

        # XXX: initialize instance variables
        self.additional_language_displayed = False
        self.additional_layout_displayed = False
        self.default_position = 0

        # Build UI
        builder = Gtk.Builder()
        builder.set_translation_domain(tailsgreeter.__appname__)
        builder.add_from_file(os.path.join(tailsgreeter.GLADE_DIR, "langpanel.glade"))
        builder.connect_signals(self)
        self.window = builder.get_object("langpanel")

        cell = Gtk.CellRendererText()

        self.cb_languages = builder.get_object("lang_list_cbox")
        self.cb_languages.pack_start(cell, True)
        self.cb_languages.add_attribute(cell, 'text', 1)

        self.cb_locales = builder.get_object("locale_cbox")
        self.cb_locales.pack_start(cell, True)
        self.cb_locales.add_attribute(cell, 'text', 1)

        self.cb_layouts = builder.get_object("layout_cbox")
        self.cb_layouts.pack_start(cell, True)
        self.cb_layouts.add_attribute(cell, 'text', 1)

        self.cb_variants = builder.get_object("variant_cbox")
        if self.cb_variants:
            self.cb_variants.pack_start(cell, True)
            self.cb_variants.add_attribute(cell, 'text', 1)

        TranslatableWindow.__init__(self, self.window)

        self.populate_languages()
        self.cb_languages.set_active(self.default_position)

        # Move/resize the panel whenever the screen size changes. This sometimes
        # happens with Spice without any user action, due to a race condition
        # between the initialization of the Greeter and the startup of
        # spice-vdagent; but it can also happen without any race condition,
        # if the user manually resizes the VM window.
        screen = self.window.get_screen()
        screen.connect("size-changed",     self.resize)
        # While we're at it, also react when monitors are added/removed.
        # E.g. the default one could change.
        screen.connect("monitors-changed", self.resize)

        self.set_panel_geometry()

    def resize(self, screen, data=None):
        self.set_panel_geometry()

    def set_panel_geometry(self):
        """Position panel to bottom and use full screen width"""
        panel = self.window
        panel.set_gravity(Gdk.Gravity.SOUTH_WEST)
        width, height = panel.get_size()
        # Let's not assume that this window is on Gdk.Screen.
        screen = self.window.get_screen()
        panel.set_default_size(screen.width(), height)
        panel.move(0, screen.height() - height)

    # Populate lists

    def populate_languages(self):
        """Create all the required entries"""
        count = 0
        for l in self.greeter.localisationsettings.get_default_languages_with_names():
            self.cb_languages.get_model().append(l)
            if l[0] == self.greeter.localisationsettings.get_language():
                self.default_position = count
            count += 1
        self.cb_languages.get_model().append(['+', _("Other...")])

    def populate_locales(self):
        """populate the lists for a given language"""
        self.cb_locales.get_model().clear()
        count = 0
        default_position = 0
        for l in self.greeter.localisationsettings.get_default_locales_with_names():
            self.cb_locales.get_model().append(l)
            if l[0] == self.greeter.localisationsettings.get_locale():
                default_position = count
            count += 1
        self.cb_locales.set_active(default_position)

    def populate_layouts(self):
        """populate the lists for current locale"""
        logging.debug("Entering populate_layouts")
        self.cb_layouts.get_model().clear()
        count = 0
        default_position = 0
        for l in self.greeter.localisationsettings.get_default_layouts_with_names():
            logging.debug("Considering layout %s", l[0])
            self.cb_layouts.get_model().append(l)
            if l[0] == self.greeter.localisationsettings.get_layout():
                logging.debug("Layout %s is the default one", l[0])
                default_position = count
            count += 1
        self.cb_layouts.get_model().append(['+', _("Other...")])
        self.cb_layouts.set_active(default_position)

    # Callbacks

    def key_event_cb(self, widget, event=None):
        """Handle key event - check for layout change"""
        if event:
            if (event.keyval == Gdk.KEY_ISO_Next_Group or
                event.keyval ==  Gdk.KEY_ISO_Prev_Group):
                pass

    def layout_selected(self, widget):
        """handler for combobox selecion event"""
        selected_layout = None
        i = self.cb_layouts.get_active_iter()
        if i and  self.cb_layouts.get_model().get(i, 0)[0] == '+':
            selected_layout = self.show_more_layouts()
        else:
            i = self.cb_layouts.get_active_iter()
            if i:
                selected_layout = self.cb_layouts.get_model().get(i, 0)[0]

        if selected_layout:
            self.greeter.localisationsettings.set_layout(selected_layout)
            i = self.cb_layouts.get_active_iter()
            if i and not selected_layout == self.cb_layouts.get_model().get(i, 0)[0]:
                self.update_other_layout_entry(selected_layout)

    # "Other..." layouts dialog handeling

    def update_other_layout_entry(self, layout=None):
        if not layout:
            layout = _("Other...")
        last_entry = self.cb_layouts.get_model().iter_n_children(None) - 1
        if not self.additional_layout_displayed:
            self.cb_layouts.get_model().insert(
                last_entry,
                [layout, language.layout_name(layout)])
            self.cb_layouts.set_active(last_entry)
            self.additional_layout_displayed = True
        else:
            self.cb_layouts.get_model().set(
                self.cb_layouts.get_model().get_iter(last_entry - 1),
                0, layout,
                1, language.layout_name(layout))
            self.cb_layouts.set_active(last_entry - 1)

    def show_more_layouts(self):
        """Show a dialog to allow selecting more layouts"""

        dialog = LangDialog()

        count = 0
        for l in self.greeter.localisationsettings.get_layouts_with_names():
            dialog.liststore.append(l)
            # XXX
            if self.greeter.localisationsettings.get_layout() == l[0]:
                self.default_position = count
            count += 1

        layout = None
        if dialog.dialog.run():
            dummy, selected_iter = dialog.treeview.get_selection().get_selected()
            if selected_iter:
                layout = dialog.liststore[selected_iter][0]

        dialog.dialog.destroy()

        return layout

    def locale_selected(self, widget):
        """handler for locale combobox selection event"""
        i = self.cb_locales.get_active_iter()
        if i:
            l = self.cb_locales.get_model().get(i, 0)[0]
            if l:
                self.greeter.localisationsettings.set_locale(l)
                self.populate_layouts()

    def language_selected(self, widget):
        """handler for language combobox selection event"""

        selected_language = None
        i = self.cb_languages.get_active_iter()
        if i:
            if self.cb_languages.get_model().get(i, 0)[0] == '+':
                selected_language = self.show_more_languages()
            else:
                selected_language = self.cb_languages.get_model().get(i, 0)[0]

        if selected_language:
            self.greeter.localisationsettings.set_language(selected_language)
            self.populate_locales()
            i = self.cb_languages.get_active_iter()
            if i and not selected_language == self.cb_languages.get_model().get(i, 0)[0]:
                self.update_other_language_entry(selected_language)

    # "Other..." language dialog handeling

    def update_other_language_entry(self, lang):
        last_entry = self.cb_languages.get_model().iter_n_children(None) - 1
        if not self.additional_language_displayed:
            self.cb_languages.get_model().insert(
                last_entry,
                [lang, language.language_name(lang)])
            self.cb_languages.set_active(last_entry)
            self.additional_language_displayed = True
        else:
            self.cb_languages.get_model().set(
                self.cb_languages.get_model().get_iter(last_entry - 1),
                0, lang,
                1, language.language_name(lang))
            self.cb_languages.set_active(last_entry - 1)

    def show_more_languages(self):
        """Show a dialog to allow selecting more languages"""

        langdialog = LangDialog()

        count = 0
        for l in self.greeter.localisationsettings.get_languages_with_names():
            langdialog.liststore.append(l)
            # XXX
            if self.greeter.localisationsettings.get_language() == l[0]:
                self.default_position = count
            count += 1

        lang = None
        if langdialog.dialog.run():
            dummy, selected_iter = langdialog.treeview.get_selection().get_selected()
            if selected_iter:
                lang = langdialog.liststore[selected_iter][0]

        langdialog.dialog.destroy()

        return lang
