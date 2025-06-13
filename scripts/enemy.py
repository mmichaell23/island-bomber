import pygame
import random
import math

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 50
        self.color = (255, 0, 0)  # Red
        self.speed = 1.8  # Reduced from 2 for more realistic movement
        self.health = 100
        self.max_health = 100
        self.is_alive = True
        self.z = 0  # Height for 3D effect
        self.z_velocity = 0
        self.jumping = False
        self.hit_cooldown = 0  # Prevent multiple hits from same explosion
        
        # Movement physics
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration = 0.2
        self.friction = 0.92
        self.max_speed = self.speed
        
        # Attack properties
        self.attack_range = 60
        self.attack_damage = 15  # Increased from 10 to 15
        self.attack_cooldown = 0
        self.attack_cooldown_max = 45  # Reduced from 60 to 45 (attack more frequently)
        
        # Bomb throwing properties - more aggressive
        self.can_throw_bombs = True  # All enemies can throw bombs now
        self.bomb_cooldown = random.randint(60, 120)  # 1-2 seconds between bomb throws
        self.bomb_throw_range = 400  # Maximum distance to throw bombs
        self.bomb_throw_min_range = 80  # Minimum distance to throw bombs
        
        # AI behavior
        self.state = "patrol"  # patrol, chase, flee, attack, throw_bomb
        self.patrol_point_x = x
        self.patrol_point_y = y
        self.patrol_radius = 100
        self.patrol_angle = random.uniform(0, 2 * math.pi)
        self.detection_range = 500  # Increased from 300 to 500 (detect player from further away)
        self.target = None
        
        # Animation variables
        self.animation_frame = 0
        self.animation_speed = 0.1
        self.direction_facing = 1  # 1 for right, -1 for left
        
        # AI behavior
        self.state = "patrol"  # patrol, chase, flee, attack, throw_bomb
        self.patrol_point_x = x
        self.patrol_point_y = y
        self.patrol_radius = 100
        self.patrol_angle = random.uniform(0, 2 * math.pi)
        self.detection_range = 300  # Increased from 200
        self.target = None
        
        # Animation variables
        self.animation_frame = 0
        self.animation_speed = 0.1
        self.direction_facing = 1  # 1 for right, -1 for left
        
        # AI behavior
        self.state = "patrol"  # patrol, chase, flee, attack, throw_bomb
        self.patrol_point_x = x
        self.patrol_point_y = y
        self.patrol_radius = 100
        self.patrol_angle = random.uniform(0, 2 * math.pi)
        self.detection_range = 300  # Increased from 200
        self.target = None
        
        # Animation variables
        self.animation_frame = 0
        self.animation_speed = 0.1
        self.direction_facing = 1  # 1 for right, -1 for left
        
        # AI behavior
        self.state = "patrol"  # patrol, chase, flee, attack, throw_bomb
        self.patrol_point_x = x
        self.patrol_point_y = y
        self.patrol_radius = 100
        self.patrol_angle = random.uniform(0, 2 * math.pi)
        self.detection_range = 200
        self.target = None
        
        # Animation variables
        self.animation_frame = 0
        self.animation_speed = 0.1
        self.direction_facing = 1  # 1 for right, -1 for left
        
    def move_towards(self, target_x, target_y, speed_modifier=1.0):
        # Calculate direction
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            # Set direction facing for animation
            self.direction_facing = 1 if dx > 0 else -1
            
            # Normalize direction
            dx /= distance
            dy /= distance
            
            # Apply acceleration in the target direction
            self.velocity_x += dx * self.acceleration * speed_modifier
            self.velocity_y += dy * self.acceleration * speed_modifier
            
            # Apply friction
            self.velocity_x *= self.friction
            self.velocity_y *= self.friction
            
            # Limit maximum speed
            speed_magnitude = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
            max_speed = self.max_speed * speed_modifier
            
            if speed_magnitude > max_speed:
                speed_ratio = max_speed / speed_magnitude
                self.velocity_x *= speed_ratio
                self.velocity_y *= speed_ratio
                
            # Apply velocity
            self.x += self.velocity_x
            self.y += self.velocity_y
            
            # Update animation frame when moving
            self.animation_frame += self.animation_speed * (speed_magnitude / self.max_speed)
            return True
        return False
        
    def update(self, player, bombs):
        if not self.is_alive:
            return None
            
        # Update hit cooldown
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1
            
        # Update bomb cooldown
        if self.can_throw_bombs and self.bomb_cooldown > 0:
            self.bomb_cooldown -= 1
            
        # Check for bomb damage
        for bomb in bombs:
            if bomb.exploding and self.hit_cooldown == 0:
                # Calculate distance to bomb explosion
                dx = self.x - bomb.x
                dy = self.y - bomb.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                # Check if within explosion radius
                if distance < bomb.explosion_radius:
                    # Calculate damage based on distance (more damage closer to center)
                    damage_factor = 1 - (distance / bomb.explosion_radius)
                    
                    # Apply damage multiplier if bomb has one
                    damage_multiplier = getattr(bomb, 'damage_multiplier', 1.0)
                    damage = int(50 * damage_factor * damage_multiplier)
                    
                    print(f"Bomb hit enemy! Distance: {distance:.1f}, Damage: {damage}")
                    
                    # Apply damage and check if enemy died
                    self.take_damage(damage)
                    self.hit_cooldown = 10  # Prevent multiple hits from same explosion
                    
                    # Knockback effect from explosion
                    if distance > 0 and self.is_alive:  # Only apply knockback if still alive
                        knockback_strength = 10 * damage_factor
                        knockback_x = (self.x - bomb.x) / distance * knockback_strength
                        knockback_y = (self.y - bomb.y) / distance * knockback_strength
                        
                        # Apply knockback to velocity instead of position for smoother effect
                        self.velocity_x += knockback_x
                        self.velocity_y += knockback_y
                        self.z_velocity = 5 * damage_factor  # Jump up from explosion
        
        # Update 3D jumping effect
        if self.z > 0 or self.z_velocity != 0:
            self.z += self.z_velocity
            self.z_velocity -= 0.5  # Gravity
            
            # Ground collision
            if self.z <= 0:
                self.z = 0
                self.z_velocity = 0
                self.jumping = False
        
        # Calculate distance to player
        dx = player.x - self.x
        dy = player.y - self.y
        distance_to_player = math.sqrt(dx*dx + dy*dy)
        
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Always target the player - more aggressive behavior
        self.target = player
        
        # Check if we should throw a bomb - more aggressive
        if (self.can_throw_bombs and 
            self.bomb_cooldown <= 0 and 
            distance_to_player < self.bomb_throw_range and 
            distance_to_player > self.bomb_throw_min_range):
            
            # Set state to throw bomb
            self.state = "throw_bomb"
            
            # Throw the bomb and return the bomb data
            bomb_data = self.throw_bomb(player)
            
            # Reset bomb cooldown - shorter cooldown for more aggression
            self.bomb_cooldown = random.randint(60, 120)  # 1-2 seconds between throws
            
            # Go back to chasing after throwing
            self.state = "chase"
            
            # Return the bomb data to be added to the game
            return bomb_data
        
        # AI behavior - more aggressive
        if distance_to_player < self.detection_range:
            # Always chase or attack when player is in range
            if distance_to_player < self.attack_range:
                self.state = "attack"
            else:
                self.state = "chase"
        else:
            # Patrol when player is out of range
            self.state = "patrol"
        
        # Execute behavior based on state
        if self.state == "patrol":
            # Move in a circular patrol pattern
            self.patrol_angle += 0.01  # Slower patrol
            target_x = self.patrol_point_x + math.cos(self.patrol_angle) * self.patrol_radius
            target_y = self.patrol_point_y + math.sin(self.patrol_angle) * self.patrol_radius
            
            # Move towards patrol point with reduced speed
            self.move_towards(target_x, target_y, 0.7)
            
            # Check if player is in detection range - redundant but kept for safety
            if distance_to_player < self.detection_range:
                self.state = "chase"
                # Occasionally jump when spotting player
                if random.random() < 0.3 and self.z == 0:
                    self.z_velocity = 8
                    self.jumping = True
        
        elif self.state == "chase":
            # Chase the player
            target_x = player.x
            target_y = player.y
            
            # Move towards player with increased speed for more aggression
            self.move_towards(target_x, target_y, 1.2)
            
            # Check if close enough to attack
            if distance_to_player < self.attack_range:
                self.state = "attack"
                
            # Occasionally jump while chasing
            if random.random() < 0.02 and self.z == 0:  # Increased jump frequency
                self.z_velocity = 6
                self.jumping = True
        
        elif self.state == "attack":
            # Attack the player if in range and cooldown is ready
            if distance_to_player < self.attack_range and self.attack_cooldown == 0:
                self.attack(player)
                
            # Move slightly closer if not perfectly in range
            target_x = player.x
            target_y = player.y
            
            # Move towards player with reduced speed during attack
            self.move_towards(target_x, target_y, 0.5)
            
            # Switch back to chase if player moves away
            if distance_to_player > self.attack_range * 1.2:
                self.state = "chase"
        
        elif self.state == "throw_bomb":
            # Stop moving while throwing
            self.velocity_x *= 0.7
            self.velocity_y *= 0.7
            
            # Face the player
            self.direction_facing = 1 if player.x > self.x else -1
            
            # Jump slightly when throwing
            if self.z == 0:
                self.z_velocity = 3
                self.jumping = True
                
        # Return None if no bomb is thrown
        return None
        
    def throw_bomb(self, player):
        # Calculate direction to player
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            # Normalize direction
            dir_x = dx / distance
            dir_y = dy / distance
            
            # Add less randomness for more accurate throws
            dir_x += random.uniform(-0.1, 0.1)
            dir_y += random.uniform(-0.1, 0.1)
            
            # Normalize again after adding randomness
            magnitude = math.sqrt(dir_x**2 + dir_y**2)
            if magnitude > 0:
                dir_x /= magnitude
                dir_y /= magnitude
            
            # Create a bomb (will be added to the game's bomb list in main.py)
            bomb_type = random.choice(["regular", "cracking", "timer"])  # Added timer bombs
            
            # Jump slightly when throwing
            if self.z == 0:
                self.z_velocity = 3
                self.jumping = True
                
            print(f"Enemy throws a {bomb_type} bomb at player from distance {distance:.1f}!")
            
            # Return bomb data to be created in main.py
            return {
                'x': self.x,
                'y': self.y,
                'dir_x': dir_x,
                'dir_y': dir_y,
                'type': bomb_type,
                'enemy_bomb': True  # Flag to identify enemy bombs
            }
        return None
        
    def attack(self, player):
        print(f"Enemy attacks player for {self.attack_damage} damage!")
        player.take_damage(self.attack_damage)
        self.attack_cooldown = self.attack_cooldown_max
        
        # Jump slightly during attack
        if self.z == 0:
            self.z_velocity = 3
            self.jumping = True
    
    def take_damage(self, amount):
        self.health -= amount
        print(f"Enemy took {amount} damage! Health: {self.health}")
        
        # Visual feedback - jump when hit
        if self.z == 0:
            self.z_velocity = 4
            self.jumping = True
        
        if self.health <= 0:
            self.die()
            return True  # Return True if enemy died from this damage
        return False
    
    def die(self):
        self.is_alive = False
        print("Enemy defeated!")
    
    def draw(self, screen, camera):
        if not self.is_alive:
            return
            
        # Calculate screen position with 3D effect
        screen_x = int(self.x - camera.x + screen.get_width() // 2)
        screen_y = int(self.y - camera.y + screen.get_height() // 2 - self.z)
        
        # Scale based on z position for 3D effect
        scale_factor = 1.0 - (self.z / 200)  # Smaller when jumping higher
        scale_factor = max(0.5, min(1.0, scale_factor))  # Clamp between 0.5 and 1.0
        
        width = int(self.width * scale_factor)
        height = int(self.height * scale_factor)
        
        # Draw shadow (gets larger as enemy jumps higher)
        shadow_size = width * (1 + self.z / 50)
        shadow_alpha = max(40, min(150, 150 - self.z))  # Fade shadow with height
        shadow_surface = pygame.Surface((shadow_size, shadow_size // 2), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, shadow_alpha), 
                          (0, 0, shadow_size, shadow_size // 2))
        screen.blit(shadow_surface, 
                  (screen_x - shadow_size // 2, 
                   int(self.y - camera.y + screen.get_height() // 2) - shadow_size // 4))
        
        # Flash red when hit (if hit cooldown is active)
        if self.hit_cooldown > 0:
            body_color = (255, 100, 100)  # Bright red when hit
        else:
            # Normal color with 3D effect
            if self.can_throw_bombs:
                # Bomber enemies have a slightly different color (orange-red)
                body_color = (max(100, 200 - self.z//2), 
                             max(0, 100 - self.z//2), 
                             max(0, 0 - self.z//2))
            else:
                body_color = (max(100, self.color[0] - self.z//2), 
                             max(0, self.color[1] - self.z//2), 
                             max(0, self.color[2] - self.z//2))
        
        # Animation effect - slight bobbing when moving
        bob_offset = int(math.sin(self.animation_frame) * 2)
        
        # Draw legs
        leg_width = width // 3
        leg_height = height // 2
        leg_spacing = width // 2
        
        # Animate legs based on movement
        left_leg_offset = int(math.sin(self.animation_frame) * 5)
        right_leg_offset = int(math.sin(self.animation_frame + math.pi) * 5)
        
        pygame.draw.rect(screen, (100, 0, 0), 
                       (screen_x - leg_spacing//2 - leg_width//2, 
                        screen_y + height//2 - leg_height + left_leg_offset, 
                        leg_width, leg_height))
        
        pygame.draw.rect(screen, (100, 0, 0), 
                       (screen_x + leg_spacing//2 - leg_width//2, 
                        screen_y + height//2 - leg_height + right_leg_offset, 
                        leg_width, leg_height))
        
        # Draw body
        pygame.draw.rect(screen, body_color, 
                       (screen_x - width // 2, 
                        screen_y - height // 2 + bob_offset, 
                        width, height))
        
        # Draw arms
        arm_width = width // 3
        arm_height = height // 2
        arm_spacing = width * 0.8
        
        # Animate arms based on state
        if self.state == "attack" and self.attack_cooldown > self.attack_cooldown_max * 0.8:
            # Attack animation - extend arm forward
            attack_arm_extension = 15
            pygame.draw.rect(screen, (150, 0, 0), 
                           (screen_x + self.direction_facing * (width//2), 
                            screen_y - height//4, 
                            self.direction_facing * attack_arm_extension, arm_width))
        elif self.state == "throw_bomb" and self.bomb_cooldown > 0 and self.bomb_cooldown < 10:
            # Bomb throwing animation - extend arm forward
            throw_arm_extension = 20
            pygame.draw.rect(screen, (150, 0, 0), 
                           (screen_x + self.direction_facing * (width//2), 
                            screen_y - height//4, 
                            self.direction_facing * throw_arm_extension, arm_width))
            
            # Draw bomb in hand
            if self.bomb_cooldown < 5:
                bomb_x = screen_x + self.direction_facing * (width//2 + throw_arm_extension)
                bomb_y = screen_y - height//4 + arm_width//2
                pygame.draw.circle(screen, (0, 0, 0), (bomb_x, bomb_y), 8)
        else:
            # Normal arm animation
            left_arm_offset = int(math.sin(self.animation_frame + math.pi/2) * 5)
            right_arm_offset = int(math.sin(self.animation_frame + 3*math.pi/2) * 5)
            
            pygame.draw.rect(screen, (150, 0, 0), 
                           (screen_x - arm_spacing//2 - arm_width//2, 
                            screen_y - height//4 + left_arm_offset, 
                            arm_width, arm_height))
            
            pygame.draw.rect(screen, (150, 0, 0), 
                           (screen_x + arm_spacing//2 - arm_width//2, 
                            screen_y - height//4 + right_arm_offset, 
                            arm_width, arm_height))
        
        # Draw enemy head
        head_radius = int(12 * scale_factor)
        pygame.draw.circle(screen, (200, 0, 0),  # Darker red
                         (screen_x, screen_y - height // 2 - head_radius // 2 + bob_offset),
                         head_radius)
        
        # Draw eyes
        eye_radius = head_radius // 3
        eye_spacing = head_radius // 2
        
        # Eyes direction - use target if available or default to direction facing
        if self.target:
            eye_direction_x = self.target.x - self.x
            eye_direction_y = self.target.y - self.y
            eye_distance = math.sqrt(eye_direction_x**2 + eye_direction_y**2)
            
            if eye_distance > 0:
                eye_direction_x /= eye_distance
                eye_direction_y /= eye_distance
        else:
            # Default eye direction if no target
            eye_direction_x = self.direction_facing
            eye_direction_y = 0
        
        eye_offset_x = eye_direction_x * (head_radius // 4)
        eye_offset_y = eye_direction_y * (head_radius // 4)
        
        # White of eyes
        pygame.draw.circle(screen, (255, 255, 255),
                         (screen_x - eye_spacing, screen_y - height // 2 - head_radius // 2 + bob_offset),
                         eye_radius)
        pygame.draw.circle(screen, (255, 255, 255),
                         (screen_x + eye_spacing, screen_y - height // 2 - head_radius // 2 + bob_offset),
                         eye_radius)
        
        # Pupils
        pygame.draw.circle(screen, (0, 0, 0),
                         (int(screen_x - eye_spacing + eye_offset_x), 
                          int(screen_y - height // 2 - head_radius // 2 + bob_offset + eye_offset_y)),
                         eye_radius // 2)
        pygame.draw.circle(screen, (0, 0, 0),
                         (int(screen_x + eye_spacing + eye_offset_x), 
                          int(screen_y - height // 2 - head_radius // 2 + bob_offset + eye_offset_y)),
                         eye_radius // 2)
        
        # Draw health bar
        health_bar_width = 40
        health_bar_height = 5
        health_percentage = max(0, self.health / 100)
        
        # Background (empty health)
        pygame.draw.rect(screen, (255, 0, 0),
                       (screen_x - health_bar_width // 2,
                        screen_y - height // 2 - head_radius - 10,
                        health_bar_width, health_bar_height))
        
        # Foreground (current health)
        pygame.draw.rect(screen, (0, 255, 0),
                       (screen_x - health_bar_width // 2,
                        screen_y - height // 2 - head_radius - 10,
                        int(health_bar_width * health_percentage), health_bar_height))
        
        # Draw bomb icon above bomber enemies
        if self.can_throw_bombs and self.bomb_cooldown < 60:  # Show icon when bomb is almost ready
            bomb_icon_radius = 6
            pygame.draw.circle(screen, (0, 0, 0), 
                             (screen_x, screen_y - height // 2 - head_radius - 20),
                             bomb_icon_radius)
            # Draw fuse
            pygame.draw.line(screen, (100, 100, 100),
                           (screen_x, screen_y - height // 2 - head_radius - 20 - bomb_icon_radius),
                           (screen_x, screen_y - height // 2 - head_radius - 20 - bomb_icon_radius - 3), 2)
            # Draw spark (blinking)
            if self.bomb_cooldown % 10 < 5:
                pygame.draw.circle(screen, (255, 200, 0),
                                 (screen_x, screen_y - height // 2 - head_radius - 20 - bomb_icon_radius - 3),
                                 2)
