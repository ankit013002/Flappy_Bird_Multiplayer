from Config import *
from Utilities import *
from InputBox import *

def settings_screen(adversary_input_box, confirm_button):
    global difficulty_buttons
    move_background()

    # Draw the prompt for adversary count
    draw_centered_text('Enter number of adversaries (0-99):', 150)
    adversary_input_box.draw(SCREEN) 
    # Draw difficulty selection
    draw_centered_text('Select adversary difficulty:', 50)
    for button in difficulty_buttons:
        button.draw(SCREEN)
    confirm_button.draw(SCREEN)
