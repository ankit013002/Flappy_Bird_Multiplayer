from Config import *
from Utilities import *
from InputBox import *

def multiplayer_screen(connection_code_input_box, connection_button):
    move_background()

    # Draw the prompt for adversary count
    draw_centered_text('Enter code to connect to:', 150)
    connection_code_input_box.draw(SCREEN) 
    # Draw difficulty selection
    connection_button.draw(SCREEN)