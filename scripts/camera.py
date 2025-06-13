class Camera:
    def __init__(self, screen_width, screen_height):
        self.x = 0
        self.y = 0
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.smoothness = 0.1  # Lower values make camera movement smoother
        
    def update(self, target):
        # Smoothly move camera to follow target
        target_x = target.x
        target_y = target.y
        
        # Calculate distance to target
        dx = target_x - self.x
        dy = target_y - self.y
        
        # Move camera a fraction of the distance to target (smooth follow)
        self.x += dx * self.smoothness
        self.y += dy * self.smoothness
