import pygame as pg
from pygame import Vector2
from App.input import InputManager


class DebugCameraController:
    def __init__(self, input_manager: InputManager):
        self.input_manager = input_manager

    def get_movement(self) -> Vector2:
        movement = Vector2(0, 0)
        if self.input_manager.is_key_down(pg.K_i):
            movement.y += 1
        if self.input_manager.is_key_down(pg.K_k):
            movement.y -= 1
        if self.input_manager.is_key_down(pg.K_j):
            movement.x += 1
        if self.input_manager.is_key_down(pg.K_l):
            movement.x -= 1
        # Normalize it (Movement speed equalized in all directions)
        if movement.length_squared() > 0:
            movement = movement.normalize()

        return movement


class BlueController:
    def __init__(self, input_manager: InputManager):
        self.input_manager = input_manager

    def get_movement(self) -> Vector2:
        movement = Vector2(0, 0)
        if self.input_manager.is_key_down(pg.K_w):
            movement.y -= 1
        if self.input_manager.is_key_down(pg.K_s):
            movement.y += 1
        if self.input_manager.is_key_down(pg.K_a):
            movement.x -= 1
        if self.input_manager.is_key_down(pg.K_d):
            movement.x += 1
        # Normalize it (Movement speed equalized in all directions)
        if movement.length_squared() > 0:
            movement = movement.normalize()

        return movement

    def get_click(self) -> bool:
        if self.input_manager.is_key_down(pg.K_SPACE):
            return True
        return False


class RedController:
    def __init__(self, input_manager: InputManager):
        self.input_manager = input_manager

    def get_movement(self) -> Vector2:
        movement = Vector2(0, 0)
        if self.input_manager.is_key_down(pg.K_UP):
            movement.y -= 1
        if self.input_manager.is_key_down(pg.K_DOWN):
            movement.y += 1
        if self.input_manager.is_key_down(pg.K_LEFT):
            movement.x -= 1
        if self.input_manager.is_key_down(pg.K_RIGHT):
            movement.x += 1
        # Normalize it (Movement speed equalized in all directions)
        if movement.length_squared() > 0:
            movement = movement.normalize()

        return movement

    def get_click(self) -> bool:
        if self.input_manager.is_key_down(pg.K_m):
            return True
        return False
