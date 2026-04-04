from pygame import mixer

class Mixer:
    def __init__(self):
        mixer.init()
        self.library = {}
        self.volume = 1.0
        self.set_volume(self.volume)
        self.music_library = {}
        self.music_volume = 1.0
        self.set_music_volume(self.music_volume)

    def load_settings(self, settings):
        self.volume = settings.audio.master
        self.music_volume = settings.audio.music

    def load_sound(self, key, path):
        self.library[key] = mixer.Sound(path)

    def play_sound(self, name):
        self.library[name].play()

    def set_volume(self, value: float):
        self.volume = max(0.0, min(1.0, value))  # Set Range: 0.0-1.0
        for sound in self.library.values():
            sound.set_volume(self.volume)

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

    def set_music_volume(self, value: float):
        self.music_volume = max(0.0, min(1.0, value))
        mixer.music.set_volume(self.music_volume)

    def change_music_volume(self, value: float):
        self.set_music_volume(self.music_volume + value)
