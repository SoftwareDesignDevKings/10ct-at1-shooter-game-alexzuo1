import pygame
import app
import math
from bullet import Bullet

class Enemy:
    def __init__(self, game, x, y, enemy_type, enemy_assets, speed=app.DEFAULT_ENEMY_SPEED):
        self.game = game  # Store game reference
        self.x = x
        self.y = y
        self.speed = speed
        
        self.frames = enemy_assets[enemy_type]
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 8
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=(self.x, self.y))
        
        self.enemy_type = enemy_type 
        self.facing_left = False

        self.knockback_dist_remaining = 0
        self.knockback_dx = 0
        self.knockback_dy = 0
        
        self.health = 1
        self.max_health = 1  

    def take_damage(self, amount):
        """Applies damage, considering armor-piercing effects."""
        if self.game.player.armor_piercing:
            actual_damage = amount
        else:
            actual_damage = max(0, amount - getattr(self, 'armor', 0))  # Default armor to 0 if missing
        
        self.health -= actual_damage
        if self.health <= 0:
            self.die()

    def die(self):
        """Handles enemy death logic."""
        self.game.enemies.remove(self)  # Remove from game enemy list

    def update(self, player):
        if self.knockback_dist_remaining > 0:
            self.apply_knockback()
        else:
            self.move_toward_player(player)
        
        # Resize enemy sprite based on type
        size = 60 if self.enemy_type.startswith("enemyboss") else 45 if self.enemy_type.startswith("enemyarmored") else 30
        self.image = pygame.transform.scale(self.image, (size, size))

        self.animate()

    def move_toward_player(self, player):
        """Moves enemy toward the player."""
        dx = player.x - self.x
        dy = player.y - self.y
        dist = (dx**2 + dy**2) ** 0.5
        
        if dist != 0:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
        
        self.facing_left = dx < 0
        self.rect.center = (self.x, self.y)

    def apply_knockback(self):
        """Applies knockback effect."""
        step = min(app.ENEMY_KNOCKBACK_SPEED, self.knockback_dist_remaining)
        self.knockback_dist_remaining -= step

        self.x += self.knockback_dx * step
        self.y += self.knockback_dy * step

        self.facing_left = self.knockback_dx < 0
        self.rect.center = (self.x, self.y)

    def animate(self):
        """Handles animation updates."""
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]
            self.rect = self.image.get_rect(center=self.rect.center)

    def draw(self, surface):
        """Draws the enemy and health bar."""
        image = pygame.transform.flip(self.image, True, False) if self.facing_left else self.image
        surface.blit(image, self.rect)

        # Draw health bar
        health_width, health_height = 40, 6
        border_rect = pygame.Rect(self.x - health_width // 2, self.y - 40, health_width, health_height)
        health_rect = pygame.Rect(self.x - health_width // 2, self.y - 40, health_width * (self.health / self.max_health), health_height)

        pygame.draw.rect(surface, (255, 0, 0), border_rect)  # Red background
        pygame.draw.rect(surface, (0, 255, 0), health_rect)  # Green health

    def set_knockback(self, px, py, dist):
        """Calculates knockback effect."""
        dx = self.x - px
        dy = self.y - py
        length = math.sqrt(dx*dx + dy*dy)
        if length != 0:
            self.knockback_dx = dx / length
            self.knockback_dy = dy / length
            self.knockback_dist_remaining = dist

class FlyingEnemy(Enemy):
    def __init__(self, game, *args, **kwargs):
        super().__init__(game, *args, **kwargs)
        self.health = self.max_health = 2
        self.speed *= 1.5

class ArmoredEnemy(Enemy):
    def __init__(self, game, *args, **kwargs):
        super().__init__(game, *args, **kwargs)
        self.health = self.max_health = 3
        self.armor = 2

class BossEnemy(Enemy):
    def __init__(self, game, *args, **kwargs):
        super().__init__(game, *args, **kwargs)
        self.health = self.max_health = 10
        self.speed = 2

    def move_toward_player(self, player):
        """Moves faster toward the player."""
        dx = player.x - self.x
        dy = player.y - self.y
        dist = (dx**2 + dy**2) ** 0.5
        
        if dist != 0:
            self.x += (dx / dist) * self.speed * 1.2
            self.y += (dy / dist) * self.speed * 1.2
        
        self.rect.center = (self.x, self.y)

    def create_shockwave(self, player):
        """Creates a shockwave attack."""
        for angle in range(0, 360, 45):
            dx = math.cos(math.radians(angle)) * 5
            dy = math.sin(math.radians(angle)) * 5
            new_bullet = Bullet(self.x, self.y, dx, dy, 15)
            player.bullets.append(new_bullet)