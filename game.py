import pygame
import random
import os
import math
import app
from player import Player
from enemy import Enemy, FlyingEnemy, ArmoredEnemy, BossEnemy
from coin import Coin

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((app.WIDTH, app.HEIGHT))
        pygame.display.set_caption("meow")
        self.clock = pygame.time.Clock()

        self.enemy_asset_map = {
            Enemy: "regular",
            FlyingEnemy: "flying",
            ArmoredEnemy: "armored",
            BossEnemy: "boss"
        }

        self.assets = app.load_assets()
        self.running = True
        self.game_over = False
        self.enemies = []
        self.coins = []
        self.enemy_spawn_timer = 0
        self.enemy_spawn_interval = 60
        self.enemies_per_spawn = 1
        self.in_level_up_menu = False
        self.upgrade_options = []
        self.enemies_killed = 0
        self.boss_level = 0
        self.current_boss = None
        self.screen_shake = 0
        self.screen_shake_offset = [0, 0]
        self.boss_music_playing = False

        font_path = os.path.join("assets", "PressStart2P.ttf")
        self.font_small = pygame.font.Font(font_path, 18)
        self.font_large = pygame.font.Font(font_path, 32)

        self.background = self.create_random_background(
            app.WIDTH, app.HEIGHT, self.assets["floor_tiles"]
        )
        self.reset_game()

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

    
    def spawn_boss(self):
        """Spawns a scaled boss with dramatic effects"""
        # Clear existing enemies
        self.enemies = [e for e in self.enemies if isinstance(e, BossEnemy)]
        
        # Calculate boss stats
        boss_scale = 1.0 + (self.boss_level * 0.5)
        health = 10 + (self.boss_level * 5)
        speed = max(1.0, 2.0 - (self.boss_level * 0.1))

        # Spawn position (top center)
        x, y = app.WIDTH // 2, -200
        boss = BossEnemy(
            self, x, y, "boss", self.assets["enemies"],
            health=health,
            speed=speed,
            scale=boss_scale
        )
        self.enemies.append(boss)
        self.current_boss = boss
        self.screen_shake = 30  # Screen shake effect

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
        # Handle screen shake
        if self.screen_shake > 0:
            self.screen_shake -= 1
            self.screen_shake_offset = [
                random.randint(-5, 5),
                random.randint(-5, 5)
            ]
        else:
            self.screen_shake_offset = [0, 0]

        # Existing update logic
        self.player.handle_input()
        self.player.update(self.enemies)

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
    
    def draw_boss_healthbar(self):
        """Draws dramatic boss health bar"""
        if not self.current_boss or self.current_boss not in self.enemies:
            return

        boss = self.current_boss
        bar_width, bar_height = 600, 30
        border_thickness = 4
        bar_x = (app.WIDTH - bar_width) // 2
        bar_y = 20

        # Background
        pygame.draw.rect(
            self.screen, (50, 50, 50),
            (bar_x - border_thickness,
             bar_y - border_thickness,
             bar_width + 2*border_thickness,
             bar_height + 2*border_thickness)
        )

        # Health fill
        health_pct = boss.health / boss.max_health
        health_width = max(0, bar_width * health_pct)
        
        # Color changes based on health
        if health_pct < 0.25:
            health_color = (255, 40, 40)  # Red when low
        else:
            health_color = (255, 0, 0)   # Normal red

        pygame.draw.rect(
            self.screen, health_color,
            (bar_x, bar_y, health_width, bar_height)
        )

        # Pulsing effect when low health
        if health_pct < 0.25:
            pulse = int(10 * abs(math.sin(pygame.time.get_ticks() / 200)))
            pygame.draw.rect(
                self.screen, (255, 255, 255),
                (bar_x, bar_y, health_width, bar_height),
                pulse//2
            )

        # Boss level text
        boss_text = self.font_large.render(
            f"BOSS LEVEL {self.boss_level}",
            True, (255, 215, 0))  # Gold color
        self.screen.blit(
            boss_text,
            (app.WIDTH//2 - boss_text.get_width()//2, bar_y - 40)
        )

    def draw(self):
        # Apply screen shake offset
        shake_x, shake_y = self.screen_shake_offset
        self.screen.blit(self.background, (shake_x, shake_y))

        # Draw game elements with offset
        for coin in self.coins:
            coin.draw(self.screen, shake_x, shake_y)

        if not self.game_over:
            self.player.draw(self.screen, shake_x, shake_y)

        for enemy in self.enemies:
            enemy.draw(self.screen, shake_x, shake_y)

        # Draw UI elements (not affected by shake)
        self.draw_ui()
        self.draw_boss_healthbar()

        if self.game_over:
            self.draw_game_over_screen()

        if self.in_level_up_menu:
            self.draw_upgrade_menu()

        pygame.display.flip()

    
    def spawn_enemies(self):
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer >= self.enemy_spawn_interval:
            self.enemy_spawn_timer = 0

            enemy_types = [
                (Enemy, 0.6, "regular"),
                (FlyingEnemy, 0.25, "flying"),
                (ArmoredEnemy, 0.1, "armored"), 
                (BossEnemy, 0.05, "boss")
            ]
            
            # Fixed selection - gets the whole tuple-similar to list,set,dictonary first
            enemy_class, prob, asset_key = random.choices(
                enemy_types,
                weights=[et[1] for et in enemy_types]
            )[0]

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

            enemy = enemy_class(self, x, y, asset_key, self.assets["enemies"])
            self.enemies.append(enemy)

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
                    
                    if hasattr(bullet, 'explode') and not bullet.exploded:
                        bullet.explode(self)
                    
                    if hasattr(enemy, 'take_damage'):
                        enemy_killed = enemy.take_damage(1)
                        if enemy_killed:
                            self.enemies_killed += 1
                            coins_to_spawn = 1
                            
                            if isinstance(enemy, BossEnemy):
                                coins_to_spawn = 10 + self.boss_level * 5
                                self.current_boss = None
                            
                            # Spawn coins
                            for _ in range(coins_to_spawn):
                                self.coins.append(Coin(enemy.x, enemy.y))
                            
                            # Spawn boss every 10 kills
                            if self.enemies_killed % 10 == 0:
                                self.boss_level = self.enemies_killed // 10
                                self.spawn_boss()
                    break
    
    def check_player_enemy_collisions(self):
        for enemy in self.enemies[:]:
            if self.player.rect.colliderect(enemy.rect):
                self.player.take_damage(1)
                enemy.set_knockback(self.player.x, self.player.y, app.PUSHBACK_DISTANCE)
    
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

    def draw_ui(self):
        """Draw the player's health, level, and score information."""
        # Draw player health
        health_text = self.font_small.render(f"Health: {self.player.health}/{self.player.max_health}", True, (255, 255, 255))
        self.screen.blit(health_text, (20, 20))
        
        # Draw player level and XP
        next_level_xp = self.player.level * self.player.level * 5
        xp_text = self.font_small.render(f"Level: {self.player.level} (XP: {self.player.xp}/{next_level_xp})", True, (255, 255, 255))
        self.screen.blit(xp_text, (20, 50))
        
        # Draw enemies killed count
        kills_text = self.font_small.render(f"Kills: {self.enemies_killed}", True, (255, 255, 255))
        self.screen.blit(kills_text, (20, 80))