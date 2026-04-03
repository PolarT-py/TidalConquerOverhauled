from __future__ import annotations
from pathlib import Path

import moderngl
import numpy as np
import pygame


# I just wanted to say, I did NOT make Tism part. 💔

class Texture2D:
    """Small wrapper around a GPU texture plus its original pixel size."""

    def __init__(self, texture: moderngl.Texture, size: tuple[int, int]) -> None:
        self.texture = texture
        self.size = size


class Renderer:
    """
    ModernGL renderer for a fixed virtual resolution.

    The game draws in virtual coordinates (for example 1280x720), then this
    renderer maps that virtual space into the actual window while preserving
    aspect ratio and adding letterboxing when needed.
    """

    def __init__(self, window_size: tuple[int, int], render_size: tuple[int, int]) -> None:
        self.window_size = window_size
        self.virtual_size = render_size

        # Get the active OpenGL context created by pygame.
        self.ctx = moderngl.create_context()

        # Enable alpha blending so transparent textures render properly.
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = (
            moderngl.SRC_ALPHA,
            moderngl.ONE_MINUS_SRC_ALPHA,
        )

        # Shader program for textured quads (sprites/images).
        self.program = self.ctx.program(
            vertex_shader="""
                #version 330

                in vec2 in_position;
                in vec2 in_uv;

                out vec2 v_uv;

                void main() {
                    gl_Position = vec4(in_position, 0.0, 1.0);
                    v_uv = in_uv;
                }
            """,
            fragment_shader="""
                #version 330

                uniform sampler2D u_texture;

                in vec2 v_uv;
                out vec4 fragColor;

                void main() {
                    fragColor = texture(u_texture, v_uv);
                }
            """,
        )

        # Vertex buffer for one textured quad.
        # 6 vertices = 2 triangles
        # 4 floats per vertex = x, y, u, v
        self.vbo = self.ctx.buffer(reserve=6 * 4 * 4)
        self.vao = self.ctx.vertex_array(
            self.program,
            [(self.vbo, "2f 2f", "in_position", "in_uv")],
        )

        # Separate shader program for solid-color rectangles.
        self.color_program = self.ctx.program(
            vertex_shader="""
                #version 330

                in vec2 in_position;

                void main() {
                    gl_Position = vec4(in_position, 0.0, 1.0);
                }
            """,
            fragment_shader="""
                #version 330

                uniform vec3 u_color;
                out vec4 fragColor;

                void main() {
                    fragColor = vec4(u_color, 1.0);
                }
            """,
        )

        # Vertex buffer for one solid rectangle.
        # 6 vertices, 2 floats each = x, y
        self.rect_vbo = self.ctx.buffer(reserve=6 * 2 * 4)
        self.rect_vao = self.ctx.vertex_array(
            self.color_program,
            [(self.rect_vbo, "2f", "in_position")],
        )

    def set_window_size(self, size: tuple[int, int]) -> None:
        """Update the renderer when the window is resized."""
        self.window_size = size
        self.ctx.viewport = (0, 0, size[0], size[1])

    def _get_letterbox(self):
        """
        Compute the centered rectangle where the virtual render area should appear.

        Returns:
            x, y, width, height, scale
        """
        ww, wh = self.window_size
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

    def _apply_scissor(self):
        """
        Clip drawing so nothing can render outside the virtual game area.

        ModernGL/OpenGL scissor coordinates use a bottom-left origin, so the Y
        value has to be converted from our top-left style window math.
        """
        x, y, w, h, _scale = self._get_letterbox()
        _window_width, window_height = self.window_size

        scissor_y = window_height - (y + h)
        self.ctx.scissor = (x, scissor_y, w, h)

    def clear(self, color):
        """Clear the entire window, including the letterbox bars."""
        r, g, b = color
        self.ctx.viewport = (0, 0, *self.window_size)
        self.ctx.clear(r / 255.0, g / 255.0, b / 255.0, 1.0)

    def fill(self, color):
        """Fill only the virtual render area, not the outer bars."""
        x, y, w, h, _ = self._get_letterbox()
        self.draw_rect_window((x, y, w, h), color)

    def load_texture(self, path: str | Path) -> Texture2D:
        """
        Load an image with pygame, convert it to RGBA bytes, and upload it to GPU.
        """
        surface = pygame.image.load(path).convert_alpha()
        width, height = surface.get_size()

        # Pygame image data is effectively upside down for OpenGL texture UVs,
        # so flip vertically before uploading.
        flipped = pygame.transform.flip(surface, False, True)
        data = pygame.image.tobytes(flipped, "RGBA", False)

        texture = self.ctx.texture((width, height), 4, data)

        # NEAREST keeps scaling crisp instead of blurry.
        texture.filter = (moderngl.NEAREST, moderngl.NEAREST)

        return Texture2D(texture=texture, size=(width, height))

    def draw_texture(self, texture: Texture2D, pos):
        """
        Draw a texture using virtual coordinates.

        `pos` is in virtual-space pixels, not real window pixels.
        """
        self._apply_scissor()
        vx, vy, _vw, _vh, scale = self._get_letterbox()

        x, y = pos
        tw, th = texture.size

        # Convert from virtual-space pixels into actual window-space pixels.
        x = vx + x * scale
        y = vy + y * scale
        tw *= scale
        th *= scale

        ww, wh = self.window_size

        # Convert window pixel coordinates into OpenGL clip space [-1, 1].
        left = (x / ww) * 2.0 - 1.0
        right = ((x + tw) / ww) * 2.0 - 1.0

        # Screen Y grows downward, but OpenGL Y grows upward, so this is flipped.
        top = 1.0 - (y / wh) * 2.0
        bottom = 1.0 - ((y + th) / wh) * 2.0

        # Two triangles forming one textured quad.
        vertices = np.array([
            left,  top,    0.0, 1.0,
            right, top,    1.0, 1.0,
            left,  bottom, 0.0, 0.0,

            right, top,    1.0, 1.0,
            right, bottom, 1.0, 0.0,
            left,  bottom, 0.0, 0.0,
        ], dtype="f4")

        self.vbo.write(vertices.tobytes())
        texture.texture.use(0)
        self.program["u_texture"] = 0
        self.vao.render(moderngl.TRIANGLES)

        # Disable clipping after this draw call so later window-space operations
        # can choose whether to use scissoring or not.
        self.ctx.scissor = None

    def draw_rect_window(self, rect, color):
        """
        Draw a solid rectangle directly in real window coordinates.

        This is useful for UI, overlays, or filling the letterboxed render area.
        """
        x, y, w, h = rect
        ww, wh = self.window_size

        # Convert window-space pixels into clip space.
        left = (x / ww) * 2.0 - 1.0
        right = ((x + w) / ww) * 2.0 - 1.0

        top = 1.0 - (y / wh) * 2.0
        bottom = 1.0 - ((y + h) / wh) * 2.0

        vertices = np.array([
            left,  top,
            right, top,
            left,  bottom,

            right, top,
            right, bottom,
            left,  bottom,
        ], dtype="f4")

        self.rect_vbo.write(vertices.tobytes())

        r, g, b = color
        self.color_program["u_color"] = (r / 255.0, g / 255.0, b / 255.0)

        self.rect_vao.render(moderngl.TRIANGLES)

    def draw_rect(self, rect, color):
        """
        Draw a solid rectangle in virtual coordinates.

        This uses the same virtual-space-to-window-space conversion as textures.
        """
        vx, vy, _vw, _vh, scale = self._get_letterbox()

        x, y, w, h = rect

        # Convert from virtual space into actual window space.
        x = vx + x * scale
        y = vy + y * scale
        w *= scale
        h *= scale

        self.draw_rect_window((x, y, w, h), color)
