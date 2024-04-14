import random
import pygame
import sys
import math
from enum import Enum

class GameState(Enum):
    MAIN_MENU = 1
    IN_GAME = 2
    LANDED_CRASHED = 3


class Button:
    def __init__(self, x, y, width, height, text=''):
        self.color = (0, 200, 0)  # Green
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self, win, outline=None):
        # Call this method to draw the button on the screen
        if outline:
            pygame.draw.rect(win, outline, (self.x-2, self.y-2, self.width+4, self.height+4), 0)
            
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 0)
        
        if self.text != '':
            font = pygame.font.SysFont('comicsans', 60)
            text = font.render(self.text, 1, (0,0,0))
            win.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))

    def is_over(self, pos):
        # Pos is the mouse position or a tuple of (x,y) coordinates
        if self.x < pos[0] < self.x + self.width:
            if self.y < pos[1] < self.y + self.height:
                return True
            
        return False


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
        self.rotation_speed = 1.75  # Speed of rotation animation
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

    def update_position(self):
        if self.landed:
            # Skip position and velocity updates if landed to prevent bobbing or phasing through.
            return
        self.velocity[1] += self.gravity
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]
        self.position[0] = max(0, min(self.position[0], WINDOW_WIDTH))
        self.position[1] = max(0, min(self.position[1], WINDOW_HEIGHT))

    def check_collision(self, platform):
        # Calculate the corners of the lander based on its position, size, and angle
        points = [
            (self.position[0] + self.size * math.sin(math.radians(self.angle)), self.position[1] - self.size * math.cos(math.radians(self.angle))),
            (self.position[0] - self.size * math.sin(math.radians(self.angle + 120)), self.position[1] + self.size * math.cos(math.radians(self.angle + 120))),
            (self.position[0] - self.size * math.sin(math.radians(self.angle - 120)), self.position[1] + self.size * math.cos(math.radians(self.angle - 120))),
        ]

        # Check if any of the lander's corners are touching the platform
        for point in points:
            if platform.rect.collidepoint(point):
                # Check landing conditions
                if -5 <= self.angle <= 5 and abs(self.velocity[0]) <= 10 and abs(self.velocity[1]) <= 10:
                    if not self.landed:
                        print("Landing successful.")
                        self.velocity = [0, 0]  # Stop the lander's motion
                        self.landed = True  # Set the landed flag to True
                        if not self.score_added:
                            self.update_score(100 * platform.bonus_multiplier)  # Add points for successful landing
                            self.fuel += 100 + (100 * platform.bonus_multiplier)  # Increase fuel based on landing success
                            self.fuel = min(self.fuel, 1000)  # Optional: Cap the fuel
                            self.score_added = True  # Set the score_added flag to True
                            self.position[1] = platform.rect.top + self.size  # Adjust the lander's position to sit on the platform
                            return 'landed'
                    else:
                        print("Lander already landed.")
                    return  # Exit the method after a successful landing
                else:
                    # Crash scenario
                    self.velocity = [0, 0]  # Stop the lander's motion
                    print("Crash! Game Over.")
                    return 'crashed'

        
        # Reset the flags if not touching any platform for more than 3 seconds 
        self.landed = False
        self.score_added = False

    def reset_position(self):
        self.position = [random.randint(0, WINDOW_WIDTH), -self.size]  # Start above the visible area
        self.velocity = [0, 0]
        self.landed = False
        self.score_added = False  # Reset score flag for next landing or crash
        
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
        altitude_text = font.render(f"Altitude: {int(WINDOW_HEIGHT - self.position[1])}", True, (255, 255, 255))
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
BLACK = (0, 0, 0)

def update_window_size(width, height):
    global WINDOW_WIDTH, WINDOW_HEIGHT, screen, lander
    WINDOW_WIDTH = width
    WINDOW_HEIGHT = height
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
    for pad in landing_pads:
        pad.update_rect()
    for terrain in terrain_group:
        terrain.update_rect()
    lander.position = [WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2]  # Update lander position

class LandingPad(pygame.sprite.Sprite):
    def __init__(self, x_ratio, y_ratio, width_ratio, height_ratio, bonus_multiplier=1):
        super().__init__()
        self.x_ratio = x_ratio
        self.y_ratio = y_ratio
        self.width_ratio = width_ratio
        self.height_ratio = height_ratio
        self.bonus_multiplier = bonus_multiplier
        self.update_rect()

    def update_rect(self):
        self.rect = pygame.Rect(
            int(self.x_ratio * WINDOW_WIDTH),
            int(self.y_ratio * WINDOW_HEIGHT),
            int(self.width_ratio * WINDOW_WIDTH),
            int(self.height_ratio * WINDOW_HEIGHT)
        )

class Terrain(pygame.sprite.Sprite):
    def __init__(self, x_ratio, y_ratio, width_ratio, height_ratio):
        super().__init__()
        self.x_ratio = x_ratio
        self.y_ratio = y_ratio
        self.width_ratio = width_ratio
        self.height_ratio = height_ratio
        self.update_rect()

    def update_rect(self):
        self.rect = pygame.Rect(
            int(self.x_ratio * WINDOW_WIDTH),
            int(self.y_ratio * WINDOW_HEIGHT),
            int(self.width_ratio * WINDOW_WIDTH),
            int(self.height_ratio * WINDOW_HEIGHT)
        )


WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
clock = pygame.time.Clock()
FPS = 120

score = 0
start_time = pygame.time.get_ticks()


def reset_game():
    global lander
    lander = Lander([WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2], initial_fuel=1000)


landing_pads = pygame.sprite.Group()
landing_pads.add(LandingPad(30, 20, 20, 20))
landing_pads.add(LandingPad(0.1, 0.7, 0.1, 0.02, bonus_multiplier=2))
landing_pads.add(LandingPad(0.8, 0.5, 0.1, 0.02, bonus_multiplier=3))

terrain_group = pygame.sprite.Group()
terrain_group.add(Terrain(0, 0.95, 1, 0.05))

lander = Lander([WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2], initial_fuel=1000)

def show_main_menu():
    global current_game_state
    # Here, you would typically display the main menu and wait for the player to start the game.
    # For simplicity, let's just switch to the IN_GAME state directly.
    current_game_state = GameState.IN_GAME

current_game_state = GameState.MAIN_MENU

running = True
while running:
    
    if current_game_state == GameState.MAIN_MENU:
            start_button = Button(WINDOW_WIDTH/2 - 100, WINDOW_HEIGHT/2 - 40, 200, 80, 'Start')
            if current_game_state == GameState.MAIN_MENU:
                start_button.draw(screen, (0,0,0))  # screen is your Pygame display surface
                pygame.display.update()
            for event in pygame.event.get():
                pos = pygame.mouse.get_pos()
                
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if current_game_state == GameState.MAIN_MENU:
                        if start_button.is_over(pos):
                            current_game_state = GameState.IN_GAME

    elif current_game_state == GameState.IN_GAME:
        # Handle all the in-game updates, inputs, and rendering
        # This includes moving the lander, checking for collisions, etc.
        screen.fill(BLUE)

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

        lander.draw(screen)
        lander.update_position()
        lander.update_rotation()

        for pad in landing_pads:
            pygame.draw.rect(screen, GREEN, pad.rect)
        for terrain in terrain_group:
            pygame.draw.rect(screen, GREEN, terrain.rect)

        for pad in landing_pads:
            lander.check_collision(pad)
            collision_result_pad = lander.check_collision(pad)
            if collision_result_pad == 'landed' or collision_result_pad == 'crashed':
                current_game_state = GameState.LANDED_CRASHED
        for terrain in terrain_group:
            lander.check_collision(terrain)
            collision_result_terrain = lander.check_collision(pad)
            if collision_result_terrain == 'landed' or collision_result_terrain == 'crashed':
                current_game_state = GameState.LANDED_CRASHED




        font = pygame.font.SysFont("Arial", 18)
        fuel_text = font.render(f"Fuel: {lander.fuel}", True, (255, 255, 255))
        screen.blit(fuel_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                update_window_size(event.w, event.h)

    elif current_game_state == GameState.LANDED_CRASHED:
        # Pause, show results, wait for input, or automatically restart after a delay
        pygame.time.delay(7000)  # For example, a 7-second pause
        current_game_state = GameState.IN_GAME  # Go back to in-game state for this example


pygame.quit()
sys.exit()