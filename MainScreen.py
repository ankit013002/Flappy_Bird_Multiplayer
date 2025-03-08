import pygame
from Button import *
from Config import *

buttons = []

def create_main_screen():
    button_font = pygame.font.Font(None, 48)
    button_width = 250
    button_height = 60

    button_spacing = 20
    button_bg_color = WHITE  # But we will set alpha to make it transparent
    button_text_color = (0, 0, 0)  # Black text

    button_texts = ['Play', 'Leaderboard', 'Settings', 'Exit']
    num_buttons = len(button_texts)
    total_height = num_buttons * button_height + (num_buttons - 1) * button_spacing
    start_y = (HEIGHT - total_height) / 2 + 100  # Offset 100 pixels down

    for i, text in enumerate(button_texts):
        x = (WIDTH - button_width) / 2
        y = start_y + i * (button_height + button_spacing)
        button = Button(text, (x, y), (button_width, button_height), button_font, button_bg_color, button_text_color)
        buttons.append(button)
        
        