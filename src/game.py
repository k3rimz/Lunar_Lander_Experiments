import random
import pygame
import sys
import math
from enum import Enum
from landscape import Landscape, LandscapeLine, Vector2


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
        self.position[0] = self.position[0] % landscape.width
        self.position[1] = max(0, min(self.position[1], landscape.height))

    def check_collision(self, landscape):
        lander_rect = pygame.Rect(self.position[0] - self.size, self.position[1] - self.size, self.size * 2, self.size * 2)

        # Calculate which tile the lander is in
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

    def handle_landing(self, obj):
        if not self.landed:
            print("Landing successful.")
            self.velocity = [0, 0]
            self.landed = True
            if not self.score_added:
                multiplier = obj.multiplier if hasattr(obj, 'multiplier') else obj.bonus_multiplier
                self.update_score(100 * multiplier)
                self.fuel += 100 + (100 * multiplier)
                self.fuel = min(self.fuel, 1000)
                self.score_added = True
                if isinstance(obj, LandscapeLine):
                    self.position[1] = obj.p1.y - self.size
                elif isinstance(obj, LandingPad):
                    self.position[1] = obj.rect.top - self.size
            return 'landed'
        else:
            print("Lander already landed.")
            return None

    def draw_collision_box(self, surface, camera):
        points = [
            (self.position[0] + self.size * math.sin(math.radians(self.angle)), self.position[1] - self.size * math.cos(math.radians(self.angle))),
            (self.position[0] - self.size * math.sin(math.radians(self.angle + 120)), self.position[1] + self.size * math.cos(math.radians(self.angle + 120))),
            (self.position[0] - self.size * math.sin(math.radians(self.angle - 120)), self.position[1] + self.size * math.cos(math.radians(self.angle - 120))),
        ]

        adjusted_points = [world_to_screen(p, camera, landscape) for p in points]
        pygame.draw.polygon(surface, (255, 0, 0), adjusted_points, 2)

    def reset_position(self):
        self.position = [random.randint(0, WINDOW_WIDTH), -self.size]  # Start above the visible area
        self.velocity = [0, 0]
        self.landed = False
        self.score_added = False  # Reset score flag for next landing or crash
        
    def draw(self, surface, camera):
        screen_pos = world_to_screen(self.position, camera, landscape)
        lander_icon = pygame.image.load("assets/lander.png").convert_alpha()
        rotated_icon = pygame.transform.rotate(lander_icon, -self.angle)
        icon_rect = rotated_icon.get_rect(center=screen_pos)
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
    def __init__(self, x, y, width, height, bonus_multiplier=1):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.bonus_multiplier = bonus_multiplier

class LandingPad(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, bonus_multiplier=1):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.bonus_multiplier = bonus_multiplier


class Camera:
    def __init__(self, width, height):
        self.rect = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def update(self, target_pos, landscape):
        # Center the camera on the target
        self.rect.centerx = target_pos[0]
        self.rect.centery = target_pos[1]

        # Vertical clamping
        if self.rect.top < 0:
            self.rect.top = 0
        elif self.rect.bottom > landscape.height:
            self.rect.bottom = landscape.height

        # Horizontal wrapping
        if self.rect.left < 0:
            self.rect.left += landscape.width
        elif self.rect.right > landscape.width:
            self.rect.left -= landscape.width


def world_to_screen(pos, camera, landscape):
    x = (pos[0] - camera.rect.left) % landscape.width
    y = pos[1] - camera.rect.top
    return (x, y)


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
    global lander, camera
    lander = Lander([WINDOW_WIDTH / 2, 50], initial_fuel=1000)
    camera = Camera(WINDOW_WIDTH, WINDOW_HEIGHT)



lander = Lander([WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2], initial_fuel=1000)
landscape = Landscape()
camera = Camera(WINDOW_WIDTH, WINDOW_HEIGHT)

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

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                WINDOW_WIDTH, WINDOW_HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
                camera.width, camera.height = WINDOW_WIDTH, WINDOW_HEIGHT

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

        # Update lander, landscape, camera
        lander.update_position()
        lander.update_rotation()
        camera.update(lander.position, landscape)


        screen.fill((0, 0, 0))
        landscape.render(screen, camera.rect)
        lander.draw(screen, camera)
        lander.draw_collision_box(screen, camera)  
        lander.draw_metrics(screen)

        collision_result = lander.check_collision(landscape)
        if collision_result:
            print(collision_result)
            lander = Lander([lander.position[0], 50])  # Reset vertical position but keep horizontal

        if collision_result == 'landed':
            current_game_state = GameState.LANDED_CRASHED
            print("Landed successfully!")
        elif collision_result == 'crashed':
            current_game_state = GameState.LANDED_CRASHED
            print("Crashed!")

        landscape.render(screen, camera.rect)
        lander_screen_pos = (
                lander.position[0] - camera.rect.left,
                lander.position[1] - camera.rect.top
            )


        font = pygame.font.SysFont("Arial", 18)
        fuel_text = font.render(f"Fuel: {lander.fuel}", True, (255, 255, 255))
        screen.blit(fuel_text, (10, 10))


        
        pygame.display.flip()
        clock.tick(FPS)


        

    elif current_game_state == GameState.LANDED_CRASHED:
        # Pause, show results, wait for input, or automatically restart after a delay
        pygame.time.delay(1)  # For example, a 7-second pause
        current_game_state = GameState.IN_GAME  # Go back to in-game state for this example


pygame.quit()
sys.exit()