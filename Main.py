import pygame
import sys
import random
from Adversary import AdversaryBird  # Import the AdversaryBird class
from Config import *
from Button import *
from MainScreen import *
from InputBox import *
from LeaderBoard import *
from Settings import *

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

def display_score():
    """Display the current score on the screen."""
    score_surface = font.render(f'Score: {int(score)}', True, WHITE)
    score_rect = score_surface.get_rect(center=(WIDTH / 2, 50))
    SCREEN.blit(score_surface, score_rect)

def start_screen():
    global input_box
    move_background()
    # Draw the prompt
    prompt_surface = font.render('Enter name to save to leaderboard:', True, WHITE)
    prompt_rect = prompt_surface.get_rect(center=(WIDTH / 2, input_box_y - 30))
    SCREEN.blit(prompt_surface, prompt_rect)
    # Draw the input box
    input_box.draw(SCREEN)
    # Draw the bird image
    bird_start_rect = bird_image.get_rect(center=(WIDTH / 2, 200))
    SCREEN.blit(bird_image, bird_start_rect)
    # Draw the buttons
    for button in buttons:
        button.draw(SCREEN)

def game_over_screen():
    move_background()
    game_over_surface = font.render(f'Game Over. Your Score: {int(score)}', True, WHITE)
    game_over_rect = game_over_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2))
    SCREEN.blit(game_over_surface, game_over_rect)
    # Prompt to return to main menu
    prompt_surface = font.render('Press SPACE to return to Main Menu', True, WHITE)
    prompt_rect = prompt_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 50))
    SCREEN.blit(prompt_surface, prompt_rect)






def main_game_loop():
    global game_state, player_name, pipe_list, num_adversaries, score, input_box
    
    while True:
        if game_state == 'start':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type in [pygame.KEYDOWN or event.type, pygame.MOUSEBUTTONDOWN]:
                    input_box.handle_event(event)
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = event.pos
                        for button in buttons:
                            if button.is_hovered(mouse_pos):
                                match button.text:
                                    case 'Play':
                                        player_name = input_box.text.strip()
                                        if player_name == '':
                                            player_name = 'Player'  # Assign a default name if empty

                                        game_state = 'play'
                                        game_active = True
                                        pipe_list.clear()
                                        bird_rect.center = (70, HEIGHT / 2)
                                        bird_movement = 0
                                        score = 0
                                        # Reset input box text
                                        input_box.text = ''
                                        input_box.txt_surface = input_box.font.render(input_box.text, True, input_box.color)
                                        
                                    case 'Leaderboard':
                                        game_state = 'leaderboard'
                                    case 'Settings':
                                        game_state = 'settings'
                                    case 'Exit':
                                        pygame.quit()
                                        sys.exit()
            input_box.update()
            start_screen()

        elif game_state == 'play':
            
            for event in pygame.event.get():
                
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE and game_active):
                    bird_movement = -6

                if event.type == SPAWNPIPE:
                    pipe_list.extend(create_pipe())

            move_background()

            if game_active:
                bird_movement += GRAVITY
                bird_rect.centery += bird_movement

                SCREEN.blit(bird_image, bird_rect)

                pipe_list = move_pipes(pipe_list)
                draw_pipes(pipe_list)

                game_active = check_collision(pipe_list)

                if not game_active:
                    game_state = 'game_over'
                    update_leader_board(player_name, score)

                score += 0.01
                display_score()
            else:
                game_state = 'game_over'

        elif game_state == 'game_over':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    game_state = 'start'
            game_over_screen()

        elif game_state == 'leaderboard':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
                    game_state = 'start'
            leaderboard_screen()

        elif game_state == 'settings':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                adversary_input_box.handle_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    # Check difficulty buttons
                    for button in difficulty_buttons:
                        if button.is_hovered(mouse_pos):
                            adversary_difficulty = button.text
                            # Update selected state of buttons
                            for btn in difficulty_buttons:
                                btn.selected = (btn.text == adversary_difficulty)
                    # Check confirm button
                    if confirm_button.is_hovered(mouse_pos):
                        # Validate and set the number of adversaries
                        try:
                            value = int(adversary_input_box.text.strip())
                            num_adversaries = value if 0 <= value <= 99 else 0
                        except ValueError:
                            num_adversaries = 0
                        game_state = 'start'
            adversary_input_box.update()
            settings_screen(confirm_button)

        pygame.display.update()
        clock.tick(60)


def main():
    global adversary_input_box, difficulty_buttons, confirm_button, input_box
    
    pygame.init()
    
    adversary_input_box = InputBox(WIDTH / 2 - 150, HEIGHT / 2 - 120, 300, 40, font, str(num_adversaries))
    input_box = InputBox(input_box_x, input_box_y, input_box_width, input_box_height, font)
    
    confirm_button = Button('Confirm', (WIDTH / 2 - 125, HEIGHT / 2 + 100), (250, 60), pygame.font.Font(None, 48), WHITE, BLACK)
    
    # Difficulty buttons
    button_y = HEIGHT / 2
    button_x = WIDTH / 2 - (len(difficulty_levels) * 110) / 2  # Adjusted for button width and spacing

    for i, level in enumerate(difficulty_levels):
        selected = (level == adversary_difficulty)
        btn = Button(level, (button_x + i * (100 + 10), button_y), (100, 40), font, WHITE, BLACK, selected=selected)
        difficulty_buttons.append(btn)
    

    create_main_screen()
    
    main_game_loop()

if __name__ == "__main__":
    main()