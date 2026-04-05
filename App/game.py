from __future__ import annotations
import pygame as pg
from pygame import Vector2
from pathlib import Path
from App.settings import load_settings, save_settings
from App.renderer import Renderer
from App.asset_manager import AssetManager
from App.mixer import Mixer
from App.camera import DebugCameraController
from App.input import InputManager
from App.ui import SceneManager, UIScene
from App.ui_loader import load_scenes
from World.background import Background

class Game:
    def __init__(self):
        # Load Settings
        self.settings = load_settings()

        # Initialize pygame and Essentials
        pg.init()
        self.debug_mode = False

        self.renderer = Renderer(
            window_size=self.settings.main.window_size,
            render_size=self.settings.main.render_size,
            main_title=self.settings.main.window_title,
            vsync=self.settings.main.vsync,
            fullscreen=self.settings.main.fullscreen,
            fps=self.settings.main.fps,
        )
        self.renderer.reset_camera()
        self.mixer = Mixer()
        self.mixer.load_settings(self.settings)
        self.asset_manager = AssetManager(self.renderer, self.mixer)
        self.asset_manager.load_all()
        self.input_manager = InputManager()
        self.scene_library = load_scenes(self.asset_manager, self.renderer,
                                         self.input_manager, self.mixer)
        self.scene_manager = SceneManager(self.scene_library.scenes, "main_menu")
        self.scene_manager.call_ui_beginning_functions(self.settings)
        self.debug_menu = UIScene("debug_menu")
        self.debug_menu.elements = self.scene_library.scenes.get("debug_menu").elements

        self.clock = pg.time.Clock()
        self.running = True

        # Set Window Icon
        icon = pg.image.load(Path(__file__).resolve().parent.parent.joinpath\
                                 ("Assets/Images/misc/coin.png"))
        self.renderer.set_icon(icon)

        # Set Input Controllers
        self.debug_controller = DebugCameraController(self.input_manager)
        self.DEBUG_CAMERA_SPEED = 500  # Only for debugging. Used to move camera (Outside)

        # Set Objects
        self.background = Background(self.renderer, self.asset_manager)

        # Set Actions
        self.mixer.play_music("music/Thatched Villagers")

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.WINDOWRESIZED:
                self.settings.main.window_size = self.renderer.window.size
            self.input_manager.process_event(event)  # Get input

    def handle_ui_interactions(self, dt):
        # Search through all interactable UI Buttons to check if they're activated
        # Do something if True
        for e in self.scene_manager.update(dt):
            # Main Menu
            if e.id == "start_button":
                self.running = False
            elif e.id == "exit_button":
                self.running = False
            elif e.id == "resume_button":
                self.running = False
            elif e.id == "credits_button":
                self.scene_manager.set_scene("credits")
                self.renderer.camera.move(Vector2(-1280, 0))
            elif e.id == "settings_button":
                self.scene_manager.set_scene("main_settings")
                self.renderer.camera.move(Vector2(1280, 0))
            # Credits Page
            elif e.id == "back_button_credits":
                self.scene_manager.set_scene("main_menu")
                self.renderer.camera.move(Vector2(0, 0))
            # Settings Page
            elif e.id == "back_button_settings":
                save_settings(self.settings)  # Save settings on back to Menu
                self.scene_manager.set_scene("main_menu")
                self.renderer.camera.move(Vector2(0, 0))
            elif e.id == "vsync_toggle_button":
                self.renderer.set_vsync(not self.settings.main.vsync)  # Kind of Hacky
                self.settings.main.vsync = not self.settings.main.vsync
                self.scene_manager.get("vsync_toggle_button").text.content =\
                    f"Vsync:                  {str(self.settings.main.vsync)}"
                self.scene_manager.get("vsync_text_warn").visible = True
            elif e.id == "fps_change_button":
                # Loop through the FPS Options
                current = self.settings.main.fps
                if current in self.renderer.FPS_OPTIONS:
                    index = self.renderer.FPS_OPTIONS.index(current)
                    new_index = (index + 1) % len(self.renderer.FPS_OPTIONS)
                else:
                    new_index = 2  # Fallback to 60 if something unique happens
                new_fps = self.renderer.FPS_OPTIONS[new_index]
                # Actually set it
                self.renderer.fps = new_fps
                self.settings.main.fps = new_fps
                self.scene_manager.get("fps_change_button").text.content =\
                    f"FPS:                    {new_fps}"
            elif e.id == "fullscreen_toggle_button":
                self.renderer.toggle_fullscreen()
                self.settings.main.fullscreen = not self.settings.main.fullscreen
                if self.settings.main.fullscreen:  # Fullscreen
                    e.text.content = f"Display Mode: Fullscreen"
                else:  # Windowed
                    e.text.content = f"Display Mode: Windowed"
        # Update Debug Elements every frame
        for e in self.debug_menu.elements:
            if e.id == "debug_fps":
                e.text.content = f" FPS: {round(self.clock.get_fps(), 1)} "
        # Check if toggle Debug Mode
        if self.input_manager.was_key_pressed(pg.K_F3):
            self.debug_mode = not self.debug_mode

    def update(self, dt: float):
        # Update Background Elements
        self.background.update(dt)
        # Reset Camera and Update Debug Camera
        self.renderer.reset_camera()
        if self.debug_mode:
            self.renderer.camera.update(dt, self.debug_controller.get_movement(), self.DEBUG_CAMERA_SPEED)
        # Update UI Scene Functions
        self.handle_ui_interactions(dt)
        self.debug_menu.update_all(dt)

    def draw(self):
        # Draw the Window Background Color (Clear Screen)
        self.renderer.clear(self.settings.main.window_bg_color)
        # Reset Camera to Main Camera
        self.renderer.reset_camera()
        # Draw Background (Sky and Sea)
        self.background.draw_all()
        # Draw UI
        self.scene_manager.draw()
        # Draw Black Bars
        self.renderer.draw_bars(self.settings.main.window_bg_color)
        # Draw Debug UI
        if self.debug_mode:
            self.debug_menu.draw_all()

    def run(self):
        while self.running:
            # Set delta time
            dt = self.clock.tick(self.renderer.fps) / 1000.0

            # Main logic
            self.input_manager.begin_frame()
            self.handle_events()
            self.input_manager.mouse_pos_virtual = self.renderer.window_to_virtual(
                self.input_manager.mouse_pos_window)
            self.update(dt)
            self.draw()

            # Update the screen
            self.renderer.renderer.present()

            # Check if stop run then quit
            if not self.running:
                pg.quit()

        # Save settings and Quit game after loop stops
        save_settings(self.settings)
        pg.quit()
