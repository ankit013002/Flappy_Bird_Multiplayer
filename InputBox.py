import pygame
from Config import *


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
            self.active = bool(self.rect.collidepoint(event.pos))
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < 20:
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