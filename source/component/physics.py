__author__ = 'marble_xu'

import math
import pygame as pg
import pymunk as pm
from pymunk import Vec2d
from .. import tool
from .. import constants as c

COLLISION_BIRD = 1
COLLISION_PIG = 2
COLLISION_BLOCK = 3
COLLISION_LINE = 4
COLLISION_EXPLODE = 5
COLLISION_EGG = 6

BIRD_IMPULSE_TIMES = 3
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
        self.explodes = []
        self.eggs = []
        self.path_timer = 0
        self.check_collide = False
        self.explode_timer = 0
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
                my_phy.handle_pig_collide(pig_shape, arbiter.total_impulse.length * BIRD_IMPULSE_TIMES)
        def post_solve_pig_line(arbiter, space, data):
            if self.check_collide:
                pig_shape = arbiter.shapes[0]
                my_phy.handle_pig_collide(pig_shape, arbiter.total_impulse.length, True)
        def post_solve_pig_block(arbiter, space, data):
            if self.check_collide:
                if arbiter.total_impulse.length >= MIN_DAMAGE_IMPULSE:
                    pig_shape = arbiter.shapes[0]
                    my_phy.handle_pig_collide(pig_shape, arbiter.total_impulse.length)
        def post_solve_block_bird(arbiter, space, data):
            if self.check_collide:
                block_shape, bird_shape = arbiter.shapes
                my_phy.handle_bird_collide(bird_shape)
                if arbiter.total_impulse.length >= MIN_DAMAGE_IMPULSE:
                    my_phy.handle_block_collide(block_shape, arbiter.total_impulse.length)

        def post_solve_block_explode(arbiter, space, data):
            if self.check_collide:
                block_shape = arbiter.shapes[0]
                if arbiter.total_impulse.length > MIN_DAMAGE_IMPULSE:
                    my_phy.handle_block_collide(block_shape, arbiter.total_impulse.length)

        def post_solve_pig_explode(arbiter, space, data):
            if self.check_collide:
                pig_shape = arbiter.shapes[0]
                if arbiter.total_impulse.length > MIN_DAMAGE_IMPULSE:
                    my_phy.handle_pig_collide(pig_shape, arbiter.total_impulse.length)

        def post_solve_egg(arbiter, space, data):
            if self.check_collide:
                egg_shape = arbiter.shapes[0]
                my_phy.handle_egg_collide(egg_shape)

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

        self.space.add_collision_handler(
            COLLISION_BLOCK, COLLISION_EXPLODE).post_solve = post_solve_block_explode

        self.space.add_collision_handler(
            COLLISION_PIG, COLLISION_EXPLODE).post_solve = post_solve_pig_explode

        self.space.add_collision_handler(
            COLLISION_EGG, COLLISION_LINE).post_solve = post_solve_egg
        self.space.add_collision_handler(
            COLLISION_EGG, COLLISION_BLOCK).post_solve = post_solve_egg
        self.space.add_collision_handler(
            COLLISION_EGG, COLLISION_PIG).post_solve = post_solve_egg

    def enable_check_collide(self):
        self.check_collide = True

    def add_bird(self, bird, distance, angle, x, y):
        x, y = to_pymunk(x, y)
        radius = bird.get_radius()
        phybird = PhyBird(distance, angle, x, y, self.space, bird.get_radius(), bird.mass)
        bird.set_physics(phybird)
        self.birds.append(bird)

    def add_egg(self, egg):
        x, y = to_pymunk(egg.rect.centerx, egg.rect.centery)
        phy = PhyEgg((x, y), egg.rect.w, egg.rect.h, self.space, 10)
        egg.set_physics(phy)
        self.eggs.append(egg)

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

    def add_explode(self, pos, angle, length, mass):
        phyexplode = PhyExplode(pos, angle, length, self.space, mass)
        self.explodes.append(phyexplode)

    def create_explosion(self, pos, radius, length, mass):
        ''' parameter pos is the pymunk position'''
        explode_num = 12
        sub_pi = math.pi * 2 / explode_num
        for i in range(explode_num):
            angle = sub_pi * i
            x = pos[0] + radius * math.sin(angle)
            y = pos[1] + radius * math.cos(angle)
            # angle value must calculated by math.pi * 2
            self.add_explode((x,y), angle, length, mass)

    def check_explosion(self):
        explodes_to_remove = []
        if len(self.explodes) == 0:
            return

        if self.explode_timer == 0:
            self.explode_timer = self.current_time
        elif (self.current_time - self.explode_timer) > 1000:
            for explode in self.explodes:
                self.space.remove(explode.shape, explode.shape.body)
                self.explodes.remove(explode)
                self.explode_timer = 0

        for explode in self.explodes:
            if explode.is_out_of_length():
                explodes_to_remove.append(explode)

        for explode in explodes_to_remove:
            self.space.remove(explode.shape, explode.shape.body)
            self.explodes.remove(explode)

    def update(self, game_info, level, mouse_pressed):
        birds_to_remove = []
        pigs_to_remove = []
        blocks_to_remove = []
        eggs_to_remove = []
        self.current_time = game_info[c.CURRENT_TIME]

        #From pymunk doc:Performing multiple calls with a smaller dt
        #                creates a more stable and accurate simulation
        #So make five updates per frame for better stability
        for x in range(5):
            self.space.step(self.dt)

        for bird in self.birds:
            bird.update(game_info, level, mouse_pressed)
            if (bird.phy.shape.body.position.y < 0 or bird.state == c.DEAD
                or bird.phy.shape.body.position.x > c.SCREEN_WIDTH * 2):
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

        for egg in self.eggs:
            egg.update(game_info, level, mouse_pressed)
            if egg.state == c.DEAD:
                eggs_to_remove.append(egg)
            poly = egg.phy.shape
            p = to_pygame(poly.body.position)
            x, y = p
            w, h = egg.image.get_size()
            # change to [left, top] position of pygame
            x -= w * 0.5
            y -= h * 0.5
            angle_degree = math.degrees(poly.body.angle)
            egg.update_position(x, y, angle_degree)

        for egg in eggs_to_remove:
            self.space.remove(egg.phy.shape, egg.phy.shape.body)
            self.eggs.remove(egg)

        self.check_explosion()

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
                    if not (bird.name == c.BIG_RED_BIRD and bird.jump):
                        bird.phy.body.velocity = bird.phy.body.velocity * 0.5
                elif bird.name == c.BIG_RED_BIRD:
                    bird.jump = False
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

    def handle_egg_collide(self, egg_shape):
        for egg in self.eggs:
            if egg_shape == egg.phy.shape:
                egg.set_explode()
                egg.phy.body.velocity = egg.phy.body.velocity * 0.01
                break

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

        for egg in self.eggs:
            egg.draw(surface)

        if c.DEBUG:
            for explode in self.explodes:
                pos = to_pygame(explode.body.position)
                pg.draw.circle(surface, c.RED, pos, 5)

class PhyBird():
    def __init__(self, distance, angle, x, y, space, radius, mass):
        self.life = 10
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

class PhyExplode():
    def __init__(self, pos, angle, length, space, mass=5.0):
        ''' parater angle is clockwise value '''
        radius = 3
        moment = 1000
        body = pm.Body(mass, moment)
        body.position = Vec2d(pos)

        power = mass * 2000
        impulse = power * Vec2d(0, 1)
        # the angle of rotated function is counter-clockwise, need to reverse it
        angle = -angle
        body.apply_impulse_at_local_point(impulse.rotated(angle))

        shape = pm.Circle(body, radius, (0, 0))
        shape.friction = 1
        shape.collision_type = COLLISION_EXPLODE
        space.add(body, shape)
        self.body = body
        self.shape = shape
        self.orig_pos = pos
        self.length = length

    def is_out_of_length(self):
        pos = self.body.position
        distance = tool.distance(*pos, *self.orig_pos)
        if distance >= self.length:
            return True
        return False

class PhyEgg():
    def __init__(self, pos, length, height, space, mass=5.0):
        moment = 1000
        body = pm.Body(mass, moment)
        body.position = Vec2d(pos)

        power = 5000
        impulse = power * Vec2d(0, -1)
        body.apply_impulse_at_local_point(impulse)

        shape = pm.Poly.create_box(body, (length, height))
        shape.friction = 1
        shape.collision_type = COLLISION_EGG
        space.add(body, shape)
        self.body = body
        self.shape = shape

# must init as a global parameter to use in the post_solve handler
my_phy = Physics()
