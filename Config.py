import pygame
import random
import sys
import csv
from datetime import datetime

pygame.init()

# Game constants (independent of pygame)
WIDTH = 1200
HEIGHT = 800
GRAVITY = 0.3

SCREEN = None  # Will initialize later

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)

SPAWNPIPE = pygame.USEREVENT

# Other global variables
game_active = True
leaderboard_file = 'leaderboard.csv'
leaderboard = []
adversaries = []
adversary_difficulty = 'Medium'

bird_movement = 0


clock = None  # Will initialize later
font = None  # Will initialize later
background = None
bird_image = None
bird_rect = None

pygame.time.set_timer(SPAWNPIPE, 1200)
pipe_height_options = [400, 500, 600]


SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Flappy Bird')

# Load images
background = pygame.image.load('background.jpg').convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
background_width = background.get_width()

bird_image = pygame.image.load('bird.png').convert_alpha()
original_width, original_height = bird_image.get_size()
new_width = 70
new_height = int(original_height * new_width / original_width)
bird_image = pygame.transform.scale(bird_image, (new_width, new_height))
bird_rect = bird_image.get_rect(center=(70, HEIGHT / 2))

font = pygame.font.Font(None, 36)

clock = pygame.time.Clock()

bg_x1 = 0
bg_x2 = background_width


adversary_input_box = None
difficulty_levels = ['Easy', 'Medium', 'Hard', 'Godsend', 'Varying']
difficulty_buttons = []
confirm_button = None

connection_code_input_box = None
connection_button = None
connection_code = 0
