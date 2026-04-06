from dataclasses import dataclass, field
from pygame import Vector2
from App.renderer import Renderer
from App.asset_manager import AssetManager
from App.mixer import Mixer
from App.input import InputManager
from World.background import Background
from Entities.boats import Boat
from Entities.explosion import Explosion


# The actual Gameplay part of the Game
class InGame:
    def __init__(self,
                 renderer: Renderer,
                 asset_manager: AssetManager,
                 mixer: Mixer,
                 input_manager: InputManager):
        # Set Managers
        self.renderer: Renderer = renderer
        self.asset_manager: AssetManager = asset_manager
        self.mixer: Mixer = mixer
        self.input_manager: InputManager = input_manager
        self.background = Background(self.renderer, self.asset_manager)
        # Set States
        self.running: bool = False
        # Declare Teams
        self.teams: Teams | None = None
        # Declare Objects (Explosions, Cannonballs, Mines, etc)
        self.explosions: list[Explosion] | None = None
        # Declare Constants
        self.TEAM_BOAT_EDGE_X: dict[str, int] = {  # Team Boat Spawn/Win X positions
            "blue": 200,
            "red": 1080,
        }
        self.LANE_LEVEL_Y: dict[int, int] = {  # Y level for each Lane (To spawn boats in)
            1: 870,
            2: 930,
            3: 990,
        }
        # New Game
        self.new(False)

    # Start a new game
    def new(self, start=True):
        # Set Teams
        self.teams = Teams(Team("blue"), Team("red"))
        # Set Objects (Explosions, Cannonballs, Mines, etc)
        self.explosions = []
        # Start the Game if said so
        if start:
            self.unpause()
        # Create Test Objects
        self.teams.blue.boats.append(Boat("blue",
                                          Vector2(self.TEAM_BOAT_EDGE_X["blue"], self.LANE_LEVEL_Y[1]),
                                          1,
                                          self.asset_manager))
        self.teams.red.boats.append(Boat("red",
                                          Vector2(self.TEAM_BOAT_EDGE_X["red"], self.LANE_LEVEL_Y[1]),
                                          1,
                                          self.asset_manager))
        self.teams.blue.boats.append(Boat("blue",
                                          Vector2(self.TEAM_BOAT_EDGE_X["blue"], self.LANE_LEVEL_Y[2]),
                                          1,
                                          self.asset_manager))
        self.teams.red.boats.append(Boat("red",
                                          Vector2(self.TEAM_BOAT_EDGE_X["red"]-50, self.LANE_LEVEL_Y[2]),
                                          1,
                                          self.asset_manager))
        self.teams.blue.boats.append(Boat("blue",
                                          Vector2(self.TEAM_BOAT_EDGE_X["blue"], self.LANE_LEVEL_Y[3]),
                                          1,
                                          self.asset_manager))
        self.teams.red.boats.append(Boat("red",
                                          Vector2(self.TEAM_BOAT_EDGE_X["red"]-100, self.LANE_LEVEL_Y[3]),
                                          1,
                                          self.asset_manager))

    def unpause(self): self.running = True  # Unpauses the game

    def pause(self): self.running = False  # Pauses the game

    def update(self, dt):
        # Update Background (Sky, Sea, Islands, Lanes animation)
        self.background.update(dt)
        # Update Game Objects
        if self.running:
            # Loop through all boats to update them
            for boat in self.teams.red.boats + self.teams.blue.boats:
                boat.update(dt, self.teams, self.TEAM_BOAT_EDGE_X)
            # Loop through all boats to clean them up
            for boat in self.teams.red.boats + self.teams.blue.boats:
                if boat.dead:
                    if boat.team_name == "blue":  # If Blue
                        # Summon Explosion
                        self.explosions.append(Explosion(boat.position, self.asset_manager))
                        self.teams.blue.boats.remove(boat)
                    elif boat.team_name == "red":  # If Red
                        # Summon Explosion
                        self.explosions.append(Explosion(boat.position, self.asset_manager))
                        self.teams.red.boats.remove(boat)
            # Loop through all explosions to update them
            for explosion in self.explosions:
                explosion.update(dt)

    def draw(self, debug_mode=False):
        # Draw Background in the back
        self.background.draw_all()
        # Draw Boats (Add lane layering support for boats: boat.layer)
        for boat in self.teams.red.boats + self.teams.blue.boats:
            boat.draw(self.renderer, debug_mode)
        # Draw Explosions
        for explosion in self.explosions:
            explosion.draw(self.renderer, debug_mode)


@dataclass
class Team:
    name: str
    money: int = 100
    money_base_increase: int = 20
    money_multiplier: float = 1.0
    boats: list[Boat] = field(default_factory=list)
    island_health: int = 100


@dataclass
class Teams:
    blue: Team
    red: Team
