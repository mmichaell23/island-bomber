import pygame
import math
import random

class Bomb:
    def __init__(self, x, y, dir_x, dir_y):
        self.x = x
        self.y = y
        self.z = 10  # Start slightly above ground for 3D effect
        self.z_velocity = 5  # Initial upward velocity
        self.radius = 10
        self.color = (0, 0, 0)  # Black
        self.speed = 8
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.lifetime = 90  # Reduced from 120 for faster explosion
        self.explosion_radius = 50
        self.explosion_duration = 30
        self.exploding = False
        self.should_remove = False
        self.rotation = 0
        self.rotation_speed = random.uniform(-0.1, 0.1)
        self.can_explode_on_contact = True  # Allow bombs to explode on enemy contact
        self.enemy_bomb = False  # Flag to identify if this is an enemy bomb
        
    def update(self):
        if not self.exploding:
            # Move the bomb
            self.x += self.dir_x * self.speed
            self.y += self.dir_y * self.speed
            
            # Update 3D effect
            self.z += self.z_velocity
            self.z_velocity -= 0.5  # Gravity
            
            # Bounce if hitting ground
            if self.z <= 0:
                self.z = 0
                # Reduce bounce energy based on speed
                bounce_factor = min(0.6, 0.6 * (self.speed / 8))
                self.z_velocity = self.z_velocity * -bounce_factor  # Bounce with energy loss
                
                # Reduce horizontal speed on bounce
                self.speed *= 0.8
                
                # Stop bouncing if velocity is too low
                if abs(self.z_velocity) < 1 or self.speed < 1:
                    self.z_velocity = 0
                    self.z = 0
                    self.speed *= 0.9  # Slow down on ground
            
            # Update rotation - faster rotation for faster bombs
            self.rotation += self.rotation_speed * (self.speed / 8)
            
            # Countdown to explosion
            self.lifetime -= 1
            if self.lifetime <= 0:
                self.explode()
                
            # Check for enemy collision (will be handled in main.py)
            # This is just a flag to indicate the bomb can explode on contact
            self.can_explode_on_contact = True
        else:
            # Handle explosion animation
            self.explosion_duration -= 1
            if self.explosion_duration <= 0:
                self.should_remove = True
                
    def explode(self):
        self.exploding = True
        self.explosion_duration = 30
        
    def draw(self, screen, camera):
        # Calculate screen position with 3D effect
        screen_x = int(self.x - camera.x + screen.get_width() // 2)
        screen_y = int(self.y - camera.y + screen.get_height() // 2 - self.z)
        
        if not self.exploding:
            # Draw shadow
            shadow_size = self.radius * 2
            shadow_alpha = max(40, min(150, 150 - self.z))
            shadow_surface = pygame.Surface((shadow_size, shadow_size // 2), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surface, (0, 0, 0, shadow_alpha), 
                              (0, 0, shadow_size, shadow_size // 2))
            screen.blit(shadow_surface, 
                      (screen_x - shadow_size // 2, 
                       int(self.y - camera.y + screen.get_height() // 2) - shadow_size // 4))
            
            # Draw bomb with rotation
            bomb_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(bomb_surface, self.color, (self.radius, self.radius), self.radius)
            
            # Add fuse to bomb
            fuse_length = self.radius * 0.7
            fuse_end_x = self.radius + math.cos(self.rotation) * fuse_length
            fuse_end_y = self.radius + math.sin(self.rotation) * fuse_length
            pygame.draw.line(bomb_surface, (100, 100, 100), 
                           (self.radius, self.radius), 
                           (fuse_end_x, fuse_end_y), 2)
            
            # Add spark to fuse (blinking)
            if pygame.time.get_ticks() % 500 < 250:
                pygame.draw.circle(bomb_surface, (255, 200, 0), 
                                 (int(fuse_end_x), int(fuse_end_y)), 2)
            
            # Rotate bomb
            rotated_bomb = pygame.transform.rotate(bomb_surface, math.degrees(self.rotation))
            bomb_rect = rotated_bomb.get_rect(center=(screen_x, screen_y))
            screen.blit(rotated_bomb, bomb_rect.topleft)
            
            # Add motion blur for fast-moving bombs
            if self.speed > 5:
                blur_alpha = min(150, int(self.speed * 10))
                blur_length = int(self.speed * 1.5)
                for i in range(1, 4):
                    blur_x = screen_x - int(self.dir_x * blur_length * i / 3)
                    blur_y = screen_y - int(self.dir_y * blur_length * i / 3)
                    blur_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
                    blur_color = (*self.color, blur_alpha // (i * 2))
                    pygame.draw.circle(blur_surface, blur_color, 
                                     (self.radius, self.radius), self.radius * (1 - i/5))
                    blur_rect = blur_surface.get_rect(center=(blur_x, blur_y))
                    screen.blit(blur_surface, blur_rect.topleft)
        else:
            # Draw explosion
            explosion_progress = 1 - (self.explosion_duration / 30)  # 0 to 1
            explosion_radius = int(self.explosion_radius * explosion_progress)
            
            # Create gradient explosion
            for r in range(explosion_radius, 0, -5):
                alpha = max(0, 255 - (explosion_radius - r) * 5)
                color_mix = explosion_progress  # 0 to 1
                
                # Color transition: yellow -> orange -> red
                red = 255
                green = max(0, int(255 * (1 - color_mix * 0.8)))
                blue = 0
                
                pygame.draw.circle(screen, (red, green, blue, alpha), 
                                 (screen_x, screen_y), r)
            
            # Add explosion particles
            particle_count = 20
            for _ in range(particle_count):
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(0, explosion_radius)
                particle_x = screen_x + math.cos(angle) * distance
                particle_y = screen_y + math.sin(angle) * distance
                particle_size = random.randint(2, 6)
                particle_alpha = random.randint(100, 200)
                
                pygame.draw.circle(screen, (255, 255, 100, particle_alpha), 
                                 (int(particle_x), int(particle_y)), particle_size)


class TimerBomb(Bomb):
    def __init__(self, x, y, dir_x, dir_y):
        super().__init__(x, y, dir_x, dir_y)
        self.color = (255, 0, 0)  # Red
        self.lifetime = 90  # 1.5 seconds at 60 FPS (reduced from 120)
        self.explosion_radius = 80  # Bigger explosion
        self.timer_display = 1.5  # Seconds (reduced from 2)
        self.last_second = self.lifetime // 60
        self.damage_multiplier = 1.5  # More damage than regular bombs
        self.can_explode_on_contact = False  # Timer bombs only explode on timer
        self.held = False  # Whether the bomb is being held by the player
        
    def update(self):
        if self.held:
            # Don't move or apply gravity when held
            # But still count down the timer
            self.lifetime -= 1
            if self.lifetime <= 0:
                self.explode()
        else:
            # Normal update when not held
            super().update()
        
        # Update timer display
        if not self.exploding:
            current_second = self.lifetime // 60
            if current_second < self.last_second:
                self.last_second = current_second
                print(f"Timer bomb: {current_second + 1}...")
                
    def draw(self, screen, camera):
        super().draw(screen, camera)
        
        # Add timer display if not exploding
        if not self.exploding:
            screen_x = int(self.x - camera.x + screen.get_width() // 2)
            screen_y = int(self.y - camera.y + screen.get_height() // 2 - self.z)
            
            # Display timer
            seconds_left = (self.lifetime / 60)  # Show fractional seconds
            font = pygame.font.SysFont(None, 20)
            text_surface = font.render(f"{seconds_left:.1f}", True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(screen_x, screen_y))
            screen.blit(text_surface, text_rect)


class CrackingBomb(Bomb):
    def __init__(self, x, y, dir_x, dir_y):
        super().__init__(x, y, dir_x, dir_y)
        self.color = (0, 255, 0)  # Green
        self.lifetime = 60  # Shorter fuse (reduced from 90)
        self.explosion_radius = 30  # Smaller initial explosion
        self.fragments = []
        self.fragment_count = 6
        self.crack_lines = []
        self.damage_multiplier = 0.7  # Less damage per explosion but multiple explosions
        self.can_explode_on_contact = True  # Can explode on contact
        
        # Generate crack lines for visual effect
        for _ in range(4):
            angle = random.uniform(0, 2 * math.pi)
            length = random.uniform(0.4, 0.9)
            self.crack_lines.append((angle, length))
            
    def explode(self):
        super().explode()
        
        # Create fragments
        for i in range(self.fragment_count):
            angle = 2 * math.pi * i / self.fragment_count
            
            # Add some randomness to the angle
            angle += random.uniform(-0.3, 0.3)
            
            dir_x = math.cos(angle)
            dir_y = math.sin(angle)
            
            # Create a fragment bomb
            fragment = Bomb(self.x, self.y, dir_x, dir_y)
            fragment.color = (0, 200, 0)  # Slightly darker green
            fragment.radius = self.radius * 0.6
            fragment.lifetime = random.randint(30, 60)
            fragment.explosion_radius = self.explosion_radius * 0.7
            fragment.speed = random.uniform(3, 6)
            fragment.z_velocity = random.uniform(3, 7)
            fragment.damage_multiplier = self.damage_multiplier * 0.8
            
            self.fragments.append(fragment)
            
    def update(self):
        super().update()
        
        # Update fragments
        for fragment in self.fragments[:]:
            fragment.update()
            if fragment.should_remove:
                self.fragments.remove(fragment)
                
    def draw(self, screen, camera):
        # Draw main bomb or explosion
        super().draw(screen, camera)
        
        # Draw fragments
        for fragment in self.fragments:
            fragment.draw(screen, camera)
            
        # Draw crack lines if not exploding
        if not self.exploding:
            screen_x = int(self.x - camera.x + screen.get_width() // 2)
            screen_y = int(self.y - camera.y + screen.get_height() // 2 - self.z)
            
            for angle, length in self.crack_lines:
                end_x = screen_x + math.cos(angle) * self.radius * length
                end_y = screen_y + math.sin(angle) * self.radius * length
                pygame.draw.line(screen, (0, 100, 0), (screen_x, screen_y), (end_x, end_y), 2)
