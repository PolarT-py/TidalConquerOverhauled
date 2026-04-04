from __future__ import annotations
import pygame as pg
from App.settings import load_settings, save_settings
from App.renderer import Renderer, Sprite2D
from App.asset_manager import AssetManager
from App.mixer import Mixer
from App.camera import Camera2D
from World.background import Background

class Game:
    def __init__(self):
        # Load Settings
        self.settings = load_settings()

        # Initialize pygame and Essentials
        pg.init()

        self.renderer = Renderer(
            self.settings.main.window_size,
            self.settings.main.render_size,
            self.settings.main.window_title
        )
        self.renderer.set_camera(Camera2D())
        self.mixer = Mixer()
        self.mixer.load_settings(self.settings)
        self.asset_manager = AssetManager(self.renderer, self.mixer)
        self.asset_manager.load_all()
        self.mixer.play_sound("effects/click1")  # Test opening sound

        self.clock = pg.time.Clock()
        self.running = True

        # Set Objects
        self.background = Background(self.renderer, self.asset_manager)
        self.renderer.camera.slide(500, 100)

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.WINDOWRESIZED:
                self.settings.main.window_size = self.renderer.window.size

    def update(self, dt: float):
        self.background.update(dt)
        self.renderer.camera.update(dt)

    def draw(self):
        # Draw the Window Background Color (Clear Screen)
        self.renderer.clear(self.settings.main.window_bg_color)
        # Draw Background (Sky and Sea)
        self.background.draw_all()
        # Draw Black Bars
        self.renderer.draw_bars(self.settings.main.window_bg_color)

    def run(self):
        while self.running:
            # Set delta time
            dt = self.clock.tick(self.settings.main.fps) / 1000.0

            # Main logic
            self.handle_events()
            self.update(dt)
            self.draw()

            # Update the screen
            self.renderer.renderer.present()

        # Save settings and Quit game after loop stops
        save_settings(self.settings)
        pg.quit()
