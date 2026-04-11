from pygame import Vector2, Rect
from App.asset_manager import AssetManager
from App.renderer import Sprite2D
from Entities.boats import Boat
from App.clock import Timer


class ExplosiveBoat(Boat):
    # External Data
    name = "Explosive Boat"  # Name
    id = "ExplosiveBoat"  # ID
    cost = 120  # Cost to buy the boat
    texture_id = "boats/boat5_"  # ID for getting the texture for boat. After the _ is team name.
    scale = Vector2(0.32, 0.32)  # Scale of the boat
    def __init__(self, team_name: str, position: Vector2, lane: int, asset_manager: AssetManager):
        super().__init__(team_name, position, lane, asset_manager)
        # Main Data
        self.position: Vector2 = position  # Position (Centered)
        self.rect: Rect = Rect((*position, 100, 30))  # X Y Position, Width, Height
        self.rect_offset: Vector2 = Vector2(0, 25)  # Offset for rect (Applied in self.fix_other_positions)
        self.lane: int = lane  # Which lane (1/2/3) it's on
        self.sprite: Sprite2D = Sprite2D(  # Boat Sprite
            texture=asset_manager.get("textures", f"{self.texture_id}{team_name.upper()}"),  # Get Texture
            position=self.position,  # Sprite should always follow self.position
            position_mode="center",  # Position Mode. Keep centered.
            scale=Vector2(0.32, 0.32))  # Rescale of the sprite
        self.health_max: int = 50  # Boat's Max Health
        self.health: int = self.health_max  # Boat's Health
        self.speed: int = 50  # Boat's Speed in px/s calculated by (speed*dt). Can be -/+ Depending on Team
        self.damage: int = 25  # Boat's Damage (When collision, damage is exchanged twice. Technically 25==50DMG)
        self.abilities: list = ["explosive"]  # Special abilities the boat has
        self.fix_direction()  # Fix the Boat's direction immediately
        # Some fun stuff
        self.far_hurt_radius = 400  # Largest explosion radius, least damage
        self.far_damage = 50
        self.near_hurt_radius = 300  # Medium explosion radius, okay damage
        self.near_damage = 100
        self.close_hurt_radius = 200  # Small explosion radius, BIG damage
        self.close_damage = 250
        self.arm_timer: Timer = Timer(4.0, start=True)  # Time to arm itself
        self.can_explode = False  # If it can explode

    def update(self, dt: float, teams, team_edges: dict[str, int], asset_manager, mixer):
        self.update_basic(dt, teams, team_edges)
        if self.arm_timer.update(dt):  # Ready to explode
            self.can_explode = True

    def draw_others(self, renderer, debug_mode=False):
        # Draw explosion radius in debug mode
        if debug_mode:
            # Calculate Rects
            half_far_hurt_radius = self.far_hurt_radius / 2
            rect_far = Rect(self.position.x - half_far_hurt_radius, self.position.y,
                            self.far_hurt_radius, 60)
            half_near_hurt_radius = self.near_hurt_radius / 2
            rect_near = Rect(self.position.x - half_near_hurt_radius, self.position.y,
                            self.near_hurt_radius, 60)
            half_close_hurt_radius = self.close_hurt_radius / 2
            rect_close = Rect(self.position.x - half_close_hurt_radius, self.position.y,
                            self.close_hurt_radius, 60)
            # Draw Rects
            renderer.draw_rect(
                rect_far,
                color=(255, 179, 0, 100)
            )
            renderer.draw_rect(
                rect_near,
                color=(255, 106, 0, 100)
            )
            renderer.draw_rect(
                rect_close,
                color=(255, 10, 0, 100)
            )
