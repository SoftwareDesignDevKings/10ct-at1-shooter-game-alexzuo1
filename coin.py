import pygame
import app
import os
import math
import random

class Coin:
    """
    The Coin class represents collectible items dropped by defeated enemies.
    Players can collect coins to gain XP.
    """
    def __init__(self, x, y):
        """
        Initialize a new coin object.
        
        Args:
            x, y: Initial position coordinates
        """
        self.x = x
        self.y = y
        
        # Add randomness to initial coin position for spread effect
        self.x += random.randint(-10, 10)
        self.y += random.randint(-10, 10)
        
        # Load the coin image
        try:
            coin_path = os.path.join("assets", "coin.png")
            self.original_image = pygame.image.load(coin_path).convert_alpha()
            self.image = pygame.transform.scale(self.original_image, (20, 20))
        except pygame.error:
            # Fallback if image loading fails
            self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 215, 0), (10, 10), 10)
            pygame.draw.circle(self.image, (255, 255, 0), (10, 10), 6)
        
        self.rect = self.image.get_rect(center=(self.x, self.y))
        
        # Animation variables
        self.animation_timer = 0
        self.animation_speed = 5
        self.scale_factor = 1.0
        self.scale_direction = 0.02
        self.angle = 0
        
        # Movement variables for a more dynamic feel
        self.velocity_y = -2  # Initial upward movement
        self.gravity = 0.1
        self.bounce_factor = 0.5
        self.friction = 0.95

    def update(self):
        """Update coin position, animation and physics"""
        # Apply gravity and friction
        self.velocity_y += self.gravity
        self.y += self.velocity_y
        self.velocity_y *= self.friction
        
        # Bounce if hit ground
        if self.y > self.rect.height + app.HEIGHT - 100:
            self.y = app.HEIGHT - 100
            if abs(self.velocity_y) > 0.5:
                self.velocity_y = -self.velocity_y * self.bounce_factor
            else:
                self.velocity_y = 0
        
        # Pulsing animation
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.scale_factor += self.scale_direction
            if self.scale_factor > 1.2 or self.scale_factor < 0.8:
                self.scale_direction *= -1
            
            # Rotate coin
            self.angle = (self.angle + 5) % 360
            
            # Update image with new size and rotation
            rotated = pygame.transform.rotate(self.original_image, self.angle)
            new_size = int(20 * self.scale_factor)
            self.image = pygame.transform.scale(rotated, (new_size, new_size))
            
            # Keep center position
            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center
            
        # Update rect position
        self.rect.center = (self.x, self.y)

    def draw(self, surface, offset_x=0, offset_y=0):
        """
        Draw the coin on the given surface.
        
        Args:
            surface: The surface to draw on
            offset_x, offset_y: Screen shake offsets
        """
        # Apply screen shake offset
        adjusted_rect = self.rect.copy()
        adjusted_rect.x += offset_x
        adjusted_rect.y += offset_y
        surface.blit(self.image, adjusted_rect)