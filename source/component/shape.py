__author__ = 'marble_xu'

import pygame as pg
from .. import tool
from .. import constants as c

def create_shape(type, x, y):
    shape = None
    if type == c.BEAM:
        shape = Beam(x, y)
    elif type == c.COLUMN:
        shape = Column(x, y)
    return shape

class Shape():
    def __init__(self, x, y, name, life):
        self.name = name
        self.life = life

        self.load_images()
        self.setup_images()
        self.image = self.images[self.image_index]
        self.orig_image = self.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = y

    def load_images(self):
        pass

    def setup_images(self):
        '''image_threshold is used for change the image of the shape
           for 3 images of a shape, the values of image_threshold is [life, life//3 * 2, life//3]'''
        self.image_index = 0
        self.image_num = len(self.images)
        self.image_threshold = []
        for i in reversed(range(self.image_num)):
            i += 1
            temp_life = self.life//self.image_num * i
            self.image_threshold.append(temp_life)

    def set_physics(self, phy):
        self.phy = phy

    def update_position(self, x, y, image):
        self.rect.x = x
        self.rect.y = y
        self.image = image

    def set_damage(self, damage):
        self.life -= damage
        if self.life < self.image_threshold[self.image_index]:
            self.change_image()
            
    def change_image(self):
        if (self.image_index + 1) < self.image_num:
            self.image_index += 1
            self.image = self.orig_image = self.images[self.image_index]

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Beam(Shape):
    def __init__(self, x, y):
        Shape.__init__(self, x, y, c.BEAM, 6)

    def load_images(self):
        rect_list = [(251, 357, 86, 22), (337, 357, 86, 22), (337, 380, 86, 22)]
        self.images = []
        for rect in rect_list:
            self.images.append(tool.get_image(tool.GFX['wood'], *rect, c.BLACK, 1))

class Column(Shape):
    def __init__(self, x, y):
        Shape.__init__(self, x, y, c.COLUMN, 6)

    def load_images(self):
        rect_list = [(39, 252, 22, 84), (16, 336, 22, 84), (39, 336, 22, 84)]
        self.images = []
        for rect in rect_list:
            self.images.append(tool.get_image(tool.GFX['wood2'], *rect, c.BLACK, 1))