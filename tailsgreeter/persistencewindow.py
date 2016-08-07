#!/usr/bin/python
#
# Copyright 2012-2013 Tails developers <tails@boum.org>
# Copyright 2011 Max <govnototalitarizm@gmail.com>
# Copyright 2011 Martin Owens
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
"""First screen

"""

from gi.repository import Gdk, Gtk
import logging, os
import tailsgreeter
import tailsgreeter.config
from tailsgreeter.language import TranslatableWindow
from tailsgreeter.helpwindow import HelpWindow

class PersistenceWindow(TranslatableWindow):
    """First greeter screen"""

    def __init__(self, greeter):
        self.greeter = greeter

        builder = Gtk.Builder()
        builder.set_translation_domain(tailsgreeter.__appname__)
        builder.add_from_file(os.path.join(tailsgreeter.GLADE_DIR, "persistencewindow.glade"))
        builder.connect_signals(self)

        self.moreoptions = False

        # Sets self.window
        self.login_dialog = builder.get_object("login_dialog")
        TranslatableWindow.__init__(self, self.login_dialog)
        self.btn_persistence_yes = builder.get_object("persistence_yes_button")
        self.btn_persistence_no = builder.get_object("persistence_no_button")
        self.passphrase_box = builder.get_object("passphrase_box")
        self.entry_passphrase = builder.get_object("passphrase_entry")
        self.btn_moreoptions_yes = builder.get_object("moreoptions_yes_button")
        self.btn_moreoptions_no = builder.get_object("moreoptions_no_button")
        self.btn_login = builder.get_object("login_button")
        self.btn_next = builder.get_object("next_button")
        self.box_persistence = builder.get_object("persistence_box")
        self.readonly_checkbutton = builder.get_object("readonly_checkbutton")
        self.warning_label = builder.get_object("warning_label")
        self.warning_area = builder.get_object("warning_area")
        self.warning_image = builder.get_object("warning_area")
        # self.spinner = builder.get_object("spinner")
        self.checked_img_moreoptions_yes = builder.get_object("moreoptions_yes_checked_img")
        self.checked_img_moreoptions_no  = builder.get_object("moreoptions_no_checked_img")
        self.checked_img_persistence_yes = builder.get_object("persistence_yes_checked_img")
        self.checked_img_persistence_no  = builder.get_object("persistence_no_checked_img")
        self.lbl_moreoptions = builder.get_object("moreoptions_label")
        self.lbl_main = builder.get_object("main_label")

        self.warning_area.hide()

        # FIXME: list_containers may raise exceptions. Deal with that.
        self.containers = []
        if tailsgreeter.config.tails_persistence_support:
                self.containers = [
                { "path": container, "locked": True }
                for container in self.greeter.persistence.list_containers()
                ]

        if len(self.containers) == 0:
            self.box_persistence.hide()

        if not tailsgreeter.config.tails_persistence_support:
                self.btn_moreoptions_yes.hide()
                self.btn_moreoptions_no.hide()
                self.checked_img_persistence_yes.hide()
                self.checked_img_moreoptions_no.hide()
                self.lbl_moreoptions.hide()
        if not tailsgreeter.config.tails_show_welcome_message:
                self.lbl_main.hide()

        # FIXME:
        # * support multiple persistent containers:
        #   - display brand, model, partition path and size for each container
        #   - create as many passphrase input fields as needed

    # Help callback handler
    cb_doc_handler = HelpWindow.cb_doc_handler

    def activate_persistence(self):
        """Ask the backend to activate persistence and handle errors

        Returns: True if everything went fine, False if the user should try again"""
        if self.btn_persistence_yes.get_active():
            try:
                self.greeter.persistence.activate(
                    device=self.containers[0]['path'],
                    password=self.entry_passphrase.get_text(),
                    readonly=self.readonly_checkbutton.get_active()
                    )
                return True
            except tailsgreeter.errors.WrongPassphraseError:
                self.entry_passphrase.set_text('')
                self.warning_area.show_all()
                return False
        else:
            return True

    def set_persistence_visibility(self, persistence):
        self.passphrase_box.set_visible(persistence)
        if not persistence:
            self.warning_area.hide()
        self.btn_persistence_yes.set_active(persistence)
        self.btn_persistence_no.set_active(not persistence)
        if persistence:
            self.checked_img_persistence_yes.show()
            self.checked_img_persistence_no.hide()
        else:
            self.checked_img_persistence_yes.hide()
            self.checked_img_persistence_no.show()
        if persistence:
            self.entry_passphrase.grab_focus()

    def cb_persistence_yes_toggled(self, widget, data=None):
        persistence = widget.get_active()
        self.set_persistence_visibility(persistence)

    def cb_persistence_no_toggled(self, widget, data=None):
        persistence = not widget.get_active()
        self.set_persistence_visibility(persistence)

    def update_login_button(self, moreoptions):
        if moreoptions:
            self.btn_login.hide()
            self.btn_next.show()
        else:
            self.btn_login.show()
            self.btn_next.hide()

    def update_moreoptions_buttons(self, moreoptions):
        self.btn_moreoptions_yes.set_active(moreoptions)
        self.btn_moreoptions_no.set_active(not moreoptions)
        if moreoptions:
            self.checked_img_moreoptions_yes.show()
            self.checked_img_moreoptions_no.hide()
        else:
            self.checked_img_moreoptions_yes.hide()
            self.checked_img_moreoptions_no.show()

    def cb_moreoptions_yes_toggled(self, widget, data=None):
        moreoptions = widget.get_active()
        self.moreoptions = moreoptions
        self.update_login_button(moreoptions)
        self.update_moreoptions_buttons(moreoptions)

    def cb_moreoptions_no_toggled(self, widget, data=None):
        moreoptions = not widget.get_active()
        self.moreoptions = moreoptions
        self.update_login_button(moreoptions)
        self.update_moreoptions_buttons(moreoptions)

    def toggle_watch_cursor(self, on=True):
        if on:
            self.window.get_window().set_cursor(Gdk.Cursor.new(Gdk.CursorType.WATCH))
        else:
            self.window.get_window().set_cursor(None)
        Gdk.flush()

    def working(self, working=True):
        # FIXME: set_sensitive more widgets?
        self.btn_login.set_sensitive(not working)
        self.toggle_watch_cursor(working)
        # if working:
        #     self.spinner.start()
        #     self.spinner.show()
        # else:
        #     self.spinner.stop()
        #     self.spinner.hide()

    def go(self):
        self.working(True)
        success = self.activate_persistence()
        self.working(False)
        if success:
            # next
            if self.moreoptions:
                self.window.hide()
                self.greeter.optionswindow.window.show()
            # login
            else:
                self.greeter.login()

    def cb_login_clicked(self, widget, data=None):
        self.go()

    def cb_next_clicked(self, widget, data=None):
        self.go()

    def key_press_event_cb(self, widget, event=None):
        """Handle key press"""
        if event:
            if event.keyval in [ Gdk.KEY_Return, Gdk.KEY_KP_Enter ]:
                if self.window.get_focus().__class__.__name__ == "Label":
                    # The only labels that we allow to be focused are
                    # the help links, for which Return will activate
                    # the link.
                    return
                else:
                    self.go()

    def delete_event_cb(self, widget, event=None):
        """Ignore delete event (Esc)"""
        return True
