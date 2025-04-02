import pygame
import math
from app import DEFAULT_ENEMY_SPEED, ENEMY_SCALE_FACTOR, ENEMY_KNOCKBACK_SPEED

class Enemy:
    def __init__(self, game, x, y, enemy_type, enemy_assets, speed=DEFAULT_ENEMY_SPEED):
        self.game = game
        self.x = x
        self.y = y
        self.speed = speed
        self.enemy_type = enemy_type
        
        # Load image from assets
        self.frames = enemy_assets[enemy_type]
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(self.x, self.y))
        
        # Basic enemy properties
        self.facing_left = False
        self.is_boss = (enemy_type == 'boss')
        self.scale_factor = ENEMY_SCALE_FACTOR if self.is_boss else 1
        self.health = 10 if self.is_boss else 2
        self.max_health = self.health
        
        # Combat properties
        self.knockback_dist_remaining = 0
        self.knockback_dx = 0
        self.knockback_dy = 0
        self.dying = False

    def update(self, player=None):
        if self.dying:
            return
            
        # Simple animation - cycle through frames
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.image = self.frames[self.current_frame]
        
        # Apply scaling if needed
        if self.scale_factor != 1:
            w = int(self.image.get_width() * self.scale_factor)
            h = int(self.image.get_height() * self.scale_factor)
            self.image = pygame.transform.scale(self.image, (w, h))
            
        # Flip image if facing left
        if self.facing_left:
            self.image = pygame.transform.flip(self.image, True, False)
            
        # Update rect position
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.die()

    def die(self):
        self.dying = True
        if self in self.game.enemies:
            self.game.enemies.remove(self)

    def set_knockback(self, source_x, source_y, distance):
        dx = self.x - source_x
        dy = self.y - source_y
        length = math.sqrt(dx*dx + dy*dy)
        
        if length > 0:  # Avoid division by zero
            self.knockback_dx = dx / length
            self.knockback_dy = dy / length
            self.knockback_dist_remaining = distance

    def draw(self, surface, offset_x=0, offset_y=0):
        if not self.dying:
            pos_x = self.x - offset_x - self.image.get_width() // 2
            pos_y = self.y - offset_y - self.image.get_height() // 2
            surface.blit(self.image, (pos_x, pos_y))


class FlyingEnemy(Enemy):
    def __init__(self, game, x, y, enemy_type, enemy_assets, speed=None):
        if speed is None:
            speed = DEFAULT_ENEMY_SPEED * 1.5
        super().__init__(game, x, y, enemy_type, enemy_assets, speed)
        self.health = 1
        self.max_health = 1


class ArmoredEnemy(Enemy):
    def __init__(self, game, x, y, enemy_type, enemy_assets, speed=None):
        if speed is None:
            speed = DEFAULT_ENEMY_SPEED
        super().__init__(game, x, y, enemy_type, enemy_assets, speed)
        self.health = 4
        self.max_health = 4
        self.armor = 0.5  # 50% damage reduction


class BossEnemy(Enemy):
    def __init__(self, game, x, y, enemy_type, enemy_assets, speed=None):
        if speed is None:
            speed = DEFAULT_ENEMY_SPEED * 0.75  # Bosses are slower
        super().__init__(game, x, y, enemy_type, enemy_assets, speed)
        self.health = 20
        self.max_health = 20