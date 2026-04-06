from App.clock import Timer
from App.renderer import Texture2D
from App.asset_manager import AssetManager
from App.animation import Animation


class Explosion(Animation):
    def __init__(self, position, asset_manager: AssetManager):
        super().__init__(position)
        self.fps = 6
        self.flip_timer = Timer(1 / self.fps, True, True)
        self.frames: list[Texture2D] = [
            asset_manager.get("textures", "explosion/1"),
            asset_manager.get("textures", "explosion/2"),
            asset_manager.get("textures", "explosion/3"),
        ]
