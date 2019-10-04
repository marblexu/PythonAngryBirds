__author__ = 'marble_xu'

import pygame as pg
from . import tool
from . import constants as c
from .state import level

def main():
    game = tool.Control()
    state_dict = {c.LEVEL: level.Level()}
    game.setup_states(state_dict, c.LEVEL)
    game.main()
