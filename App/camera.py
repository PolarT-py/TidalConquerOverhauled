import pygame as pg
from pygame import Vector2
from App.input import InputManager
from App.debug import debug_print


debug_mode = False

class Camera2D:
    def __init__(self, start_position=None, smoothness=5):
        # Camera position is top-left
        self.offset = Vector2(start_position) if start_position is not None else Vector2(0, 0)
        # Where to go. Used for Camera Smoothing
        self.target_offset = Vector2(start_position) if start_position is not None else Vector2(0, 0)
        self.smoothing = True  # Camera Smoothing. Good for move() teleport type movements
        self.smoothness = smoothness

    def update(self, dt: float):
        if self.smoothing:
            self.offset += (self.target_offset - self.offset) * self.smoothness * dt
        debug_print(self.offset, debug_mode)

    def debug_update(self, dt: float, debug_movement=None, debug_camera_speed=500):
        if debug_movement is not None:
            self.slide(*debug_movement*debug_camera_speed*dt)

    def move(self, pos: Vector2, smoothness=5):
        self.smoothness = smoothness
        if self.smoothing:
            self.target_offset = pos
        else:
            self.offset = pos
            self.target_offset = pos  # Set here, so when re-enabling smoothing, it doesn't tweak out

    def slide(self, x, y):
        # Move x y amount from current position
        self.move(self.target_offset + Vector2(x, y))


class DebugCameraController:
    def __init__(self, input_manager: InputManager):
        self.input_manager = input_manager

    def get_movement(self) -> Vector2:
        movement = Vector2(0, 0)
        if  self.input_manager.is_key_down(pg.K_i):
            movement.y += 1
        if  self.input_manager.is_key_down(pg.K_k):
            movement.y -= 1
        if  self.input_manager.is_key_down(pg.K_j):
            movement.x += 1
        if  self.input_manager.is_key_down(pg.K_l):
            movement.x -= 1
        # Normalize it (Movement speed equalized in all directions)
        if movement.length_squared() > 0:
            movement = movement.normalize()

        return movement
