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
    elif type == c.BLACK_BIRD:
        bird = BlackBird(x, y)
    elif type == c.WHITE_BIRD:
        bird = WhiteBird(x, y)
    elif type == c.BIG_RED_BIRD:
        bird = BigRedBird(x, y)
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
        self.mass = 5.0

    def load_frames(self, sheet, frame_rect_list, scale, color=c.WHITE):
        frames = []
        for frame_rect in frame_rect_list:
            frames.append(tool.get_image(sheet, *frame_rect, color, scale))
        return frames

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
        elif self.state == c.INIT_EXPLODE:
            self.init_explode()
        elif self.state == c.EXPLODE:
            self.exploding(level)

    def attacking(self, level, mouse_pressed):
        pass

    def init_explode(self):
        pass

    def exploding(self, level):
        pass

    def check_attack_finish(self):
        if self.pos_timer == 0:
            self.pos_timer = self.current_time
            self.old_pos = (self.rect.x, self.rect.y)
        elif (self.current_time - self.pos_timer) > 500:
            distance = tool.distance(self.old_pos[0], self.old_pos[1], self.rect.x, self.rect.y)
            if distance < 10:
                if self.name == c.BLACK_BIRD:
                    self.state = c.INIT_EXPLODE
                else:
                    self.state = c.DEAD
            self.pos_timer = self.current_time
            self.old_pos = (self.rect.x, self.rect.y)

    def animation(self):
        if self.state == c.INIT_EXPLODE:
            interval = 400
        elif self.state == c.EXPLODE:
            interval = 100
        elif self.frame_index == 0:
            interval = 2000 + random.randint(0, 2000)
        else:
            interval = self.animate_interval

        if (self.current_time - self.animate_timer) > interval:
            self.frame_index += 1
            if self.frame_index >= self.frame_num:
                if self.state == c.INIT_EXPLODE:
                    self.state = c.EXPLODE
                    self.frame_index = self.frame_num-1
                elif self.state == c.EXPLODE:
                    self.state = c.DEAD
                    self.frame_index = self.frame_num-1
                else:
                    self.frame_index = 0
            self.animate_timer = self.current_time
        
        image = self.frames[self.frame_index]
        self.image = pg.transform.rotate(image, self.angle_degree)

    def change_image(self, frames):
        self.frames = frames
        self.frame_num = len(self.frames)
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.animate_timer = self.current_time

    def set_attack(self):
        self.state = c.ATTACK

    def set_physics(self, phy):
        self.phy = phy

    def set_collide(self):
        self.collide = True

    def set_explode(self):
        self.state = c.EXPLODE

    def set_dead(self):
        self.state = c.DEAD

    def get_radius(self):
        return self.rect.w//2

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
        self.frames = self.load_frames(sheet, frame_rect_list, c.BIRD_MULTIPLIER)

class BlueBird(Bird):
    def __init__(self, x, y):
        Bird.__init__(self, x, y, c.BLUE_BIRD)
        self.clicked = False

    def load_images(self):
        sheet = tool.GFX[c.BIRD_SHEET]
        frame_rect_list = [(218, 138, 42, 42), (277, 138, 42, 42), (340, 138, 42, 42),
                           (404, 138, 42, 42), (462, 138, 42, 42)]
        self.frames = self.load_frames(sheet, frame_rect_list, 0.7)

    def attacking(self, level, mouse_pressed):
        if not self.clicked and mouse_pressed and not self.collide:
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
        self.frames = self.load_frames(sheet, frame_rect_list, c.BIRD_MULTIPLIER)

    def attacking(self, level, mouse_pressed):
        if not self.clicked and mouse_pressed and not self.collide:
            self.clicked = True
            # speed velocity of bird when first mouse click
            self.phy.body.velocity = self.phy.body.velocity * 3
            print('yellow bird:', self.phy.body.velocity)

class BlackBird(Bird):
    def __init__(self, x, y):
        Bird.__init__(self, x, y, c.BLACK_BIRD)
        self.clicked = False
        self.init_explode_show = False
        self.exploded = False

    def load_images(self):
        sheet = tool.GFX[c.BIRD_SHEET]
        frame_rect_list = [(114, 330, 75, 75), (189, 330, 75, 75), (263, 330, 75, 75),
                           (331, 330, 75, 75), (406, 330, 75, 75)]
        self.frames = self.load_frames(sheet, frame_rect_list, c.BIRD_MULTIPLIER)

        init_explode_rect_list = [(114, 330, 75, 75), (481, 330, 75, 75),
                             (553, 330, 75, 75), (621, 330, 75, 75)]
        self.init_explode_frames = self.load_frames(sheet, init_explode_rect_list, c.BIRD_MULTIPLIER)

        sheet = tool.GFX[c.PIG_SHEET]
        explode_rect_list = [(408, 199, 112, 112), (275, 200, 130, 130), (133, 201, 139, 139)]
        self.explode_frames = self.load_frames(sheet, explode_rect_list, c.BIRD_MULTIPLIER, c.BLACK)

    def attacking(self, level, mouse_pressed):
        if not self.clicked and mouse_pressed and not self.collide:
            self.clicked = True
            self.state = c.EXPLODE
            self.phy.body.velocity = self.phy.body.velocity * 0.01
        if self.collide:
            #if bird collided with other things, it can't explode by clicking
            if not self.clicked:
                self.state = c.INIT_EXPLODE
            self.clicked = True

    def init_explode(self):
        if not self.init_explode_show:
            self.change_image(self.init_explode_frames)
            self.init_explode_show= True

    def exploding(self, level):
        if not self.exploded:
            self.change_image(self.explode_frames)
            level.physics.create_explosion(self.phy.body.position, self.get_radius(), 60, 5)
            self.exploded = True

class WhiteBird(Bird):
    def __init__(self, x, y):
        Bird.__init__(self, x, y, c.WHITE_BIRD)
        self.clicked = False

    def load_images(self):
        sheet = tool.GFX[c.BIRD_SHEET]
        frame_rect_list = [(141, 443, 85, 85), (228, 441, 85, 85), (313, 438, 85, 85),
                           (400, 439, 85, 85), (564, 439, 85, 85)]
        self.frames = self.load_frames(sheet, frame_rect_list, c.BIRD_MULTIPLIER)

    def attacking(self, level, mouse_pressed):
        if not self.clicked and mouse_pressed and not self.collide:
            self.clicked = True
            vel_x, vel_y = self.phy.body.velocity
            self.phy.body.velocity = (vel_x * 2, vel_y + 1000)
            egg = Egg(self.rect.centerx, self.rect.bottom + 30)
            level.physics.add_egg(egg)

class Egg(Bird):
    def __init__(self, x, y):
        Bird.__init__(self, x, y, c.EGG)
        self.exploded = False

    def load_images(self):
        sheet = tool.GFX[c.PIG_SHEET]
        frame_rect_list = [(61, 1035, 44, 59)]
        self.frames = self.load_frames(sheet, frame_rect_list, c.BIRD_MULTIPLIER, c.BLACK)

        sheet = tool.GFX[c.PIG_SHEET]
        explode_rect_list = [(408, 199, 112, 112), (275, 200, 130, 130), (133, 201, 139, 139)]
        self.explode_frames = self.load_frames(sheet, explode_rect_list, c.BIRD_MULTIPLIER, c.BLACK)

    def exploding(self, level):
        if not self.exploded:
            self.change_image(self.explode_frames)
            level.physics.create_explosion(self.phy.body.position, self.get_radius(), 50, 5)
            self.exploded = True

class BigRedBird(Bird):
    def __init__(self, x, y):
        Bird.__init__(self, x, y, c.BIG_RED_BIRD)
        self.mass = 8.0
        self.jump = True

    def load_images(self):
        sheet = tool.GFX[c.BIRD_SHEET]
        frame_rect_list = [(120, 638, 120, 120), (247, 638, 120, 120), (376, 639, 120, 120),
                           (501, 638, 120, 120)]
        self.frames = self.load_frames(sheet, frame_rect_list, c.BIRD_MULTIPLIER)
