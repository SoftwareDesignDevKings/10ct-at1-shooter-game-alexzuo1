import pygame
import os

# --------------------------------------------------------------------------
#                               CONSTANTS
# --------------------------------------------------------------------------

WIDTH = 1200
HEIGHT = 700
FPS = 60

PLAYER_SPEED = 3
DEFAULT_ENEMY_SPEED = 1

SPAWN_MARGIN = 50

ENEMY_SCALE_FACTOR = 3
PLAYER_SCALE_FACTOR = 2
FLOOR_TILE_SCALE_FACTOR = 2
HEALTH_SCALE_FACTOR = 3

PUSHBACK_DISTANCE = 80
ENEMY_KNOCKBACK_SPEED = 5

# --------------------------------------------------------------------------
#                       ASSET LOADING FUNCTIONS
# --------------------------------------------------------------------------

def load_frames(prefix, frame_count, scale_factor=1, folder="assets"):
    frames = []
    for i in range(frame_count):
        image_path = os.path.join(folder, f"{prefix}_{i}.png")
        img = pygame.image.load(image_path).convert_alpha()

        if scale_factor != 1:
            w = img.get_width() * scale_factor
            h = img.get_height() * scale_factor
            img = pygame.transform.scale(img, (w, h))

        frames.append(img)
    return frames

def load_floor_tiles(folder="assets"):
    floor_tiles = []
    for i in range(8):
        path = os.path.join(folder, f"floor_{i}.png")
        tile = pygame.image.load(path).convert()

        if FLOOR_TILE_SCALE_FACTOR != 1:
            tw = tile.get_width() * FLOOR_TILE_SCALE_FACTOR
            th = tile.get_height() * FLOOR_TILE_SCALE_FACTOR
            tile = pygame.transform.scale(tile, (tw, th))

        floor_tiles.append(tile)
    return floor_tiles

def load_assets():
    assets = {
        "enemies": {
            "regular": load_frames("enemy_regular", 4),  # enemy_regular_0.png, etc.
            "flying": load_frames("flying_Enemy", 4),    # flying_Enemy_0.png
            "armored": load_frames("armored_Enemy", 4),  # armored_Enemy_0.png
            "boss": load_frames("boss_Enemy", 4)         # boss_Enemy_0.png
        },
        # Player
        "player": {
            "idle": load_frames("player_idle", 4, scale_factor=PLAYER_SCALE_FACTOR),
            "run": load_frames("player_run", 4, scale_factor=PLAYER_SCALE_FACTOR),
        },
        # Floor tiles
        "floor_tiles": load_floor_tiles(),
        # Health images
        "health": load_frames("health", 6, scale_factor=HEALTH_SCALE_FACTOR)
    }
    return assets