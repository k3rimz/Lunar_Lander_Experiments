# game.py
import pygame
import sys
from enum import Enum
from lander import Lander
from landscape import Landscape
from camera import Camera
from ui import Button
from utils import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, update_window_size, world_to_screen

class GameState(Enum):
    MAIN_MENU = 1
    IN_GAME = 2
    LANDED_CRASHED = 3

def reset_game():
    global lander, camera
    lander = Lander([WINDOW_WIDTH / 2, 50], initial_fuel=1000)
    camera = Camera(WINDOW_WIDTH, WINDOW_HEIGHT)

def main():
    global score, start_time, lander, camera, landscape

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
    clock = pygame.time.Clock()

    # Load assets after pygame.init()
    Lander.load_assets()

    score = 0
    start_time = pygame.time.get_ticks()

    lander = Lander([WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2], initial_fuel=1000)
    landscape = Landscape()
    camera = Camera(WINDOW_WIDTH, WINDOW_HEIGHT)

    current_game_state = GameState.MAIN_MENU

    running = True
    while running:
        if current_game_state == GameState.MAIN_MENU:
            current_game_state = handle_main_menu(screen)
        elif current_game_state == GameState.IN_GAME:
            current_game_state = handle_in_game(screen, clock)
        elif current_game_state == GameState.LANDED_CRASHED:
            current_game_state = handle_landed_crashed()

        if current_game_state is None:
            running = False

    pygame.quit()
    sys.exit()

def handle_main_menu(screen):
    start_button = Button(WINDOW_WIDTH/2 - 100, WINDOW_HEIGHT/2 - 40, 200, 80, 'Start')
    start_button.draw(screen, (0,0,0))
    pygame.display.update()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return None
        if event.type == pygame.MOUSEBUTTONDOWN:
            if start_button.is_over(pygame.mouse.get_pos()):
                return GameState.IN_GAME
    
    return GameState.MAIN_MENU

def handle_in_game(screen, clock):
    global lander, camera, landscape

    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return None
        elif event.type == pygame.VIDEORESIZE:
            screen = update_window_size(event.w, event.h, screen, camera, lander, landscape)

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
        return None

    lander.update_position(landscape.width, landscape.height)
    lander.update_rotation()
    camera.update(lander.position, landscape)

    landscape.render(screen, camera.rect)
    lander.draw(screen, camera, landscape)
    lander.draw_collision_box(screen, camera, landscape)
    lander.draw_metrics(screen, WINDOW_HEIGHT)

    font = pygame.font.SysFont("Arial", 18)
    fuel_text = font.render(f"Fuel: {lander.fuel}", True, (255, 255, 255))
    screen.blit(fuel_text, (10, 10))

    collision_result = lander.check_collision(landscape)
    if collision_result:
        print(collision_result)
        if collision_result in ['landed', 'crashed']:
            return GameState.LANDED_CRASHED

    pygame.display.flip()
    clock.tick(FPS)

    return GameState.IN_GAME

def handle_landed_crashed():
    pygame.time.delay(2000)  # 2-second pause
    reset_game()
    return GameState.IN_GAME

if __name__ == "__main__":
    main()
