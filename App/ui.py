from __future__ import annotations

import pygame as pg
from pygame import Vector2
from pathlib import Path
from typing import TYPE_CHECKING
from App.input import InputManager
from App.asset_manager import AssetManager
from App.mixer import Mixer

if TYPE_CHECKING:
    from App.renderer import Renderer, Texture2D


class UIElement:
    def __init__(self):
        self.id = None
        self.rect = None
        self.visible = True
        self.enabled = True

    def update(self, dt, mixer: Mixer):
        pass

    def draw(self, renderer, asset_manager):
        pass


class UIScene:
    def __init__(self, name):
        self.name = name
        self.elements = []

    def update_all(self, input_manager: InputManager, mixer: Mixer):
        activated = []
        # Search through all Elements to see which ones have been activated
        for e in self.elements:
            if e.update(input_manager, mixer):
                activated.append(e)
        return activated

    def draw_all(self, renderer: Renderer, asset_manager: AssetManager):
        for e in self.elements:
            e.draw(renderer, asset_manager)


class SceneManager:
    def __init__(self, scenes: dict[str, UIScene], start_scene: str):
        if start_scene not in scenes:
            raise ValueError(f"Scene '{start_scene}' does not exist.")
        self.scenes: dict[str, UIScene] = scenes
        self.current_scene_name: str = start_scene
        self.current_scene: UIScene = scenes[start_scene]

    def set_scene(self, scene_name: str):
        if scene_name not in self.scenes:
            raise ValueError(f"Scene '{scene_name}' does not exist.")
        self.current_scene_name = scene_name
        self.current_scene = self.scenes[scene_name]

    def update(self, input_manager, mixer):
        return self.current_scene.update_all(input_manager, mixer)

    def draw(self, renderer, asset_manager):
        self.current_scene.draw_all(renderer, asset_manager)

    def get(self, element_id: str):
        for e in self.current_scene.elements:
            if e.id == element_id:
                return e
        return None


class UIButton(UIElement):
    def __init__(self, rect: tuple[int, int, int, int], text="", text_size=24, text_font=None):
        super().__init__()
        self.rect = pg.Rect(rect)
        self.hovered = False
        self.pressed_inside = False  # Prevent you from holding click from outside, drag in and release click
        self.font = Font(text_font, text_size)
        self.text = Text(text, self.font)

    def update(self, input_manager: InputManager, mixer: Mixer):  # Returns if pressed/not
        # Fetch Mouse Position
        mouse_position = input_manager.mouse_pos_virtual
        if mouse_position is None:
            self.hovered = False
            return False  # Mouse position Out of Virtual Space
        mx, my = mouse_position

        # Check if it's enabled
        if not self.enabled: return False

        # Check if mouse is hovering
        self.hovered = self.rect.collidepoint(mx, my)
        if self.hovered and input_manager.was_mouse_pressed(1):
            self.pressed_inside = True

        # Check if mouse is clicked
        if input_manager.was_mouse_released(1):
            if self.hovered and self.pressed_inside:
                self.pressed_inside = False
                mixer.play_sound("effects/click1")
                return True
            self.pressed_inside = False
        return False

    def draw(self, renderer, asset_manager):
        if self.visible:
            # Draw Background
            color = (100, 100, 100, 100) if not (self.hovered and self.enabled) else (160, 160, 160, 100)
            renderer.draw_rect(self.rect, color)

            # Draw Text
            if self.text.content:
                font_cache = asset_manager.library["font_cache"]
                font_id = (str(self.text.font.path), self.text.font.size)
                if font_id not in font_cache:
                    font_cache[font_id] = pg.font.Font(self.text.font.path, self.text.font.size)
                font: pg.font.Font = font_cache[font_id]
                # Get size
                text_w, text_h = font.size(self.text.content)
                # Center text
                center_x = self.rect.x + (self.rect.width - text_w) / 2
                center_y = self.rect.y + (self.rect.height - text_h) / 2

                renderer.draw_text(
                    self.text,
                    asset_manager,
                    Vector2(center_x, center_y),
                    text_size_override=(text_w, text_h)
                )


class UITextureButton(UIButton):
    def __init__(self, rect: tuple[int, int, int, int], texture, draw_background=False):
        super().__init__(rect)
        self.texture: Texture2D | None = texture
        self.draw_background = draw_background

    def draw(self, renderer, asset_manager):
        if self.visible:
            # Calculate Center Of Button
            x, y, w, h = self.rect
            center_pos = Vector2(x + w / 2, y + h / 2)
            # Draw Texture in the Center
            renderer.draw_texture(
                self.texture,
                pos=center_pos,
                rotation=0.0,
                scale=Vector2(1.0, 1.0),
                position_mode="center",
            )
            # If: want to draw Rect Background
            if self.draw_background:
                color = (100, 100, 100, 100) if not (self.hovered and self.enabled) else (160, 160, 160, 100)
                renderer.draw_rect(self.rect, color)


class UILabel(UIElement):
    def __init__(self, position, text="", text_size=24, text_font=None, draw_background=False):
        super().__init__()
        self.position: Vector2 = Vector2(position)
        self.rect = pg.Rect(self.position.x, self.position.y, 0, 0)
        self.font = Font(text_font, text_size)
        self.text = Text(text, self.font)
        self.draw_background = draw_background

    def update(self, input_manager: InputManager, mixer: Mixer):  # Returns if pressed/not
        self.rect.x, self.rect.y = self.position.x, self.position.y

    def draw(self, renderer, asset_manager):
        if self.visible:
            if self.text.content:
                font_cache = asset_manager.library["font_cache"]
                font_id = (str(self.text.font.path), self.text.font.size)
                if font_id not in font_cache:
                    font_cache[font_id] = pg.font.Font(self.text.font.path, self.text.font.size)
                font: pg.font.Font = font_cache[font_id]
                # Get size
                text_w, text_h = font.size(self.text.content)

                # Update rect size
                self.rect.width = text_w
                self.rect.height = text_h

                # Draw Background
                if self.draw_background:
                    color = (100, 100, 100, 100)
                    renderer.draw_rect(self.rect, color)

                # Draw Text
                renderer.draw_text(
                    self.text,
                    asset_manager,
                    Vector2(self.rect.x, self.rect.y),
                    text_size_override=(text_w, text_h)
                )


class UITexture(UIElement):
    def __init__(self, texture, position, anchor="topleft"):
        super().__init__()
        self.texture = texture
        self.position: Vector2 = position
        self.anchor = anchor

    def draw(self, renderer, asset_manager):
        if self.visible:
            renderer.draw_texture(
                self.texture,
                pos=self.position,
                rotation=0.0,
                scale=Vector2(1.0, 1.0),
                position_mode=self.anchor,
            )


class Font:
    def __init__(self, path: Path | None, size: int):
        self.path = path
        self.size = size


class Text:
    def __init__(self, content: str, font: Font, color=(255, 255, 255, 255)):
        self.content = content
        self.font = font
        self.color = color
