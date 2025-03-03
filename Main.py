import pygame
import sys
import random
import csv
from datetime import datetime
from Adversary import AdversaryBird  # Import the AdversaryBird class

pygame.init()

WIDTH = 1200
HEIGHT = 800
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Flappy Bird')

GRAVITY = 0.3
bird_movement = 0
game_active = True
score = 0

WHITE = (255, 255, 255)
GREEN = (0, 200, 0)

background = pygame.image.load('background.jpg').convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
background_width = background.get_width()

bg_x1 = 0
bg_x2 = background_width

bird_image = pygame.image.load('bird.png').convert_alpha()
original_width, original_height = bird_image.get_size()

new_width = 70
new_height = int(original_height * new_width / original_width)

bird_image = pygame.transform.scale(bird_image, (new_width, new_height))
bird_rect = bird_image.get_rect(center=(70, HEIGHT / 2))

pipe_list = []
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1200)
pipe_height_options = [400, 500, 600]

font = pygame.font.Font(None, 36)

game_state = 'start'  # Initialize game state

leaderboard_file = 'leaderboard.csv'
leaderboard = []

num_adversaries = 0  # Default number of AI adversaries
adversaries = []     # List to hold AI birds
adversary_difficulty = 'Medium'  # Default difficulty

def load_leaderboard():
    """Load the leaderboard from the CSV file."""
    try:
        with open(leaderboard_file, mode='r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            return list(reader)
    except FileNotFoundError:
        return []

def save_leaderboard(leaderboard):
    """Save the leaderboard to the CSV file."""
    with open(leaderboard_file, mode='w', newline='') as csvfile:
        fieldnames = ['Name', 'Time', 'Score']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for entry in leaderboard:
            writer.writerow(entry)

leaderboard = load_leaderboard()

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
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            return False
    if bird_rect.top <= 0 or bird_rect.bottom >= HEIGHT:
        return False
    return True

def display_score():
    """Display the current score on the screen."""
    score_surface = font.render(f'Score: {int(score)}', True, WHITE)
    score_rect = score_surface.get_rect(center=(WIDTH / 2, 50))
    SCREEN.blit(score_surface, score_rect)

def move_background():
    global bg_x1, bg_x2
    bg_x1 -= 1
    bg_x2 -= 1

    if bg_x1 <= -background_width:
        bg_x1 = background_width
    if bg_x2 <= -background_width:
        bg_x2 = background_width

    SCREEN.blit(background, (bg_x1, 0))
    SCREEN.blit(background, (bg_x2, 0))

class Button:
    def __init__(self, text, pos, size, font, bg_color, text_color, selected=False):
        self.text = text
        self.pos = pos  # (x, y)
        self.size = size  # (width, height)
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color
        self.rect = pygame.Rect(pos, size)
        self.render_text()
        self.selected = selected  # New attribute

    def render_text(self):
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(
            center=(self.pos[0] + self.size[0] // 2, self.pos[1] + self.size[1] // 2))

    def draw(self, surface):
        # Draw the glass-like button
        button_surface = pygame.Surface(self.size, pygame.SRCALPHA)
        # Change background alpha or color if selected
        if self.selected:
            pygame.draw.rect(button_surface, (*self.bg_color, 200), button_surface.get_rect(), border_radius=12)
            # Optional: Change text color or add border when selected
            # self.text_color = (255, 255, 255)  # White text when selected
        else:
            pygame.draw.rect(button_surface, (*self.bg_color, 100), button_surface.get_rect(), border_radius=12)
            # self.text_color = (0, 0, 0)  # Black text when not selected
        # Draw a highlight
        highlight_rect = pygame.Rect(0, 0, self.size[0], self.size[1] // 2)
        pygame.draw.rect(button_surface, (255, 255, 255, 50), highlight_rect, border_radius=12)
        # Blit the button surface onto the main surface
        surface.blit(button_surface, self.pos)
        # Draw the text
        surface.blit(self.text_surface, self.text_rect)

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

class InputBox:
    def __init__(self, x, y, w, h, font, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = WHITE
        self.text = text
        self.font = font
        self.txt_surface = font.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If user clicked on the input box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = True
            else:
                self.active = False
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if len(self.text) < 20:
                        self.text += event.unicode
                # Re-render the text.
                self.txt_surface = self.font.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(300, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Draw the glass-like input box
        input_surface = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        # Draw a semi-transparent rounded rectangle
        pygame.draw.rect(input_surface, (*self.color, 100), input_surface.get_rect(), border_radius=12)
        # Draw a highlight
        highlight_rect = pygame.Rect(0, 0, self.rect.w, self.rect.h // 2)
        pygame.draw.rect(input_surface, (255, 255, 255, 50), highlight_rect, border_radius=12)
        # Blit the input surface onto the main surface
        screen.blit(input_surface, (self.rect.x, self.rect.y))
        # Blit the text
        text_y = self.rect.y + (self.rect.h - self.txt_surface.get_height()) // 2
        screen.blit(self.txt_surface, (self.rect.x + 5, text_y))
        # Optional: Draw a border around the input box
        # pygame.draw.rect(screen, self.color, self.rect, 2)

# Button parameters
button_width = 250
button_height = 60
button_size = (button_width, button_height)
button_spacing = 20
button_font = pygame.font.Font(None, 48)
button_bg_color = WHITE  # But we will set alpha to make it transparent
button_text_color = (0, 0, 0)  # Black text

button_texts = ['Play', 'Leaderboard', 'Settings', 'Exit']
num_buttons = len(button_texts)
total_height = num_buttons * button_height + (num_buttons - 1) * button_spacing
start_y = (HEIGHT - total_height) / 2 + 100  # Offset 100 pixels down

buttons = []
for i, text in enumerate(button_texts):
    x = (WIDTH - button_width) / 2
    y = start_y + i * (button_height + button_spacing)
    button = Button(text, (x, y), (button_width, button_height), button_font, button_bg_color, button_text_color)
    buttons.append(button)

# Input box parameters
input_box_font = pygame.font.Font(None, 36)
input_box_width = 300
input_box_height = 40
input_box_x = (WIDTH - input_box_width) / 2
input_box_y = 80  # Position above the bird image

input_box = InputBox(input_box_x, input_box_y, input_box_width, input_box_height, input_box_font)

def start_screen():
    move_background()
    # Draw the prompt
    prompt_surface = input_box_font.render('Enter name to save to leaderboard:', True, WHITE)
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
    game_over_surface = font.render('Game Over. Your Score: ' + str(int(score)), True, WHITE)
    game_over_rect = game_over_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2))
    SCREEN.blit(game_over_surface, game_over_rect)
    # Prompt to return to main menu
    prompt_surface = font.render('Press SPACE to return to Main Menu', True, WHITE)
    prompt_rect = prompt_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 50))
    SCREEN.blit(prompt_surface, prompt_rect)

def leaderboard_screen():
    move_background()
    # Display the leaderboard entries
    title_surface = font.render('Leaderboard', True, WHITE)
    title_rect = title_surface.get_rect(center=(WIDTH / 2, 50))
    SCREEN.blit(title_surface, title_rect)

    # Column headers
    name_header = font.render('Name', True, WHITE)
    time_header = font.render('Time', True, WHITE)
    score_header = font.render('Score', True, WHITE)
    SCREEN.blit(name_header, (200, 100))
    SCREEN.blit(time_header, (500, 100))
    SCREEN.blit(score_header, (900, 100))

    # Display entries
    y_offset = 150
    for entry in leaderboard:
        name_text = font.render(entry['Name'], True, WHITE)
        time_text = font.render(entry['Time'], True, WHITE)
        score_text = font.render(entry['Score'], True, WHITE)
        SCREEN.blit(name_text, (200, y_offset))
        SCREEN.blit(time_text, (500, y_offset))
        SCREEN.blit(score_text, (900, y_offset))
        y_offset += 40  # Move down for next entry

def settings_screen():
    move_background()
    # Draw the prompt for adversary count
    prompt_surface = font.render('Enter number of adversaries (0-99):', True, WHITE)
    prompt_rect = prompt_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 150))
    SCREEN.blit(prompt_surface, prompt_rect)
    # Draw the input box for adversary count
    adversary_input_box.draw(SCREEN)
    # Draw the difficulty selection
    difficulty_prompt = font.render('Select adversary difficulty:', True, WHITE)
    difficulty_rect = difficulty_prompt.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 50))
    SCREEN.blit(difficulty_prompt, difficulty_rect)
    # Draw difficulty buttons
    for button in difficulty_buttons:
        button.draw(SCREEN)
    # Draw the confirm button
    confirm_button.draw(SCREEN)

# Input box for adversary count
adversary_input_box = InputBox(WIDTH / 2 - 150, HEIGHT / 2 - 120, 300, 40, input_box_font, str(num_adversaries))

# Difficulty buttons
difficulty_levels = ['Easy', 'Medium', 'Hard', 'Godsend', 'Varying']
difficulty_buttons = []
button_y = HEIGHT / 2
button_x = WIDTH / 2 - (len(difficulty_levels) * 110) / 2  # Adjusted for button width and spacing

for i, level in enumerate(difficulty_levels):
    selected = (level == adversary_difficulty)
    btn = Button(level, (button_x + i * (100 + 10), button_y), (100, 40), input_box_font, button_bg_color, button_text_color, selected=selected)
    difficulty_buttons.append(btn)

# Confirm button for settings
confirm_button = Button('Confirm', (WIDTH / 2 - 125, HEIGHT / 2 + 100), (250, 60), button_font, button_bg_color, button_text_color)

clock = pygame.time.Clock()
player_name = ''
while True:
    if game_state == 'start':
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                input_box.handle_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    for button in buttons:
                        if button.is_hovered(mouse_pos):
                            if button.text == 'Play':
                                # Check if a name has been entered
                                player_name = input_box.text.strip()
                                if player_name == '':
                                    player_name = 'Player'
                                game_state = 'play'
                                game_active = True
                                pipe_list.clear()
                                bird_rect.center = (70, HEIGHT / 2)
                                bird_movement = 0
                                score = 0
                                # Reset input box text
                                input_box.text = ''
                                input_box.txt_surface = input_box.font.render(input_box.text, True, input_box.color)
                                # Create adversaries
                                adversaries = []
                                # for _ in range(num_adversaries):
                                #     x = 70  # Start position
                                #     y = random.randint(100, HEIGHT - 100)
                                #     if adversary_difficulty == 'Varying':
                                #         difficulty = random.choice(['Easy', 'Medium', 'Hard', 'Godsend'])
                                #     else:
                                #         difficulty = adversary_difficulty
                                #     adversary = AdversaryBird(x, y, bird_image, difficulty)
                                #     adversaries.append(adversary)
                                
                                # When creating adversaries (no change needed if already correct)
                                for _ in range(num_adversaries):
                                    x = 70  # Start position
                                    y = random.randint(100, HEIGHT - 100)
                                    if adversary_difficulty == 'Varying':
                                        difficulty = random.choice(['Easy', 'Medium', 'Hard', 'Godsend'])
                                    else:
                                        difficulty = adversary_difficulty
                                    adversary = AdversaryBird(x, y, bird_image, difficulty)
                                    adversaries.append(adversary)
                                    
                            elif button.text == 'Leaderboard':
                                game_state = 'leaderboard'
                            elif button.text == 'Settings':
                                game_state = 'settings'
                            elif button.text == 'Exit':
                                pygame.quit()
                                sys.exit()
        input_box.update()
        start_screen()

    elif game_state == 'play':
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_active:
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

            # Update and draw adversaries
            for adversary in adversaries:
                adversary.update(pipe_list, GRAVITY)
                adversary.draw(SCREEN)

            # Remove dead adversaries
            adversaries = [adv for adv in adversaries if adv.alive]

            if not game_active:
                game_state = 'game_over'
                # Save the player's data to the leaderboard
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                leaderboard_entry = {'Name': player_name, 'Time': current_time, 'Score': str(int(score))}
                leaderboard.append(leaderboard_entry)
                # Sort the leaderboard by score in descending order
                leaderboard.sort(key=lambda x: int(x['Score']), reverse=True)
                save_leaderboard(leaderboard)

            score += 0.01
            display_score()
        else:
            game_state = 'game_over'

    elif game_state == 'game_over':
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_state = 'start'
        game_over_screen()

    elif game_state == 'leaderboard':
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
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
                        if 0 <= value <= 99:
                            num_adversaries = value
                        else:
                            num_adversaries = 0
                    except ValueError:
                        num_adversaries = 0
                    game_state = 'start'
        adversary_input_box.update()
        settings_screen()

    pygame.display.update()
    clock.tick(60)
