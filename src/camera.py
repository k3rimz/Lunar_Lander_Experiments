import pygame

class Camera:
    def __init__(self, width, height):
        self.rect = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.deadzone_left = int(width * 0.2)
        self.deadzone_right = int(width * 0.8)

    def update(self, target_pos, landscape):
        # Calculate target position relative to camera
        rel_x = (target_pos[0] - self.rect.left) % landscape.width

        # Horizontal movement
        if rel_x < self.deadzone_left:
            self.rect.x += rel_x - self.deadzone_left
        elif rel_x > self.deadzone_right:
            self.rect.x -= rel_x - self.deadzone_right

        # Vertical movement
        self.rect.centery = target_pos[1]

        # Ensure camera stays within vertical bounds
        if self.rect.top < 0:
            self.rect.top = 0
        elif self.rect.bottom > landscape.height:
            self.rect.bottom = landscape.height

        # Wrap camera horizontally
        self.rect.left = self.rect.left % landscape.width