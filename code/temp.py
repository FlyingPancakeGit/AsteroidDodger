import pygame
import math

pygame.init()

# Screen setup
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Sprite setup (replace with your sprite)
sprite_image = pygame.Surface((50, 50))  # Example sprite
sprite_image.fill((255, 0, 0))  # Red sprite
sprite_rect = sprite_image.get_rect(center=(100, 200))  # Initial position

# Movement variables
speed = 5  # Adjust the speed as needed

def normalize_vector(vector):
    """Normalizes a vector."""
    magnitude = math.sqrt(vector[0]**2 + vector[1]**2)
    if magnitude == 0:
        return (0, 0) #Avoid division by zero
    return (vector[0] / magnitude, vector[1] / magnitude)

def move_towards_center(sprite_rect, screen, speed):
    """Moves a sprite towards the center of the screen."""
    center_x, center_y = screen.get_width() / 2, screen.get_height() / 2
    vector_x = center_x - sprite_rect.centerx
    vector_y = center_y - sprite_rect.centery
    normalized_vector = normalize_vector((vector_x, vector_y))
    sprite_rect.x += normalized_vector[0] * speed
    sprite_rect.y += normalized_vector[1] * speed

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))  # Clear the screen
    move_towards_center(sprite_rect, screen, speed)
    screen.blit(sprite_image, sprite_rect)  # Draw the sprite
    pygame.display.flip()

pygame.quit()