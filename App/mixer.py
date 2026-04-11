from pygame import mixer

class Mixer:
    def __init__(self):
        mixer.init()
        self.library = {}
        self.volume = 1.0
        self.music_library = {}
        self.music_volume = 1.0
        self.set_volume(self.volume)
        self.set_music_volume(self.music_volume)

    def load_settings(self, settings):
        self.volume = settings.audio.master
        self.music_volume = settings.audio.music

    def apply_settings(self, settings, scene_manager):
        # Set audio volumes here because sounds are loaded by now here
        self.set_music_volume(self.music_volume)
        self.set_volume(self.volume)
        # Apply some stuff
        percent = int(settings.audio.master * 100)
        if percent == 100:
            text = f"       Master Volume: {percent}%       "
        elif percent < 10:
            text = f"         Master Volume: {percent}%         "
        else:
            text = f"        Master Volume: {percent}%        "
        scene_manager.get_from_all("master_volume").text.content = text
        percent = int(settings.audio.music * 100)
        if percent == 100:
            text = f"        Music Volume: {percent}%        "
        elif percent < 10:
            text = f"          Music Volume: {percent}%          "
        else:
            text = f"         Music Volume: {percent}%         "
        scene_manager.get_from_all("music_volume").text.content = text

    def load_sound(self, key, path):
        self.library[key] = mixer.Sound(path)

    def play_sound(self, name):
        self.library[name].play()

    def set_volume(self, value: float):
        self.volume = max(0.0, min(1.0, value))
        # Update SFX
        for sound in self.library.values():
            sound.set_volume(self.volume)
        # Apply* to Music
        self.set_music_volume(self.music_volume, change=False)

    def change_volume(self, value: float):
        self.set_volume(self.volume + value)

    def load_music_track(self, key, path):
        self.music_library[key] = path

    def play_music(self, name, loops: int = -1, start: float = 0.0):
        mixer.music.load(self.music_library[name])
        mixer.music.play(loops=loops, start=start)

    def stop_music(self):
        mixer.music.stop()

    def pause_music(self):
        mixer.music.pause()

    def unpause_music(self):
        mixer.music.unpause()

    def set_music_volume(self, value: float, change: bool = True):
        if change:  # Only don't change direct music_volume if asked to
            self.music_volume = max(0.0, min(1.0, value))
        final_volume = self.music_volume * self.volume
        mixer.music.set_volume(final_volume)

    def change_music_volume(self, value: float):
        self.set_music_volume(self.music_volume + value)
