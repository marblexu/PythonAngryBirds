__author__ = 'marble_xu'

import os
import json
import math
import pygame as pg
from .. import tool
from .. import constants as c
from ..component import button, physics, bird, pig, block

bold_font = pg.font.SysFont("arial", 30, bold=True)

def vector(p0, p1):
    """Return the vector of the points
       p0 = (xo,yo), p1 = (x1,y1)"""
    a = p1[0] - p0[0]
    b = p1[1] - p0[1]
    return (a, b)

def unit_vector(v):
    """Return the unit vector of the points
       v = (a,b)"""
    h = ((v[0]**2)+(v[1]**2))**0.5
    if h == 0:
        h = 0.000000000000001
    ua = v[0] / h
    ub = v[1] / h
    return (ua, ub)

def distance(xo, yo, x, y):
    """distance between points"""
    dx = x - xo
    dy = y - yo
    d = ((dx ** 2) + (dy ** 2)) ** 0.5
    return d

class Level(tool.State):
    def __init__(self):
        tool.State.__init__(self)
        self.player = None

    def startup(self, current_time, persist):
        self.game_info = persist
        self.persist = self.game_info
        self.game_info[c.CURRENT_TIME] = current_time
        self.reset()

    def reset(self):
        self.score = self.game_info[c.SCORE]
        self.state = c.IDLE
        self.physics = physics.my_phy
        self.physics.reset(self)
        self.load_map()
        self.setup_background()
        self.setup_buttons()
        self.setup_sling()
        self.setup_birds()
        self.setup_pigs()
        self.setup_blocks()
        self.over_timer = 0

    def load_map(self):
        map_file = 'level_' + str(self.game_info[c.LEVEL_NUM]) + '.json'
        file_path = os.path.join('source', 'data', 'map', map_file)
        f = open(file_path)
        self.map_data = json.load(f)
        f.close()

    def setup_background(self):
        self.background = tool.GFX['background']
        self.bg_rect = self.background.get_rect()
        self.background = pg.transform.scale(self.background, 
                                    (int(self.bg_rect.width*c.BACKGROUND_MULTIPLER),
                                    int(self.bg_rect.height*c.BACKGROUND_MULTIPLER)))
        self.bg_rect = self.background.get_rect()
        self.bg_rect.y = -40

    def setup_buttons(self):
        self.buttons = []
        self.buttons.append(button.Button(5, c.BUTTON_HEIGHT, c.NEXT_BUTTON))
        self.buttons.append(button.Button(70, c.BUTTON_HEIGHT, c.REPLAY_BUTTON))

    def setup_sling(self):
        rect_list = [(50, 0, 70, 200), (0, 0, 60, 200)]

        image = tool.get_image(tool.GFX['sling'], *rect_list[0], c.BLACK, 1)
        self.sling1_image = image
        self.sling1_rect = image.get_rect()
        self.sling1_rect.x = 138
        self.sling1_rect.y = 420

        image = tool.get_image(tool.GFX['sling'], *rect_list[1], c.BLACK, 1)
        self.sling2_image = image
        self.sling2_rect = image.get_rect()
        self.sling2_rect.x = 120
        self.sling2_rect.y = 420
        
        self.sling_click = False
        self.mouse_distance = 0
        self.sling_angle = 0

    def setup_birds(self):
        self.birds = []
        y = c.GROUND_HEIGHT

        for i, data in enumerate(self.map_data[c.BIRDS]):
            x = 120 - (i*35)
            tmp = bird.create_bird(data[c.TYPE], x, y)
            if tmp:
                self.birds.append(tmp)
        self.bird_path = []
        self.bird_old_path = []
        self.active_bird = None
        self.select_bird()

    def setup_pigs(self):
        for data in self.map_data[c.PIGS]:
            tmp = pig.create_pig(data[c.TYPE], data['x'], data['y'])
            if tmp:
                self.physics.add_pig(tmp)
                
    def setup_blocks(self):
        for data in self.map_data[c.BLOCKS]:
            if c.DIRECTION in data:
                direction = data[c.DIRECTION]
            else:
                direction = 0
            tmp = block.create_block(data['x'], data['y'], data[c.MATERIAL],
                              data[c.SHAPE], data[c.TYPE], direction)
            if tmp:
                self.physics.add_block(tmp)

    def update(self, surface, current_time, mouse_pos, mouse_pressed):
        self.game_info[c.CURRENT_TIME] = self.current_time = current_time
        self.handle_states(mouse_pos, mouse_pressed)
        self.check_game_state()
        self.draw(surface)
    
    def handle_states(self, mouse_pos, mouse_pressed):
        if self.state == c.IDLE:
            self.handle_sling(mouse_pos, mouse_pressed)
        elif self.state == c.ATTACK:
            if self.active_bird.state == c.DEAD:
                self.active_bird = None
                self.select_bird()
                self.swith_bird_path()
                self.state = c.IDLE
        elif self.state == c.OVER:
            if self.over_timer == 0:
                self.over_timer = self.current_time

        for bird in self.birds:
            bird.update(self.game_info, self, mouse_pressed)
        self.physics.update(self.game_info, self, mouse_pressed)

        self.check_button_click(mouse_pos, mouse_pressed)

    def select_bird(self):
        if len(self.birds) > 0:
            self.active_bird = self.birds[0]
            self.active_bird.update_position(130, 426)

    def handle_sling(self, mouse_pos, mouse_pressed):
        if not mouse_pressed:
            if self.sling_click:
                self.sling_click = False
                xo = 154
                yo = 444
                self.physics.add_bird(self.active_bird, self.mouse_distance,
                                      self.sling_angle, xo, yo)
                self.active_bird.set_attack()
                self.birds.remove(self.active_bird)
                self.physics.enable_check_collide()
                self.state = c.ATTACK
        elif not self.sling_click:
            if mouse_pos:
                mouse_x, mouse_y = mouse_pos
                if (mouse_x > 100 and mouse_x < 250 and 
                    mouse_y > 370 and mouse_y < 550):
                    self.sling_click = True

    def draw_sling_and_active_bird(self, surface):
        sling_x, sling_y = 135, 450
        sling2_x, sling2_y = 160, 450
        rope_length = 90
        bigger_rope = 102

        if self.sling_click:
            mouse_x, mouse_y = pg.mouse.get_pos()
            v = vector((sling_x, sling_y), (mouse_x, mouse_y))
            uv_x, uv_y = unit_vector(v)
            mouse_distance = distance(sling_x, sling_y, mouse_x, mouse_y)
            pu = (uv_x * rope_length + sling_x, uv_y * rope_length + sling_y)
            
            if mouse_distance > rope_length:
                mouse_distance = rope_length
                pux, puy = pu
                pux -= 20
                puy -= 20
                pul = pux, puy
                pu2 = (uv_x * bigger_rope + sling_x, uv_y * bigger_rope + sling_y)
                pg.draw.line(surface, (0, 0, 0), (sling2_x, sling2_y), pu2, 5)
                self.active_bird.update_position(pux, puy)
                self.active_bird.draw(surface)
                pg.draw.line(surface, (0, 0, 0), (sling_x, sling_y), pu2, 5)
                
            else:
                mouse_distance += 10
                pu3 = (uv_x * mouse_distance + sling_x, uv_y * mouse_distance + sling_y)
                pg.draw.line(surface, (0, 0, 0), (sling2_x, sling2_y), pu3, 5)
                self.active_bird.update_position(mouse_x - 20, mouse_y - 20)
                self.active_bird.draw(surface)
                pg.draw.line(surface, (0, 0, 0), (sling_x, sling_y), pu3, 5)

            # Angle of impulse
            dy = mouse_y - sling_y
            dx = mouse_x - sling_x
            if dx == 0:
                dx = 0.00000000000001
            self.sling_angle = math.atan((float(dy))/dx)

            if mouse_x < sling_x + 5:
                self.mouse_distance = mouse_distance
            else:
                self.mouse_distance = -mouse_distance
        else:
            pg.draw.line(surface, (0, 0, 0), (sling_x, sling_y-8), (sling2_x, sling2_y-7), 5)
            if self.active_bird.state == c.IDLE:
                self.active_bird.draw(surface)

    def check_button_click(self, mouse_pos, mouse_pressed):
        if mouse_pressed and mouse_pos:
            for button in self.buttons:
                if button.check_mouse_click(mouse_pos):
                    if button.name == c.NEXT_BUTTON:
                        self.game_info[c.LEVEL_NUM] += 1
                        self.reset()
                    elif button.name == c.REPLAY_BUTTON:
                        self.reset()

    def update_score(self, score):
        self.score += score

    def check_victory(self):
        if len(self.physics.pigs) > 0:
            return False
        return True
    
    def check_lose(self):
        if len(self.birds) == 0 and len(self.physics.birds) == 0:
            return True
        return False

    def check_game_state(self):
        if self.state == c.OVER:
            if (self.current_time - self.over_timer) > 2000:
                self.done = True
        elif self.check_victory():
            self.game_info[c.LEVEL_NUM] += 1
            self.update_score(len(self.birds) * 10000)
            self.game_info[c.SCORE] = self.score
            self.next = c.LEVEL
            self.state = c.OVER
        elif self.check_lose():
            self.next = c.LEVEL
            self.state = c.OVER

    def swith_bird_path(self):
        self.bird_old_path = self.bird_path.copy()
        self.bird_path = []

    def draw_bird_path(self, surface, path):
        for i, pos in enumerate(path):
            if i % 3 == 0:
                size = 4
            elif i % 3 == 1:
                size = 5
            else:
                size = 6
            pg.draw.circle(surface, c.WHITE, pos, size, 0)

    def draw(self, surface):
        surface.fill(c.GRASS_GREEN)
        surface.blit(self.background, self.bg_rect)
        for button in self.buttons:
            button.draw(surface)

        score_font = bold_font.render("SCORE:", 1, c.WHITE)
        number_font = bold_font.render(str(self.score), 1, c.WHITE)
        surface.blit(score_font, (1020, c.BUTTON_HEIGHT))
        surface.blit(number_font, (1120, c.BUTTON_HEIGHT))

        self.draw_bird_path(surface, self.bird_old_path)
        self.draw_bird_path(surface, self.bird_path)

        surface.blit(self.sling1_image, self.sling1_rect)
        self.draw_sling_and_active_bird(surface)
        for bird in self.birds:
            bird.draw(surface)
        
        surface.blit(self.sling2_image, self.sling2_rect)

        self.physics.draw(surface)