from App.renderer import Sprite2D, Renderer
from App.asset_manager import AssetManager
from App.clock import Timer
from pygame import Vector2
from math import sin

class Background:
    def __init__(self, renderer, asset_manager):
        # Initialize Sprites
        self.sky: Sprite2D | None = None
        # Sea is not a sprite. No need to initialize here
        self.lanes: Sprite2D | None = None
        self.islands: Sprite2D | None = None

        # Set Properties
        self.animation_state = 0  # 0-1
        self.sea_colors = (
        (74, 227, 255),
        (70, 214, 242),
        )
        self.current_sea_color = self.sea_colors[self.animation_state]
        self.animation_state_change_timer: Timer = Timer(60/95*2, start=True, repeat=True)  # Cuz music is 95BPM
        self.LANE_POSITION = Vector2(640, 990)
        self.lane_sine_speed = Vector2(1, 1)
        self.ISLANDS_POSITION = Vector2(640, 960)

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
        ) # Animations: bg/bg1 bg/bg2
        self.lanes = Sprite2D(
            self.asset_manager.get("textures", "island/lanes1"),
            position=self.LANE_POSITION,
            rotation=0.0,
            scale=Vector2(1.28, 1.28),
            position_mode="center"
        )  # Animations: island/lanes1 island/lanes2
        self.islands = Sprite2D(
            self.asset_manager.get("textures", "island/islands1"),
            position=self.ISLANDS_POSITION,
            rotation=0.0,
            scale=Vector2(1.28, 1.28),
            position_mode="center"
        )  # Animations: island/islands1 island/islands2

    def update(self, dt):
        # When animation can update
        if self.animation_state_change_timer.update(dt):
            # Flip animation state
            self.animation_state ^= 1
            self.current_sea_color = self.sea_colors[self.animation_state]
            self.sky.texture = self.asset_manager.get(
                "textures", f"bg/bg{self.animation_state+1}")
            self.lanes.texture = self.asset_manager.get(
                "textures", f"island/lanes{self.animation_state+1}")
            self.islands.texture = self.asset_manager.get(
                "textures", f"island/islands{self.animation_state+1}")
        # Update lanes sine animation
        self.lane_sine_speed.x += 0.5 * dt
        self.lanes.position.x = sin(self.lane_sine_speed.x) * 100 + self.LANE_POSITION.x
        self.lane_sine_speed.y += 3 * dt
        self.lanes.position.y = sin(self.lane_sine_speed.y) * 4 + self.LANE_POSITION.y

    def draw_all(self):
        self.renderer.fill(self.current_sea_color)  # Draw Sea
        self.sky.position.x = 0
        self.renderer.draw_sprite(self.sky)  # Draw Sky
        self.sky.position.x = 1280
        self.renderer.draw_sprite(self.sky)  # Draw Sky on the Right side
        self.sky.position.x = -1280
        self.renderer.draw_sprite(self.sky)  # Draw Sky on the Left side
        self.renderer.draw_sprite(self.lanes) # Draw lanes
        self.renderer.draw_sprite(self.islands) # Draw islands
