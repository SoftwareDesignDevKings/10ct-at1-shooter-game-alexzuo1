import pygame
import app
import math
from bullet import Bullet, HomingBullet, ExplosiveBullet  # Fixed import

class Player:
    def __init__(self, x, y, assets):
        self.x = x
        self.y = y
        self.speed = app.PLAYER_SPEED
        self.animations = assets["player"]
        self.state = "idle"
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 8
        self.image = self.animations[self.state][self.frame_index]
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.facing_left = False
        self.health = 5
        self.max_health = 5
        self.xp = 0
        self.level = 1
        
        # Bullet system attributes
        self.bullet_speed = 10
        self.bullet_size = 10
        self.bullet_count = 1
        self.shoot_cooldown = 20
        self.shoot_timer = 0
        self.bullets = []
        self.special_bullets = []  # Tracks homing/explosive bullets
        self.bullet_type = "normal"  # normal/homing/explosive
        self.armor_piercing = False

    def handle_input(self):
        keys = pygame.key.get_pressed()
        vel_x, vel_y = 0, 0
 
        if keys[pygame.K_LEFT]:
            vel_x -= self.speed
        if keys[pygame.K_RIGHT]:
            vel_x += self.speed
        if keys[pygame.K_UP]:
            vel_y -= self.speed
        if keys[pygame.K_DOWN]:
            vel_y += self.speed

        self.x += vel_x
        self.y += vel_y
        self.x = max(0, min(self.x, app.WIDTH))
        self.y = max(0, min(self.y, app.HEIGHT))
        self.rect.center = (self.x, self.y)

        if vel_x != 0 or vel_y != 0:
            self.state = "run"
        else:
            self.state = "idle"

        if vel_x < 0:
            self.facing_left = True
        elif vel_x > 0:
            self.facing_left = False

    def update(self, enemies=None):  # Added enemies parameter
        # Update normal bullets
        for bullet in self.bullets[:]:
            if isinstance(bullet, HomingBullet) and enemies:
                bullet.update(enemies)
            else:
                bullet.update()
                
            if (bullet.y < 0 or bullet.y > app.HEIGHT or 
                bullet.x < 0 or bullet.x > app.WIDTH):
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
                if bullet in self.special_bullets:
                    self.special_bullets.remove(bullet)

        # Update special bullets that need special handling
        for bullet in self.special_bullets[:]:
            if isinstance(bullet, ExplosiveBullet) and bullet.exploded:
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
                self.special_bullets.remove(bullet)

        # Animation updates
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            frames = self.animations[self.state]
            self.frame_index = (self.frame_index + 1) % len(frames)
            self.image = frames[self.frame_index]
            center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = center

        # Cooldown
        if self.shoot_timer < self.shoot_cooldown:
            self.shoot_timer += 1

    def draw(self, surface, offset_x=0, offset_y=0):
    #"""Draw the player character with optional screen shake offset
    #Args:
     #   surface: The pygame surface to draw on
      ## offset_y: Y offset for screen shake effects
    #"""
    # Draw player with correct facing direction
        if self.facing_left:
            flipped_image = pygame.transform.flip(self.image, True, False)
            surface.blit(flipped_image, (self.rect.x + offset_x, self.rect.y + offset_y))
        else:
            surface.blit(self.image, (self.rect.x + offset_x, self.rect.y + offset_y))
        
        # Draw all bullets
        for bullet in self.bullets:
            bullet.draw(surface, offset_x, offset_y)
        
    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
       
    def shoot_toward_position(self, tx, ty):
        if self.shoot_timer < self.shoot_cooldown:
            return

        dx = tx - self.x
        dy = ty - self.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist == 0:
            return

        angle_spread = 10
        base_angle = math.atan2(dy, dx)
        mid = (self.bullet_count - 1) / 2

        for i in range(self.bullet_count):
            offset = i - mid
            angle = base_angle + math.radians(angle_spread * offset)
            vx = math.cos(angle) * self.bullet_speed
            vy = math.sin(angle) * self.bullet_speed

            if self.bullet_type == "homing":
                bullet = HomingBullet(self.x, self.y, vx, vy, self.bullet_size)
                self.special_bullets.append(bullet)
            elif self.bullet_type == "explosive":
                bullet = ExplosiveBullet(self.x, self.y, vx, vy, self.bullet_size)
                self.special_bullets.append(bullet)
            else:
                bullet = Bullet(self.x, self.y, vx, vy, self.bullet_size)
            
            self.bullets.append(bullet)
        
        self.shoot_timer = 0

    def shoot_toward_mouse(self, pos):
        self.shoot_toward_position(pos[0], pos[1])

    def shoot_toward_enemy(self, enemy):
        self.shoot_toward_position(enemy.x, enemy.y)

    def add_xp(self, amount):
        self.xp += amount

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)