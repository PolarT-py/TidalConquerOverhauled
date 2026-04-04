from __future__ import annotations
from pathlib import Path
import pygame as pg
from App.settings import load_settings, save_settings
from App.renderer import Renderer, Sprite2D
from App.asset_manager import AssetManager
from App.mixer import Mixer

class Game:
    def __init__(self):
        # Load Settings
        self.settings = load_settings()

        # Initialize pygame and Essentials
        pg.init()

        flags = pg.OPENGL | pg.DOUBLEBUF | pg.RESIZABLE
        self.window = pg.display.set_mode(self.settings.main.window_size, flags)
        pg.display.set_caption(self.settings.main.window_title)

        self.renderer = Renderer(self.settings.main.window_size, self.settings.main.render_size)
        self.mixer = Mixer()
        self.asset_manager = AssetManager(self.renderer, self.mixer)
        self.asset_manager.load_all()

        self.clock = pg.time.Clock()
        self.running = True
        self.test = -200
        self.test_sprite = Sprite2D(
            self.asset_manager.library["textures"]["boats/boat2"],
            pg.Vector2(100, 300),
            140.0,
            pg.Vector2(1.1, 1.1),
        )

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.VIDEORESIZE:
                self.settings.main.window_size = (event.w, event.h)
                flags = pg.OPENGL | pg.DOUBLEBUF | pg.RESIZABLE
                self.window = pg.display.set_mode(self.settings.main.window_size, flags)
                self.renderer.set_window_size(self.settings.main.window_size)

    def update(self, dt: float):
        # nothing yet
        pass

    def draw(self):
        # Draw the Window Background Color and Playfield Background Color
        self.renderer.clear(self.settings.main.window_bg_color)
        self.renderer.fill((0, 0, 0))
        # Draw Test Object
        self.renderer.draw_texture(
            self.asset_manager.library["textures"]["boats/boat1"], (self.test, 0)
        ) # Test draw
        self.test += 1
        # Draw another Test Object
        self.renderer.draw_sprite(self.test_sprite)
        self.test_sprite.rotation += 1

    def run(self):
        while self.running:
            # Set delta time
            dt = self.clock.tick(self.settings.main.fps) / 1000.0

            # Main logic
            self.handle_events()
            self.update(dt)
            self.draw()

            # Update the screen
            pg.display.flip()

        # Save settings and Quit game after loop stops
        save_settings(self.settings)
        pg.quit()
