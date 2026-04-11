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
    def __init__(self,
            renderer: Renderer,
            asset_manager: AssetManager,
            mixer: Mixer,
            input_manager: InputManager,
            use_camera=False,
            enabled=True
        ):
        self.id = None
        self.rect = None
        self.visible = True
        self.enabled = enabled
        self.use_camera = use_camera
        self.renderer = renderer
        self.asset_manager = asset_manager
        self.mixer = mixer
        self.input_manager = input_manager

    def update(self, dt):
        pass

    def draw(self):
        pass


class UIScene:
    def __init__(self, name):
        self.name = name
        self.elements = []
        self.visible = True

    def get(self, e_id):
        for e in self.elements:
            if e.id == e_id:
                return e
        return None

    def call_ui_beginning_functions(self, settings):  # Run at start of game
        for e in self.elements:
            if e.id == "vsync_toggle_button":
                e.text.content = f"Vsync:                  {str(settings.main.vsync)}"
            elif e.id == "fps_change_button":
                e.text.content = f"FPS:                    {str(settings.main.fps)}"
            elif e.id == "fullscreen_toggle_button":
                if settings.main.fullscreen:  # Fullscreen
                    e.text.content = f"Display Mode: Fullscreen"
                else:  # Windowed
                    e.text.content = f"Display Mode: Windowed"

    def update_all(self, dt):
        activated = []
        # Search through all Elements to see which ones have been activated
        for e in self.elements:
            if e.update(dt):
                activated.append(e)
        return activated

    def draw_all(self):
        if self.visible:
            for e in self.elements:
                e.draw()


class SceneManager:
    def __init__(self, scenes: dict[str, UIScene], start_scene: str):
        if start_scene not in scenes:
            raise ValueError(f"Scene '{start_scene}' does not exist.")
        self.scenes: dict[str, UIScene] = scenes
        self.current_scene_name: str = start_scene
        self.current_scene: UIScene = scenes[start_scene]

    def call_ui_beginning_functions(self, settings):
        for scene in self.scenes.values():
            scene.call_ui_beginning_functions(settings)

    def set_scene(self, scene_name: str, mixer=None):
        if scene_name not in self.scenes:
            raise ValueError(f"Scene '{scene_name}' does not exist.")
        self.current_scene_name = scene_name
        self.current_scene = self.scenes[scene_name]
        if mixer is not None:
            mixer.play_sound("effects/whoosh")

    def update(self, dt):
        return self.current_scene.update_all(dt)

    def draw(self):
        self.current_scene.draw_all()

    def get(self, element_id: str):
        for e in self.current_scene.elements:
            if e.id == element_id:
                return e
        return None

    def get_from_all(self, element_id: str):
        for scene in self.scenes.values():
            for e in scene.elements:
                if e.id == element_id:
                    return e
        return None


class UIButton(UIElement):
    def __init__(self,
                 rect: tuple[int, int, int, int],
                 renderer: Renderer,
                 asset_manager: AssetManager,
                 mixer: Mixer,
                 input_manager: InputManager,
                 text="",
                 text_size=24,
                 text_font=None,
                 position_mode="topleft",
                 use_camera=False,
                 shadow=True,
                 enabled=True):
        super().__init__(renderer, asset_manager, mixer, input_manager, enabled)
        self.rect = pg.Rect(rect)
        self.hovered = False
        self.pressed_inside = False
        self.font = Font(text_font, text_size)
        self.text = Text(text, self.font)
        self.use_camera = use_camera
        self.position_mode = position_mode
        self.shadow = shadow

    def update_others(self, dt):  # For other classes
        pass

    def update(self, dt, custom_cursor=None, camera=None):  # Returns if pressed/not
        # Fetch Mouse Position
        mouse_position = self.input_manager.mouse_pos_virtual
        if mouse_position is None:
            self.hovered = False
            return False  # Mouse position Out of Virtual Space
        mx, my = mouse_position

        # Fetch custom Cursor Position
        if custom_cursor is not None:
            cx, cy = custom_cursor.position + camera.offset
        else:
            cx, cy = Vector2(-10000000000, -10000000000)

        # Set click states
        mouse_clicked = self.input_manager.was_mouse_pressed(1)
        custom_cursor_clicked = False if custom_cursor is None else custom_cursor.has_normal_click()

        # Check if it's enabled
        if not self.enabled:
            return False

        # Check hover
        new_rect = self.get_draw_rect()
        if self.use_camera:  # Use Main camera
            new_rect.x += self.renderer.main_camera.offset.x
            new_rect.y += self.renderer.main_camera.offset.y

        mouse_hovered = new_rect.collidepoint(mx, my)
        custom_hovered = False if custom_cursor is None else new_rect.collidepoint(cx, cy)

        self.hovered = mouse_hovered or custom_hovered

        # Check if pressed by matching input source
        if (mouse_hovered and mouse_clicked) or (custom_hovered and custom_cursor_clicked):
            self.mixer.play_sound("effects/click1")
            self.update_others(dt)
            return True

        self.update_others(dt)
        return False

    def get_draw_rect(self):
        x, y, w, h = self.rect

        if self.position_mode == "center":
            x -= w / 2
            y -= h / 2
        elif self.position_mode == "topright":
            x -= w
        elif self.position_mode != "topleft":
            raise ValueError(f"Invalid position_mode: {self.position_mode}")

        return pg.Rect(x, y, w, h)

    def draw(self):
        if self.visible:
            # Get draw Rect
            draw_rect = self.get_draw_rect()

            if self.use_camera:
                self.renderer.camera = self.renderer.main_camera
            else:
                self.renderer.camera = None

            # Draw Background
            color = (100, 100, 100, 100) if not (self.hovered and self.enabled) else (160, 160, 160, 100)
            self.renderer.draw_rect(draw_rect, color)

            # Cache Font and Draw Text
            if self.text.content:
                font_cache = self.asset_manager.library["font_cache"]
                font_id = (str(self.text.font.path), self.text.font.size)
                if font_id not in font_cache:
                    font_cache[font_id] = pg.font.Font(self.text.font.path, self.text.font.size)
                font: pg.font.Font = font_cache[font_id]
                # Get size
                text_w, text_h = font.size(self.text.content)
                # Center text
                center_x = draw_rect.x + (draw_rect.width - text_w) / 2
                center_y = draw_rect.y + (draw_rect.height - text_h) / 2

                # Draw Shadow
                color = self.text.color
                if self.shadow:
                    self.text.color = (0, 0, 0, 155)
                    self.renderer.draw_text(
                        self.text,
                        self.asset_manager,
                        Vector2(center_x, center_y+2),
                        text_size_override=(text_w, text_h)
                    )
                self.text.color = color
                self.renderer.draw_text(
                    self.text,
                    self.asset_manager,
                    Vector2(center_x, center_y),
                    text_size_override=(text_w, text_h)
                )
            # If disabled, draw extra layer of rect for darkness
            if not self.enabled:
                self.renderer.draw_rect(draw_rect, (0, 0, 0, 100))


class UITextureButton(UIButton):
    def __init__(self,
                 renderer: Renderer,
                 asset_manager: AssetManager,
                 mixer: Mixer,
                 input_manager: InputManager,
                 rect: tuple[int, int, int, int],
                 texture,
                 draw_background=False,
                 position_mode="topleft",
                 use_camera=False,
                 enabled=True,
                 scale=Vector2(1.0, 1.0)):
        super().__init__(rect, renderer, asset_manager, mixer, input_manager, enabled=enabled)
        self.texture: Texture2D | None = texture
        self.draw_background = draw_background
        self.position_mode = position_mode
        self.use_camera = use_camera
        self.scale = scale

    def draw(self):
        if self.visible:
            # Calculate Center Of Button
            draw_rect = self.get_draw_rect()
            x, y, w, h = draw_rect

            if self.use_camera:
                self.renderer.camera = self.renderer.main_camera
            else:
                self.renderer.camera = None
            center_pos = Vector2(x + w / 2, y + h / 2)

            # Draw Texture in the Center
            self.renderer.draw_texture(
                self.texture,
                pos=center_pos,
                rotation=0.0,
                scale=self.scale,
                position_mode="center"
            )
            # If: want to draw Rect Foreground (Debug/Hitbox Check)
            if self.draw_background or not self.enabled:
                color = (100, 100, 100, 100) if not (self.hovered and self.enabled) else (160, 160, 160, 100)
                self.renderer.draw_rect(draw_rect, color)


class UILabel(UIElement):
    def __init__(self,
                 position,
                 text,
                 renderer: Renderer,
                 asset_manager: AssetManager,
                 mixer: Mixer,
                 input_manager: InputManager,
                 text_size=24,
                 text_font=None,
                 draw_background=False,
                 position_mode="topleft",
                 use_camera=False,
                 shadow=True,
                 do_cache=True):
        super().__init__(renderer, asset_manager, mixer, input_manager)
        self.position: Vector2 = Vector2(position)
        self.rect = pg.Rect(self.position.x, self.position.y, 0, 0)
        self.font = Font(text_font, text_size)
        self.text = Text(text, self.font)
        self.draw_background = draw_background
        self.position_mode = position_mode
        self.use_camera = use_camera
        self.shadow = shadow
        self.do_cache = do_cache

    def update_rect(self, text_w, text_h):
        x, y = self.position.x, self.position.y

        if self.position_mode == "center":
            x -= text_w / 2
            y -= text_h / 2
        elif self.position_mode == "topright":
            x -= text_w
        elif self.position_mode != "topleft":
            raise ValueError(f"Invalid position_mode: {self.position_mode}")

        self.rect.x = x
        self.rect.y = y
        self.rect.width = text_w
        self.rect.height = text_h

    def draw(self):
        if self.visible:
            if self.text.content:
                font_cache = self.asset_manager.library["font_cache"]
                font_id = (str(self.text.font.path), self.text.font.size)
                if font_id not in font_cache:
                    font_cache[font_id] = pg.font.Font(self.text.font.path, self.text.font.size)
                font: pg.font.Font = font_cache[font_id]
                # Get size
                text_w, text_h = font.size(self.text.content)

                # Update rect size
                self.update_rect(text_w, text_h)

                # Draw Background
                if self.draw_background:
                    if self.use_camera:
                        self.renderer.camera = self.renderer.main_camera
                    else:
                        self.renderer.camera = None
                    color = (100, 100, 100, 100)
                    self.renderer.draw_rect(self.rect, color)

                # Apply Camera/ or Not
                if self.use_camera:
                    self.renderer.camera = self.renderer.main_camera
                else:
                    self.renderer.camera = None
                # Draw Shadow
                color = self.text.color
                if self.shadow:
                    self.text.color = (0, 0, 0, 155)
                    self.renderer.draw_text(
                        self.text,
                        self.asset_manager,
                        self.position - Vector2(0, -2),
                        text_size_override=(text_w, text_h),
                        position_mode=self.position_mode,
                        do_cache=self.do_cache,
                    )
                # Draw Text
                self.text.color = color
                self.renderer.draw_text(
                    self.text,
                    self.asset_manager,
                    self.position,
                    text_size_override=(text_w, text_h),
                    position_mode=self.position_mode,
                    do_cache=self.do_cache,
                )


class UITexture(UIElement):
    def __init__(self,
                 texture,
                 position,
                 renderer: Renderer,
                 asset_manager: AssetManager,
                 mixer: Mixer,
                 input_manager: InputManager,
                 position_mode="topleft",
                 use_camera=False):
        super().__init__(renderer, asset_manager, mixer, input_manager)
        self.texture = texture
        self.position: Vector2 = position
        self.position_mode = position_mode
        self.use_camera = use_camera

    def draw(self):
        if self.visible:
            if self.use_camera:
                self.renderer.camera = self.renderer.main_camera
            else:
                self.renderer.camera = None
            self.renderer.draw_texture(
                self.texture,
                pos=self.position,
                rotation=0.0,
                scale=Vector2(1.0, 1.0),
                position_mode=self.position_mode,
            )


class UIRadioButtonGroup:
    def __init__(self, selected: str | None, renderer: Renderer):
        self.elements: dict[str, UIRadioButton] = {}
        self.selected_key: str | None = selected
        self.renderer = renderer

    def __getitem__(self, key):
        return self.elements[key]

    def __iter__(self):
        return iter(self.elements.values())

    def __len__(self):
        return len(self.elements)

    def add(self, key, value):
        # Sets key to value
        self.elements[key] = value
        # Selects the key
        if self.selected_key == key:  # If self.selected_key matches key, set it (Used for init)
            self.select(key)
        elif self.selected_key is None:  # If there's no selected key already, set it as selected
            self.select(key)

    def select(self, key: str):
        # Sets key to selected
        self.selected_key = key
        for k, btn in self.elements.items():  # Loop and Set matching key to be selected
            btn.selected = (k == key)

    def update(self, dt, custom_cursor=None, camera=None) -> UIRadioButton | None:
        for key, radio_button in self.elements.items():
            if radio_button.update(dt, custom_cursor, camera):
                self.select(key)
                return radio_button  # Return activated button
        return None

    def draw_all(self):
        for radio_button in self:
            radio_button.draw()


class UIRadioButton(UITextureButton):  # Radio button, but specifically for boat selector (For ease of use)
    def __init__(self,
                 renderer: Renderer,
                 asset_manager: AssetManager,
                 mixer: Mixer,
                 input_manager: InputManager,
                 rect: tuple[int, int, int, int],  # (64, 64, 64, 64)
                 texture,
                 icon,
                 label,
                 scale=Vector2(1.0, 1.0),
                 draw_background=False,
                 position_mode="topleft",
                 use_camera=False):
        super().__init__(renderer, asset_manager, mixer, input_manager, rect, texture,
                         draw_background, position_mode, use_camera)
        self.texture_on: Texture2D = self.asset_manager.get("textures", "buttons/selected_button")
        self.texture_off: Texture2D = self.asset_manager.get("textures", "buttons/button")
        self.texture: Texture2D = self.texture_off
        self.icon: Texture2D = asset_manager.get("textures", icon)
        self.label: UILabel = label
        self.label.position_mode = "center"
        self.label.position = Vector2(self.rect.x, self.rect.y - 38)
        self.label.font = Font(asset_manager.get("fonts", "PirataOne"), 28)
        self.label.text.font = self.label.font
        self.label.use_camera = True
        self.selected = False
        self.scale = scale

    def update_others(self, dt):
        self.label.update(dt)

    def draw(self):
        if self.visible:
            # Calculate Center Of Button
            draw_rect = self.get_draw_rect()
            x, y, w, h = draw_rect

            if self.use_camera:
                self.renderer.camera = self.renderer.main_camera
            else:
                self.renderer.camera = None
            center_pos = Vector2(x + w / 2, y + h / 2)

            # Update Texture
            self.texture = self.texture_on if self.selected else self.texture_off

            # Draw Button Texture in the Center
            self.renderer.draw_texture(
                self.texture,
                pos=center_pos,
                rotation=0.0,
                scale=Vector2(1.4, 1.4) if self.selected else Vector2(1.28, 1.28),  # Bigger if selected
                position_mode="center",
            )
            # Draw Icon Texture in the Center
            base_scale = Vector2(0.27, 0.27) if self.selected else Vector2(0.25, 0.25)
            scale = base_scale * self.scale  # Bigger if selected
            self.renderer.draw_texture(
                self.icon,
                pos=center_pos,
                rotation=0.0,
                scale=scale,
                position_mode="center",
            )
            # Draw money label
            self.label.draw()
            # If: want to draw Rect Foreground (Debug/Hitbox Check)
            if self.draw_background:
                color = (100, 100, 100, 100) if not (self.hovered and self.enabled) else (160, 160, 160, 100)
                self.renderer.draw_rect(draw_rect, color)


class Font:
    def __init__(self, path: Path | None, size: int):
        self.path = path
        self.size = size


class Text:
    def __init__(self, content: str, font: Font, color=(255, 255, 255, 255)):
        self.content = content
        self.font = font
        self.color = color
