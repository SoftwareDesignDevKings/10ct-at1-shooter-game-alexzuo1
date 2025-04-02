import pygame
import app
import os
import math

class Bullet:
    """
    The Bullet class represents projectiles fired by the player.
    It handles movement, rendering, and collision detection.
    """
    def __init__(self, x, y, vx, vy, size):
        """
        Initialize a new bullet object.
        
        Args:
            x, y: Initial position coordinates
            vx, vy: Velocity components
            size: Size of the bullet
        """
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        
        # Calculate bullet rotation based on velocity
        self.angle = math.degrees(math.atan2(vy, vx))
        
        # Load the bullet image
        try:
            bullet_path = os.path.join("assets", "bullet.png")
            self.original_image = pygame.image.load(bullet_path).convert_alpha()
            self.image = pygame.transform.scale(self.original_image, (self.size, self.size))
        except pygame.error:
            # Fallback if image loading fails
            self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 255, 100), 
                              (self.size//2, self.size//2), self.size//2)
            pygame.draw.circle(self.image, (255, 255, 255), 
                              (self.size//2, self.size//2), self.size//4)
        
        self.rect = self.image.get_rect(center=(self.x, self.y))
    
    def update(self):
        """Update bullet position and handle rotation"""
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (self.x, self.y)
    
    def draw(self, surface, offset_x=0, offset_y=0):
        """
        Draw the bullet on the given surface.
        
        Args:
            surface: The surface to draw on
            offset_x, offset_y: Screen shake offsets
        """
        # Apply screen shake offset
        adjusted_rect = self.rect.copy()
        adjusted_rect.x += offset_x
        adjusted_rect.y += offset_y
        surface.blit(self.image, adjusted_rect)
        

class HomingBullet(Bullet):
    """
    A bullet that follows enemies. Inherits from the Bullet class.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.homing_strength = 0.1
        self.target = None
        
        # Give homing bullets a different color tint
        try:
            # Tint the bullet blue
            self.image.fill((100, 100, 255, 150), special_flags=pygame.BLEND_RGBA_MULT)
        except:
            pass
    
    def find_target(self, enemies):
        """Find the closest enemy to target"""
        if not enemies:
            return None
        closest = None
        min_dist = float('inf')
        for enemy in enemies:
            dist = (self.x - enemy.x)**2 + (self.y - enemy.y)**2
            if dist < min_dist:
                min_dist = dist
                closest = enemy
        return closest
    
    def update(self, enemies=None):
        """Update the homing bullet's trajectory to follow enemies"""
        if enemies:
            if not self.target or self.target not in enemies:
                self.target = self.find_target(enemies)
            
            if self.target:
                dx = self.target.x - self.x
                dy = self.target.y - self.y
                dist = (dx**2 + dy**2) ** 0.5
                if dist != 0:
                    self.vx += dx/dist * self.homing_strength
                    self.vy += dy/dist * self.homing_strength
                    
                    # Calculate new angle for rotation
                    self.angle = math.degrees(math.atan2(self.vy, self.vx))
        
        super().update()


class ExplosiveBullet(Bullet):
    """
    A bullet that explodes on impact, dealing area damage.
    Inherits from the Bullet class.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.explosion_radius = 50
        self.exploded = False
        
        # Give explosive bullets a red tint
        try:
            # Tint the bullet red
            self.image.fill((255, 100, 100, 150), special_flags=pygame.BLEND_RGBA_MULT)
        except:
            pass
    
    def explode(self, game):
        """Handle the explosion effect and damage"""
        if not self.exploded:
            # Damage all enemies in radius
            for enemy in game.enemies[:]:
                dx = enemy.x - self.x
                dy = enemy.y - self.y
                if (dx**2 + dy**2) ** 0.5 <= self.explosion_radius:
                    enemy.take_damage(2)
                    
                    # Add visual effect - knockback all enemies in radius
                    enemy.set_knockback(self.x, self.y, 20)
            
            # Add explosion visual effect
            self.exploded = True