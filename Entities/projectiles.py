from pygame import Vector2, Rect
from App.asset_manager import AssetManager
from App.renderer import Renderer, Texture2D
from App.clock import Timer


class CannonBall:
    def __init__(self, position: Vector2, x_velocity: float, y_velocity: float, stop_y: float, team: str, lane: int,
                 asset_manager: AssetManager):
        self.position: Vector2 = Vector2(position)  # Set Position
        self.x_velocity: float = x_velocity  # Horizontal movement speed
        self.y_velocity: float = y_velocity  # Vertical movement speed
        self.team = team  # Which team it's from
        self.gravity_accel: float = 200.0  # Downward acceleration in px/s^2
        self.stop_y: float = stop_y  # Y level where cannonball should stop
        self.rect: Rect = Rect(*self.position, 15, 15)  # Set Rect
        self.fix_rect()  # Fix Rectangle to center
        self.texture_sink: Texture2D = asset_manager.get("textures", "misc/cannonballsink")
        self.texture_sand: Texture2D = asset_manager.get("textures", "misc/cannonballsinksand")
        self.texture: Texture2D = asset_manager.get("textures", "misc/cannonball")
        self.despawn_timer: Timer = Timer(3.0, start=False)
        self.despawn = False  # To activate the Despawn Timer
        self.dead = False  # To wait for cleanup
        self.damage = 150  # Damage it does when hit
        self.lane = lane  # Which lane its on

    def fix_rect(self):
        self.rect.center = self.position

    def kill(self):
        self.despawn = True
        self.dead = True

    def do_despawn(self):
        # Set despawn values and timer
        self.despawn = True
        self.despawn_timer.reset()
        # Set new texture depending on where it lands
        if self.position.x < 180 or self.position.x > 1100:
            self.texture = self.texture_sand
        else:
            self.texture = self.texture_sink

    def update(self, dt):
        if self.dead:
            return
        if not self.despawn:  # Is Alive
            self.position.x += self.x_velocity * dt  # Apply horizontal velocity
            self.position.y += self.y_velocity * dt  # Apply vertical velocity
            self.y_velocity += self.gravity_accel * dt  # Apply gravity

            if self.position.y >= self.stop_y:
                self.position.y = self.stop_y
                self.do_despawn()
            self.fix_rect()  # Fix rect to center position
        else:
            if self.despawn_timer.update(dt):  # When despawn time is over
                self.dead = True

    def draw(self, renderer: Renderer, debug_mode):
        # Draw cannonball
        renderer.draw_texture(self.texture, self.position, position_mode="center")
        # Draw cannonball hitbox in debug mode
        if debug_mode:
            renderer.draw_rect(self.rect, (50, 50, 50, 100))
