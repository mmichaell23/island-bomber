import pygame
import math
import random

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.speed = 3.2  # Reduced from 5 for more realistic movement
        self.color = (0, 0, 255)  # Blue
        self.health = 100
        self.max_health = 100
        
        # 3D effect variables
        self.z = 0  # Height for 3D effect
        self.z_velocity = 0
        self.jumping = False
        self.shadow_alpha = 150
        
        # For third-person view
        self.camera_offset_x = 0
        self.camera_offset_y = 0
        
        # Bomb throwing cooldown
        self.throw_cooldown = 0
        self.throw_cooldown_max = 15  # frames
        
        # Bomb ammo system
        self.max_bombs = 3  # Maximum bombs the player can carry
        self.bombs = self.max_bombs  # Current bomb count
        self.reload_timer = 0
        self.reload_time = 120  # 2 seconds at 60 FPS
        
        # Animation variables
        self.animation_frame = 0
        self.animation_speed = 0.1
        self.direction_facing = 1  # 1 for right, -1 for left
        self.moving = False
        
        # Acceleration and deceleration for realistic movement
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration = 0.5
        self.friction = 0.85  # Value between 0 and 1
        
        # Damage cooldown (invincibility frames)
        self.damage_cooldown = 0
        
        # Powerup effects
        self.speed_boost = 1.0
        self.speed_boost_time = 0
        self.damage_boost = 1.0
        self.damage_boost_time = 0
        self.shield = 0
        
    def update(self, keys):
        # Update damage cooldown
        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1
            
        # Update powerup timers
        if self.speed_boost_time > 0:
            self.speed_boost_time -= 1
            if self.speed_boost_time <= 0:
                self.speed_boost = 1.0
                print("Speed boost expired!")
                
        if self.damage_boost_time > 0:
            self.damage_boost_time -= 1
            if self.damage_boost_time <= 0:
                self.damage_boost = 1.0
                print("Damage boost expired!")
                
        # Update bomb reload timer
        if self.bombs < self.max_bombs:
            self.reload_timer += 1
            if self.reload_timer >= self.reload_time:
                self.bombs += 1
                self.reload_timer = 0
                print(f"Reloaded a bomb! Bombs: {self.bombs}/{self.max_bombs}")
            
        # Movement with acceleration and deceleration
        self.moving = False
        input_x = 0
        input_y = 0
        
        if keys[pygame.K_w]:
            input_y -= 1
            self.moving = True
        if keys[pygame.K_s]:
            input_y += 1
            self.moving = True
        if keys[pygame.K_a]:
            input_x -= 1
            self.moving = True
            self.direction_facing = -1
        if keys[pygame.K_d]:
            input_x += 1
            self.moving = True
            self.direction_facing = 1
            
        # Normalize diagonal movement
        if input_x != 0 and input_y != 0:
            magnitude = math.sqrt(input_x**2 + input_y**2)
            input_x /= magnitude
            input_y /= magnitude
            
        # Apply acceleration
        self.velocity_x += input_x * self.acceleration
        self.velocity_y += input_y * self.acceleration
        
        # Apply friction
        self.velocity_x *= self.friction
        self.velocity_y *= self.friction
        
        # Apply speed boost if active
        current_speed = self.speed * self.speed_boost
        
        # Limit maximum speed
        speed_magnitude = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
        if speed_magnitude > current_speed:
            speed_ratio = current_speed / speed_magnitude
            self.velocity_x *= speed_ratio
            self.velocity_y *= speed_ratio
            
        # Apply velocity
        self.x += self.velocity_x
        self.y += self.velocity_y
            
        # Update cooldown
        if self.throw_cooldown > 0:
            self.throw_cooldown -= 1
            
        # Update 3D jumping effect
        if self.z > 0 or self.z_velocity != 0:
            self.z += self.z_velocity
            self.z_velocity -= 0.5  # Gravity
            
            # Ground collision
            if self.z <= 0:
                self.z = 0
                self.z_velocity = 0
                self.jumping = False
                
        # Jump with spacebar
        if keys[pygame.K_SPACE] and self.z == 0:
            self.z_velocity = 10
            self.jumping = True
            
        # Update animation - speed based on movement speed
        if self.moving or self.jumping:
            # Animation speed proportional to movement speed
            actual_speed = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
            self.animation_frame += self.animation_speed * (actual_speed / self.speed)
            
    def take_damage(self, amount):
        # Check if we have a shield
        if self.shield > 0:
            # Shield absorbs damage
            if self.shield >= amount:
                self.shield -= amount
                print(f"Shield absorbed {amount} damage! Shield remaining: {self.shield}")
                return
            else:
                # Shield absorbs part of the damage
                remaining_damage = amount - self.shield
                print(f"Shield absorbed {self.shield} damage! Shield depleted!")
                self.shield = 0
                amount = remaining_damage
        
        # Check for invincibility frames
        if self.damage_cooldown > 0:
            return
            
        self.health -= amount
        print(f"Player took {amount} damage! Health: {self.health}")
        
        # Set damage cooldown (invincibility frames)
        self.damage_cooldown = 30  # Half a second at 60 FPS
        
        # Visual feedback - jump when hit
        if self.z == 0:
            self.z_velocity = 4
            self.jumping = True
        
        if self.health <= 0:
            self.health = 0
            print("Player defeated!")
            
    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)
        print(f"Player healed {amount}! Health: {self.health}")
            
    def draw(self, screen):
        # Draw player at center of screen (third-person view)
        screen_center_x = screen.get_width() // 2
        screen_center_y = screen.get_height() // 2
        
        # Calculate shadow alpha based on height
        self.shadow_alpha = max(40, min(150, 150 - self.z))
        
        # Draw shadow (gets larger as player jumps higher)
        shadow_size = self.width * (1 + self.z / 50)
        shadow_surface = pygame.Surface((shadow_size, shadow_size // 2), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, self.shadow_alpha), 
                          (0, 0, shadow_size, shadow_size // 2))
        screen.blit(shadow_surface, 
                  (screen_center_x - shadow_size // 2, 
                   screen_center_y + self.height // 2 - shadow_size // 4))
        
        # Animation effect - slight bobbing when moving
        bob_offset = int(math.sin(self.animation_frame) * 2) if self.moving else 0
        
        # Calculate y position with 3D effect
        screen_y = screen_center_y - self.z
        
        # Draw legs
        leg_width = self.width // 3
        leg_height = self.height // 2
        leg_spacing = self.width // 2
        
        # Animate legs based on movement
        left_leg_offset = int(math.sin(self.animation_frame) * 5) if self.moving else 0
        right_leg_offset = int(math.sin(self.animation_frame + math.pi) * 5) if self.moving else 0
        
        # Adjust color based on height for 3D lighting effect
        body_color = (max(0, self.color[0] - self.z//2), 
                     max(0, self.color[1] - self.z//2), 
                     max(100, self.color[2] - self.z//2))
                     
        # Flash when taking damage (invincibility frames)
        if self.damage_cooldown > 0:
            if self.damage_cooldown % 6 < 3:  # Blink every few frames
                body_color = (255, 255, 255)  # Flash white
                
        # Show speed boost effect
        if self.speed_boost_time > 0:
            # Add blue trail particles
            for i in range(3):
                trail_x = screen_center_x + random.randint(-self.width//2, self.width//2)
                trail_y = screen_y + self.height//2 + random.randint(-5, 5)
                trail_size = random.randint(3, 8)
                trail_alpha = random.randint(100, 200)
                
                trail_surface = pygame.Surface((trail_size*2, trail_size*2), pygame.SRCALPHA)
                pygame.draw.circle(trail_surface, (50, 50, 255, trail_alpha), 
                                 (trail_size, trail_size), trail_size)
                screen.blit(trail_surface, (trail_x - trail_size, trail_y - trail_size))
        
        # Draw shield effect if active
        if self.shield > 0:
            shield_radius = self.width * 0.8
            shield_alpha = 100 + int(50 * math.sin(pygame.time.get_ticks() * 0.01))
            shield_surface = pygame.Surface((shield_radius*2, shield_radius*2), pygame.SRCALPHA)
            
            # Draw shield circle
            pygame.draw.circle(shield_surface, (50, 255, 50, shield_alpha), 
                             (shield_radius, shield_radius), shield_radius)
            
            # Draw shield border
            pygame.draw.circle(shield_surface, (255, 255, 255, shield_alpha), 
                             (shield_radius, shield_radius), shield_radius, 2)
            
            shield_rect = shield_surface.get_rect(center=(screen_center_x, screen_y))
            screen.blit(shield_surface, shield_rect.topleft)
        
        # Draw legs
        pygame.draw.rect(screen, (0, 0, 150), 
                       (screen_center_x - leg_spacing//2 - leg_width//2, 
                        screen_y + self.height//2 - leg_height + left_leg_offset, 
                        leg_width, leg_height))
        
        pygame.draw.rect(screen, (0, 0, 150), 
                       (screen_center_x + leg_spacing//2 - leg_width//2, 
                        screen_y + self.height//2 - leg_height + right_leg_offset, 
                        leg_width, leg_height))
        
        # Draw player body
        pygame.draw.rect(screen, body_color, 
                        (screen_center_x - self.width // 2, 
                         screen_y - self.height // 2 + bob_offset, 
                         self.width, self.height))
                         
        # Draw arms
        arm_width = self.width // 3
        arm_height = self.height // 2
        arm_spacing = self.width * 0.8
        
        # Get mouse position for arm aiming
        mouse_x, mouse_y = pygame.mouse.get_pos()
        direction_x = mouse_x - screen_center_x
        direction_y = mouse_y - screen_y
        
        # Normalize and scale
        length = (direction_x**2 + direction_y**2)**0.5
        if length > 0:
            direction_x = direction_x / length
            direction_y = direction_y / length
            
        # Animate arms based on movement and aiming
        arm_angle = math.atan2(direction_y, direction_x)
        
        # Draw throwing arm (follows mouse)
        arm_length = 25
        arm_end_x = screen_center_x + int(math.cos(arm_angle) * arm_length)
        arm_end_y = screen_y - self.height//4 + int(math.sin(arm_angle) * arm_length)
        
        pygame.draw.line(screen, (0, 0, 200), 
                       (screen_center_x, screen_y - self.height//4),
                       (arm_end_x, arm_end_y), 6)
        
        # Draw other arm with movement animation
        other_arm_offset = int(math.sin(self.animation_frame + 3*math.pi/2) * 5) if self.moving else 0
        pygame.draw.rect(screen, (0, 0, 200), 
                       (screen_center_x - arm_spacing//2, 
                        screen_y - self.height//4 + other_arm_offset, 
                        arm_width, arm_height))
        
        # Draw player head
        head_radius = 15
        pygame.draw.circle(screen, (255, 200, 150),  # Skin color
                          (screen_center_x, screen_y - self.height // 2 - head_radius // 2 + bob_offset),
                          head_radius)
        
        # Draw eyes
        eye_radius = head_radius // 3
        eye_spacing = head_radius // 2
        
        # Eyes follow mouse
        eye_offset_x = direction_x * (head_radius // 4)
        eye_offset_y = direction_y * (head_radius // 4)
        
        # White of eyes
        pygame.draw.circle(screen, (255, 255, 255),
                         (screen_center_x - eye_spacing, screen_y - self.height // 2 - head_radius // 2 + bob_offset),
                         eye_radius)
        pygame.draw.circle(screen, (255, 255, 255),
                         (screen_center_x + eye_spacing, screen_y - self.height // 2 - head_radius // 2 + bob_offset),
                         eye_radius)
        
        # Pupils
        pygame.draw.circle(screen, (0, 0, 0),
                         (int(screen_center_x - eye_spacing + eye_offset_x), 
                          int(screen_y - self.height // 2 - head_radius // 2 + bob_offset + eye_offset_y)),
                         eye_radius // 2)
        pygame.draw.circle(screen, (0, 0, 0),
                         (int(screen_center_x + eye_spacing + eye_offset_x), 
                          int(screen_y - self.height // 2 - head_radius // 2 + bob_offset + eye_offset_y)),
                         eye_radius // 2)
        
        # Draw bomb in hand if ready to throw and has bombs
        if self.throw_cooldown == 0 and self.bombs > 0:
            bomb_radius = 8
            bomb_x = arm_end_x + int(math.cos(arm_angle) * bomb_radius)
            bomb_y = arm_end_y + int(math.sin(arm_angle) * bomb_radius)
            
            # Show damage boost effect on bomb
            bomb_color = (0, 0, 0)
            if self.damage_boost_time > 0:
                bomb_color = (255, 165, 0)  # Orange for damage boost
                
                # Add glow effect
                glow_radius = bomb_radius + 4
                glow_surface = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
                for r in range(glow_radius, glow_radius-4, -1):
                    alpha = max(0, 150 - (glow_radius - r) * 50)
                    pygame.draw.circle(glow_surface, (255, 165, 0, alpha), 
                                     (glow_radius, glow_radius), r)
                
                glow_rect = glow_surface.get_rect(center=(bomb_x, bomb_y))
                screen.blit(glow_surface, glow_rect.topleft)
            
            pygame.draw.circle(screen, bomb_color, (bomb_x, bomb_y), bomb_radius)
            
            # Draw fuse
            fuse_end_x = bomb_x + int(math.cos(arm_angle - math.pi/4) * 7)
            fuse_end_y = bomb_y + int(math.sin(arm_angle - math.pi/4) * 7)
            pygame.draw.line(screen, (100, 100, 100), (bomb_x, bomb_y), (fuse_end_x, fuse_end_y), 2)
            
            # Draw spark (blinking)
            if pygame.time.get_ticks() % 500 < 250:
                pygame.draw.circle(screen, (255, 200, 0), (fuse_end_x, fuse_end_y), 2)
        
        # Draw health bar
        health_bar_width = 100
        health_bar_height = 10
        health_percentage = max(0, self.health / self.max_health)
        
        # Background (empty health)
        pygame.draw.rect(screen, (255, 0, 0),
                       (screen_center_x - health_bar_width // 2,
                        screen_center_y + self.height // 2 + 10,
                        health_bar_width, health_bar_height))
        
        # Foreground (current health)
        pygame.draw.rect(screen, (0, 255, 0),
                       (screen_center_x - health_bar_width // 2,
                        screen_center_y + self.height // 2 + 10,
                        int(health_bar_width * health_percentage), health_bar_height))
        
        # Draw shield bar if active
        if self.shield > 0:
            shield_bar_width = int(health_bar_width * (self.shield / 50))  # 50 is max shield
            pygame.draw.rect(screen, (50, 150, 255),
                           (screen_center_x - health_bar_width // 2,
                            screen_center_y + self.height // 2 + 10 - health_bar_height - 2,
                            shield_bar_width, health_bar_height))
        
        # Draw bomb ammo indicator
        bomb_indicator_y = screen_center_y + self.height // 2 + 25
        bomb_indicator_size = 15
        bomb_spacing = 20
        
        # Draw bomb count
        for i in range(self.max_bombs):
            bomb_x = screen_center_x - (self.max_bombs * bomb_spacing) // 2 + i * bomb_spacing
            
            if i < self.bombs:
                # Available bomb
                pygame.draw.circle(screen, (0, 0, 0), (bomb_x, bomb_indicator_y), bomb_indicator_size // 2)
            else:
                # Empty bomb slot
                pygame.draw.circle(screen, (100, 100, 100), (bomb_x, bomb_indicator_y), bomb_indicator_size // 2, 2)
                
                # Show reload progress for the next bomb
                if i == self.bombs:
                    reload_percentage = self.reload_timer / self.reload_time
                    reload_angle = 360 * reload_percentage
                    
                    # Draw reload progress arc
                    if reload_percentage > 0:
                        pygame.draw.arc(screen, (0, 0, 0), 
                                      (bomb_x - bomb_indicator_size//2, bomb_indicator_y - bomb_indicator_size//2,
                                       bomb_indicator_size, bomb_indicator_size),
                                      0, math.radians(reload_angle), 2)
        
        # Draw powerup indicators
        indicator_y = screen_center_y + self.height // 2 + 45
        indicator_size = 15
        indicator_spacing = 20
        
        # Speed boost indicator
        if self.speed_boost_time > 0:
            speed_icon = pygame.Surface((indicator_size, indicator_size), pygame.SRCALPHA)
            pygame.draw.polygon(speed_icon, (50, 50, 255), 
                              [(0, indicator_size), (indicator_size, indicator_size//2), (0, 0)])
            screen.blit(speed_icon, (screen_center_x - 50, indicator_y))
            
            # Draw timer
            time_text = str(self.speed_boost_time // 60 + 1)
            font = pygame.font.SysFont(None, 16)
            text_surface = font.render(time_text, True, (255, 255, 255))
            screen.blit(text_surface, (screen_center_x - 50 + indicator_size + 2, indicator_y))
        
        # Damage boost indicator
        if self.damage_boost_time > 0:
            damage_icon = pygame.Surface((indicator_size, indicator_size), pygame.SRCALPHA)
            pygame.draw.polygon(damage_icon, (255, 165, 0), 
                              [(indicator_size//2, 0), (0, indicator_size), (indicator_size, indicator_size)])
            screen.blit(damage_icon, (screen_center_x, indicator_y))
            
            # Draw timer
            time_text = str(self.damage_boost_time // 60 + 1)
            font = pygame.font.SysFont(None, 16)
            text_surface = font.render(time_text, True, (255, 255, 255))
            screen.blit(text_surface, (screen_center_x + indicator_size + 2, indicator_y))
