"""Obstacle: a static rectangular object that blocks the player."""

import pygame


class Obstacle:
    def __init__(self, x, y, width, height, color=(110, 110, 110)):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def get_rect(self):
        return self.rect
