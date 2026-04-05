from App.renderer import Sprite2D, Renderer
from App.asset_manager import AssetManager
from App.clock import Timer
from pygame import Vector2

class Background:
    def __init__(self, renderer, asset_manager):
        # Initialize Sprites
        self.sky: Sprite2D = None
        # Sea is not a sprite
        # self.lanes = None

        # Set Properties
        self.animation_state = 0  # 0-1
        self.sea_colors = (
        (74, 227, 255),
        (70, 214, 242),
        )
        self.current_sea_color = self.sea_colors[self.animation_state]
        self.animation_state_change_timer: Timer = Timer(1.0, start=True, repeat=True)

        # Set renderer and asset library and load sprites
        self.renderer: Renderer = renderer
        self.asset_manager: AssetManager = asset_manager
        self.load_all_sprites()

    def load_all_sprites(self):
        self.sky = Sprite2D(
            self.asset_manager.get("textures", "bg/bg1"),
            position=Vector2(0, 0),
            rotation=0.0,
            scale=Vector2(1.28, 1.28),
            position_mode="topleft",
        )
        # self.lanes = Sprite2D(
        #     self.asset_manager.library["island/lanes"],
        #     position=Vector2(0, 500),
        #     rotation=0.0,
        #     scale=Vector2(1.28, 1.28),
        #     position_mode="topleft"
        # )

    def update(self, dt):
        # Test Check if it can update animation
        # self.sky.rotation += 1
        if self.animation_state_change_timer.update(dt):
            # Flip animation state
            self.animation_state ^= 1
            self.current_sea_color = self.sea_colors[self.animation_state]
            self.sky.texture = self.asset_manager.get("textures", f"bg/bg{self.animation_state+1}")

    def draw_all(self):
        self.renderer.fill(self.current_sea_color)  # Draw Sea
        self.renderer.draw_sprite(self.sky)  # Draw Sky
        # self.renderer.draw_sprite(self.lanes)
