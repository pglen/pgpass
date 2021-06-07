#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function

import os, sys, getopt, signal, random, time, warnings, string

import  lesspass
import qrcode
from PIL import Image, ImageFilter, ImageOps

from pymenu import  *

sys.path.append('../pycommon')

from pgutil import  *
from pgui import  *

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import GdkPixbuf
from gi.repository import Pango

# ------------------------------------------------------------------------

class MainWin(Gtk.Window):

    def __init__(self):

        Gtk.Window.__init__(self, Gtk.WindowType.TOPLEVEL)

        #self = Gtk.Window(Gtk.WindowType.TOPLEVEL)

        #Gtk.register_stock_icons()

        self.set_title("pypass")
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

        #ic = Gtk.Image(); ic.set_from_stock(Gtk.STOCK_DIALOG_INFO, Gtk.ICON_SIZE_BUTTON)
        #window.set_icon(ic.get_pixbuf())

        www = Gdk.Screen.width(); hhh = Gdk.Screen.height();

        disp2 = Gdk.Display()
        disp = disp2.get_default()
        #print( disp)
        scr = disp.get_default_screen()
        ptr = disp.get_pointer()
        mon = scr.get_monitor_at_point(ptr[1], ptr[2])
        geo = scr.get_monitor_geometry(mon)
        www = geo.width; hhh = geo.height
        xxx = geo.x;     yyy = geo.y

        # Resort to old means of getting screen w / h
        if www == 0 or hhh == 0:
            www = Gdk.screen_width(); hhh = Gdk.screen_height();

        if www / hhh > 2:
            self.set_default_size(5*www/8, 7*hhh/8)
        else:
            self.set_default_size(7*www/8, 7*hhh/8)

        self.connect("destroy", self.OnExit)
        self.connect("key-press-event", self.key_press_event)
        self.connect("button-press-event", self.button_press_event)

        try:
            self.set_icon_from_file("icon.png")
        except:
            pass

        vbox = Gtk.VBox(); hbox4 = Gtk.HBox(); hbox5 = Gtk.HBox()

        merge = Gtk.UIManager()
        #self.mywin.set_data("ui-manager", merge)

        aa = create_action_group(self)
        merge.insert_action_group(aa, 0)
        self.add_accel_group(merge.get_accel_group())

        merge_id = merge.new_merge_id()

        try:
            mergeid = merge.add_ui_from_string(ui_info)
        except GLib.GError as msg:
            print("Building menus failed: %s" % msg)

        self.mbar = merge.get_widget("/MenuBar")
        self.mbar.show()

        self.tbar = merge.get_widget("/ToolBar");
        self.tbar.show()

        bbox = Gtk.VBox()
        bbox.pack_start(self.mbar, 0,0, 0)
        bbox.pack_start(self.tbar, 0,0, 0)
        vbox.pack_start(bbox, False, 0, 0)

        hbox4.pack_start(Gtk.Label("  "), 0, 0, 4)
        hbox4.pack_start(Gtk.Label("Master Pass:"), 0, 0, 4)
        self.input = Gtk.Entry()
        self.input.set_visibility(False)

        hbox4.pack_start(self.input, 0, 0, 4)

        buttA = Gtk.Button.new_with_mnemonic(" _Apply ")
        buttA.connect("clicked", self.master_new)
        hbox4.pack_start(buttA, False, 0, 2)

        lab1 = Gtk.Label("");  hbox4.pack_start(lab1, 1, 1, 0)

        butt1 = Gtk.Button.new_with_mnemonic(" _New ")
        #butt1.connect("clicked", self.show_new, window)
        hbox4.pack_start(butt1, False, 0, 2)

        butt2 = Gtk.Button.new_with_mnemonic(" E_xit ")
        butt2.connect("clicked", self.OnExit, self)
        hbox4.pack_start(butt2, False, 0, 0)

        lab2 = Gtk.Label("  ");  hbox4.pack_start(lab2, 0, 0, 0)

        #hbox2 = Gtk.HBox()
        #lab3 = Gtk.Label("aa");  hbox2.pack_start(lab3, 0, 0, 0)
        #lab4 = Gtk.Label("");  hbox2.pack_start(lab4, 0, 0, 0)
        #vbox.pack_start(hbox2, False, 0, 0)

        hbox3 = Gtk.HBox()
        #self.edit = SimpleEdit();
        #self.edit = Gtk.Label(" L1 ")

        qq = qrcode.make()
        xx =  ImageOps.grayscale(qq)
        qqq = xx.convert("RGB")
        dd = self.image2pixbuf(qqq)

        self.edit = Gtk.Image()
        self.apply_qr("12345678")

        ttt = type("")
        self.model = Gtk.TreeStore(type(""), type(""), type(""), type(""), type(""), type(""))
        self.tree = Gtk.TreeView(self.model)
        self.tree.connect("cursor-changed", self.row_activate)

        col = Gtk.TreeViewColumn("Site", self.cellx(0), text=0)
        self.tree.append_column(col)

        col = Gtk.TreeViewColumn("Login",  self.cellx(1), text=1)
        self.tree.append_column(col)

        col = Gtk.TreeViewColumn("Serial",  self.cellx(2), text=2)
        self.tree.append_column(col)

        col = Gtk.TreeViewColumn("Pass",  self.cellx(3), text=3)
        self.tree.append_column(col)

        col = Gtk.TreeViewColumn("Len",   self.cellx(4), text=4)
        self.tree.append_column(col)

        col = Gtk.TreeViewColumn("Notes",  self.cellx(5), text=5)
        self.tree.append_column(col)

        self.hpane = Gtk.HPaned()

        self.fill_samples()

        self.scroll = Gtk.ScrolledWindow()
        self.scroll.add_with_viewport(self.tree)

        self.hpane.add(self.scroll)
        self.hpane.add(self.edit)

        #for row in self.model:
        #    print(row[:])

        #print ("size", self.get_default_size())

        self.hpane.set_position(self.get_default_size()[0] / 3)
        hbox3.pack_start(self.hpane, True, True, 6)

        vbox.pack_start(hbox5, False, False, 2)
        vbox.pack_start(hbox3, True, True, 2)
        vbox.pack_start(hbox4, False, 0, 6)

        self.add(vbox)
        self.show_all()

    def row_activate(self, arg1):
        sel = self.tree.get_selection()
        tree, curr = sel.get_selected()
        #print("row_activate",  curr)
        ppp = self.model.get_path(curr)
        row = self.model[ppp]
        self.apply_qr(row[3])

    def apply_qr(self, strx):
        #print ("new QR", strx)
        qq =  qrcode.make(strx, version=1)
        xx =  ImageOps.grayscale(qq)
        qqq = xx.convert("RGB")
        dd = self.image2pixbuf(qqq)
        self.edit.set_from_pixbuf(dd)

    def image2pixbuf(self, im):
        """Convert Pillow image to GdkPixbuf"""
        #print("mode", im.mode)
        data = im.tobytes()
        w, h = im.size
        data = GLib.Bytes.new(data)
        pix = GdkPixbuf.Pixbuf.new_from_bytes(data, GdkPixbuf.Colorspace.RGB,
                False, 8, w, h, w*3 )
        return pix

    def cellx(self, idx):
        cell = Gtk.CellRendererText()
        cell.set_property("editable", True)
        cell.connect("edited", self.text_edited, idx)
        return cell

    def text_edited(self, widget, path, text, idx):
        #print("path", path)
        if  self.model[path][idx] != text:
            #print("modified",  self.model[path][idx], text)
            if idx == 2:
                try:
                    self.model[path][idx] = str(int(text))
                except:
                    self.message("\nSerial field must be an integer")
            elif idx == 4:
                try:
                    self.model[path][idx] = str(int(text))
                except:
                    self.message("\nLength field must be an integer")

                if int(self.model[path][idx]) > 32:
                    self.model[path][idx] = "32"
                    self.message("\nLength field must be 32 or less")
            else:
                self.model[path][idx] = text
            self.apply_master()

    def  OnExit(self, arg, srg2 = None):
        self.exit_all()

    def exit_all(self):
        Gtk.main_quit()

    def fill_samples(self):

        serial = "0";  passx = " - " * 18
        xlen = "14"
        host = "google.com"; login = "username1"
        self.model.append(None, (host, login,  serial, passx, xlen, "Notes"))

        host = "google.com"; login = "username2"
        self.model.append(None, (host, login,  serial, passx, xlen, "Notes"))

        host = "google.com"; login = "username3"
        self.model.append(None, (host, login,  serial, passx, xlen, "Notes"))

        host = "google.com"; login = "peterglen"
        self.model.append(None, (host, login,  serial, passx, xlen, "Notes"))

    def apply_master(self):

        master = self.input.get_text()
        if not master:
            self.message("\nCannot use empty Master Pass")
            return

        serial = 0;  cno = 0
        for row in self.model:
            strx = lesspass.gen_pass(row[0] + row[1] + master + str(int(row[2])))
            self.model[cno]= (row[0], row[1], row[2], strx[:int(row[4])], row[4], "Notes ")
            cno += 1

        self.row_activate(None)

    def key_press_event(self, win, event):
        #print( "key_press_event", win, event)
        pass

    def button_press_event(self, win, event):
        #print( "button_press_event", win, event)
        pass

    def message(self, strx):
        ddd = Gtk.MessageDialog()
        ddd.set_markup(strx)
        ddd.add_button("OK", Gtk.ResponseType.OK)
        #ddd.add_button("Cancel", Gtk.ResponseType.CANCEL)
        ret = ddd.run()
        #print ("ret", ret)
        ddd.destroy()

    def master_new(self, action):
        #print("master pressed", self.input.get_text())
        if not self.input.get_text():
            self.message("\nCannot use empty Master Pass")
            return
        self.apply_master()

    def activate_action(self, action):

        #dialog = Gtk.MessageDialog(None, Gtk.DIALOG_DESTROY_WITH_PARENT,
        #    Gtk.MESSAGE_INFO, Gtk.BUTTONS_CLOSE,
        #    'Action: "%s" of type "%s"' % (action.get_name(), type(action)))
        # Close dialog on user response
        #dialog.connect ("response", lambda d, r: d.destroy())
        #dialog.show()

        warnings.simplefilter("ignore")
        strx = action.get_name()
        warnings.simplefilter("default")

        print ("activate_action", strx)

    def activate_quit(self, action):
        print( "activate_quit called")
        self.OnExit(False)

    def activate_exit(self, action):
        print( "activate_exit called" )
        self.OnExit(False)

    def activate_about(self, action):
        print( "activate_about called")
        pass

# Start of program:

if __name__ == '__main__':

    mainwin = MainWin()
    Gtk.main()

# EOF