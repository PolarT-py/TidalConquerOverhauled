from __future__ import annotations
from pathlib import Path

import pygame as pg, pygame._sdl2.video as sdl2
from pygame import Vector2
from App.camera import Camera2D
from App.asset_manager import AssetManager
from App.ui import Text


class Texture2D:
    # Small wrapper for texture
    # Too lazy to remove
    def __init__(self, texture: sdl2.Texture, size: tuple[int, int]) -> None:
        self.texture = texture
        self.size = size
        self.texture.blend_mode = pg.BLENDMODE_BLEND  # Allows transparent textures

class Sprite2D:
    def __init__(
        self,
        texture,
        position=None,
        rotation=0.0,
        scale=None,
        origin=None,
        position_mode="topleft"  # topleft center topright
    ):
        self.texture = texture

        self.position = pg.Vector2(position) if position is not None else pg.Vector2(0, 0)
        self.scale = pg.Vector2(scale) if scale is not None else pg.Vector2(1, 1)
        self.origin = pg.Vector2(origin) if origin is not None else pg.Vector2(0.5, 0.5)

        self.position_mode = position_mode
        self.rotation = rotation


class Renderer:
    # Pygame-CE SDL2 Renderer
    def __init__(self, window_size: tuple[int, int], render_size: tuple[int, int],
                 main_title="Window", vsync=False, fullscreen=False, fps=60):
        # Set trackers
        self.is_fullscreen = fullscreen
        self.is_vsync = vsync
        self.fps = fps
        # Values
        self.FPS_OPTIONS = [30, 40, 60, 70, 80, 120, 144, 180, 240, 1000]
        # Set Window features
        self.virtual_size = render_size
        self.main_title = main_title
        # Make Window
        self.window = sdl2.Window(
            size=window_size,
            title=self.main_title,
            resizable=True,
        )
        if self.is_fullscreen:  # Don't need to set as windowed, it's windowed by default
            self.window.set_fullscreen()
        # Set Renderer
        self.renderer = sdl2.Renderer(self.window, vsync=vsync)
        self.renderer.draw_blend_mode = pg.BLENDMODE_BLEND  # Allow transparency in Rects and other shapes
        # Set Camera
        self.camera: Camera2D | None = None
        self.main_camera: Camera2D = Camera2D()

    def set_icon(self, icon):
        self.window.set_icon(icon)

    def set_vsync(self, value):
        # Set value
        # Restart game to apply
        # It applies when the game starts, and it grabs vsync from setting
        # Update tracker
        self.is_vsync = value

    def toggle_fullscreen(self):
        # Set value
        if self.is_fullscreen:
            self.window.set_windowed()
            self.window.size = (1280, 720)  # Set to a size
            self.window.position = sdl2.WINDOWPOS_CENTERED
        else:
            self.window.set_fullscreen(True)  # "True" here is desktop size, not Set fullscreen/not
        # Update tracker
        self.is_fullscreen = not self.is_fullscreen

    def set_camera(self, camera: Camera2D | None):
        self.camera = camera

    def reset_camera(self):
        self.camera = self.main_camera

    def window_to_virtual(self, pos):
        x, y = pos
        vx, vy, vw, vh, scale = self._get_letterbox()

        # Outside the virtual display
        if x < vx or x > vx + vw or y < vy or y > vy + vh:
            return None

        virtual_x = (x - vx) / scale
        virtual_y = (y - vy) / scale
        return pg.Vector2(virtual_x, virtual_y)

    def _get_letterbox(self):
        """
        Compute the centered rectangle where the virtual render area should appear.

        Returns:
            x, y, width, height, scale
        """
        ww, wh = self.window.size
        vw, vh = self.virtual_size

        # Pick the smaller scale so the whole virtual area fits inside the window
        # without stretching.
        scale = min(ww / vw, wh / vh)

        rw = int(vw * scale)
        rh = int(vh * scale)

        # Center the render area in the window.
        x = (ww - rw) // 2
        y = (wh - rh) // 2

        return x, y, rw, rh, scale

    def draw_bars(self, color=(0, 0, 0)):
        # Draw Black Bars around the Virtual Screen
        ww, wh = self.window.size
        x, y, w, h, _ = self._get_letterbox()

        self.renderer.draw_color = (*color, 255)

        # Top bar
        if y > 0:
            self.renderer.fill_rect((0, 0, ww, y))
        # Bottom bar
        bottom_h = wh - (y + h)
        if bottom_h > 0:
            self.renderer.fill_rect((0, y + h, ww, bottom_h))
        # Left bar
        if x > 0:
            self.renderer.fill_rect((0, y, x, h))
        # Right bar
        right_w = ww - (x + w)
        if right_w > 0:
            self.renderer.fill_rect((x + w, y, right_w, h))

    def set_color(self, color):
        self.renderer.draw_color = (*color, 255)

    def clear(self, color):
        # Clear the entire Window
        self.renderer.draw_color = (*color, 255)
        self.renderer.clear()

    def fill(self, color):
        # Fill only the Virtual area
        x, y, w, h, _ = self._get_letterbox()
        self.renderer.draw_color = (*color, 255)
        self.renderer.fill_rect((x, y, w, h))

    def load_texture(self, path: str | Path) -> Texture2D:
        # Load into a surface, then convert it into a SDL Texture (Then return Texture2D)
        surface = pg.image.load(path)
        width, height = surface.get_size()
        texture = sdl2.Texture.from_surface(self.renderer, surface)
        # Already uses NEAREST scaling
        return Texture2D(texture=texture, size=(width, height))

    def draw_texture(
            self,
            texture: Texture2D,
            pos,
            rotation: float = 0.0,
            scale=(1.0, 1.0),
            origin=(0.5, 0.5),
            position_mode: str = "topleft",
    ):
        # Draws Texture in Virtual Space

        # Get letterbox values
        vx, vy, _rw, _rh, letterbox_scale = self._get_letterbox()

        # Set Draw positions and Apply camera
        x, y = pos

        if self.camera is not None:
            x += self.camera.offset.x
            y += self.camera.offset.y

        tw, th = texture.size

        # Support both scalar scale and (x, y) scale.
        if isinstance(scale, (int, float)):
            sx = sy = float(scale)
        else:
            sx, sy = scale

        # Size in VIRTUAL space after scaling.
        scaled_w = tw * sx
        scaled_h = th * sy

        # Set position mode
        if position_mode == "center":
            x -= scaled_w / 2
            y -= scaled_h / 2
        elif position_mode != "topleft":
            raise ValueError(f'Invalid position_mode: {position_mode}\nAccepted modes: "topleft" "center"')

        # Convert from Virtual space to Window space.
        window_x = vx + x * letterbox_scale
        window_y = vy + y * letterbox_scale
        window_w = scaled_w * letterbox_scale
        window_h = scaled_h * letterbox_scale

        # SDL2 origin is in destination-rect pixels (not normalized 0..1 values)
        origin_px = (window_w * origin[0], window_h * origin[1])

        # Actually draw it
        texture.texture.draw(
            dstrect=(window_x, window_y, window_w, window_h),
            angle=rotation,
            origin=origin_px,
        )

    def draw_sprite(self, sprite):
        self.draw_texture(
            texture=sprite.texture,
            pos=sprite.position,
            rotation=sprite.rotation,
            scale=sprite.scale,
            origin=sprite.origin,
            position_mode=sprite.position_mode,
        )

    def draw_rect_window(self, rect, color):
        self.renderer.draw_color = color
        self.renderer.fill_rect(rect)

    def draw_rect(self, rect, color):
        """
        Draw a solid rectangle in virtual coordinates.

        This uses the same virtual-space-to-window-space conversion as textures.
        """
        vx, vy, _vw, _vh, scale = self._get_letterbox()

        x, y, w, h = rect

        # Apply Camera
        if self.camera is not None:
            x += self.camera.offset.x
            y += self.camera.offset.y

        # Convert from virtual space into actual window space.
        x = vx + x * scale
        y = vy + y * scale
        w *= scale
        h *= scale

        self.draw_rect_window((x, y, w, h), color)

    def draw_text(
            self,
            text_obj: Text,
            asset_manager: AssetManager,
            position: Vector2,
            text_size_override: tuple[int, int] | None = None,
            position_mode: str = "topleft",
    ):
        # Check cache
        font_cache = asset_manager.library["font_cache"]
        font_id = (str(text_obj.font.path), text_obj.font.size)
        if font_id not in font_cache:
            font_cache[font_id] = pg.font.Font(text_obj.font.path, text_obj.font.size)
        font: pg.font.Font = font_cache[font_id]
        # Render font
        rendered_surface = font.render(text_obj.content, False, text_obj.color)
        # Use override if provided
        if text_size_override is not None:
            rendered_size = text_size_override
        else:
            rendered_size = rendered_surface.get_size()
        # Anchor it based on position mode
        tw, th = rendered_size
        x, y = position
        if position_mode == "center":
            x -= tw / 2
            y -= th / 2
        elif position_mode == "topright":
            x -= tw
        elif position_mode != "topleft":
            raise ValueError(f'Invalid position_mode: {position_mode}')
        # Draw it
        font_texture = sdl2.Texture.from_surface(self.renderer, rendered_surface)
        self.draw_texture(Texture2D(font_texture, rendered_size), Vector2(x, y))
