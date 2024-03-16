#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
## Copyright 2024 Henry Kroll <nospam@thenerdshow.com>
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
from gi.repository import Gtk, Adw
import sys, os, threading
from transformers.pipelines.audio_utils import ffmpeg_read
from interface import MainWindow
print("Importing FlaxWhisperPipline... Please wait...")
from tqdm_loader import tqdm_generate, init_pipeline
sample_rate = 16000
task = "transcribe"
return_timestamps = False
pipeline = None

class cpWindow(MainWindow):
    def transcribe(self, fname, start_time, end_time):
        with open(fname, "rb") as f:
            inputs = f.read()
            # ffmpeg_read also converts inputs to the required type numpy.ndarray
            inputs = ffmpeg_read(inputs, sample_rate)
            inputs = {"array": inputs, "sampling_rate": sample_rate}
            text_chunk, runtime = tqdm_generate(inputs, task=task, return_timestamps=return_timestamps)
            os.remove(fname)
            # Show the captions
        if text_chunk != "you":
            print(text_chunk)
            self.show_caption(text_chunk)
            self.text.append([start_time, end_time, text_chunk])

    def get_pipeline(self):
        global pipeline
        pipeline = init_pipeline()
        self.captions_box.set_css_classes(['info'])
        self.captions_box.set_text("Language model ready.")
        self.allow_transcribing = True # Allow transcribing
        print("Ready")

class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = cpWindow(application=app)
        self.win.present()
        self.win.captions_box.set_text("Loading language model...")

app = MyApp(application_id="com.comptune.rec")
app.run(sys.argv)
