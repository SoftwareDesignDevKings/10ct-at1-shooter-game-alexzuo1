import pygame
import app

class Bullet:
    def __init__(self, x, y, vx, vy, size):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size

        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(center=(self.x, self.y))
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (self.x, self.y)
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)

class HomingBullet(Bullet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.homing_strength = 0.1
        self.target = None
    
    def find_target(self, enemies):
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
        
        super().update()

class ExplosiveBullet(Bullet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.explosion_radius = 50
        self.exploded = False
    
    def explode(self, game):
        if not self.exploded:
            # Damage all enemies in radius
            for enemy in game.enemies[:]:
                dx = enemy.x - self.x
                dy = enemy.y - self.y
                if (dx**2 + dy**2) ** 0.5 <= self.explosion_radius:
                    enemy.take_damage(2)
            self.exploded = True