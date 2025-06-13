import pygame
import sys
import math
import random
import time
import threading
from scripts.player import Player
from scripts.bomb import Bomb, TimerBomb, CrackingBomb
from scripts.island import Island
from scripts.camera import Camera
from scripts.enemy import Enemy
from scripts.powerup import PowerUp
from scripts.recorder_fallback import GameRecorder
from scripts.sound_manager import SoundManager

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
SKY_BLUE = (135, 206, 235)
GREEN = (34, 139, 34)

class Game:
    def __init__(self):
        # Set up display - check if fullscreen is enabled
        self.fullscreen = False
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.screen_width = self.screen.get_width()
            self.screen_height = self.screen.get_height()
        else:
            self.screen_width = SCREEN_WIDTH
            self.screen_height = SCREEN_HEIGHT
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
            
        pygame.display.set_caption("Island Bomber")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.score = 0
        self.show_fps = True  # Debug option to show FPS
        
        # Game objects
        self.island = Island()
        self.player = Player(self.screen_width // 2, self.screen_height // 2)
        self.camera = Camera(self.screen_width, self.screen_height)
        self.bombs = []
        self.enemies = []
        self.powerups = []
        self.current_bomb_type = "timer"  # Default bomb type
        
        # Game recorder
        self.recorder = GameRecorder()
        
        # Sound manager
        self.sound_manager = SoundManager()
        
        # Spawn initial enemies
        self.spawn_enemies(5)
            
        # Powerup spawn timer
        self.powerup_spawn_timer = 300  # 5 seconds at 60 FPS
        
        # Initialize held bomb to None
        self.held_bomb = None
    def start_holding_bomb(self):
        # Check if player has bombs available
        if self.player.bombs <= 0:
            print("Out of bombs! Waiting for reload...")
            return
            
        # Create a bomb to hold
        if self.current_bomb_type == "timer":
            # Create a timer bomb at player's position
            self.held_bomb = TimerBomb(self.player.x, self.player.y, 0, 0)
            self.held_bomb.held = True  # Mark as being held
            
            # Decrease player's bomb count
            self.player.bombs -= 1
            
            print("Holding timer bomb... Release to throw!")
        else:
            # For other bomb types, just throw immediately
            self.throw_bomb()
            
    def throw_held_bomb(self):
        if not hasattr(self, 'held_bomb') or not self.held_bomb:
            return
            
        # Get mouse position for direction
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Calculate direction vector from screen center
        screen_center_x = self.screen_width // 2
        screen_center_y = self.screen_height // 2
        dir_x = mouse_x - screen_center_x
        dir_y = mouse_y - screen_center_y
        
        # Normalize direction
        length = math.sqrt(dir_x**2 + dir_y**2)
        if length > 0:
            dir_x /= length
            dir_y /= length
        
        # Calculate throw velocity based on distance to cursor
        distance_factor = min(1.0, length / 300)  # Cap at 300 pixels distance
        throw_speed = 5 + 8 * distance_factor  # Speed between 5-13 based on cursor distance
        
        # Update the held bomb's properties for throwing
        self.held_bomb.dir_x = dir_x
        self.held_bomb.dir_y = dir_y
        self.held_bomb.speed = throw_speed
        self.held_bomb.z_velocity = 7 + 3 * distance_factor  # Higher arc for longer throws
        self.held_bomb.held = False  # No longer being held
        
        # Calculate starting position based on player's arm position
        arm_angle = math.atan2(dir_y, dir_x)
        arm_length = 30  # Length of player's arm
        self.held_bomb.x = self.player.x + math.cos(arm_angle) * arm_length
        self.held_bomb.y = self.player.y + math.sin(arm_angle) * arm_length
        
        # Add to bombs list
        self.bombs.append(self.held_bomb)
        
        # Play throw sound
        self.sound_manager.play('throw')
        
        # Clear held bomb
        self.held_bomb = None
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Restart game if game over
            if self.game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.__init__()
                    return
            
            # Toggle fullscreen
            if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                self.toggle_fullscreen()
                
            # Toggle FPS display
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
                self.show_fps = not self.show_fps
                print(f"FPS display: {'on' if self.show_fps else 'off'}")
            
            # Sound controls
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    muted = self.sound_manager.toggle_mute()
                    print(f"Sound {'muted' if muted else 'unmuted'}")
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    self.sound_manager.set_master_volume(self.sound_manager.master_volume + 0.1)
                    print(f"Volume: {int(self.sound_manager.master_volume * 100)}%")
                elif event.key == pygame.K_MINUS:
                    self.sound_manager.set_master_volume(self.sound_manager.master_volume - 0.1)
                    print(f"Volume: {int(self.sound_manager.master_volume * 100)}%")
            
            # Bomb throwing
            if not self.game_over:
                # Mouse button down - start holding bomb
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Check if clicked on record button
                    if self.recorder.check_button_click(event.pos):
                        self.recorder.toggle_recording()
                    else:
                        # Start holding a bomb
                        self.start_holding_bomb()
                
                # Mouse button up - throw the held bomb
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    # Throw the held bomb if we have one
                    if hasattr(self, 'held_bomb') and self.held_bomb:
                        self.throw_held_bomb()
            
            # Switch bomb type
            if not self.game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.current_bomb_type = "timer"
                    print("Selected: Timer Bomb")
                elif event.key == pygame.K_2:
                    self.current_bomb_type = "cracking"
                    print("Selected: Cracking Bomb")
                elif event.key == pygame.K_3:
                    self.current_bomb_type = "regular"
                    print("Selected: Regular Bomb")
                    
    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            # Save current screen size
            self.windowed_size = (self.screen_width, self.screen_height)
            # Switch to fullscreen
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.screen_width = self.screen.get_width()
            self.screen_height = self.screen.get_height()
        else:
            # Switch back to windowed mode
            self.screen_width, self.screen_height = self.windowed_size if hasattr(self, 'windowed_size') else (SCREEN_WIDTH, SCREEN_HEIGHT)
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
            
        # Update camera dimensions
        self.camera.screen_width = self.screen_width
        self.camera.screen_height = self.screen_height
        
        print(f"Fullscreen: {self.fullscreen}, Resolution: {self.screen_width}x{self.screen_height}")
    def throw_bomb(self):
        # Check if player has bombs available
        if self.player.bombs <= 0:
            print("Out of bombs! Waiting for reload...")
            return
            
        # Get mouse position for direction
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Calculate direction vector from screen center
        screen_center_x = self.screen_width // 2
        screen_center_y = self.screen_height // 2
        dir_x = mouse_x - screen_center_x
        dir_y = mouse_y - screen_center_y
        
        # Normalize direction
        length = math.sqrt(dir_x**2 + dir_y**2)
        if length > 0:
            dir_x /= length
            dir_y /= length
        
        # Calculate throw velocity based on distance to cursor (more realistic)
        # Closer cursor = slower throw, further cursor = faster throw
        distance_factor = min(1.0, length / 300)  # Cap at 300 pixels distance
        throw_speed = 5 + 8 * distance_factor  # Speed between 5-13 based on cursor distance
        
        # Calculate starting position based on player's arm position
        # Get arm angle from mouse position
        arm_angle = math.atan2(dir_y, dir_x)
        arm_length = 30  # Length of player's arm
        
        # Start bomb at the end of player's arm
        start_x = self.player.x + math.cos(arm_angle) * arm_length
        start_y = self.player.y + math.sin(arm_angle) * arm_length
        
        # Create the appropriate bomb type
        if self.current_bomb_type == "timer":
            bomb = TimerBomb(start_x, start_y, dir_x, dir_y)
        elif self.current_bomb_type == "cracking":
            bomb = CrackingBomb(start_x, start_y, dir_x, dir_y)
        else:
            bomb = Bomb(start_x, start_y, dir_x, dir_y)
            
        # Apply custom throw speed
        bomb.speed = throw_speed
        
        # Add vertical arc to throw
        bomb.z_velocity = 7 + 3 * distance_factor  # Higher arc for longer throws
        
        # Apply damage boost if active
        if hasattr(self.player, 'damage_boost') and self.player.damage_boost > 1.0:
            if not hasattr(bomb, 'damage_multiplier'):
                bomb.damage_multiplier = 1.0
            bomb.damage_multiplier *= self.player.damage_boost
            
        self.bombs.append(bomb)
        
        # Decrease player's bomb count
        self.player.bombs -= 1
        
        # Play throw sound
        self.sound_manager.play('throw')
    def update(self):
        if self.game_over:
            return
            
        # Update player
        keys = pygame.key.get_pressed()
        self.player.update(keys)
        
        # Update camera
        self.camera.update(self.player)
        
        # Update held bomb if we have one
        if hasattr(self, 'held_bomb') and self.held_bomb:
            # Update the bomb's position to follow the player
            self.held_bomb.x = self.player.x
            self.held_bomb.y = self.player.y
            
            # Update the bomb (this will count down the timer)
            self.held_bomb.update()
            
            # If the bomb exploded while being held, it damages the player
            if self.held_bomb.exploding:
                print("Bomb exploded while being held!")
                self.player.take_damage(50)  # Direct damage for holding too long
                self.bombs.append(self.held_bomb)  # Add to bombs list for explosion effects
                self.held_bomb = None  # Clear held bomb
        
        # Update powerup spawn timer
        self.powerup_spawn_timer -= 1
        if self.powerup_spawn_timer <= 0:
            self.spawn_powerup()
            self.powerup_spawn_timer = random.randint(300, 600)  # 5-10 seconds
        
        # Update powerups
        powerups_to_remove = []
        for i, powerup in enumerate(self.powerups):
            if powerup.update():
                powerups_to_remove.append(i)
                
            # Check for player collision with powerup
            dx = self.player.x - powerup.x
            dy = self.player.y - powerup.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < self.player.width/2 + powerup.radius:
                powerup.collect(self.player)
                powerups_to_remove.append(i)
                self.sound_manager.play('powerup')
        
        # Remove powerups (in reverse order to avoid index issues)
        for i in sorted(powerups_to_remove, reverse=True):
            if i < len(self.powerups):  # Safety check
                self.powerups.pop(i)
        
        # Update bombs and check for collisions
        bombs_to_remove = []
        for i, bomb in enumerate(self.bombs):
            bomb.update()
            
            # Check for bomb-enemy collisions (only for non-exploding bombs that can explode on contact)
            if not bomb.exploding and getattr(bomb, 'can_explode_on_contact', False):
                # Player bombs can hit enemies
                if not getattr(bomb, 'enemy_bomb', False):
                    for enemy in self.enemies:
                        if enemy.is_alive:
                            # Calculate distance between bomb and enemy
                            dx = bomb.x - enemy.x
                            dy = bomb.y - enemy.y
                            distance = math.sqrt(dx*dx + dy*dy)
                            
                            # Check if bomb is close enough to enemy to trigger explosion
                            if distance < enemy.width/2 + bomb.radius:
                                print("Bomb hit enemy directly! Exploding on contact!")
                                bomb.explode()
                                break
                # Enemy bombs can hit player
                else:
                    # Calculate distance between bomb and player
                    dx = bomb.x - self.player.x
                    dy = bomb.y - self.player.y
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    # Check if bomb is close enough to player to trigger explosion
                    if distance < self.player.width/2 + bomb.radius:
                        print("Enemy bomb hit player directly! Exploding on contact!")
                        bomb.explode()
            
            # Check if exploding bombs damage the player (only enemy bombs)
            if bomb.exploding and getattr(bomb, 'enemy_bomb', False):
                # Calculate distance between explosion and player
                dx = self.player.x - bomb.x
                dy = self.player.y - bomb.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                # Check if player is within explosion radius
                if distance < bomb.explosion_radius:
                    # Calculate damage based on distance (more damage closer to center)
                    damage_factor = 1 - (distance / bomb.explosion_radius)
                    damage = int(25 * damage_factor)  # Increased from 20 to 25 for more challenge
                    
                    print(f"Enemy bomb explosion hit player! Distance: {distance:.1f}, Damage: {damage}")
                    self.player.take_damage(damage)
                    self.sound_manager.play('hit')
                    
                    # Knockback effect from explosion
                    if distance > 0:
                        knockback_strength = 8 * damage_factor
                        knockback_x = (self.player.x - bomb.x) / distance * knockback_strength
                        knockback_y = (self.player.y - bomb.y) / distance * knockback_strength
                        
                        # Apply knockback to velocity
                        self.player.velocity_x += knockback_x
                        self.player.velocity_y += knockback_y
                        self.player.z_velocity = 5 * damage_factor  # Jump up from explosion
            
            # Play explosion sound when bomb explodes
            if bomb.exploding and bomb.explosion_duration == bomb.explosion_duration - 1:
                self.sound_manager.play('explosion')
                    
            if bomb.should_remove:
                bombs_to_remove.append(i)
                
        # Remove bombs (in reverse order to avoid index issues)
        for i in sorted(bombs_to_remove, reverse=True):
            if i < len(self.bombs):  # Safety check
                self.bombs.pop(i)
        # Update enemies and check for damage
        enemies_to_remove = []
        enemy_bombs_to_add = []
        
        # Count how many enemies are currently throwing bombs
        enemies_throwing = 0
        for enemy in self.enemies:
            if enemy.state == "throw_bomb":
                enemies_throwing += 1
        
        # Limit how many enemies can throw bombs simultaneously - increased for more challenge
        max_simultaneous_throwers = 3  # Increased from 2 to 3
        
        for i, enemy in enumerate(self.enemies):
            # Update enemy and check if it wants to throw a bomb
            bomb_data = enemy.update(self.player, self.bombs)
            
            # Handle enemy bomb throwing - limit simultaneous throwers
            if bomb_data and enemies_throwing < max_simultaneous_throwers:
                enemy_bombs_to_add.append(bomb_data)
                enemies_throwing += 1
                print(f"Enemy {i} is throwing a bomb!")
            
            # Check if enemy is dead
            if not enemy.is_alive:
                enemies_to_remove.append(i)
                self.score += 100
                print(f"Enemy defeated! Score +100. Total score: {self.score}")
                
                # Chance to spawn a powerup when enemy is defeated
                if random.random() < 0.3:  # 30% chance
                    self.spawn_powerup_at(enemy.x, enemy.y)
        
        # Add enemy bombs to the game
        for bomb_data in enemy_bombs_to_add:
            if bomb_data['type'] == "regular":
                bomb = Bomb(bomb_data['x'], bomb_data['y'], bomb_data['dir_x'], bomb_data['dir_y'])
                bomb.color = (50, 50, 50)  # Darker color for enemy bombs
            elif bomb_data['type'] == "cracking":
                bomb = CrackingBomb(bomb_data['x'], bomb_data['y'], bomb_data['dir_x'], bomb_data['dir_y'])
                bomb.color = (50, 100, 50)  # Darker color for enemy bombs
            elif bomb_data['type'] == "timer":
                bomb = TimerBomb(bomb_data['x'], bomb_data['y'], bomb_data['dir_x'], bomb_data['dir_y'])
                bomb.color = (100, 50, 50)  # Darker color for enemy timer bombs
            else:
                bomb = Bomb(bomb_data['x'], bomb_data['y'], bomb_data['dir_x'], bomb_data['dir_y'])
            
            # Mark as enemy bomb
            bomb.enemy_bomb = True
            self.bombs.append(bomb)
            print(f"Added enemy bomb at ({bomb.x}, {bomb.y})")
        
        # Remove dead enemies (in reverse order to avoid index issues)
        for i in sorted(enemies_to_remove, reverse=True):
            if i < len(self.enemies):  # Safety check
                self.enemies.pop(i)
                
        # Check if all enemies are defeated
        if len(self.enemies) == 0:
            # Spawn more enemies
            new_enemy_count = self.score // 500 + 5  # Increase difficulty with score
            print(f"Spawning {new_enemy_count} new enemies!")
            self.spawn_enemies(new_enemy_count)
        
        # Check for game over (player health)
        if self.player.health <= 0:
            self.game_over = True
            print("Game Over! Press R to restart.")
            
    def spawn_powerup_at(self, x, y):
        """Spawn a powerup at the specified location"""
        powerup_type = random.choice(["health", "speed", "damage", "shield"])
        self.powerups.append(PowerUp(x, y, powerup_type))
        print(f"Spawned {powerup_type} powerup at ({x}, {y})")
        
    def spawn_powerup(self):
        """Spawn a powerup at a random location on the island"""
        # Random position not too far from player
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(100, 300)
        x = self.player.x + math.cos(angle) * distance
        y = self.player.y + math.sin(angle) * distance
        
        powerup_type = random.choice(["health", "speed", "damage", "shield"])
        self.powerups.append(PowerUp(x, y, powerup_type))
        print(f"Spawned {powerup_type} powerup at ({x}, {y})")
        
    def spawn_enemies(self, count):
        for _ in range(count):
            # Spawn enemies at random positions on the island, but not too close to player
            min_distance = 200  # Minimum distance from player
            max_attempts = 10   # Maximum attempts to find a valid position
            
            for attempt in range(max_attempts):
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(min_distance, 600)  # Between min and max distance
                x = self.player.x + math.cos(angle) * distance
                y = self.player.y + math.sin(angle) * distance
                
                # Check if position is valid (not too close to other enemies)
                valid_position = True
                for enemy in self.enemies:
                    dx = x - enemy.x
                    dy = y - enemy.y
                    if math.sqrt(dx*dx + dy*dy) < 100:  # Minimum distance between enemies
                        valid_position = False
                        break
                
                if valid_position:
                    self.enemies.append(Enemy(x, y))
                    break
                    
            # If no valid position found after max attempts, just place randomly but not too close
            if attempt == max_attempts - 1:
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(min_distance, 800)
                x = self.player.x + math.cos(angle) * distance
                y = self.player.y + math.sin(angle) * distance
                self.enemies.append(Enemy(x, y))
    def render(self):
        # Clear screen
        self.screen.fill(SKY_BLUE)
        
        # Draw island
        self.island.draw(self.screen, self.camera)
        
        # Draw powerups
        for powerup in self.powerups:
            powerup.draw(self.screen, self.camera)
        
        # Draw bombs
        for bomb in self.bombs:
            bomb.draw(self.screen, self.camera)
            
        # Draw held bomb if we have one
        if hasattr(self, 'held_bomb') and self.held_bomb:
            self.held_bomb.draw(self.screen, self.camera)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw HUD
        self.draw_hud()
        
        # Draw recording button
        self.recorder.draw_button(self.screen)
        
        # Draw game over screen
        if self.game_over:
            self.draw_game_over()
        
        # Capture frame if recording (only if not in game over state to reduce lag)
        # Skip frame capture if FPS is too low to reduce lag
        if not self.game_over and (not hasattr(self, 'show_fps') or not self.show_fps or self.clock.get_fps() > 20):
            self.recorder.capture_frame(self.screen)
        
        # Display FPS if in debug mode
        if hasattr(self, 'show_fps') and self.show_fps:
            fps = self.clock.get_fps()
            fps_text = f"FPS: {fps:.1f}"
            font = pygame.font.SysFont(None, 24)
            fps_surface = font.render(fps_text, True, (255, 255, 255))
            self.screen.blit(fps_surface, (10, self.screen_height - 60))
        
        # Update display
        pygame.display.flip()
        
    def draw_hud(self):
        # Display current bomb type
        font = pygame.font.SysFont(None, 24)
        
        # Show bomb type with special properties
        if self.current_bomb_type == "timer":
            bomb_text = f"Current Bomb: Timer Bomb (High Damage)"
        elif self.current_bomb_type == "cracking":
            bomb_text = f"Current Bomb: Cracking Bomb (Multiple Hits)"
        else:
            bomb_text = f"Current Bomb: Regular Bomb (Contact Explosion)"
            
        text_surface = font.render(bomb_text, True, (0, 0, 0))
        self.screen.blit(text_surface, (10, 10))
        
        # Display score
        score_text = f"Score: {self.score}"
        score_surface = font.render(score_text, True, (0, 0, 0))
        self.screen.blit(score_surface, (10, 40))
        
        # Display player health
        health_text = f"Health: {self.player.health}"
        health_surface = font.render(health_text, True, (0, 0, 0))
        self.screen.blit(health_surface, (10, 70))
        
        # Display enemies left
        enemies_text = f"Enemies: {len(self.enemies)}"
        enemies_surface = font.render(enemies_text, True, (0, 0, 0))
        self.screen.blit(enemies_surface, (10, 100))
        
        # Display bomb ammo
        ammo_text = f"Bombs: {self.player.bombs}/{self.player.max_bombs}"
        ammo_surface = font.render(ammo_text, True, (0, 0, 0))
        self.screen.blit(ammo_surface, (10, 130))
        
        # Count bomber enemies
        bomber_count = sum(1 for enemy in self.enemies if enemy.can_throw_bombs)
        if bomber_count > 0:
            bomber_text = f"Bomber Enemies: {bomber_count}"
            bomber_surface = font.render(bomber_text, True, (200, 50, 0))
            self.screen.blit(bomber_surface, (10, 160))
            
            warning_text = "WATCH OUT FOR ENEMY BOMBS!"
            if pygame.time.get_ticks() % 1000 < 500:  # Blinking warning
                warning_surface = font.render(warning_text, True, (255, 0, 0))
                self.screen.blit(warning_surface, (10, 190))
                
        # Display active powerups
        powerup_text = f"Active Powerups:"
        powerup_surface = font.render(powerup_text, True, (0, 0, 0))
        self.screen.blit(powerup_surface, (self.screen_width - 200, 10))
        
        y_offset = 40
        if hasattr(self.player, 'speed_boost') and self.player.speed_boost > 1.0:
            speed_text = f"Speed Boost: {self.player.speed_boost_time // 60 + 1}s"
            speed_surface = font.render(speed_text, True, (50, 50, 255))
            self.screen.blit(speed_surface, (self.screen_width - 200, y_offset))
            y_offset += 30
            
        if hasattr(self.player, 'damage_boost') and self.player.damage_boost > 1.0:
            damage_text = f"Damage Boost: {self.player.damage_boost_time // 60 + 1}s"
            damage_surface = font.render(damage_text, True, (255, 165, 0))
            self.screen.blit(damage_surface, (self.screen_width - 200, y_offset))
            y_offset += 30
            
        if hasattr(self.player, 'shield') and self.player.shield > 0:
            shield_text = f"Shield: {self.player.shield}"
            shield_surface = font.render(shield_text, True, (50, 255, 50))
            self.screen.blit(shield_surface, (self.screen_width - 200, y_offset))
            y_offset += 30
            
        # Display sound status
        if self.sound_manager.is_muted:
            sound_text = "Sound: MUTED (M)"
            sound_color = (150, 150, 150)
        else:
            sound_text = f"Sound: {int(self.sound_manager.master_volume * 100)}% (M)"
            sound_color = (0, 0, 0)
            
        sound_surface = font.render(sound_text, True, sound_color)
        self.screen.blit(sound_surface, (self.screen_width - 200, y_offset))
        y_offset += 30
        
        # Display fullscreen status
        fullscreen_text = f"Fullscreen: {'ON' if self.fullscreen else 'OFF'} (F)"
        fullscreen_surface = font.render(fullscreen_text, True, (0, 0, 0))
        self.screen.blit(fullscreen_surface, (self.screen_width - 200, y_offset))
        y_offset += 30
        
        # Display recording status if recording
        if self.recorder.recording:
            recording_text = "RECORDING"
            if pygame.time.get_ticks() % 1000 < 500:  # Blinking text
                recording_surface = font.render(recording_text, True, (255, 0, 0))
                self.screen.blit(recording_surface, (self.screen_width - 200, y_offset))
        
        # Display controls
        controls_text = "Controls: WASD to move, Mouse to aim, Left Click to throw, 1-3 to switch bombs"
        controls_surface = font.render(controls_text, True, (0, 0, 0))
        self.screen.blit(controls_surface, (10, self.screen_height - 30))
        
    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        font_large = pygame.font.SysFont(None, 72)
        font_medium = pygame.font.SysFont(None, 36)
        
        game_over_text = font_large.render("GAME OVER", True, (255, 0, 0))
        score_text = font_medium.render(f"Final Score: {self.score}", True, (255, 255, 255))
        restart_text = font_medium.render("Press R to Restart", True, (255, 255, 255))
        
        self.screen.blit(game_over_text, 
                       (self.screen_width // 2 - game_over_text.get_width() // 2, 
                        self.screen_height // 2 - 80))
        self.screen.blit(score_text, 
                       (self.screen_width // 2 - score_text.get_width() // 2, 
                        self.screen_height // 2))
        self.screen.blit(restart_text, 
                       (self.screen_width // 2 - restart_text.get_width() // 2, 
                        self.screen_height // 2 + 60))
        
        # Play game over sound once
        if not hasattr(self, 'game_over_sound_played'):
            self.sound_manager.play('game_over')
            self.game_over_sound_played = True
            
    def run(self):
        target_fps = FPS
        last_time = time.time()
        
        while self.running:
            # Calculate delta time for consistent game speed regardless of frame rate
            current_time = time.time()
            delta_time = current_time - last_time
            last_time = current_time
            
            # Handle events
            self.handle_events()
            
            # Update game state
            self.update()
            
            # Render game
            self.render()
            
            # Limit frame rate
            self.clock.tick(target_fps)
            
            # Adjust target FPS based on recording status to reduce lag
            if self.recorder.recording:
                target_fps = max(30, FPS - 15)  # Lower FPS during recording (more aggressive)
            else:
                target_fps = FPS
        
        # Make sure to save recording if game is closed while recording
        if self.recorder.recording:
            print("Game closing, stopping recording...")
            self.recorder.toggle_recording()
            # Wait a moment for the recording to finish saving
            time.sleep(1)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
