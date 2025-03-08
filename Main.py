import pygame
import sys
from Adversary import AdversaryBird  # Import the AdversaryBird class
from Config import *
from Button import *
from MainScreen import *
from InputBox import *
from LeaderBoard import *
from Settings import *
from Utilities import *
from Multiplayer import *
from GameLogic import *



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
    global game_state, player_name, pipe_list, num_adversaries, score, input_box, connection_code
    
    while True:
        if game_state == 'start':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
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
                                    case 'Multiplayer':
                                        game_state = 'multiplayer'
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
                display_score(score)
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
            
        elif game_state == "multiplayer":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                connection_code_input_box.handle_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    # Check difficulty buttons
                    # Check confirm button
                    if connection_button.is_hovered(mouse_pos):
                        # Validate and set the number of adversaries
                        try:
                            connection_code = int(connection_code_input_box.text.strip())
                        except ValueError:
                            connection_code = 0
                        game_state = 'start'
            connection_code_input_box.update()
            multiplayer_screen(connection_code_input_box, connection_button)
            
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
            settings_screen(adversary_input_box, confirm_button)

        pygame.display.update()
        clock.tick(60)


def main():
    global adversary_input_box, connection_code_input_box, difficulty_buttons, confirm_button, input_box, connection_button
    
    pygame.init()
    
    adversary_input_box = InputBox(WIDTH / 2 - 150, HEIGHT / 2 - 120, 300, 40, font, str(num_adversaries))
    connection_code_input_box = InputBox(WIDTH / 2 - 150, HEIGHT / 2 - 120, 300, 40, font, str(connection_code))
    input_box = InputBox(input_box_x, input_box_y, input_box_width, input_box_height, font)
    
    confirm_button = Button('Confirm', (WIDTH / 2 - 125, HEIGHT / 2 + 100), (250, 60), pygame.font.Font(None, 48), WHITE, BLACK)
    connection_button = Button('Connect', (WIDTH / 2 - 125, HEIGHT / 2 + 100), (250, 60), pygame.font.Font(None, 48), WHITE, BLACK)
    
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