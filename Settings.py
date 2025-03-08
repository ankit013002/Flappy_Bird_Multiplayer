from Config import *
from InputBox import *

def settings_screen(confirm_button):
    global adversary_input_box , difficulty_buttons
    move_background()

    # Ensure adversary_input_box is initialized
    if adversary_input_box is None:
        adversary_input_box = InputBox(WIDTH / 2 - 150, HEIGHT / 2 - 120, 300, 40, font, str(num_adversaries))

    # Draw the prompt for adversary count
    draw_centered_text('Enter number of adversaries (0-99):', 150)
    adversary_input_box.draw(SCREEN)  # ✅ Now it won't fail
    # Draw difficulty selection
    draw_centered_text('Select adversary difficulty:', 50)
    for button in difficulty_buttons:
        button.draw(SCREEN)
    confirm_button.draw(SCREEN)
