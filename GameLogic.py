from Config import *
from Utilities import *
import random


def create_pipe():
    """Create a pair of pipes (upper and lower) for the game."""
    random_pipe_pos = random.choice(pipe_height_options)
    gap = 200  # Gap between upper and lower pipes

    # Bottom pipe
    bottom_pipe = pygame.Rect(WIDTH, random_pipe_pos, 80, 800)
    # Top pipe (flipped, positioned with a gap)
    top_pipe = pygame.Rect(WIDTH, random_pipe_pos - gap - 800, 80, 800)

    return [bottom_pipe, top_pipe]


def move_pipes(pipes):
    """Move pipes to the left and remove them when they're off screen."""
    for pipe in pipes:
        pipe.x -= 5  # Speed of pipes moving left

    # Remove pipes that have moved off screen
    visible_pipes = [pipe for pipe in pipes if pipe.x > -100]
    return visible_pipes


def draw_pipes(pipes):
    """Draw all pipes on the screen."""
    pipe_color = (0, 153, 0)  # Green color for pipes

    for pipe in pipes:
        pygame.draw.rect(SCREEN, pipe_color, pipe)


def check_collision(pipes):
    """Check if the bird has collided with any pipes or the screen boundaries."""
    if bird_rect.top <= 0 or bird_rect.bottom >= HEIGHT:
        return False  # Collision with top or bottom of screen

    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            return False  # Collision with pipe

    return True  # No collision


def display_score(score):
    """Display the current score on the screen."""
    score_text = font.render(f"Score: {int(score)}", True, WHITE)
    SCREEN.blit(score_text, (WIDTH - 200, 20))


def play_state(pipe_list, score):
    """Main game logic for single player mode."""
    global bird_movement, game_active

    game_state = 'play'

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_active:
                bird_movement = -6
            if event.key == pygame.K_ESCAPE:
                game_state = 'start'
        if event.type == SPAWNPIPE and game_active:
            pipe_list.extend(create_pipe())

    # Game logic
    move_background()

    if game_active:
        # Bird movement
        bird_movement += GRAVITY
        bird_rect.centery += bird_movement
        SCREEN.blit(bird_image, bird_rect)

        # Pipes
        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)

        # Collision detection
        game_active = check_collision(pipe_list)

        # Score
        score += 0.01
        display_score(score)
    else:
        game_state = 'game_over'

    return game_state, score
