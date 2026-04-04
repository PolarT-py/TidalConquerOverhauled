from __future__ import annotations
from pathlib import Path

import pygame, pygame._sdl2.video as sdl2
from App.camera import Camera2D


class Texture2D:
    # Small wrapper for texture
    # Too lazy to remove
    def __init__(self, texture: sdl2.Texture, size: tuple[int, int]) -> None:
        self.texture = texture
        self.size = size

class Sprite2D:
    def __init__(
        self,
        texture,
        position=None,
        rotation=0.0,
        scale=None,
        origin=None,
        position_mode="topleft"
    ):
        self.texture = texture

        self.position = pygame.Vector2(position) if position is not None else pygame.Vector2(0, 0)
        self.scale = pygame.Vector2(scale) if scale is not None else pygame.Vector2(1, 1)
        self.origin = pygame.Vector2(origin) if origin is not None else pygame.Vector2(0.5, 0.5)

        self.position_mode = position_mode
        self.rotation = rotation


class Renderer:
    # Pygame-CE SDL2 Renderer
    def __init__(self, window_size: tuple[int, int], render_size: tuple[int, int], main_title="Window") -> None:
        # Set Window features
        self.virtual_size = render_size
        self.main_title = main_title
        # Make Window
        self.window = sdl2.Window(
            size=window_size,
            title=self.main_title,
            resizable=True,
        )
        # Set Renderer
        self.renderer = sdl2.Renderer(self.window, vsync=True)
        # Set Camera
        self.camera: Camera2D | None = None

    def set_camera(self, camera: Camera2D):
        self.camera = camera

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
        surface = pygame.image.load(path)
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
        self.renderer.draw_color = (*color, 255)
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
