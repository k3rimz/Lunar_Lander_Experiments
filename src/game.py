import pygame
import sys
import math

class Lander:
    def __init__(self, position, angle=0, gravity=0.02, thrust_power=0.04, initial_fuel=1000):
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
        self.rotation_speed = 1.75  # Speed of rotation animation

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

    def update_position(self):
        self.velocity[1] += self.gravity
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]

    def check_collision(self, platform):
        # Calculate the corners of the lander based on its position, size, and angle
        points = [
            (self.position[0] + self.size * math.sin(math.radians(self.angle)), self.position[1] - self.size * math.cos(math.radians(self.angle))),
            (self.position[0] - self.size * math.sin(math.radians(self.angle + 120)), self.position[1] + self.size * math.cos(math.radians(self.angle + 120))),
            (self.position[0] - self.size * math.sin(math.radians(self.angle - 120)), self.position[1] + self.size * math.cos(math.radians(self.angle - 120))),
        ]

        # Check if any of the lander's corners are touching the platform
        for point in points:
            if platform.collidepoint(point):
                self.velocity = [0, 0]  # Stop the lander's motion
                
                # Adjust the lander's position based on the angle
                if -30 <= self.angle <= 30:
                    # Lander is relatively flat, adjust position to sit on the platform
                    self.position[1] = platform.top - self.size
                else:
                    # Lander is tilted, adjust position to touch the platform with the tip
                    if self.angle > 0:
                        # Tilted to the right
                        self.position[0] = platform.right - self.size * math.sin(math.radians(self.angle))
                    else:
                        # Tilted to the left
                        self.position[0] = platform.left + self.size * math.sin(math.radians(self.angle))
                    self.position[1] = platform.top - self.size * math.cos(math.radians(self.angle))
                
                break

    def draw(self, surface):
        # Load the lander icon image with transparency
        lander_icon = pygame.image.load("assets/lander.png").convert_alpha()

        # Rotate the lander icon based on the current angle
        rotated_icon = pygame.transform.rotate(lander_icon, -self.angle)

        # Calculate the position to draw the rotated lander icon
        icon_rect = rotated_icon.get_rect(center=self.position)

        # Draw the rotated lander icon on the surface
        surface.blit(rotated_icon, icon_rect)

        # Draw the metrics, score, and time
        self.draw_metrics(surface)
        self.draw_score(surface)
        self.draw_time(surface)

    def draw_metrics(self, surface):
        font = pygame.font.SysFont("Arial", 18)
        altitude_text = font.render(f"Altitude: {int(HEIGHT - self.position[1])}", True, (255, 255, 255))
        horizontal_speed_text = font.render(f"Horizontal Speed: {int(self.velocity[0])}", True, (255, 255, 255))
        vertical_speed_text = font.render(f"Vertical Speed: {int(self.velocity[1])}", True, (255, 255, 255))
        surface.blit(altitude_text, (10, 30))
        surface.blit(horizontal_speed_text, (10, 50))
        surface.blit(vertical_speed_text, (10, 70))

    def update_score(self, points):
        global score
        score += points

    def draw_score(self, surface):
        font = pygame.font.SysFont("Arial", 18)
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        surface.blit(score_text, (10, 90))

    def draw_time(self, surface):
        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - start_time) // 1000
        font = pygame.font.SysFont("Arial", 18)
        time_text = font.render(f"Time: {elapsed_time}", True, (255, 255, 255))
        surface.blit(time_text, (10, 110))

BLUE = (0, 0, 122)
GREEN = (0, 255, 0)
WIDTH = 1400
HEIGHT = 900

platform = pygame.Rect(WIDTH / 2 - 100, HEIGHT - 50, 200, 10)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

clock = pygame.time.Clock()
FPS = 60

lander = Lander([WIDTH / 2, HEIGHT / 2])
score = 0
start_time = pygame.time.get_ticks()

def reset_game():
    global lander, score, start_time
    lander = Lander([WIDTH / 2, HEIGHT / 2], initial_fuel=1000)
    score = 0
    start_time = pygame.time.get_ticks()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        lander.rotate_left()
    if keys[pygame.K_RIGHT]:
        lander.rotate_right()
    if keys[pygame.K_UP]:
        lander.apply_thrust()
    if keys[pygame.K_r]:
        reset_game()
    if keys[pygame.K_q]:
        pygame.quit()

    lander.update_position()
    lander.update_rotation()
    lander.check_collision(platform)

    screen.fill(BLUE)
    pygame.draw.rect(screen, GREEN, platform)
    lander.draw(screen)

    font = pygame.font.SysFont("Arial", 18)
    fuel_text = font.render(f"Fuel: {lander.fuel}", True, (255, 255, 255))
    screen.blit(fuel_text, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()