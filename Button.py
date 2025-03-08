import pygame
from Config import *

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

    