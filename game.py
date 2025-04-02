# game.py
import pygame
import random
import os

import app
from player import Player
from enemy import Enemy, FlyingEnemy, ArmoredEnemy, BossEnemy
from coin import Coin
import math

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((app.WIDTH, app.HEIGHT))
        pygame.display.set_caption("meow")
        self.clock = pygame.time.Clock()

        self.assets = app.load_assets()

        font_path = os.path.join("assets", "PressStart2P.ttf")
        self.font_small = pygame.font.Font(font_path, 18)
        self.font_large = pygame.font.Font(font_path, 32)

        self.background = self.create_random_background(
            app.WIDTH, app.HEIGHT, self.assets["floor_tiles"]
        )

        self.running = True
        self.game_over = False

        self.enemies = []
        self.enemy_spawn_timer = 0
        self.enemy_spawn_inverval = 60
        self.enemies_per_spawn = 1

        self.coins = []

        self.reset_game()

        self.in_level_up_menu = False
        self.upgrade_options = []

    def check_for_level_up(self):
        # Calculate the XP needed for next level (same formula you use in draw method)
        next_level_xp = self.player.level * self.player.level * 5
        
        # Check if player has enough XP to level up
        if self.player.xp >= next_level_xp:
            # Level up the player
            self.player.level += 1
            
            # Generate upgrade options
            self.upgrade_options = self.pick_random_upgrades(3)
            
            # Show the level up menu
            self.in_level_up_menu = True

    def reset_game(self):
        self.player = Player(app.WIDTH // 2, app.HEIGHT // 2, self.assets)
        self.enemies = []
        self.enemy_spawn_timer = 0
        self.enemies_per_spawn = 1
        
        self.coins = []
        self.game_over = False
    
    def create_random_background(self, width, height, floor_tiles):
        bg = pygame.Surface((width,height))
        tile_w = floor_tiles[0].get_width()
        tile_h = floor_tiles[0].get_height()

        for y in range(0, height, tile_h):
                for x in range(0, width, tile_w):
                    tile = random.choice(floor_tiles)
                    bg.blit(tile, (x, y))
        
        return bg
    
    def run(self):
        while self.running:
            self.clock.tick(app.FPS)
            self.handle_events()

            if self.in_level_up_menu:
                self.draw_upgrade_menu()  # Show the menu when leveling up
            elif not self.game_over:
                self.update()
            
            self.draw()  # Always draw, but this now includes the menu

        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif self.in_level_up_menu:  # Only handle upgrade choices
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                        index = event.key - pygame.K_1  # Convert key to index (0,1,2)
                        if 0 <= index < len(self.upgrade_options):
                            upgrade = self.upgrade_options[index]
                            self.apply_upgrade(self.player, upgrade)
                            self.in_level_up_menu = False  # Exit menu after choosing
            else:  # Normal gameplay inputs
                if event.type == pygame.KEYDOWN:
                    if self.game_over:
                        if event.key == pygame.K_r:
                            self.reset_game()
                        elif event.key == pygame.K_ESCAPE:
                            self.running = False
                    else:
                        if event.key == pygame.K_SPACE:
                            nearest_enemy = self.find_nearest_enemy()
                            if nearest_enemy:
                                self.player.shoot_toward_enemy(nearest_enemy)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.player.shoot_toward_mouse(event.pos)

    def update(self):
        self.player.handle_input()
        self.player.update(self.enemies)  # Pass enemies to player update

        for enemy in self.enemies:
            enemy.update(self.player)
        
        self.check_player_enemy_collisions()
        self.check_bullet_enemy_collisions()
        self.check_player_coin_collisions()

        if self.player.health <= 0:
            self.game_over = True
            return
        
        self.spawn_enemies()
        self.check_for_level_up()

    def draw_upgrade_menu(self):
        # Dark semi-transparent overlay
        overlay = pygame.Surface((app.WIDTH, app.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Black with 70% opacity
        self.screen.blit(overlay, (0, 0))
        
        # Title
        title_surf = self.font_large.render("LEVEL UP!", True, (255, 215, 0))  # Gold color
        title_rect = title_surf.get_rect(center=(app.WIDTH // 2, app.HEIGHT // 4))
        self.screen.blit(title_surf, title_rect)
        
        # Subtitle
        subtitle_surf = self.font_small.render(f"Level {self.player.level} Reached", True, (255, 255, 255))
        subtitle_rect = subtitle_surf.get_rect(center=(app.WIDTH // 2, app.HEIGHT // 4 + 50))
        self.screen.blit(subtitle_surf, subtitle_rect)
        
        # Instructions
        instruction_surf = self.font_small.render("Choose an upgrade (press 1, 2, or 3):", True, (255, 255, 255))
        instruction_rect = instruction_surf.get_rect(center=(app.WIDTH // 2, app.HEIGHT // 4 + 100))
        self.screen.blit(instruction_surf, instruction_rect)
        
        # List the upgrade options
        y_start = app.HEIGHT // 2 - (len(self.upgrade_options) - 1) * 25
        for i, upgrade in enumerate(self.upgrade_options):
            # Option number (now aligned with name's new position)
            key_surf = self.font_small.render(f"{i+1}.", True, (255, 215, 0))
            key_rect = key_surf.get_rect(midright=(app.WIDTH // 2 - 230, y_start + i * 50))
            self.screen.blit(key_surf, key_rect)
            
            # Upgrade name (moved further left)
            name_surf = self.font_small.render(upgrade["name"], True, (255, 255, 255))
            name_rect = name_surf.get_rect(midleft=(app.WIDTH // 2 - 210, y_start + i * 50))
            self.screen.blit(name_surf, name_rect)
            
            # Upgrade description (stays in original position)
            desc_surf = self.font_small.render(upgrade["desc"], True, (200, 200, 200))
            desc_rect = desc_surf.get_rect(midleft=(app.WIDTH // 2 + 100, y_start + i * 50))
            self.screen.blit(desc_surf, desc_rect)

    def draw(self):
        self.screen.blit(self.background, (0, 0))

        for coin in self.coins:
            coin.draw(self.screen)

        if not self.game_over:
            self.player.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        hp = max(0, min(self.player.health, 5))  
        health_img = self.assets["health"][hp]
        self.screen.blit(health_img, (10, 10))

        xp_text_surf = self.font_small.render(f"XP: {self.player.xp}", True, (255, 255, 255))
        self.screen.blit(xp_text_surf, (10, 70))

        next_level_xp = self.player.level * self.player.level * 5
        xp_to_next = max(0, next_level_xp - self.player.xp)
        xp_next_surf = self.font_small.render(f"Next Lvl XP: {xp_to_next}", True, (255, 255, 255))
        self.screen.blit(xp_next_surf, (10, 100))

        if self.game_over:
            self.draw_game_over_screen()

        if self.in_level_up_menu:
            self.draw_upgrade_menu()  # Make sure it gets drawn

        pygame.display.flip()
    
    def spawn_enemies(self):
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer >= self.enemy_spawn_inverval:
            self.enemy_spawn_timer = 0

            # Enemy type probabilities
            enemy_types = [
                (Enemy, 0.5),           # 50% regular
                (FlyingEnemy, 0.3),     # 30% flying
                (ArmoredEnemy, 0.15),   # 15% armored
                (BossEnemy, 0.05)       # 5% boss
            ]
            
            # Select a random enemy type based on the probabilities
            enemy_type, _ = random.choices([et[0] for et in enemy_types], [et[1] for et in enemy_types])[0]
            
            # Asset selection logic based on enemy type
            if enemy_type == Enemy:
                enemy_assets = ["enemyregular_0", "enemyregular_1", "enemyregular_2", "enemyregular_3"]
            elif enemy_type == FlyingEnemy:
                enemy_assets = ["flyingEnemy_0", "flyingEnemy_1", "flyingEnemy_2", "flyingEnemy_3"]
            elif enemy_type == ArmoredEnemy:
                enemy_assets = ["armoredEnemy_0", "armoredEnemy_1", "armoredEnemy_2","armoredEnemy_3"]
            elif enemy_type == BossEnemy:
                enemy_assets = ["bossEnemy_0", "bossEnemy_1", "bossEnemy_2", "bossEnemy_3"]

            # Choose a random asset from the appropriate list
            enemy_asset = random.choice(enemy_assets)

            # Select spawn position
            side = random.choice(["top", "bottom", "left", "right"])
            if side == "top":
                x = random.randint(0, app.WIDTH)
                y = -app.SPAWN_MARGIN
            elif side == "bottom":
                x = random.randint(0, app.WIDTH)
                y = app.HEIGHT + app.SPAWN_MARGIN
            elif side == "left":
                x = -app.SPAWN_MARGIN
                y = random.randint(0, app.HEIGHT)
            else:
                x = app.WIDTH + app.SPAWN_MARGIN
                y = random.randint(0, app.HEIGHT)

            # Load the selected enemy sprite from the assets folder
            enemy_sprites = self.assets["enemies"][enemy_asset]

            # Create the enemy instance
            enemy = enemy_type(self, x, y, enemy_type, enemy_sprites)

            # Append to the list of enemies
            self.enemies.append(enemy)




    def check_player_enemy_collisions(self):
        collided = False
        for enemy in self.enemies:
            if enemy.rect.colliderect(self.player.rect):
                collided = True
                break

        if collided:
            self.player.take_damage(1)
            px, py = self.player.x, self.player.y
            for enemy in self.enemies:
                enemy.set_knockback(px, py, app.PUSHBACK_DISTANCE)

    def draw_game_over_screen(self):
        # Dark overlay
        overlay = pygame.Surface((app.WIDTH, app.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Game Over text
        game_over_surf = self.font_large.render("GAME OVER!", True, (255, 0, 0))
        game_over_rect = game_over_surf.get_rect(center=(app.WIDTH // 2, app.HEIGHT // 2 - 50))
        self.screen.blit(game_over_surf, game_over_rect)

        # Prompt to restart or quit
        prompt_surf = self.font_small.render("Press R to Play Again or ESC to Quit", True, (255, 255, 255))
        prompt_rect = prompt_surf.get_rect(center=(app.WIDTH // 2, app.HEIGHT // 2 + 20))
        self.screen.blit(prompt_surf, prompt_rect)

    def find_nearest_enemy(self):
        if not self.enemies:
            return None
        nearest = None
        min_dist = float('inf')
        px, py = self.player.x, self.player.y
        for enemy in self.enemies:
            dist = math.sqrt((enemy.x - px)**2 + (enemy.y - py)**2)
            if dist < min_dist:
                min_dist = dist
                nearest = enemy
        return nearest
    
    def check_bullet_enemy_collisions(self):
        for bullet in self.player.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
                    
                    # Check if this is an explosive bullet
                    if hasattr(bullet, 'explode') and not bullet.exploded:
                        bullet.explode(self)  # Pass game instance
                    
                    # Handle enemy damage/death
                    if hasattr(enemy, 'take_damage'):
                        is_dead = enemy.take_damage(1)
                        if is_dead:
                            new_coin = Coin(enemy.x, enemy.y)
                            self.coins.append(new_coin)
                            self.enemies.remove(enemy)
                    break  # Break after hitting one enemy
    
    def check_player_coin_collisions(self):
        coins_collected = []
        for coin in self.coins:
            if coin.rect.colliderect(self.player.rect):
                coins_collected.append(coin)
                self.player.add_xp(1)

        for c in coins_collected:
            if c in self.coins:
                self.coins.remove(c)

    def pick_random_upgrades(self, num):
        possible_upgrades = [
            {"name": "Homing Bullets", "type": "bullet", "desc": "Bullets track enemies"},
            {"name": "Explosive Rounds", "type": "bullet", "desc": "Bullets explode on impact"},
            {"name": "Armor Piercing", "type": "bullet", "desc": "Ignore enemy armor"},
            {"name": "Rapid Fire", "type": "shoot", "desc": "Double fire rate"},
            {"name": "Health Boost", "type": "health", "desc": "+2 Max Health"}
        ]
        return random.sample(possible_upgrades, k=num)

    def apply_upgrade(self, player, upgrade):
        name = upgrade["name"]
        if name == "Homing Bullets":
            player.bullet_type = "homing"
        elif name == "Explosive Rounds":
            player.bullet_type = "explosive"
        elif name == "Armor Piercing":
            player.armor_piercing = True
        elif name == "Rapid Fire":
            player.shoot_cooldown = max(1, int(player.shoot_cooldown * 0.5))
        elif name == "Health Boost":
            player.max_health += 2
            player.health += 2