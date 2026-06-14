import os
import json
import time

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.listview import ListView
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock

from kivy.core.audio import SoundLoader
from plyer import filechooser

STATS_FILE = "track_stats.json"


class PlayerUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        self.playlist = []
        self.current = -1
        self.sound = None
        self.playing = False

        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, "r") as f:
                self.stats = json.load(f)
        else:
            self.stats = {}

        # TOP BAR
        self.track_label = Label(text="No Track", size_hint_y=None, height=50)
        self.add_widget(self.track_label)

        # LIST
        self.list_layout = GridLayout(cols=1, size_hint_y=None)
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))

        scroll = ScrollView()
        scroll.add_widget(self.list_layout)
        self.add_widget(scroll)

        # BUTTONS
        btn_row = BoxLayout(size_hint_y=None, height=60)

        btn_row.add_widget(Button(text="+ Files", on_press=self.add_files))
        btn_row.add_widget(Button(text="Play/Pause", on_press=self.play_pause))
        btn_row.add_widget(Button(text="Next", on_press=self.next_track))
        btn_row.add_widget(Button(text="Prev", on_press=self.prev_track))

        self.add_widget(btn_row)

        # VOLUME
        self.vol = Slider(min=0, max=1, value=0.8)
        self.vol.bind(value=self.set_volume)
        self.add_widget(self.vol)

        Clock.schedule_interval(self.update, 1)

    def add_files(self, instance):
        filechooser.open_file(on_selection=self._on_files)

    def _on_files(self, selection):
        if not selection:
            return
        for f in selection:
            title = os.path.basename(f)
            self.playlist.append({"path": f, "title": title})
            self.stats.setdefault(f, 0)
            btn = Button(text=title, size_hint_y=None, height=50)
            btn.bind(on_press=lambda x, i=len(self.playlist)-1: self.play_track(i))
            self.list_layout.add_widget(btn)

    def play_track(self, idx):
        if self.sound:
            self.sound.stop()

        self.current = idx
        track = self.playlist[idx]

        self.sound = SoundLoader.load(track["path"])
        if self.sound:
            self.sound.volume = self.vol.value
            self.sound.play()
            self.playing = True
            self.track_label.text = track["title"]

    def play_pause(self, instance):
        if not self.sound:
            return

        if self.playing:
            self.sound.stop()
            self.playing = False
        else:
            self.sound.play()
            self.playing = True

    def next_track(self, instance):
        if not self.playlist:
            return
        nxt = (self.current + 1) % len(self.playlist)
        self.play_track(nxt)

    def prev_track(self, instance):
        if not self.playlist:
            return
        prev = (self.current - 1) % len(self.playlist)
        self.play_track(prev)

    def set_volume(self, instance, value):
        if self.sound:
            self.sound.volume = value

    def update(self, dt):
        if self.current >= 0 and self.playing:
            path = self.playlist[self.current]["path"]
            self.stats[path] = self.stats.get(path, 0) + 1


class MusicApp(App):
    def build(self):
        return PlayerUI()

    def on_stop(self):
        with open(STATS_FILE, "w") as f:
            json.dump(self.root.stats, f)


if __name__ == "__main__":
    MusicApp().run()