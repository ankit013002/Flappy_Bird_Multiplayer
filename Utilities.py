from Config import *

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
    

def draw_centered_text(text, y_offset):
    """Draws centered text on the screen at a given Y offset."""
    prompt_surface = font.render(text, True, WHITE)
    prompt_rect = prompt_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2 - y_offset))
    SCREEN.blit(prompt_surface, prompt_rect)