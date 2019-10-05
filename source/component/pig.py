__author__ = 'marble_xu'

import random
import pygame as pg
from .. import tool
from .. import constants as c

def create_pig(type, x, y):
    pig = None
    if type == c.NORMAL_PIG:
        pig = NormalPig(x, y)
    elif type == c.BIG_PIG:
        pig = BigPig(x, y)
    return pig

class Pig():
    def __init__(self, x, y, name, life):
        self.name = name
        self.life = life
        self.animate_timer = 0
        self.animate_interval = 100

        self.load_images()
        self.setup_images()
        self.frame_index = 0
        self.frame_num = len(self.frames)
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = y
        self.angle_degree = 0
        self.state = c.IDLE

    def load_frames(self, sheet, frame_rect_list, scale):
        frames = []
        for frame_rect in frame_rect_list:
            frames.append(tool.get_image(sheet, *frame_rect, 
                            c.BLACK, scale))
        return frames

    def load_images(self):
        pass

    def setup_images(self):
        ''' a image is mapping to a frame list
            normalpig has 3 images: normal image, hurt1 image and hurt2 image '''
        self.image_index = 0
        self.image_num = len(self.images_list)
        self.frames = self.images_list[self.image_index]

        self.image_threshold = []
        for i in reversed(range(self.image_num)):
            i += 1
            temp_life = self.life//self.image_num * i
            self.image_threshold.append(temp_life)
        
    def update(self, game_info):
        self.current_time = game_info[c.CURRENT_TIME]
        self.animation()

    def animation(self):
        if self.frame_index == 0:
            interval = 2000 + random.randint(0, 2000)
        else:
            interval = self.animate_interval

        if (self.current_time - self.animate_timer) > interval:
            self.frame_index += 1
            if self.frame_index >= self.frame_num:
                self.frame_index = 0
            self.animate_timer = self.current_time

        image = self.frames[self.frame_index]
        self.image = pg.transform.rotate(image, self.angle_degree)

    def set_physics(self, phy):
        self.phy = phy

    def set_dead(self):
        self.state = c.DEAD

    def update_position(self, x, y, angle_degree):
        self.rect.x = x
        self.rect.y = y
        self.angle_degree = angle_degree

    def set_damage(self, damage):
        self.life -= damage
        if self.life < self.image_threshold[self.image_index]:
            self.change_image()

    def change_image(self):
        if (self.image_index + 1) < self.image_num:
            self.image_index += 1
            self.frames = self.images_list[self.image_index]
            self.frame_index = 0
            self.frame_num = len(self.frames)
            self.image = self.frames[self.frame_index]

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class NormalPig(Pig):
    def __init__(self, x, y):
        Pig.__init__(self, x, y, c.NORMAL_PIG, 12)

    def load_images(self):
        self.images_list = []
        sheet = tool.GFX[c.PIG_SHEET]
        normal_rect_list = [(438, 712, 80, 80), (438, 794, 80, 80), (438, 874, 80, 80)]
        hurt1_rect_list = [(522, 794, 80, 80), (522, 872, 80, 80), (522, 948, 80, 80)]
        hurt2_rect_list = [(438, 956, 80, 80), (522, 792, 80, 80), (522, 1026, 80, 80)]

        rect_lists = [normal_rect_list, hurt1_rect_list, hurt2_rect_list]
        for rect_list in rect_lists:
            self.images_list.append(self.load_frames(sheet, rect_list, c.NORMAL_PIG_MULTIPLIER))

class BigPig(Pig):
    def __init__(self, x, y):
        Pig.__init__(self, x, y, c.BIG_PIG, 16)

    def load_images(self):
        self.images_list = []
        sheet = tool.GFX[c.PIG_SHEET]
        normal_rect_list = [(438, 712, 80, 80), (438, 794, 80, 80), (438, 874, 80, 80)]
        hurt1_rect_list = [(522, 794, 80, 80), (522, 872, 80, 80), (522, 948, 80, 80)]
        hurt2_rect_list = [(438, 956, 80, 80), (522, 792, 80, 80), (522, 1026, 80, 80)]

        rect_lists = [normal_rect_list, hurt1_rect_list, hurt2_rect_list]
        for rect_list in rect_lists:
            self.images_list.append(self.load_frames(sheet, rect_list, c.BIG_PIG_MULTIPLIER))