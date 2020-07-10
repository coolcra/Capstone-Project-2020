import pygame as pg

# define some colors (R, G, B)
BLUE  = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BROWN = (106, 55, 5)
ORANGE   = ( 255, 165, 0)
PURPLE   = ( 100, 0, 100)

# game settings
MAP_WIDTH = 640
MAP_HEIGHT = 640
WIDTH = 650
HEIGHT = 700
#for the screen
FPS = 60
TITLE = "Dungeon Escape"
BGCOLOR = ORANGE

TILESIZE = 64
GRIDWIDTH = MAP_WIDTH / TILESIZE  #30
GRIDHEIGHT = MAP_HEIGHT / TILESIZE #30

WALL_IMG = 'wall.png'

# Player settings
PLAYER_SPEED = 300
PLAYER_ROT_SPEED = 250
PLAYER_IMG = 'player.png'
PLAYER_HIT_RECT = pg.Rect(0, 0, 5, 5)
AI_HIT_RECT = pg.Rect(10,10, 5, 5)
# enemy settings
ZOMB_IMG = 'zomb.png'

# coin settings
COIN_IMG = 'coin.png'
