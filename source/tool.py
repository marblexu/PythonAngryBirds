__author__ = 'marble_xu'

import os
import json
from abc import abstractmethod
import pygame as pg
from . import constants as c

class State():
    def __init__(self):
        self.start_time = 0.0
        self.current_time = 0.0
        self.done = False
        self.next = None
        self.persist = {}
    
    @abstractmethod
    def startup(self, current_time, persist):
        '''abstract method'''

    def cleanup(self):
        self.done = False
        return self.persist
    
    @abstractmethod
    def update(sefl, surface, keys, current_time):
        '''abstract method'''

class Control():
    def __init__(self):
        self.screen = pg.display.get_surface()
        self.done = False
        self.clock = pg.time.Clock()
        self.fps = 60
        self.keys = pg.key.get_pressed()
        self.mouse_pos = None
        self.mouse_pressed = False
        self.current_time = 0.0
        self.state_dict = {}
        self.state_name = None
        self.state = None
        self.game_info = {c.CURRENT_TIME:0.0,
                          c.LEVEL_NUM:c.START_LEVEL_NUM,
                          c.SCORE:0}
 
    def setup_states(self, state_dict, start_state):
        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]
        self.state.startup(self.current_time, self.game_info)

    def update(self):
        self.current_time = pg.time.get_ticks()
        if self.state.done:
            self.flip_state()
        self.state.update(self.screen, self.current_time, self.mouse_pos, self.mouse_pressed)
        self.mouse_pos = None

    def flip_state(self):
        previous, self.state_name = self.state_name, self.state.next
        persist = self.state.cleanup()
        self.state = self.state_dict[self.state_name]
        self.state.startup(self.current_time, persist)

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.KEYDOWN:
                self.keys = pg.key.get_pressed()
            elif event.type == pg.KEYUP:
                self.keys = pg.key.get_pressed()
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                self.mouse_pos = pg.mouse.get_pos()
                self.mouse_pressed = True
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                self.mouse_pressed = False

    def main(self):
        while not self.done:
            self.event_loop()
            self.update()
            pg.display.update()
            self.clock.tick(self.fps)
            if c.DEBUG:
                pg.display.set_caption("pos: " + str(pg.mouse.get_pos()))
        print('game over')


def get_image(sheet, x, y, width, height, colorkey, scale):
        image = pg.Surface([width, height])
        rect = image.get_rect()

        image.blit(sheet, (0, 0), (x, y, width, height))
        image.set_colorkey(colorkey)
        image = pg.transform.scale(image,
                                   (int(rect.width*scale),
                                    int(rect.height*scale)))
        return image

def load_all_gfx(directory, colorkey=(255,0,255), accept=('.png', '.jpg', '.bmp', '.gif')):
    graphics = {}
    for pic in os.listdir(directory):
        name, ext = os.path.splitext(pic)
        if ext.lower() in accept:
            img = pg.image.load(os.path.join(directory, pic))
            if img.get_alpha():
                img = img.convert_alpha()
            else:
                img = img.convert()
                img.set_colorkey(colorkey)
            graphics[name] = img
    return graphics

pg.init()
pg.display.set_caption(c.ORIGINAL_CAPTION)
SCREEN = pg.display.set_mode(c.SCREEN_SIZE)

GFX = load_all_gfx(os.path.join("resources","graphics"))