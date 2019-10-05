__author__ = 'marble_xu'

import random
import pygame as pg
from .. import tool
from .. import constants as c

def create_bird(type, x, y):
    bird = None
    if type == c.RED_BIRD:
        bird = RedBird(x, y)
    elif type == c.BLUE_BIRD:
        bird = BlueBird(x, y)
    elif type == c.YELLOW_BIRD:
        bird = YellowBird(x, y)
    return bird

class Bird():
    def __init__(self, x, y, name):
        self.frames = []
        self.frame_index = 0
        self.animate_timer = 0
        self.animate_interval = 100

        self.name = name
        self.load_images()
        self.frame_num = len(self.frames)
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = y
        self.angle_degree = 0
        self.state = c.IDLE
        self.old_pos = (self.rect.x, self.rect.y)
        self.pos_timer = 0
        self.path_timer = 0
        self.collide = False # collided with ground or shape if it is True

    def load_frames(self, sheet, frame_rect_list, scale):
        for frame_rect in frame_rect_list:
            self.frames.append(tool.get_image(sheet, *frame_rect, 
                            c.BLACK, scale))

    def load_images(self):
        pass

    def update(self, game_info, level, mouse_pressed):
        self.current_time = game_info[c.CURRENT_TIME]
        self.handle_state(level, mouse_pressed)
        self.animation()

    def handle_state(self, level, mouse_pressed):
        if self.state == c.IDLE:
            pass
        elif self.state == c.ATTACK:
            self.attacking(level, mouse_pressed)
            self.check_attack_finish()

    def attacking(self, level, mouse_pressed):
        pass

    def check_attack_finish(self):
        if self.pos_timer == 0:
            self.pos_timer = self.current_time
            self.old_pos = (self.rect.x, self.rect.y)
        elif (self.current_time - self.pos_timer) > 500:
            distance = abs(self.old_pos[0] - self.rect.x) + abs(self.old_pos[1] - self.rect.y)
            if distance < 10:
                self.state = c.DEAD
            self.pos_timer = self.current_time
            self.old_pos = (self.rect.x, self.rect.y)

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

    def set_attack(self):
        self.state = c.ATTACK

    def set_physics(self, phy):
        self.phy = phy

    def set_collide(self):
        self.collide = True

    def set_dead(self):
        self.state = c.DEAD

    def update_position(self, x, y, angle_degree=0):
        self.rect.x = x
        self.rect.y = y
        self.angle_degree = angle_degree

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class RedBird(Bird):
    def __init__(self, x, y):
        Bird.__init__(self, x, y, c.RED_BIRD)

    def load_images(self):
        sheet = tool.GFX[c.BIRD_SHEET]
        frame_rect_list = [(184, 32, 66, 66), (258, 32, 66, 66), (332, 32, 66, 66),
                           (404, 32, 66, 66), (472, 32, 66, 66)]
        self.load_frames(sheet, frame_rect_list, c.BIRD_MULTIPLIER)

class BlueBird(Bird):
    def __init__(self, x, y):
        Bird.__init__(self, x, y, c.BLUE_BIRD)
        self.clicked = False

    def load_images(self):
        sheet = tool.GFX[c.BIRD_SHEET]
        frame_rect_list = [(218, 138, 42, 42), (277, 138, 42, 42), (340, 138, 42, 42),
                           (404, 138, 42, 42), (462, 138, 42, 42)]
        self.load_frames(sheet, frame_rect_list, 0.8)

    def attacking(self, level, mouse_pressed):
        if not self.clicked and mouse_pressed:
            self.clicked = True
            # create two blue birds when first mouse click
            bird_list = [1, -1]
            for sign in bird_list:
                x, y = self.phy.get_pygame_pos()
                bird = BlueBird(x, y)
                bird.clicked = True
                bird.state = c.ATTACK
                level.physics.add_bird_by_copy(bird, self.phy.body.copy())

                old = self.phy.body.velocity
                vec_y = old[1] * 0.5 * sign
                bird.phy.body.velocity = (old[0], vec_y)
                print('bluebird:[', x, ',', y, ']', 'old:', old, '  new:', bird.phy.body.velocity)

class YellowBird(Bird):
    def __init__(self, x, y):
        Bird.__init__(self, x, y, c.YELLOW_BIRD)
        self.clicked = False

    def load_images(self):
        sheet = tool.GFX[c.BIRD_SHEET]
        frame_rect_list = [(190, 208, 74, 74), (266, 208, 74, 74), (341, 208, 74, 74),
                           (419, 208, 74, 74), (495, 208, 74, 74)]
        self.load_frames(sheet, frame_rect_list, c.BIRD_MULTIPLIER)

    def attacking(self, level, mouse_pressed):
        if not self.clicked and mouse_pressed:
            self.clicked = True
            # speed velocity of bird when first mouse click
            self.phy.body.velocity = self.phy.body.velocity * 2
            print('yellow bird:', self.phy.body.velocity)