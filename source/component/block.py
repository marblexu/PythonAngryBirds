__author__ = 'marble_xu'

import pygame as pg
from .. import tool
from .. import constants as c

def create_block(x, y, material, shape, type, direction=0):
    block = None
    if material == c.GLASS:
        if shape == c.BEAM:
            block = BeamGlass(x, y, type, direction)
        elif shape == c.CIRCLE:
            block = CircleGlass(x, y, type)
    elif material == c.WOOD:
        if shape == c.BEAM:
            block = BeamWood(x, y, type, direction)
        elif shape == c.CIRCLE:
            block = CircleWood(x, y, type)
    elif material == c.STONE:
        if shape == c.BEAM:
            block = BeamStone(x, y, type, direction)
        elif shape == c.CIRCLE:
            block = CircleStone(x, y, type)
    return block

def get_block_mass(name, type):
    mass = base = 1.0
    if name == c.BEAM:
        if type == c.BEAM_TYPE_1:  # the shortest length
            mass = base
        elif type == c.BEAM_TYPE_2:
            mass = base * 2
        elif type == c.BEAM_TYPE_3:
            mass = base * 4
        elif type == c.BEAM_TYPE_4: # the longest length
            mass = base * 5
        elif type == c.BEAM_TYPE_5: # the thick one
            mass = base * 4
        elif type == c.BEAM_TYPE_6: # the square
            mass = base * 2
    elif name == c.CIRCLE:
        if type == c.CIRCLE_TYPE_1: # the small circle
            mass = base * 1.6
        elif type == c.BEAM_TYPE_2: # the big circle
            mass = base * 6.4

    return mass

class Block():
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

    def get_rect_list(self):
        pass

    def setup_images(self):
        '''image_threshold is used for change the image of the shape
           for 4 images of a shape, the values of image_threshold is [life, life//4 * 3, life//2, life//4]'''
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

class Beam(Block):
    def __init__(self, x, y, life, direction):
        self.direction =  direction
        Block.__init__(self, x, y, c.BEAM, life)

    def load_images(self):
        rect_list = self.get_rect_list()
        self.images = []
        for rect in rect_list:
            image = tool.get_image(tool.GFX[c.BLOCK_SHEET], *rect, c.BLACK, 1)
            if self.direction == c.VERTICAL:
                image = pg.transform.rotate(image, 90)
            self.images.append(image)

class BeamGlass(Beam):
    def __init__(self, x, y, type, direction):
        self.type = type
        Beam.__init__(self, x, y, 4, direction)
        self.mass = get_block_mass(self.name, self.type) * c.GLASS_MASS_TIMES

    def get_rect_list(self):
        if self.type == c.BEAM_TYPE_1: # the shortest length
            rect_list = [(  2, 718, 38, 18), ( 86, 718, 38, 18),
                         (622, 661, 38, 18), (622, 638, 38, 18)]
        elif self.type == c.BEAM_TYPE_2:
            rect_list = [(708, 332, 80, 18), (415, 705, 80, 18),
                         (500, 705, 80, 18), (622, 551, 80, 18)]
        elif self.type == c.BEAM_TYPE_3:
            rect_list = [(622, 375, 160, 18), (622, 397, 160, 18),
                         (622, 419, 160, 18), (622, 441, 160, 18)]
        elif self.type == c.BEAM_TYPE_4: # the longest length
            rect_list = [(501, 332, 200, 18), (415, 375, 200, 18),
                         (415, 397, 200, 18), (415, 419, 200, 18),]
        elif self.type == c.BEAM_TYPE_5: # the thick one
            rect_list = [(330, 246, 80, 39), (415, 246, 80, 39),
                         (500, 246, 80, 39), (585, 246, 80, 39)]
        elif self.type == c.BEAM_TYPE_6: # the square
            rect_list = [(252, 591, 39, 39), (252, 634, 39, 39),
                         (252, 677, 39, 39), (330, 418, 39, 39)]
        return rect_list

class BeamWood(Beam):
    def __init__(self, x, y, type, direction):
        self.type = type
        Beam.__init__(self, x, y, 12, direction)
        self.mass = get_block_mass(self.name, self.type) * c.WOOD_MASS_TIMES

    def get_rect_list(self):
        if self.type == c.BEAM_TYPE_1: # the shortest length
            rect_list = [(622, 706, 38, 18), (707, 640, 38, 18),
                         (750, 640, 38, 18), (707, 662, 38, 18)]
        elif self.type == c.BEAM_TYPE_2:
            rect_list = [(707, 552, 80, 18), (622, 574, 80, 18),
                         (707, 574, 80, 18), (622, 596, 80, 18)]
        elif self.type == c.BEAM_TYPE_3:
            rect_list = [(622, 464, 160, 18), (622, 486, 160, 18),
                         (622, 508, 160, 18), (622, 530, 160, 18)]
        elif self.type == c.BEAM_TYPE_4: # the longest length
            rect_list = [(415, 464, 200, 18), (415, 464, 200, 18),
                         (415, 486, 200, 18), (415, 508, 200, 18)]
        elif self.type == c.BEAM_TYPE_5: # the thick one
            rect_list = [(670, 247, 80, 38), (330, 290, 80, 38),
                         (415, 290, 80, 38), (500, 290, 80, 38)]
        elif self.type == c.BEAM_TYPE_6: # the square
            rect_list = [(330, 462, 38, 38), (330, 505, 38, 38),
                         (330, 548, 38, 38), (330, 591, 38, 38)]
        return rect_list

class BeamStone(Beam):
    def __init__(self, x, y, type, direction):
        self.type = type
        Beam.__init__(self, x, y, 48, direction)
        self.mass = get_block_mass(self.name, self.type) * c.STONE_MASS_TIMES

    def get_rect_list(self):
        if self.type == c.BEAM_TYPE_1: # the shortest length
            rect_list = [(750, 662, 38, 18), (707, 684, 38, 18),
                         (750, 684, 38, 18), (707, 706, 38, 18)]
        elif self.type == c.BEAM_TYPE_2:
            rect_list = [(707, 596, 80, 18), (622, 618, 80, 18),
                         (707, 618, 80, 18), (622, 640, 80, 18)]
        elif self.type == c.BEAM_TYPE_3:
            rect_list = [(415, 618, 160, 18), (415, 640, 160, 18),
                         (415, 662, 160, 18), (415, 684, 160, 18)]
        elif self.type == c.BEAM_TYPE_4: # the longest length
            rect_list = [(415, 530, 200, 18), (415, 553, 200, 18),
                         (415, 574, 200, 18), (415, 596, 200, 18)]
        elif self.type == c.BEAM_TYPE_5: # the thick one
            rect_list = [(585, 290, 80, 38), (670, 290, 80, 38),
                         (330, 333, 80, 38), (330, 376, 80, 38)]
        elif self.type == c.BEAM_TYPE_6: # the square
            rect_list = [(330, 634, 38, 38), (330, 677, 38, 38),
                         (415, 333, 38, 38), (458, 333, 38, 38)]
        return rect_list

class Circle(Block):
    def __init__(self, x, y, life):
        Block.__init__(self, x, y, c.CIRCLE, life)
        self.mass = get_block_mass(self.name, self.type)

    def load_images(self):
        rect_list = self.get_rect_list()
        self.images = []
        for rect in rect_list:
            image = tool.get_image(tool.GFX[c.BLOCK_SHEET], *rect, c.BLACK, 1)
            self.images.append(image)

class CircleGlass(Circle):
    def __init__(self, x, y, type):
        self.type = type
        Circle.__init__(self, x, y, 4)
        self.mass = get_block_mass(self.name, self.type) * c.GLASS_MASS_TIMES

    def get_rect_list(self):
        if self.type == c.CIRCLE_TYPE_1: # the small circle
            rect_list = [(744,  85, 42, 42), (250, 546, 42, 42),
                         (  0, 673, 42, 42), ( 84, 673, 42, 42)]
        elif self.type == c.BEAM_TYPE_2: # the big circle
            rect_list = [(633, 169, 73, 73), (708, 169, 73, 73),
                         (558, 169, 73, 73), (482, 169, 73, 73)]
        return rect_list

class CircleWood(Circle):
    def __init__(self, x, y, type):
        self.type = type
        Circle.__init__(self, x, y, 12)
        self.mass = get_block_mass(self.name, self.type) * c.GLASS_MASS_TIMES

    def get_rect_list(self):
        if self.type == c.CIRCLE_TYPE_1: # the small circle
            rect_list = [(372, 418, 39, 39), (372, 461, 39, 39),
                         (372, 504, 39, 39), (372, 547, 39, 39)]
        elif self.type == c.BEAM_TYPE_2: # the big circle
            rect_list = [(169, 662, 73, 73), (251, 170, 73, 73),
                         (328, 170, 73, 73), (405, 170, 73, 73)]
        return rect_list

class CircleStone(Circle):
    def __init__(self, x, y, type):
        self.type = type
        Circle.__init__(self, x, y, 48)
        self.mass = get_block_mass(self.name, self.type) * c.STONE_MASS_TIMES

    def get_rect_list(self):
        if self.type == c.CIRCLE_TYPE_1: # the small circle
            rect_list = [(746, 130, 37, 37), (372, 590, 37, 37),
                         (372, 633, 37, 37), (372, 676, 37, 37)]
        elif self.type == c.BEAM_TYPE_2: # the big circle
            rect_list = [(252, 246, 73, 73), (252, 321, 73, 73),
                         (252, 396, 73, 73), (252, 471, 73, 73)]
        return rect_list