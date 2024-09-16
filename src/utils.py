import pygame

WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
FPS = 120

BLUE = (0, 0, 122)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

def world_to_screen(pos, camera, landscape):
    x = (pos[0] - camera.rect.left + landscape.width) % landscape.width
    y = pos[1] - camera.rect.top
    return (x, y)

def update_window_size(width, height, screen, camera, lander, landscape):
    global WINDOW_WIDTH, WINDOW_HEIGHT
    WINDOW_WIDTH = width
    WINDOW_HEIGHT = height
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
    
    # Update camera
    camera.width = WINDOW_WIDTH
    camera.height = WINDOW_HEIGHT
    camera.rect.width = WINDOW_WIDTH
    camera.rect.height = WINDOW_HEIGHT
    
    # Update camera position to keep lander in view
    camera.rect.center = lander.position
    
    # Ensure camera stays within landscape bounds
    camera.rect.top = max(0, min(camera.rect.top, landscape.height - camera.rect.height))
    camera.rect.left = camera.rect.left % landscape.width  # Wrap horizontally
    
    return screen