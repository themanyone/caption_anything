#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
## Copyright 2023 Henry Kroll <nospam@thenerdshow.com>
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
## MA 02110-1301, USA.
##
## Gtk includes
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gdk, Gio, GLib, Pango, GObject
import sys, os, requests
from interface import MainWindow

cpp_url = "http://127.0.0.1:7777/inference"

## Audio includes
import soundcard as sc
import soundfile as sf
import queue
import math
import time
import tempfile

class cpWindow(MainWindow):
    def transcribe(self, f, start_time, end_time):
        files = {'file': (f, open(f, 'rb'))}
        data = {'temperature': '0.2', 'response-format': 'json'}

        try:
            response = requests.post(cpp_url, files=files, data=data)
            os.remove(f)
            # Parse the JSON response
            result = [response.json()]
            text_chunk = result[0]['text'].strip()
            # Show the captions
            if text_chunk != "you":
                print(text_chunk)
                self.show_caption(text_chunk)
                self.text.append([start_time, end_time, text_chunk])
        except Exception as e:
            sys.stderr.write(f"Error: {e}")

class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = cpWindow(application=app)
        self.win.present()

app = MyApp(application_id="com.comptune.rec")
app.run(sys.argv)
