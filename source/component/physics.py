__author__ = 'marble_xu'

import math
import pygame as pg
import pygame as pg
import pymunk as pm
from pymunk import Vec2d
from .. import constants as c

COLLISION_BIRD = 1
COLLISION_PIG = 2
COLLISION_BLOCK = 3
COLLISION_LINE = 4

MAX_IMPULSE = 100000
MIN_DAMAGE_IMPULSE = 300

def to_pygame(p):
    """Convert position of pymunk to position of pygame"""
    return int(p.x), int(-p.y+600)

def to_pymunk(x, y):
    """Convert position of pygame to position of pymunk"""
    return (x, -(y-600))

class Physics():
    def __init__(self):
        self.reset()

    def reset(self, level=None):
        self.level = level
        # init space: set gravity and dt
        self.space = pm.Space()
        self.space.gravity = (0.0, -700.0)
        self.dt = 0.002
        self.birds = []
        self.pigs = []
        self.blocks = []
        self.path_timer = 0
        self.check_collide = False
        self.setup_lines()
        self.setup_collision_handler()

    def setup_lines(self):
        # Static Ground
        x, y = to_pymunk(c.SCREEN_WIDTH, c.GROUND_HEIGHT)
        static_body = pm.Body(body_type=pm.Body.STATIC)
        static_lines = [pm.Segment(static_body, (0.0, y), (x, y), 0.0)]

        for line in static_lines:
            line.elasticity = 0.95
            line.friction = 1
            line.collision_type = COLLISION_LINE
        self.space.add(static_lines)
        self.static_lines = static_lines

    def setup_collision_handler(self):
        def post_solve_bird_line(arbiter, space, data):
            if self.check_collide:
                bird_shape = arbiter.shapes[0]
                my_phy.handle_bird_collide(bird_shape, True)
        def post_solve_pig_bird(arbiter, space, data):
            if self.check_collide:
                pig_shape = arbiter.shapes[0]
                my_phy.handle_pig_collide(pig_shape, MAX_IMPULSE)
        def post_solve_pig_line(arbiter, space, data):
            if self.check_collide:
                pig_shape = arbiter.shapes[0]
                my_phy.handle_pig_collide(pig_shape, arbiter.total_impulse.length, True)
        def post_solve_pig_block(arbiter, space, data):
            if self.check_collide:
                if arbiter.total_impulse.length > MIN_DAMAGE_IMPULSE:
                    pig_shape = arbiter.shapes[0]
                    my_phy.handle_pig_collide(pig_shape, arbiter.total_impulse.length)
        def post_solve_block_bird(arbiter, space, data):
            if self.check_collide:
                block_shape, bird_shape = arbiter.shapes
                my_phy.handle_bird_collide(bird_shape)
                if arbiter.total_impulse.length > 1100:
                    my_phy.handle_block_collide(block_shape, arbiter.total_impulse.length)

        self.space.add_collision_handler(
            COLLISION_BIRD, COLLISION_LINE).post_solve = post_solve_bird_line

        self.space.add_collision_handler(
            COLLISION_PIG, COLLISION_BIRD).post_solve = post_solve_pig_bird

        self.space.add_collision_handler(
            COLLISION_PIG, COLLISION_LINE).post_solve = post_solve_pig_line

        self.space.add_collision_handler(
            COLLISION_PIG, COLLISION_BLOCK).post_solve = post_solve_pig_block

        self.space.add_collision_handler(
            COLLISION_BLOCK, COLLISION_BIRD).post_solve = post_solve_block_bird

    def enable_check_collide(self):
        self.check_collide = True

    def add_bird(self, bird, distance, angle, x, y):
        x, y = to_pymunk(x, y)
        phybird = PhyBird(distance, angle, x, y, self.space)
        bird.set_physics(phybird)
        self.birds.append(bird)

    def add_bird_by_copy(self, bird, body):
        phybird = PhyBird2(body, self.space)
        bird.set_physics(phybird)
        self.birds.append(bird)
        
    def add_pig(self, pig):
        '''must use the center position of pygame to transfer to the position of pymunk'''
        x, y = to_pymunk(pig.rect.centerx, pig.rect.centery)
        radius = pig.rect.w//2
        phypig = PhyPig(x, y, radius, self.space)
        pig.set_physics(phypig)
        self.pigs.append(pig)

    def add_block(self, block):
        '''must use the center position of pygame to transfer to the position of pymunk'''
        phy = None
        x, y = to_pymunk(block.rect.centerx, block.rect.centery)
        if block.name == c.BEAM:
            length, height = block.rect.w, block.rect.h
            phy = PhyPolygon((x, y), length, height, self.space, block.mass)
        elif block.name == c.CIRCLE:
            radius = block.rect.w//2
            phy = PhyCircle((x, y), radius, self.space, block.mass)
        if phy:
            block.set_physics(phy)
            self.blocks.append(block)
        else:
            print('not support block type:', block.name)

    def update(self, game_info, level, mouse_pressed):
        birds_to_remove = []
        pigs_to_remove = []
        blocks_to_remove = []
        self.current_time = game_info[c.CURRENT_TIME]

        #From pymunk doc:Performing multiple calls with a smaller dt
        #                creates a more stable and accurate simulation
        #So make five updates per frame for better stability
        for x in range(5):
            self.space.step(self.dt)

        for bird in self.birds:
            bird.update(game_info, level, mouse_pressed)
            if bird.phy.shape.body.position.y < 0 or bird.state == c.DEAD:
                birds_to_remove.append(bird)
            else:
                poly = bird.phy.shape
                # the postion transferred from pymunk is the center position of pygame
                p = to_pygame(poly.body.position)
                x, y = p
                w, h = bird.image.get_size()
                # change to [left, top] position of pygame
                x -= w * 0.5
                y -= h * 0.5
                angle_degree = math.degrees(poly.body.angle)
                bird.update_position(x, y, angle_degree)
                self.update_bird_path(bird, p, level)

        for bird in birds_to_remove:
            self.space.remove(bird.phy.shape, bird.phy.shape.body)
            self.birds.remove(bird)
            bird.set_dead()

        for pig in self.pigs:
            pig.update(game_info)
            if pig.phy.body.position.y < 0 or pig.life <= 0:
                pigs_to_remove.append(pig)
            poly = pig.phy.shape
            p = to_pygame(poly.body.position)
            x, y = p
            w, h = pig.image.get_size()
            x -= w * 0.5
            y -= h * 0.5
            angle_degree = math.degrees(poly.body.angle)
            pig.update_position(x, y, angle_degree)

        for pig in pigs_to_remove:
            self.space.remove(pig.phy.shape, pig.phy.shape.body)
            self.pigs.remove(pig)
            level.update_score(c.PIG_SCORE)

        for block in self.blocks:
            if block.life <= 0:
                blocks_to_remove.append(block)
            poly = block.phy.shape
            p = poly.body.position
            p = Vec2d(to_pygame(p))
            angle_degree = math.degrees(poly.body.angle) + 180
            rotated_image = pg.transform.rotate(block.orig_image, angle_degree)
            offset = Vec2d(rotated_image.get_size()) / 2.
            p = p - offset
            block.update_position(p.x, p.y, rotated_image)

        for block in blocks_to_remove:
            self.space.remove(block.phy.shape, block.phy.shape.body)
            self.blocks.remove(block)
            level.update_score(c.SHAPE_SCORE)

    def update_bird_path(self, bird, pos, level):
        if bird.path_timer == 0:
            bird.path_timer = self.current_time
        elif (self.current_time - bird.path_timer) > 50:
            bird.path_timer = self.current_time
            if not bird.collide:
                level.bird_path.append(pos)

    def handle_bird_collide(self, bird_shape, is_ground=False):
        for bird in self.birds:
            if bird_shape == bird.phy.shape:
                if is_ground: # change the velocity of bird to 50% of the original value
                    bird.phy.body.velocity = bird.phy.body.velocity * 0.5
                bird.set_collide()

    def handle_pig_collide(self, pig_shape, impulse, is_ground=False):
        for pig in self.pigs:
            if pig_shape == pig.phy.shape:
                if is_ground:
                    pig.phy.body.velocity = pig.phy.body.velocity * 0.8
                else:
                    damage = impulse // MIN_DAMAGE_IMPULSE
                    pig.set_damage(damage)
                    print('pig life:', pig.life, ' damage:', damage, ' impulse:', impulse)

    def handle_block_collide(self, block_shape, impulse):
        for block in self.blocks:
            if block_shape == block.phy.shape:
                damage = impulse // MIN_DAMAGE_IMPULSE
                block.set_damage(damage)
                print('block damage:', damage, ' impulse:', impulse, ' life:', block.life)

    def draw(self, surface):
        # Draw static lines
        if c.DEBUG:
            for line in self.static_lines:
                body = line.body
                pv1 = body.position + line.a.rotated(body.angle)
                pv2 = body.position + line.b.rotated(body.angle)
                p1 = to_pygame(pv1)
                p2 = to_pygame(pv2)
                pg.draw.lines(surface, c.RED, False, [p1, p2])

        for bird in self.birds:
            bird.draw(surface)

        for pig in self.pigs:
            pig.draw(surface)

        for block in self.blocks:
            block.draw(surface)

class PhyBird():
    def __init__(self, distance, angle, x, y, space):
        self.life = 10
        mass = 5
        radius = 12
        inertia = pm.moment_for_circle(mass, 0, radius, (0, 0))
        body = pm.Body(mass, inertia)
        body.position = x, y
        power = distance * 53
        impulse = power * Vec2d(1, 0)
        angle = -angle
        body.apply_impulse_at_local_point(impulse.rotated(angle))
        
        shape = pm.Circle(body, radius, (0, 0))
        shape.elasticity = 0.95
        shape.friction = 1
        shape.collision_type = COLLISION_BIRD
        space.add(body, shape)
        self.body = body
        self.shape = shape

    def get_pygame_pos(self):
        return to_pygame(self.body.position)

class PhyBird2():
    def __init__(self, body, space):
        self.life = 10
        radius = 12
        shape = pm.Circle(body, radius, (0, 0))
        shape.elasticity = 0.95
        shape.friction = 1
        shape.collision_type = COLLISION_BIRD
        space.add(body, shape)
        self.body = body
        self.shape = shape


class PhyPig():
    def __init__(self, x, y, radius, space):
        mass = 5
        inertia = pm.moment_for_circle(mass, 0, radius, (0, 0))
        body = pm.Body(mass, inertia)
        body.position = x, y
        shape = pm.Circle(body, radius, (0, 0))
        shape.elasticity = 0.95
        shape.friction = 1
        shape.collision_type = COLLISION_PIG
        space.add(body, shape)
        self.body = body
        self.shape = shape

class PhyPolygon():
    def __init__(self, pos, length, height, space, mass=5.0):
        moment = 1000
        body = pm.Body(mass, moment)
        body.position = Vec2d(pos)
        shape = pm.Poly.create_box(body, (length, height))
        shape.friction = 1
        shape.collision_type = COLLISION_BLOCK
        space.add(body, shape)
        self.body = body
        self.shape = shape

class PhyCircle():
    def __init__(self, pos, radius, space, mass=5.0):
        moment = 1000
        body = pm.Body(mass, moment)
        body.position = Vec2d(pos)
        shape = pm.Circle(body, radius, (0, 0))
        shape.friction = 1
        shape.collision_type = COLLISION_BLOCK
        space.add(body, shape)
        self.body = body
        self.shape = shape

# must init as a global parameter to use in the post_solve handler
my_phy = Physics()