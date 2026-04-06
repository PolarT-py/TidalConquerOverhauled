from pathlib import Path
from App.debug import debug_print
import time

debug_mode = False
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_ROOT = Path(PROJECT_ROOT).joinpath("Assets")
debug_print(f'Assets Root: {ASSETS_ROOT}', debug_mode)


class AssetManager:
    def __init__(self, renderer, mixer):
        self.renderer = renderer
        self.mixer = mixer
        self.library = {
            "textures": {},
            "fonts": {},
            "font_cache": {},
        }

    def get(self, family, key):
        try:
            return self.library[family][key]
        except KeyError:
            debug_print("No such Key (Texture/Path). ", debug_mode)
            if family == "texture":
                debug_print(f'Did you mean "textures"? (You wrote "texture")')  # Future-proof myself from be dum
        return None

    def load_texture(self, path: Path):
        # Load the texture
        loaded_texture = self.renderer.load_texture(path)
        # Get key name for library item
        relative = path.relative_to(ASSETS_ROOT / "Images")
        key = relative.with_suffix("").as_posix()
        # Add to the library
        self.library["textures"][key] = loaded_texture
        debug_print(f'Loaded Asset Texture: "{path}" as "{key}"', debug_mode)

    def load_audio(self, path: Path):
        # Get key name for library item
        relative = path.relative_to(ASSETS_ROOT / "Audio")
        key = relative.with_suffix("").as_posix()
        # Check for effects/music and separate them
        if path.parent.name == "effects":
            self.mixer.load_sound(key, path)
        elif path.parent.name == "music":
            self.mixer.load_music_track(key, path)
        debug_print(f'Loaded Asset Audio: "{key}" as "{key}"', debug_mode)

    def load_font(self, path: Path):
        # Load the texture
        loaded_font = path  # Only store the path. Font size is dynamic, that's why
        # The font key is just stem alone. No need for relative parent
        key = path.stem
        # Add to the library
        self.library["fonts"][key] = loaded_font
        debug_print(f'Loaded Asset Font: "{path}" as "{key}"', debug_mode)

    def load_all(self):
        start_time = time.time()
        # Load all the textures and audio files in ROOT/Assets/
        images_root = ASSETS_ROOT / "Images"
        audio_root = ASSETS_ROOT / "Audio"
        fonts_root = ASSETS_ROOT / "Fonts"
        # Search Image Files
        for file in images_root.rglob("*.png"):
            self.load_texture(file)
        # Search Audio Files
        for file in audio_root.rglob("*.ogg"):
            self.load_audio(file)
        # Search Font Files
        for file in fonts_root.rglob("*.ttf"):
            self.load_font(file)
        debug_print(f"Took: {(time.time() - start_time) * 1000:.2f}ms to load all assets", debug_mode)

if __name__ == "__main__":
    asset_manager = AssetManager(1, 1)  # Test with fake values (Deprecated)
    asset_manager.load_all()
    debug_print(asset_manager.library, debug_mode)
