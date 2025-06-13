import pygame
import random
import math

class Island:
    def __init__(self):
        self.width = 2000  # Increased from 1000
        self.height = 2000  # Increased from 1000
        self.color = (194, 178, 128)  # Sandy color
        
        # Generate some random trees and rocks for the island
        self.trees = []
        self.rocks = []
        self.water_spots = []
        self.grass_patches = []
        self.palm_trees = []
        
        # Generate trees - increased count for larger island
        for _ in range(60):
            x = random.randint(100, self.width - 100)
            y = random.randint(100, self.height - 100)
            size = random.randint(20, 40)
            height = random.randint(30, 60)
            self.trees.append((x, y, size, height))
        
        # Generate palm trees - increased count for larger island
        for _ in range(30):
            x = random.randint(50, self.width - 50)
            y = random.randint(50, self.height - 50)
            size = random.randint(30, 50)
            self.palm_trees.append((x, y, size))
        
        # Generate rocks - increased count for larger island
        for _ in range(40):
            x = random.randint(50, self.width - 50)
            y = random.randint(50, self.height - 50)
            size = random.randint(10, 25)
            self.rocks.append((x, y, size))
            
        # Generate water spots (small ponds) - reduced count as requested
        for _ in range(3):
            x = random.randint(200, self.width - 200)
            y = random.randint(200, self.height - 200)
            size = random.randint(30, 60)
            self.water_spots.append((x, y, size))
            
        # Generate grass patches - increased count for larger island
        for _ in range(80):
            x = random.randint(50, self.width - 50)
            y = random.randint(50, self.height - 50)
            size = random.randint(15, 40)
            self.grass_patches.append((x, y, size))
            
    def draw(self, screen, camera):
        # Calculate screen position
        screen_x = int(-camera.x + screen.get_width() // 2)
        screen_y = int(-camera.y + screen.get_height() // 2)
        
        # Draw main island
        pygame.draw.ellipse(screen, self.color, 
                          (screen_x - self.width//2, screen_y - self.height//2, 
                           self.width, self.height))
        
        # Draw grass patches
        for x, y, size in self.grass_patches:
            grass_x = screen_x - self.width//2 + x
            grass_y = screen_y - self.height//2 + y
            
            # Draw multiple grass blades
            for i in range(8):
                blade_angle = random.uniform(0, 2 * math.pi)
                blade_length = random.uniform(size * 0.5, size)
                end_x = grass_x + math.cos(blade_angle) * blade_length * 0.5
                end_y = grass_y + math.sin(blade_angle) * blade_length * 0.5
                
                # Vary the green color slightly
                green_value = random.randint(100, 150)
                pygame.draw.line(screen, (34, green_value, 34), 
                               (grass_x, grass_y), (end_x, end_y), 2)
        
        # Draw water spots (ponds)
        for x, y, size in self.water_spots:
            pond_x = screen_x - self.width//2 + x
            pond_y = screen_y - self.height//2 + y
            
            # Draw main water
            pygame.draw.ellipse(screen, (64, 164, 223), 
                              (pond_x - size//2, pond_y - size//2, size, size))
            
            # Draw water highlights
            highlight_size = size // 3
            highlight_offset = size // 6
            pygame.draw.ellipse(screen, (120, 200, 255), 
                              (pond_x - highlight_size//2 + highlight_offset, 
                               pond_y - highlight_size//2 - highlight_offset, 
                               highlight_size, highlight_size//2), 1)
        
        # Draw rocks
        for x, y, size in self.rocks:
            rock_x = screen_x - self.width//2 + x
            rock_y = screen_y - self.height//2 + y
            
            # Draw rock with slight 3D effect
            pygame.draw.ellipse(screen, (100, 100, 100), 
                              (rock_x - size//2, rock_y - size//2, size, size))
            
            # Add highlight to rock
            highlight_size = size // 2
            pygame.draw.ellipse(screen, (150, 150, 150), 
                              (rock_x - highlight_size//2, rock_y - highlight_size//2, 
                               highlight_size, highlight_size))
        
        # Draw trees
        for x, y, size, height in self.trees:
            tree_x = screen_x - self.width//2 + x
            tree_y = screen_y - self.height//2 + y
            
            # Draw tree trunk with 3D effect
            trunk_width = size // 3
            trunk_height = height
            
            # Trunk shadow
            pygame.draw.rect(screen, (80, 50, 20), 
                           (tree_x - trunk_width//2 + 2, tree_y - trunk_height//2, 
                            trunk_width, trunk_height))
            
            # Main trunk
            pygame.draw.rect(screen, (101, 67, 33), 
                           (tree_x - trunk_width//2, tree_y - trunk_height//2, 
                            trunk_width, trunk_height))
            
            # Draw tree top (leaves) with 3D effect
            # Shadow
            pygame.draw.circle(screen, (20, 100, 20), 
                             (tree_x + 3, tree_y - trunk_height//2 - size//3), size//2)
            
            # Main leaves
            pygame.draw.circle(screen, (34, 139, 34), 
                             (tree_x, tree_y - trunk_height//2 - size//3), size//2)
            
            # Highlight
            highlight_size = size // 3
            pygame.draw.circle(screen, (50, 180, 50), 
                             (tree_x - size//6, tree_y - trunk_height//2 - size//3 - size//6), 
                             highlight_size)
        
        # Draw palm trees
        for x, y, size in self.palm_trees:
            palm_x = screen_x - self.width//2 + x
            palm_y = screen_y - self.height//2 + y
            
            # Draw trunk with curve
            trunk_width = size // 6
            trunk_height = size * 1.5
            
            # Draw curved trunk
            points = []
            curve_amount = random.uniform(size//4, size//2)
            curve_direction = random.choice([-1, 1])
            
            for i in range(10):
                progress = i / 9  # 0 to 1
                curve_x = math.sin(progress * math.pi) * curve_amount * curve_direction
                point_x = palm_x + curve_x
                point_y = palm_y - progress * trunk_height
                points.append((point_x, point_y))
            
            # Draw trunk segments
            for i in range(len(points)-1):
                pygame.draw.line(screen, (80, 50, 20), points[i], points[i+1], trunk_width)
            
            # Draw palm leaves
            leaf_count = 5
            top_x, top_y = points[-1]
            
            for i in range(leaf_count):
                angle = 2 * math.pi * i / leaf_count
                leaf_length = size
                
                # Calculate control points for curved leaf
                end_x = top_x + math.cos(angle) * leaf_length
                end_y = top_y + math.sin(angle) * leaf_length
                
                ctrl_x = top_x + math.cos(angle) * leaf_length * 0.3
                ctrl_y = top_y + math.sin(angle) * leaf_length * 0.3
                
                # Draw leaf as a polygon
                leaf_width = size // 4
                
                # Calculate points for leaf shape
                leaf_points = []
                leaf_points.append((top_x, top_y))
                
                # Add points along the curve
                steps = 10
                for step in range(1, steps + 1):
                    t = step / steps
                    # Quadratic Bezier curve
                    bx = (1-t)**2 * top_x + 2*(1-t)*t * ctrl_x + t**2 * end_x
                    by = (1-t)**2 * top_y + 2*(1-t)*t * ctrl_y + t**2 * end_y
                    
                    # Add width to create leaf shape
                    width_factor = math.sin(t * math.pi) * leaf_width
                    perp_x = math.cos(angle + math.pi/2) * width_factor
                    perp_y = math.sin(angle + math.pi/2) * width_factor
                    
                    if step < steps:  # Don't add width at the very tip
                        leaf_points.append((bx + perp_x, by + perp_y))
                
                # Add points in reverse for other side of leaf
                for step in range(steps, 0, -1):
                    t = step / steps
                    bx = (1-t)**2 * top_x + 2*(1-t)*t * ctrl_x + t**2 * end_x
                    by = (1-t)**2 * top_y + 2*(1-t)*t * ctrl_y + t**2 * end_y
                    
                    width_factor = math.sin(t * math.pi) * leaf_width
                    perp_x = math.cos(angle - math.pi/2) * width_factor
                    perp_y = math.sin(angle - math.pi/2) * width_factor
                    
                    if step < steps:  # Don't add width at the very tip
                        leaf_points.append((bx + perp_x, by + perp_y))
                
                # Draw the leaf
                pygame.draw.polygon(screen, (0, 100, 0), leaf_points)
                pygame.draw.polygon(screen, (0, 150, 0), leaf_points, 1)
        
        # Draw island border (shore)
        pygame.draw.ellipse(screen, (214, 198, 148), 
                          (screen_x - self.width//2 - 10, screen_y - self.height//2 - 10, 
                           self.width + 20, self.height + 20), 20)
        
        # Draw water edge effect
        pygame.draw.ellipse(screen, (120, 200, 255, 100), 
                          (screen_x - self.width//2 - 30, screen_y - self.height//2 - 30, 
                           self.width + 60, self.height + 60), 30)
