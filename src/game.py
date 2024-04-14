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

    def update_position(self):
        if self.landed:
            # Skip position and velocity updates if landed to prevent bobbing or phasing through.
            return
        self.velocity[1] += self.gravity
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]
        self.position[0] = max(0, min(self.position[0], game_map.width))
        self.position[1] = max(0, min(self.position[1], game_map.height))

    def check_collision(self, platform):
        # Create a rect for the lander based on its position and size
        lander_rect = pygame.Rect(self.position[0] - self.size, self.position[1] - self.size, self.size * 2, self.size * 2)

        # Check if the lander's rect collides with the platform's rect
        if lander_rect.colliderect(platform.rect):
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
                        self.position[1] = platform.rect.top - self.size  # Adjust the lander's position to sit on the platform
                        return 'landed'
                else:
                    print("Lander already landed.")
                return  # Exit the method after a successful landing
            else:
                # Crash scenario
                self.velocity = [0, 0]  # Stop the lander's motion
                print("Crash! Game Over.")
                return 'crashed'

        # Reset the flags if not touching any platform
        self.landed = False
        self.score_added = False

    def draw_collision_box(self, surface, camera):
        # Calculate the corners of the lander's collision box
        points = [
            (self.position[0] + self.size * math.sin(math.radians(self.angle)), self.position[1] - self.size * math.cos(math.radians(self.angle))),
            (self.position[0] - self.size * math.sin(math.radians(self.angle + 120)), self.position[1] + self.size * math.cos(math.radians(self.angle + 120))),
            (self.position[0] - self.size * math.sin(math.radians(self.angle - 120)), self.position[1] + self.size * math.cos(math.radians(self.angle - 120))),
        ]

        # Adjust the points based on the camera position
        adjusted_points = [(x - camera.position[0], y - camera.position[1]) for x, y in points]

        # Draw the collision box
        pygame.draw.polygon(surface, (255, 0, 0), adjusted_points, 2)

    def reset_position(self):
        self.position = [random.randint(0, WINDOW_WIDTH), -self.size]  # Start above the visible area
        self.velocity = [0, 0]
        self.landed = False
        self.score_added = False  # Reset score flag for next landing or crash
        
    def draw(self, surface, camera):
        # Load the lander icon image with transparency
        lander_icon = pygame.image.load("assets/lander.png").convert_alpha()

        # Rotate the lander icon based on the current angle
        rotated_icon = pygame.transform.rotate(lander_icon, -self.angle)

        # Calculate the position to draw the rotated lander icon relative to the camera
        icon_rect = rotated_icon.get_rect(center=(self.position[0] - camera.position[0], self.position[1] - camera.position[1]))

        # Draw the rotated lander icon on the surface
        surface.blit(rotated_icon, icon_rect)

        # Draw the metrics, score, and time
        self.draw_metrics(surface, camera)
        self.draw_score(surface, camera)
        self.draw_time(surface, camera)

    def draw_metrics(self, surface, camera):
        font = pygame.font.SysFont("Arial", 18)
        altitude_text = font.render(f"Altitude: {int(WINDOW_HEIGHT - self.position[1] + camera.position[1])}", True, (255, 255, 255))
        horizontal_speed_text = font.render(f"Horizontal Speed: {int(self.velocity[0])}", True, (255, 255, 255))
        vertical_speed_text = font.render(f"Vertical Speed: {int(self.velocity[1])}", True, (255, 255, 255))
        surface.blit(altitude_text, (10, 30))
        surface.blit(horizontal_speed_text, (10, 50))
        surface.blit(vertical_speed_text, (10, 70))

    def update_score(self, points):
        global score
        score += points

    def draw_score(self, surface, camera):
        font = pygame.font.SysFont("Arial", 18)
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        surface.blit(score_text, (10, 90))

    def draw_time(self, surface, camera):
        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - start_time) // 1000
        font = pygame.font.SysFont("Arial", 18)
        time_text = font.render(f"Time: {elapsed_time}", True, (255, 255, 255))
        surface.blit(time_text, (10, 110))

BLUE = (0, 0, 122)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

def update_window_size(width, height):
    global WINDOW_WIDTH, WINDOW_HEIGHT, screen, lander, camera
    WINDOW_WIDTH = width
    WINDOW_HEIGHT = height
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
    camera.width = WINDOW_WIDTH
    camera.height = WINDOW_HEIGHT
    camera.rect.width = WINDOW_WIDTH
    camera.rect.height = WINDOW_HEIGHT
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
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)

class LandingPad(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, bonus_multiplier=1):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.bonus_multiplier = bonus_multiplier


class Camera:
    def __init__(self, position, width, height):
        self.position = position
        self.width = width
        self.height = height
        self.rect = pygame.Rect(position[0], position[1], width, height)

    def update(self, target_position):
        # Calculate the new camera position based on the target position
        new_camera_x = target_position[0] - self.width // 2
        new_camera_y = target_position[1] - self.height // 2

        # Clamp the camera position to stay within the game map boundaries
        new_camera_x = max(0, min(new_camera_x, game_map.width - self.width))
        new_camera_y = max(0, min(new_camera_y, game_map.height - self.height))

        # Smoothly interpolate between the current camera position and the new position
        smoothing_factor = 0.1
        self.position = (
            self.position[0] + (new_camera_x - self.position[0]) * smoothing_factor,
            self.position[1] + (new_camera_y - self.position[1]) * smoothing_factor
        )

        # Update the camera rect
        self.rect.x = self.position[0]
        self.rect.y = self.position[1]


class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.terrain = pygame.sprite.Group()
        self.landing_pads = pygame.sprite.Group()

    def generate(self):
        # Generate terrain
        self.terrain.add(Terrain(0, self.height - 50, self.width, 50))  # Ground
        self.terrain.add(Terrain(200, self.height - 200, 100, 50))  # Platform 1
        self.terrain.add(Terrain(500, self.height - 300, 100, 50))  # Platform 2

        # Generate landing pads
        self.landing_pads.add(LandingPad(250, self.height - 250, 50, 10, bonus_multiplier=2))
        self.landing_pads.add(LandingPad(550, self.height - 350, 50, 10, bonus_multiplier=3))


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



lander = Lander([WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2], initial_fuel=1000)
camera = Camera((0, 0), WINDOW_WIDTH, WINDOW_HEIGHT)
game_map = Map(2000, 1000)  # Example map size
game_map.generate()

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


        # Draw lander,pad,terrain collision
        relative_lander_pos = (lander.position[0] - camera.position[0], lander.position[1] - camera.position[1])
        lander.draw(screen, camera)
        lander.draw_collision_box(screen, camera)  # Draw lander's collision box

        lander.draw(screen, camera)
        lander.update_position()
        lander.update_rotation()
        '''
        for pad in landing_pads:
            pygame.draw.rect(screen, GREEN, pad.rect)
        for terrain in terrain_group:
            pygame.draw.rect(screen, GREEN, terrain.rect)
        '''
        for terrain in game_map.terrain:
            if camera.rect.colliderect(terrain.rect):
                relative_pos = (terrain.rect.x - camera.position[0], terrain.rect.y - camera.position[1])
                pygame.draw.rect(screen, GREEN, pygame.Rect(relative_pos, terrain.rect.size))

        for pad in game_map.landing_pads:
            if camera.rect.colliderect(pad.rect):
                relative_pos = (pad.rect.x - camera.position[0], pad.rect.y - camera.position[1])
                pygame.draw.rect(screen, GREEN, pygame.Rect(relative_pos, pad.rect.size))

        for pad in game_map.landing_pads:
            lander.check_collision(pad)
            collision_result_pad = lander.check_collision(pad)
            if collision_result_pad == 'landed' or collision_result_pad == 'crashed':
                current_game_state = GameState.LANDED_CRASHED
        for terrain in game_map.terrain:
            lander.check_collision(terrain)
            collision_result_terrain = lander.check_collision(terrain)
            if collision_result_terrain == 'landed' or collision_result_terrain == 'crashed':
                current_game_state = GameState.LANDED_CRASHED
        # Update camera position based on lander
        camera.update(lander.position)



        for terrain in game_map.terrain:
            if camera.rect.colliderect(terrain.rect):
                relative_pos = (terrain.rect.x - camera.position[0], terrain.rect.y - camera.position[1])
                pygame.draw.rect(screen, GREEN, pygame.Rect(relative_pos, terrain.rect.size))
                pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(relative_pos, terrain.rect.size), 2)  # Draw collision box

        for pad in game_map.landing_pads:
            if camera.rect.colliderect(pad.rect):
                relative_pos = (pad.rect.x - camera.position[0], pad.rect.y - camera.position[1])
                pygame.draw.rect(screen, GREEN, pygame.Rect(relative_pos, pad.rect.size))
                pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(relative_pos, pad.rect.size), 2)  # Draw collision box
        ###DEBUG
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
        pygame.time.delay(1)  # For example, a 7-second pause
        current_game_state = GameState.IN_GAME  # Go back to in-game state for this example


pygame.quit()
sys.exit()