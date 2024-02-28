# I will create a simple Pygame script that implements a basic lunar lander with gravity and a landing platform.
# The lander will be represented as a triangle, and there will be simple controls to apply thrust.

# Import pygame and initialize it
import pygame
import sys
import math

class Lander:
    def __init__(self, position, angle=0, gravity=0.02, thrust_power=0.1, initial_fuel=1000):
        self.position = position
        self.angle = angle
        self.velocity = [0, 0]
        self.size = 15
        self.gravity = gravity
        self.thrust_power = thrust_power
        self.fuel = initial_fuel

    def rotate_left(self):
        self.angle -= 5

    def rotate_right(self):
        self.angle += 5

    def apply_thrust(self):
        if self.fuel > 0:
            self.velocity[0] += math.sin(math.radians(self.angle)) * self.thrust_power
            self.velocity[1] -= math.cos(math.radians(self.angle)) * self.thrust_power
            self.fuel -= 1

    def update_position(self):
        self.velocity[1] += self.gravity  # Apply gravity
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]

    def check_collision(self, platform):
        if self.position[1] + self.size >= platform.top and platform.left < self.position[0] < platform.right:
            self.velocity = [0, 0]  # Stop movement
            self.position[1] = platform.top - self.size  # Adjust position to platform top

    def draw(self, surface):
        points = [
            (self.position[0] + self.size * math.sin(math.radians(self.angle)), self.position[1] - self.size * math.cos(math.radians(self.angle))),
            (self.position[0] - self.size * math.sin(math.radians(self.angle + 120)), self.position[1] + self.size * math.cos(math.radians(self.angle + 120))),
            (self.position[0] - self.size * math.sin(math.radians(self.angle - 120)), self.position[1] + self.size * math.cos(math.radians(self.angle - 120))),
        ] 
        pygame.draw.polygon(surface, (255, 255, 255), points)

# Define colors
BLUE = (0, 0, 122)
GREEN = (0, 255, 0)

# Define the game window size
WIDTH = 800
HEIGHT = 600

# Define the platform as a Pygame Rect object
platform = pygame.Rect(WIDTH / 2 - 100, HEIGHT - 50, 200, 10)

# Initialize Pygame and the display
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Create a clock object to manage the frame rate
clock = pygame.time.Clock()
FPS = 60

# Initialize the lander
lander = Lander([WIDTH / 2, HEIGHT / 2])

def reset_game():
    global lander  # Use global to modify the global instance of Lander
    # Reset or reinitialize the lander
    lander = Lander([WIDTH / 2, HEIGHT / 2], initial_fuel=1000)
    # Add reset or initialization for other elements like fuel, score, etc. here later
    # fuel = MAX_FUEL
    # score = 0

# MAIN GAME LOOP
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Control handling
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

    # Update and draw
    lander.update_position()
    lander.check_collision(platform)  # Use the defined platform

    screen.fill(BLUE)  # Fill background
    pygame.draw.rect(screen, GREEN, platform)  # Draw the platform
    lander.draw(screen)  # Draw the lander

    font = pygame.font.SysFont("Arial", 18) 
    fuel_text = font.render(f"Fuel: {lander.fuel}", True, (255, 255, 255))
    screen.blit(fuel_text, (10, 10))  

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()