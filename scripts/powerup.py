import pygame
import random
import math

class PowerUp:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.z = 0  # Height for 3D effect
        self.z_velocity = 0
        self.type = type  # "health", "speed", "damage", "shield"
        self.radius = 15
        self.collected = False
        self.bob_height = 10
        self.bob_speed = 0.05
        self.bob_offset = random.uniform(0, 2 * math.pi)  # Random starting position
        self.rotation = 0
        self.rotation_speed = 0.02
        self.lifetime = 600  # 10 seconds at 60 FPS
        self.flash_start = 120  # Start flashing when 2 seconds remain
        
        # Set color based on type
        if self.type == "health":
            self.color = (255, 50, 50)  # Red
            self.icon = "+"
        elif self.type == "speed":
            self.color = (50, 50, 255)  # Blue
            self.icon = ">"
        elif self.type == "damage":
            self.color = (255, 165, 0)  # Orange
            self.icon = "!"
        elif self.type == "shield":
            self.color = (50, 255, 50)  # Green
            self.icon = "O"
        else:
            self.color = (255, 255, 255)  # White
            self.icon = "?"
    
    def update(self):
        # Update lifetime
        self.lifetime -= 1
        
        # Update bobbing motion
        self.z = self.bob_height * math.sin(self.bob_offset + pygame.time.get_ticks() * self.bob_speed)
        
        # Update rotation
        self.rotation += self.rotation_speed
        
        # Return True if powerup should be removed
        return self.collected or self.lifetime <= 0
    
    def collect(self, player):
        if self.collected:
            return
            
        self.collected = True
        
        # Apply effect based on type
        if self.type == "health":
            heal_amount = 50
            player.heal(heal_amount)
            print(f"Collected health powerup! Healed {heal_amount} HP.")
            
        elif self.type == "speed":
            # Increase speed for a limited time
            player.speed_boost = 1.5  # 50% speed boost
            player.speed_boost_time = 300  # 5 seconds
            print("Collected speed powerup! Movement speed increased for 5 seconds.")
            
        elif self.type == "damage":
            # Increase bomb damage for a limited time
            player.damage_boost = 1.5  # 50% damage boost
            player.damage_boost_time = 300  # 5 seconds
            print("Collected damage powerup! Bomb damage increased for 5 seconds.")
            
        elif self.type == "shield":
            # Add a shield that absorbs damage
            player.shield = 50  # Shield absorbs 50 damage
            print("Collected shield powerup! Next 50 damage will be absorbed.")
    
    def draw(self, screen, camera):
        # Calculate screen position with 3D effect
        screen_x = int(self.x - camera.x + screen.get_width() // 2)
        screen_y = int(self.y - camera.y + screen.get_height() // 2 - self.z)
        
        # Draw shadow
        shadow_size = self.radius * 2
        shadow_alpha = max(40, min(150, 150 - self.z))
        shadow_surface = pygame.Surface((shadow_size, shadow_size // 2), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, shadow_alpha), 
                          (0, 0, shadow_size, shadow_size // 2))
        screen.blit(shadow_surface, 
                  (screen_x - shadow_size // 2, 
                   int(self.y - camera.y + screen.get_height() // 2) - shadow_size // 4))
        
        # Create powerup surface for rotation
        powerup_size = self.radius * 2
        powerup_surface = pygame.Surface((powerup_size, powerup_size), pygame.SRCALPHA)
        
        # Flash if about to disappear
        alpha = 255
        if self.lifetime < self.flash_start:
            alpha = int(255 * (self.lifetime / self.flash_start))
            if self.lifetime % 10 < 5:  # Blink effect
                alpha = min(255, alpha + 100)
        
        # Draw powerup circle
        pygame.draw.circle(powerup_surface, (*self.color, alpha), 
                         (self.radius, self.radius), self.radius)
        
        # Draw powerup icon
        font = pygame.font.SysFont(None, 24)
        icon_surface = font.render(self.icon, True, (255, 255, 255, alpha))
        icon_rect = icon_surface.get_rect(center=(self.radius, self.radius))
        powerup_surface.blit(icon_surface, icon_rect)
        
        # Apply rotation and draw
        rotated_powerup = pygame.transform.rotate(powerup_surface, math.degrees(self.rotation))
        powerup_rect = rotated_powerup.get_rect(center=(screen_x, screen_y))
        screen.blit(rotated_powerup, powerup_rect.topleft)
        
        # Draw glow effect
        glow_radius = self.radius + 5 + int(2 * math.sin(pygame.time.get_ticks() * 0.01))
        glow_surface = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
        for r in range(glow_radius, glow_radius-5, -1):
            alpha = max(0, 150 - (glow_radius - r) * 30)
            pygame.draw.circle(glow_surface, (*self.color, alpha), 
                             (glow_radius, glow_radius), r)
        
        glow_rect = glow_surface.get_rect(center=(screen_x, screen_y))
        screen.blit(glow_surface, glow_rect.topleft)
