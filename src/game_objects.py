import pygame
from utils import WINDOW_WIDTH, WINDOW_HEIGHT

class GameObstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, obstacle_type, bonus_multiplier=1):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.type = obstacle_type  # 'landing_pad' or 'terrain'
        self.bonus_multiplier = bonus_multiplier

    def update(self, new_width, new_height):
        # This method can be used to update the obstacle's position and size
        # if the window is resized or if we implement scrolling
        pass

    def draw(self, surface, camera):
        # This method can be implemented to draw the obstacle on the screen
        # taking into account the camera position
        pass

class LandingZone(GameObstacle):
    def __init__(self, x_ratio, y_ratio, width_ratio, height_ratio, bonus_multiplier=1):
        self.x_ratio = x_ratio
        self.y_ratio = y_ratio
        self.width_ratio = width_ratio
        self.height_ratio = height_ratio
        x = int(x_ratio * WINDOW_WIDTH)
        y = int(y_ratio * WINDOW_HEIGHT)
        width = int(width_ratio * WINDOW_WIDTH)
        height = int(height_ratio * WINDOW_HEIGHT)
        super().__init__(x, y, width, height, 'landing_pad', bonus_multiplier)

    def update(self, new_width, new_height):
        self.rect.x = int(self.x_ratio * new_width)
        self.rect.y = int(self.y_ratio * new_height)
        self.rect.width = int(self.width_ratio * new_width)
        self.rect.height = int(self.height_ratio * new_height)

# You can add more specific obstacle types here if needed in the future