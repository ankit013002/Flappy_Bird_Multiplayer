from Config import *
from Utilities import *
import random

def create_pipe():
    """Create a new pair of pipes (top and bottom)."""
    random_pipe_height = random.choice(pipe_height_options)
    gap = 150  # Gap between pipes 
    bottom_pipe = pygame.Rect(WIDTH, random_pipe_height, 80, HEIGHT - random_pipe_height)
    top_pipe = pygame.Rect(WIDTH, 0, 80, random_pipe_height - gap)
    return bottom_pipe, top_pipe

def draw_pipes(pipes):
    """Draw all pipes on the screen with a cool 3D shading and shadow effect."""
    for pipe in pipes:
        pipe_color = (0, 200, 0)
        highlight_color = (0, 255, 0)
        shadow_color = (0, 150, 0)

        pygame.draw.rect(SCREEN, pipe_color, pipe)

        highlight_rect = pygame.Rect(pipe.left, pipe.top, pipe.width * 0.2, pipe.height)
        pygame.draw.rect(SCREEN, highlight_color, highlight_rect)

        shadow_rect = pygame.Rect(pipe.left + pipe.width * 0.8, pipe.top, pipe.width * 0.2, pipe.height)
        pygame.draw.rect(SCREEN, shadow_color, shadow_rect)

        cap_height = 20
        if pipe.top == 0:
            cap_rect = pygame.Rect(pipe.left - 5, pipe.bottom - 10, pipe.width + 10, cap_height)
        else:
            cap_rect = pygame.Rect(pipe.left - 5, pipe.top - cap_height + 10, pipe.width + 10, cap_height)
        pygame.draw.ellipse(SCREEN, pipe_color, cap_rect)

        cap_highlight_rect = pygame.Rect(
            cap_rect.left + cap_rect.width * 0.1,
            cap_rect.top + cap_height * 0.2,
            cap_rect.width * 0.3,
            cap_height * 0.6
        )
        pygame.draw.ellipse(SCREEN, highlight_color, cap_highlight_rect)

        cap_shadow_rect = pygame.Rect(
            cap_rect.left + cap_rect.width * 0.6,
            cap_rect.top + cap_height * 0.2,
            cap_rect.width * 0.3,
            cap_height * 0.6
        )
        pygame.draw.ellipse(SCREEN, shadow_color, cap_shadow_rect)

def move_pipes(pipes):
    """Move pipes to the left and remove them if they go off-screen."""
    for pipe in pipes:
        pipe.centerx -= 5  # Pipe speed
    return [pipe for pipe in pipes if pipe.right > 0]

def check_collision(pipes):
    """Check for collisions between the bird and pipes or boundaries."""
    return next(
        (False for pipe in pipes if bird_rect.colliderect(pipe)),
        bird_rect.top > 0 and bird_rect.bottom < HEIGHT,
    )

def display_score(score):
    """Display the current score on the screen."""
    score_surface = font.render(f'Score: {int(score)}', True, WHITE)
    score_rect = score_surface.get_rect(center=(WIDTH / 2, 50))
    SCREEN.blit(score_surface, score_rect)
