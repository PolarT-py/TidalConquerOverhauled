from math import sin
from pygame import Vector2, Rect
from App.asset_manager import AssetManager
from App.renderer import Sprite2D
# from Entities.projectiles import CannonBall


class Boat:
    # External Data
    name = "Generic Boat"  # Name
    id = "Boat"  # ID (Class name)
    cost = 10  # Cost to buy the boat
    texture_id = "boats/boat1_"  # ID for getting the texture for boat. After the _ is team name.
    scale = Vector2(1.0, 1.0)  # Scale of the boat
    show = True  # Show by default in the boat list
    def __init__(self, team_name: str, position: Vector2, lane: int, asset_manager: AssetManager):
        # Main Data
        self.live_time: float = 0  # Time it's been alive. Used for bobbing effect
        self.SWAY_AMPLIFIER: float = 2.0  # How much the boats sway
        self.position: Vector2 = position  # Position (Centered)
        self.rect: Rect = Rect((*position, 100, 35))  # X Y Position, Width, Height
        self.rect_offset: Vector2 = Vector2(0, 25)  # Offset for rect (Applied in self.fix_other_positions)
        self.texture_offset: Vector2 = Vector2(0, 0)  # Offset for texture rendering
        self.sway_offset: Vector2 = Vector2(0, 0)  # Offset for a bobbing effect
        self.lane: int = lane  # Which lane (1/2/3) it's on
        self.sprite: Sprite2D = Sprite2D(  # Boat Sprite
            texture=asset_manager.get("textures", f"{self.texture_id}{team_name.upper()}"),  # Get Texture
            position=self.position,  # Sprite should always follow self.position
            position_mode="center",)  # Position Mode. Keep centered.
        self.team_name: str = team_name  # Boat's Team
        self.opponent_team_name: str = self.get_opponent_team_name()  # Opponent team
        self.health_max: int = 100  # Boat's Max Health
        self.health: int = self.health_max  # Boat's Health
        self.speed: int = 100  # Boat's Speed in px/s calculated by (speed*dt). Can be -/+ Depending on Team
        self.damage: int = 25  # Boat's Damage (When collision, damage is exchanged twice. Technically 25==50DMG)
        self.dead: bool = False  # If the boat is dead or not
        self.won: bool = False  # If the boat has captured the opponent's island (island_health<=0)
        self.damaged_island: bool = False  # If the boat damaged the island or not
        self.abilities: list = []  # Special abilities the boat has
        self.fix_direction()  # Fix the Boat's direction immediately
        # Fix rect position to center immediately
        self.fix_other_positions()
        # Other stuff
        self.cannonballs = []
        self.mines = []

    def get_opponent_team_name(self) -> str:  # Get opponent's team name
        return "red" if self.team_name == "blue" else "blue"

    def fix_direction(self):
        # Modify Speed depending on Blue(+)/Red(-) Team
        if self.team_name == "red": self.speed *= -1

    def fix_other_positions(self):
        self.rect.center = self.position  # Center Rect position to self.position
        self.rect.x += self.rect_offset.x  # Apply Rect offset
        self.rect.y += self.rect_offset.y  # Apply Rect offset
        # Apply Position, Texture offset, and Sway offset
        self.sprite.position = self.position + self.texture_offset + self.sway_offset

    def kill(self):
        # Set self to dead
        self.dead = True
        # Wait for the Game Manager to clean up this boat, and summon an explosion

    def win(self):
        self.won = True
        # Wait for the Game Manager to clean up this boat, and execute Win for ____ Team

    def update_basic(self, dt: float, teams, team_edges: dict[str, int]):
        if not self.dead:
            # Bobbing effect
            self.live_time += dt
            self.sway_offset.y = sin(self.live_time) * self.SWAY_AMPLIFIER
            # Move the Boat
            self.position.x += self.speed * dt
            # Center the Rect
            self.fix_other_positions()
            # Check who is the opposite team
            if self.team_name == "blue":  # Red is the enemy
                enemy_boats_list: list = teams.red.boats
            else:  # Blue is the enemy
                enemy_boats_list: list = teams.blue.boats
            # Check Collisions on the opposite team
            for boat in enemy_boats_list:
                # If collided and the boat is alive and on the same lane
                if self.rect.colliderect(boat) and not boat.dead and boat.lane == self.lane:
                    # Exchange damage with each other
                    boat.health -= self.damage
                    self.health -= boat.damage
            # Check Health, if <=0 then kill itself (D:)
            if self.health <= 0:
                self.kill()
            # Check if it reached the opponent's island
            if self.team_name == "blue" and self.rect.right >= team_edges["red_hit"]:
                # If it reaches the Island, deal damage then die
                teams.red.island_health -= self.damage
                self.damaged_island = True
                self.kill()
                # Check if the Island has <= 0 health. If so, set off a Win so the Game Manager can clean up
                if teams.red.island_health <= 0:
                    self.win()
            elif self.team_name == "red" and self.rect.left <= team_edges["blue_hit"]:
                # If it reaches the Island, deal damage then die
                teams.blue.island_health -= self.damage
                self.damaged_island = True
                self.kill()
                # Check if the Island has <= 0 health, then win if so
                if teams.blue.island_health <= 0:
                    self.win()

    def update(self, dt: float, teams, team_edges: dict[str, int], asset_manager, mixer):
        self.update_basic(dt, teams, team_edges)

    def draw(self, renderer, debug_mode=False):
        # Draw others
        self.draw_others(renderer, debug_mode)
        # Draw Sprite
        renderer.draw_sprite(self.sprite)
        if debug_mode:  # Is debug?
            # Draw Debug Hitbox
            if self.team_name == "blue":
                color = (0, 0, 255)
            else:
                color = (255, 0, 0)
            renderer.draw_rect(self.rect, color=(*color, 100))
        # Draw Health Bar
        renderer.draw_rect(Rect(*self.position-Vector2(25, -50), 50, 5), (0, 0, 0, 50))  # BG
        renderer.draw_rect(Rect(*self.position-Vector2(23, -51), ((46 * (self.health / self.health_max)) if self.health > 0 else 0), 3), (255, 0, 0, 255))  # FG

    def draw_others(self, renderer, debug_mode=False):  # For other classes
        pass
