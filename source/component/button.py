__author__ = 'marble_xu'

import pygame as pg
from .. import tool
from .. import constants as c

class Button():
    def __init__(self, x, y, name):
        self.name = name
        self.image = self.load_image()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def load_image(self):
        if self.name == c.NEXT_BUTTON:
            rect = (142, 365, 130, 100)
            scale = 0.54
        elif self.name == c.REPLAY_BUTTON:
            rect = (24, 4, 100, 100)
            scale = 0.6
        return tool.get_image(tool.GFX[c.BUTTON_IMG], *rect, c.BLACK, scale)

    def check_mouse_click(self, mouse_pos):
        x, y = mouse_pos
        if(x >= self.rect.x and x <= self.rect.right and
           y >= self.rect.y and y <= self.rect.bottom):
            return True
        return False

    def draw(self, surface):
        surface.blit(self.image, self.rect)