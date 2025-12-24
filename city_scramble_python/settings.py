import pygame

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "City Scramble"

# Map settings
MAP_WIDTH = 3200
MAP_HEIGHT = 1800

# Colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DARK_GREY = (40, 40, 40)
LIGHT_GREY = (100, 100, 100)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
SANDSTONE = (180, 130, 70)
CACTUS_GREEN = (50, 150, 50)

# Game settings
ROUND_TIME = 180  # 3 minutes

# Player settings
PLAYER_SPEED = 300
PLAYER_SIZE = 40
PLAYER_COLOR = WHITE
PLAYER_HEALTH = 4000

# Enemy settings
ENEMY_SPEED = 120
ENEMY_SIZE = 40
ENEMY_COLOR = RED
ENEMY_RESPAWN_TIME = 0 # ms - instant respawn
ENEMY_SHOOT_COOLDOWN = 1000 # ms
ENEMY_DAMAGE = 50

# Weapon settings
BULLET_SPEED = 600
BULLET_LIFETIME = 1000  # ms
BULLET_COLOR = YELLOW
WEAPON_SPAWN_COUNT = 5
WEAPON_RESPAWN_TIME = 10000 # ms
WEAPON_SIZE = 20

WEAPONS = {
    'pistol': {
        'speed': 600,
        'lifetime': 1000,
        'rate': 400,
        'damage': 10,
        'count': 1,
        'spread': 0,
        'color': YELLOW
    },
    'shotgun': {
        'speed': 500,
        'lifetime': 1000,  # Doubled from 500 for double range
        'rate': 900,
        'damage': 5,
        'count': 10,  # Increased from 3 to 10 pellets
        'spread': 15,
        'color': ORANGE
    },
    'machinegun': {
        'speed': 800,
        'lifetime': 1200,
        'rate': 100,
        'damage': 4,
        'count': 1,
        'spread': 5,
        'color': CYAN
    },
    'grenade': {
        'speed': 800,  # Doubled from 400
        'lifetime': 2000,
        'rate': 600,  # Halved from 1200 for double fire rate
        'damage': 10,
        'count': 1,
        'spread': 0,
        'color': PURPLE
    },
    'rifle': {
        'speed': 700,
        'lifetime': 1500,
        'rate': 600,
        'damage': 25,  # 50 HP / 2 shots = 25 damage per shot
        'count': 1,
        'spread': 2,
        'color': GREEN
    }
}
