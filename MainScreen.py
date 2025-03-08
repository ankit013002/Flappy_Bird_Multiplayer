import pygame
from Button import *
from Config import *
from Utilities import *
from InputBox import *

buttons = []

def start_screen():
    global input_box
    move_background()
    # Draw the prompt
    prompt_surface = font.render('Enter name to save to leaderboard:', True, WHITE)
    prompt_rect = prompt_surface.get_rect(center=(WIDTH / 2, input_box_y - 30))
    SCREEN.blit(prompt_surface, prompt_rect)
    # Draw the input box
    if input_box is None:
        input_box = InputBox(input_box_x, input_box_y, input_box_width, input_box_height, font)
    input_box.update()
    input_box.draw(SCREEN)  # Ensure it's redrawn every frame
    # Draw the bird image
    bird_start_rect = bird_image.get_rect(center=(WIDTH / 2, 200))
    SCREEN.blit(bird_image, bird_start_rect)
    # Draw the buttons
    for button in buttons:
        button.draw(SCREEN)

def create_main_screen():
    button_font = pygame.font.Font(None, 48)
    button_width = 250
    button_height = 60

    button_spacing = 20
    button_bg_color = WHITE  # But we will set alpha to make it transparent
    button_text_color = (0, 0, 0)  # Black text

    button_texts = ['Play', 'Multiplayer', 'Leaderboard', 'Settings', 'Exit']
    num_buttons = len(button_texts)
    total_height = num_buttons * button_height + (num_buttons - 1) * button_spacing
    start_y = (HEIGHT - total_height) / 2 + 100  # Offset 100 pixels down

    for i, text in enumerate(button_texts):
        x = (WIDTH - button_width) / 2
        y = start_y + i * (button_height + button_spacing)
        button = Button(text, (x, y), (button_width, button_height), button_font, button_bg_color, button_text_color)
        buttons.append(button)