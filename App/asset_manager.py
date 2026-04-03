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
        self.library = {
            "textures": {},
            # Only stored textures.
            # Audio is stored in the Mixer itself
        }

    def load_texture(self, path):
        # Load the texture
        loaded_texture = self.renderer.load_texture(path)
        # Get key name for library item
        relative = path.relative_to(ASSETS_ROOT / "Images")
        key = relative.with_suffix("").as_posix()
        # Add to the library
        self.library["textures"][key] = loaded_texture
        debug_print(f'Loaded Texture: "{path}"', debug_mode)

    def load_audio(self, path):
        # Check for effects/music and separate them
        if path.parent.name == "effects":
            self.mixer.load_sound(path)
        elif path.parent.name == "music":
            self.mixer.load_music_track(path)
        debug_print(f'Loaded Audio: "{path}"', debug_mode)

    def load_all(self):
        # Instantly load all the textures and audio files in ROOT/Assets/
        for file in ASSETS_ROOT.rglob("*"):
            if file.is_file():
                # If the file is an image
                if file.suffix == ".png":
                    self.load_texture(file)
                # If the file is an audio
                if file.suffix == ".ogg":
                    self.load_audio(file)

if __name__ == "__main__":
    asset_manager = AssetManager(1, 1)  # Test with fake values (Deprecated)
    asset_manager.load_all()
    debug_print(asset_manager.library, debug_mode)
