import pygame
import math

class bullet_class():
    def __init__(self, x, y, target_x, target_y, speed):
        self.x = x
        self.y = y
        angle = math.atan2(target_y-y, target_x-x)
        self.dx = math.cos(angle)*speed
        self.dy = math.sin(angle)*speed
        self.rect = None

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.rect = pygame.Rect(self.x, self.y, 2, 2)
