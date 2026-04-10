from math import sin
from random import randint
from pygame import Vector2, Rect
from App.asset_manager import AssetManager
from App.mixer import Mixer
from App.renderer import Renderer, Texture2D
from App.clock import Timer


class CannonBall:
    def __init__(self, position: Vector2, x_velocity: float, y_velocity: float, stop_y: float, team: str, lane: int,
                 asset_manager: AssetManager, mixer: Mixer):
        self.position: Vector2 = Vector2(position)  # Set Position
        self.x_velocity: float = x_velocity  # Horizontal movement speed
        self.x_velocity = randint(int(self.x_velocity-15), int(self.x_velocity+15))  # Randomize x velocity a bit
        self.y_velocity: float = y_velocity  # Vertical movement speed
        self.team = team  # Which team it's from
        self.gravity_accel: float = 200.0  # Downward acceleration in px/s^2
        self.stop_y: float = stop_y  # Y level where cannonball should stop
        self.rect: Rect = Rect(*self.position, 15, 15)  # Set Rect
        self.fix_rect()  # Fix Rectangle to center
        self.texture_sink: Texture2D = asset_manager.get("textures", "misc/cannonballsink")
        self.texture_sand: Texture2D = asset_manager.get("textures", "misc/cannonballsinksand")
        self.texture: Texture2D = asset_manager.get("textures", "misc/cannonball")
        self.despawn_timer: Timer = Timer(15.0, start=False)
        self.despawn_timer_animation: Timer = Timer(14.5, start=False)
        self.despawn_animation_start: bool = False  # Can start despawn animation
        self.despawn_scale = Vector2(1.0, 1.0)  # For despawn animation in last 1 second
        self.despawn_speed = 2  # Adjust with despawn timer length
        self.despawn = False  # To activate the Despawn Timer
        self.dead = False  # To wait for cleanup
        self.damage = 150  # Damage it does when hit
        self.lane = lane  # Which lane its on
        self.bob_time = 0.0  # Counter for bob time
        self.bob_amplitude = 30.0  # How much it bobs
        self.bob_speed = 5.0  # How fast it bobs
        self.bob_y = 0  # How much to add to position
        self.mixer = mixer  # Cool mixer

    def fix_rect(self):
        self.rect.center = self.position

    def kill(self):
        self.despawn = True
        self.dead = True

    def do_despawn(self):
        # Set despawn values and timers
        self.despawn = True
        self.despawn_timer.reset()
        self.despawn_timer_animation.reset()
        # Set new texture depending on where it lands
        if self.position.x < 180 or self.position.x > 1100:
            self.texture = self.texture_sand
        else:
            self.texture = self.texture_sink
        # self.mixer.play_sound("effects/splash")  # Forgot how bad splash sounds

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
            # Calculate bob
            self.bob_time += dt if self.texture == self.texture_sink else 0  # Add bob time only if in water
            self.bob_y = sin(self.bob_time * self.bob_speed) * self.bob_amplitude * dt
            if self.despawn_timer_animation.update(dt):  # Can start doing despawn animation
                self.despawn_animation_start = True
            if self.despawn_timer.update(dt):  # When despawn time is over
                self.dead = True
            if self.despawn_animation_start:
                self.position.y += 4 * dt  # Sink into ground animation
                self.despawn_scale -= Vector2(self.despawn_speed * dt, self.despawn_speed * dt)  # Do despawn animation

    def draw(self, renderer: Renderer, debug_mode):
        # Draw cannonball
        renderer.draw_texture(self.texture, self.position + Vector2(0, self.bob_y), position_mode="center",
                              scale=self.despawn_scale)
        # Draw cannonball hitbox in debug mode
        if debug_mode:
            renderer.draw_rect(self.rect, (50, 50, 50, 100))


class Trap:
    def __init__(self, position: Vector2, x_velocity: float, y_velocity: float, stop_y: float, team: str, lane: int,
                 asset_manager: AssetManager, mixer: Mixer):
        self.position: Vector2 = Vector2(position)  # Set Position
        self.x_velocity: float = x_velocity  # Horizontal movement speed
        self.x_velocity = randint(int(self.x_velocity-25), int(self.x_velocity+25))  # Randomize x velocity a bit
        self.y_velocity: float = y_velocity  # Vertical movement speed
        self.team = team  # Which team it's from
        self.gravity_accel: float = 200.0  # Downward acceleration in px/s^2
        self.stop_y: float = stop_y  # Y level where cannonball should stop
        self.rect: Rect = Rect(*self.position, 15, 15)  # Set Rect
        self.fix_rect()  # Fix Rectangle to center
        self.texture_sink: Texture2D = asset_manager.get("textures", "misc/trapsink")
        self.texture: Texture2D = asset_manager.get("textures", "misc/trap")
        self.live_time: Timer = Timer(60.0, start=True)
        self.despawn_timer: Timer = Timer(1.0, start=False)
        self.despawn = False  # To activate the Despawn Timer
        self.dead = False  # To wait for cleanup
        self.damage = 200  # Damage it does when hit
        self.lane = lane  # Which lane its on
        self.despawn_scale = Vector2(1.0, 1.0)  # Despawn Scaling Animation
        self.landed = False  # Has it landed in water yet?
        self.mixer = mixer  # Cool mixer

    def fix_rect(self):
        self.rect.center = self.position

    def kill(self):
        self.despawn = True
        self.dead = True

    def do_despawn(self):
        # Set despawn values and timer
        self.despawn = True
        self.despawn_timer.reset()

    def do_landed(self):
        # Set new texture when it lands
        self.texture = self.texture_sink
        self.landed = True

    def update(self, dt):
        if self.dead:
            return
        if not self.despawn:  # Is Alive
            if not self.landed:
                self.position.x += self.x_velocity * dt  # Apply horizontal velocity
                self.position.y += self.y_velocity * dt  # Apply vertical velocity
                self.y_velocity += self.gravity_accel * dt  # Apply gravity

            if self.position.y >= self.stop_y:
                self.position.y = self.stop_y
                self.do_landed()

            if self.live_time.update(dt):  # When it's live time runs out, despawn
                self.do_despawn()
            self.fix_rect()  # Fix rect to center position
        else:
            # Despawn animation
            self.despawn_scale -= Vector2(dt, dt)  # Shrink animation
            self.position.y += 4 * dt  # Sink into ground animation
            if self.despawn_timer.update(dt):  # When despawn time is over
                self.dead = True

    def draw(self, renderer: Renderer, debug_mode):
        # Draw trap
        renderer.draw_texture(self.texture, self.position, position_mode="center", scale=self.despawn_scale)
        # Draw trap hitbox in debug mode
        if debug_mode:
            renderer.draw_rect(self.rect, (50, 50, 50, 100))
