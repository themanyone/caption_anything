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
from gi.repository import Gtk, Adw, Gdk, Gio, GLib, Pango
import sys, os, requests

cpp_url = "http://127.0.0.1:7777/inference"

## Audio includes
import soundcard as sc
import soundfile as sf
import numpy as np
import threading
import queue
import math
import time
import tempfile

sample_rate = 16000
channels = 1
chunk_time = 2 # Process 2-second chunks. Larger is more-accurate, slower.
max_duration = 120 * 60 # Max recording duration: quits after 120 minutes
task = "transcribe"

## Gtk boilerplate code
class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.allow_transcribing = False
        # Create an event object to signal mixer to stop
        self.stop_event = threading.Event()
        self.set_default_size(500, 50)

        # Create combo box
        combo = Gtk.ComboBoxText()
        self.list_inputs(combo)
        label = Gtk.Label()
        label.set_text("  From ")
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        vbox.append(hbox)
        self.set_child(vbox)
        hbox.append(label)
        hbox.append(combo)
        # Connect signal to get the selected text
        combo.connect("changed", self.on_combobox_changed)

        # Create a GtkEntry box
        txt = "Ready to transcribe."
        entry = Gtk.Entry()
        entry.set_text(txt)
        vbox.append(entry)
        self.captions_box = entry

        # Adding your custom CSS stylesheet
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path('style.css')
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), 
            css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        # self.captions_box.set_css_classes(['warning'])

        # Add a header
        self.header = Gtk.HeaderBar()
        self.set_titlebar(self.header)
        self.file_label = Gtk.Label()
        self.file_label.set_text(" File    ")
        self.header.pack_start(self.file_label)

        # Set file name
        self.file_entry = Gtk.Entry()
        self.file_entry.set_width_chars(10)
        self.header.pack_start(self.file_entry)
        self.file_entry.set_tooltip_text("optional .wav file for recordings")

        # add record button
        transcribe_button = Gtk.Button.new_with_label("Transcribe")
        self.header.pack_start(transcribe_button)
        # Connect signal to transcribe_audio function
        transcribe_button.connect("clicked", self.record_audio)
        # add stop button to vbox
        stop_button = Gtk.Button.new_with_label("Stop/Save")
        self.header.pack_start(stop_button)
        # Connect signal to stop_audio function
        stop_button.connect("clicked", self.stop_audio)

        # Create a popover
        self.popover = Gtk.PopoverMenu()

        # Create a new menu
        menu = Gio.Menu()
        self.popover.set_menu_model(menu)

        # Create a menu button
        self.hamburger = Gtk.MenuButton()
        self.hamburger.set_popover(self.popover)
        self.hamburger.set_icon_name("open-menu-symbolic")  # Give it a nice icon

        # Add menu button to the header bar
        self.header.pack_start(self.hamburger)

        # Create an action to run a *show about dialog* function we will create 
        action = Gio.SimpleAction.new("open-about", None)
        action.connect("activate", self.on_open_about)
        self.add_action(action)

        menu.append("About", "win.open-about")

        self.init_pipe = threading.Thread(target=self.get_pipeline)
        self.init_pipe.start()

    def on_open_about(self, action, param):
        dialog = Adw.AboutWindow(transient_for=app.get_active_window())
        dialog.set_application_name=("App name")
        dialog.set_version("1.0")
        dialog.set_developer_name("Henry Kroll III <nospam@thenerdshow.com>")
        dialog.set_license_type(Gtk.License(Gtk.License.GPL_3_0))
        dialog.set_comments("GTK Recorder")
        dialog.set_website("https://github.com/themanyone")
        dialog.set_issue_url("https://github.com/Tailko2k/GTK4PythonTutorial/issues")
        dialog.add_credit_section("Contributors", ["None"])
        dialog.set_translator_credits("None")
        dialog.set_copyright("\xa9 2023 developer")
        dialog.set_developers(["Developer"])
        dialog.set_application_icon("com.github.devname.appname") # icon must be uploaded in ~/.local/share/icons or /usr/share/icons
        dialog.present()

    # Populate combo box
    def list_inputs(self, combo):
        # List monitor subdevices by name
        inputs = sc.all_microphones(include_loopback=True)
        for mic in inputs:
            combo.append(mic.id, mic.name)

        # Set the active item
        self.input_id = inputs[2].id
        combo.set_active_id(self.input_id)

    def on_combobox_changed(self, combo):
        self.input_id = combo.get_active_id()
        if self.input_id:
            print(self.input_id)

    ## Audio code
    def record_audio(self, widget, **kwargs):
        if not self.allow_transcribing: return False
        self.allow_transcribing = False # Don't allow double transcribing
        self.stop_event.clear() # Permit stopping
        self.rec_thread = threading.Thread(target=self.recording_thread)
        self.rec_thread.start() # Start transcribing
        print("Transcribing")

    def recording_thread(self):
        # Start recording from the selected subdevice
        subdevice = sc.get_microphone(self.input_id, True)
        # Initialize text and audio buffers
        self.recording = []
        self.text = []
        duration = channels * sample_rate * chunk_time
        ttime = 0
        begin = time.time()
        with subdevice.recorder(samplerate=sample_rate, channels=channels) as recorder:
            while not self.stop_event.is_set():
                text_chunk = ""
                start_time = time.time() - begin
                if start_time < 0.1: start_time = 0 # correct for load time
                # Record the stream
                audio_data = recorder.record(numframes=duration)
                self.recording.append(audio_data)

                # Save to "tempfile"
                f = tempfile.mktemp()
                # Doesn't really save anything. The OS treats tempfile as memory.
                sf.write(f, audio_data, samplerate=sample_rate, format='wav')

                files = {'file': (f, open(f, 'rb'))}
                data = {'temperature': '0.2', 'response-format': 'json'}

                try:
                    response = requests.post(cpp_url, files=files, data=data)
                    print(f"Response status code: {response.status_code}")
                    print(response.json())
                    os.remove(f)

                    # Parse the JSON response
                    result = [response.json()]
                    text_chunk = result[0]['text']
                except Exception as e:
                    sys.stderr.write(f"Error: {e}")

                end_time = time.time() - begin

                # Show the captions
                if text_chunk != " you":
                    GLib.idle_add(self.show_caption, text_chunk)
                    self.text.append([start_time, end_time, text_chunk.strip()])
                ttime += end_time - start_time

                # Quit if max duration reached
                if ttime > max_duration:
                    print("Max recording duration reached. Stopping.")
                    self.stop_audio(None)

    # Show audio captions on interface
    def show_caption(self, text_chunk):
        self.captions_box.set_css_classes(['trans'])
        self.captions_box.set_text(text_chunk)
        return False

    def stop_audio(self, widget, **kwargs):
        filename = self.file_entry.get_text()
        if not self.stop_event.is_set():
            self.stop_event.set()
            try:
                self.rec_thread.join()
            except Exception as e:
                print("Exception:", e)
        if len(self.recording):
            if filename and os.path.isfile(filename):
                # File exists. Overwrite? Python gi Gtk(4.0) dialog.
                message = Gtk.MessageDialog(
                message_type=Gtk.MessageType.WARNING, buttons=Gtk.ButtonsType.YES_NO,
                text="<span foreground=\"red\" size=\"xx-large\">File exists. Overwrite?</span>")
                message.set_transient_for(self)
                message.props.use_markup = True
                message.connect("response", self.write_file)
                message.present()
            else: self.write_file(None, Gtk.ResponseType.YES)

    def write_file(self, widget, button):
        # If called as the result of a dialog, take down the dialog
        if widget: widget.destroy()
        # If it is okay to save the file
        if button == Gtk.ResponseType.YES:
            filename = self.file_entry.get_text()
            if not filename:
                filename = time.ctime().replace(" ", "_")+".wav"
            # Save the recording to a file
            rec = np.concatenate(self.recording)
            try:
                sf.write(filename, rec, samplerate=sample_rate, format='wav')
                self.recording = []
                print("File saved as", filename)
                # Also save captions
                exts = {".txt": '', ".srt": '', ".tsv": '', ".vtt": ''}
                for ext in exts:
                    if filename[-4] == '.':
                        exts[ext] = filename[:-4] + ext
                    else:
                        exts[ext] = filename + ext

                # write text tile
                f = open(exts[".txt"], 'w')
                f.write('\n'.join([x[2] for x in self.text]))
                f.close()

                # write srt
                def srt_time(time):
                    hours = int(time / 3600)
                    minutes = int((time % 3600) / 60)
                    seconds = int(time % 60)
                    milliseconds = int((time % 1) * 1000)
                    return "{:02d}:{:02d}:{:02d},{:03d}".format(hours, minutes, seconds, milliseconds)
                f = open(exts[".srt"], 'w')
                count = 0
                for x in self.text:
                    count += 1
                    f.write(f"{count}\n")
                    f.write(srt_time(x[0]) + " --> " + srt_time(x[1]) + '\n')
                    f.write(x[2] + '\n')
                    f.write('\n')
                f.close()

                # write tsv
                def tsv_time(time):
                    return math.floor(time*1000)
                f = open(exts[".tsv"], 'w')
                f.write("start\tend\ttext\n")
                for x in self.text:
                    f.write(f"{tsv_time(x[0])}\t{tsv_time(x[1])}\t{x[2]}\n")
                f.close()

                # write vtt
                def vtt_time(time):
                    minutes = int((time % 3600) / 60)
                    seconds = int(time % 60)
                    milliseconds = int((time % 1) * 1000)
                    return "{:02d}:{:02d}.{:03d}".format(minutes, seconds, milliseconds)
                f = open(exts[".vtt"], 'w')
                f.write("WEBVTT\n\n")
                for x in self.text:
                    f.write(vtt_time(x[0]) + " --> " + vtt_time(x[1]) + '\n')
                    f.write(x[2] + '\n')
                    f.write('\n')
                f.close()
                self.text = []
            except Exception as e:
                print(e)
        # Allow transcribing to begin again, even if no file was saved.
        self.allow_transcribing = True

    def get_pipeline(self):
        self.captions_box.set_css_classes(['info'])
        self.allow_transcribing = True # Allow transcribing

class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()

app = MyApp(application_id="com.comptune.rec")
app.run(sys.argv)
