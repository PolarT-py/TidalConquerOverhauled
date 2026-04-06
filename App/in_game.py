import pygame as pg
from pygame import Vector2
from dataclasses import dataclass, field
from App.renderer import Renderer
from App.asset_manager import AssetManager
from App.mixer import Mixer
from App.input import InputManager
from World.background import Background


# The actual Gameplay part of the Game
class InGame:
    def __init__(self,
                 renderer: Renderer,
                 asset_manager: AssetManager,
                 mixer: Mixer,
                 input_manager: InputManager,
                 background: Background):
        # Set Managers
        self.renderer: Renderer = renderer
        self.asset_manager: AssetManager = asset_manager
        self.mixer: Mixer = mixer
        self.input_manager: InputManager = input_manager
        self.background: Background = background
        # Set States
        self.running = False
        # Set Teams
        self.blue = Team("blue")
        self.red = Team("red")

    # Start a new game
    def new(self):
        pass

    def start(self): self.running = True  # Unpauses the game

    def pause(self): self.running = False  # Pauses the game

    def update(self, dt):
        # Update Background (Sky, Sea, Islands, Lanes animation)
        self.background.update(dt)
        # Update Game Objects
        if self.running:
            pass

    def draw(self):
        # Draw Background in the back
        self.background.draw_all()


@dataclass
class Team:
    name: str
    money: int = 0
    money_multiplier: float = 1.0
    boats: list[int] = field(default_factory=list)  # Replace list[int] with real Boats later
