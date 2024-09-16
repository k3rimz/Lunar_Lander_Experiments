import pygame
import math
from utils import world_to_screen
from pygame.math import Vector2

class Lander:
    def __init__(self, position, angle=0, gravity=0.02, thrust_power=0.04, initial_fuel=1000, init_landed=False, init_score_added=False):
        self.position = position
        self.angle = angle
        self.target_angle = angle
        self.velocity = [0, 0]
        self.size = 15
        self.gravity = gravity
        self.thrust_power = thrust_power
        self.fuel = initial_fuel
        self.last_rotation_time = 0
        self.rotation_delay = 150
        self.rotation_speed = 1.75  
        self.landed = init_landed
        self.score_added = init_score_added

    def rotate_left(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_rotation_time >= self.rotation_delay:
            self.target_angle = max(-90, self.target_angle - 15)
            self.last_rotation_time = current_time

    def rotate_right(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_rotation_time >= self.rotation_delay:
            self.target_angle = min(90, self.target_angle + 15)
            self.last_rotation_time = current_time

    def update_rotation(self):
        if self.angle != self.target_angle:
            if self.angle < self.target_angle:
                self.angle = min(self.angle + self.rotation_speed, self.target_angle)
            else:
                self.angle = max(self.angle - self.rotation_speed, self.target_angle)

    def apply_thrust(self):
        if self.fuel > 0:
            self.velocity[0] += math.sin(math.radians(self.angle)) * self.thrust_power
            self.velocity[1] -= math.cos(math.radians(self.angle)) * self.thrust_power
            self.fuel -= 1

    def update_position(self, landscape_width, landscape_height):
        if self.landed:
            return
        self.velocity[1] += self.gravity
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]
        self.position[0] = self.position[0] % landscape_width
        self.position[1] = max(0, min(self.position[1], landscape_height))

    def check_collision(self, landscape):
        lander_rect = pygame.Rect(self.position[0] - self.size, self.position[1] - self.size, self.size * 2, self.size * 2)
        tile_offset = int(self.position[0] // landscape.tileWidth) * landscape.tileWidth

        for line in landscape.lines:
            line_start = Vector2(line.p1.x + tile_offset, line.p1.y)
            line_end = Vector2(line.p2.x + tile_offset, line.p2.y)
            if lander_rect.clipline(line_start.x, line_start.y, line_end.x, line_end.y):
                if line.landable and -5 <= self.angle <= 5 and abs(self.velocity[0]) <= 0.5 and abs(self.velocity[1]) <= 0.5:
                    return 'landed'
                else:
                    return 'crashed'
        return None

    def draw(self, surface, camera, landscape):
        screen_pos = world_to_screen(self.position, camera, landscape)
        lander_icon = pygame.image.load("assets/lander.png").convert_alpha()
        rotated_icon = pygame.transform.rotate(lander_icon, -self.angle)
        icon_rect = rotated_icon.get_rect(center=screen_pos)
        surface.blit(rotated_icon, icon_rect)

    def draw_collision_box(self, surface, camera, landscape):
        points = [
            (self.position[0] + self.size * math.sin(math.radians(self.angle)), self.position[1] - self.size * math.cos(math.radians(self.angle))),
            (self.position[0] - self.size * math.sin(math.radians(self.angle + 120)), self.position[1] + self.size * math.cos(math.radians(self.angle + 120))),
            (self.position[0] - self.size * math.sin(math.radians(self.angle - 120)), self.position[1] + self.size * math.cos(math.radians(self.angle - 120))),
        ]
        adjusted_points = [world_to_screen(p, camera, landscape) for p in points]
        pygame.draw.polygon(surface, (255, 0, 0), adjusted_points, 2)

    def draw_metrics(self, surface, window_height):
        font = pygame.font.SysFont("Arial", 18)
        metrics = [
            f"Altitude: {int(window_height - self.position[1])}",
            f"Horizontal Speed: {int(self.velocity[0])}",
            f"Vertical Speed: {int(self.velocity[1])}",
            f"Fuel: {self.fuel}"
        ]
        for i, metric in enumerate(metrics):
            text = font.render(metric, True, (255, 255, 255))
            surface.blit(text, (10, 30 + i * 20))

