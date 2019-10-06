__author__ = 'marble_xu'

DEBUG = False

START_LEVEL_NUM = 1

SCREEN_HEIGHT = 650
SCREEN_WIDTH = 1200
SCREEN_SIZE = (SCREEN_WIDTH,SCREEN_HEIGHT)

GROUND_HEIGHT = 550

ORIGINAL_CAPTION = "Angry Birds"

## COLORS ##
#                R    G    B
GRAY         = (100, 100, 100)
NAVYBLUE     = ( 60,  60, 100)
WHITE        = (255, 255, 255)
RED          = (255,   0,   0)
GREEN        = (  0, 255,   0)
FOREST_GREEN = ( 31, 162,  35)
GRASS_GREEN  = (130, 200, 100)
BLUE         = (  0,   0, 255)
SKY_BLUE     = ( 39, 145, 251)
YELLOW       = (255, 255,   0)
ORANGE       = (255, 128,   0)
PURPLE       = (255,   0, 255)
CYAN         = (  0, 255, 255)
BLACK        = (  0,   0,   0)
NEAR_BLACK   = ( 19,  15,  48)
COMBLUE      = (233, 232, 255)
GOLD         = (255, 215,   0)

BGCOLOR = WHITE


BACKGROUND_MULTIPLER = 1
BIRD_MULTIPLIER = 0.5
NORMAL_PIG_MULTIPLIER = 0.4
BIG_PIG_MULTIPLIER = 0.8

#STATES FOR ENTIRE GAME
MAIN_MENU = 'main menu'
LOAD_SCREEN = 'load screen'
TIME_OUT = 'time out'
GAME_OVER = 'game over'
LEVEL = 'level'

#GAME INFO DICTIONARY KEYS
CURRENT_TIME = 'current time'
LEVEL_NUM = 'level num'
SCORE = 'score'

#STATE
IDLE = 'idle'
ATTACK = 'attack'
OVER = 'over'
DEAD = 'dead'

#LEVEL NAME
MATERIAL = 'material'
SHAPE = 'shape'
TYPE = 'type'
DIRECTION = 'direction'
BIRDS = 'birds'
PIGS = 'pigs'
BLOCKS = 'blocks'

#BIRD
BIRD_SHEET = 'angry_birds'
RED_BIRD = 'red_bird'
BLUE_BIRD = 'blue_bird'
YELLOW_BIRD = 'yellow_bird'

#PIG
PIG_SHEET = 'full-sprite'
NORMAL_PIG = 'normal_pig'
BIG_PIG = 'big_pig'

''' BLOCK INFO '''
BLOCK_SHEET = 'block'
#BLOCK MATERIAL
GLASS = 'glass'
WOOD = 'wood'
STONE = 'stone'
#SHAPE TYPE
BEAM = 'beam'
CIRCLE = 'circle'
#BEAM SUBTYPE
BEAM_TYPE_1 = 1
BEAM_TYPE_2 = 2
BEAM_TYPE_3 = 3
BEAM_TYPE_4 = 4
BEAM_TYPE_5 = 5
BEAM_TYPE_6 = 6
#CIRCLE SUBTYPE
CIRCLE_TYPE_1 = 1
CIRCLE_TYPE_2 = 2
#DIRECTION
HORIZONTAL = 0
VERTICAL = 1
#MASS TIMES
GLASS_MASS_TIMES = 1
WOOD_MASS_TIMES = 2
STONE_MASS_TIMES = 4


#BUTTON
BUTTON_HEIGHT = 10
BUTTON_IMG = 'selected-buttons'
NEXT_BUTTON = 'next_button'
REPLAY_BUTTON = 'replay_button'

#SCORE
BIRD_SCORE = 10000
PIG_SCORE = 5000
SHAPE_SCORE = 1000
