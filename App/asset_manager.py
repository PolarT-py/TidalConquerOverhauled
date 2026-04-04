from pathlib import Path
from App.debug import debug_print

debug_mode = False
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_ROOT = Path(PROJECT_ROOT).joinpath("Assets")
debug_print(f'"Assets Root:", ASSETS_ROOT', debug_mode)


class AssetManager:
    def __init__(self, renderer, mixer):
        self.renderer = renderer
        self.mixer = mixer
        self.library = {}

    def get(self, key):
        try:
            if self.library[key] is not None:
                return self.library[key]
        except KeyError:
            debug_print("No such Key (Texture/Path). ", debug_mode)
        return None

    def load_texture(self, path):
        # Load the texture
        loaded_texture = self.renderer.load_texture(path)
        # Get key name for library item
        relative = path.relative_to(ASSETS_ROOT / "Images")
        key = relative.with_suffix("").as_posix()
        # Add to the library
        self.library[key] = loaded_texture
        debug_print(f'Loaded Texture: "{path}"', debug_mode)

    def load_audio(self, path):
        # Get key name for library item
        relative = path.relative_to(ASSETS_ROOT / "Audio")
        key = relative.with_suffix("").as_posix()
        # Check for effects/music and separate them
        if path.parent.name == "effects":
            self.mixer.load_sound(key, path)
        elif path.parent.name == "music":
            self.mixer.load_music_track(key, path)
        debug_print(f'Loaded Audio: "{key}"', debug_mode)

    def load_all(self):
        # Load all the textures and audio files in ROOT/Assets/
        images_root = ASSETS_ROOT / "Images"
        audio_root = ASSETS_ROOT / "Audio"
        # Search Image Files
        for file in images_root.rglob("*.png"):
            self.load_texture(file)
        # Search Audio Files
        for file in audio_root.rglob("*.ogg"):
            self.load_audio(file)

if __name__ == "__main__":
    asset_manager = AssetManager(1, 1)  # Test with fake values (Deprecated)
    asset_manager.load_all()
    debug_print(asset_manager.library, debug_mode)
